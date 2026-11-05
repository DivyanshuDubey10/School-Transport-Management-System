import os
import sys
import psycopg2
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

TEST_DB_NAME = "neoyatra_test_phase2a"

# Configure environment to point to disposable test database
os.environ["DB_NAME"] = TEST_DB_NAME
os.environ["ENVIRONMENT"] = "development"

import database
import security
from dal import db_dal
from main import app
from middleware.rate_limiter import reset_all_rate_limits

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module", autouse=True)
def setup_disposable_database():
    """Create a completely isolated disposable PostgreSQL database for live integration tests."""
    # 1. Connect to default postgres to create test db
    admin_conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname="postgres",
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )
    admin_conn.autocommit = True
    cur = admin_conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME};")
    cur.execute(f"CREATE DATABASE {TEST_DB_NAME};")
    cur.close()
    admin_conn.close()

    # 2. Initialize schema tables in the test database
    database.initialize_database()

    # 3. Seed real records into test database
    conn = database.connect_database()
    cursor = conn.cursor()

    # Legacy plaintext admin
    cursor.execute(
        "INSERT INTO admin (USERNAME, password, full_name) VALUES (%s, %s, %s) RETURNING admin_id;",
        ("legacyadmin", "PlaintextSecret123!", "Legacy Admin User")
    )
    admin_id = cursor.fetchone()[0]

    # Bcrypt admin
    cursor.execute(
        "INSERT INTO admin (USERNAME, password, full_name) VALUES (%s, %s, %s) RETURNING admin_id;",
        ("secureadmin", security.hash_password("SecureAdmin123!"), "Secure Admin")
    )

    # Routes
    cursor.execute("INSERT INTO route (route_name) VALUES ('North Route') RETURNING route_id;")
    route1_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO route (route_name) VALUES ('South Route') RETURNING route_id;")
    route2_id = cursor.fetchone()[0]

    # Buses / Drivers
    cursor.execute(
        "INSERT INTO bus (bus_number, driver_name, driver_phone, capacity, route_id, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING bus_id;",
        ("BUS-N1", "Driver North", "9000000001", 30, route1_id, "drivernorth", security.hash_password("DriverNorth123!"))
    )
    bus1_id = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO bus (bus_number, driver_name, driver_phone, capacity, route_id, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING bus_id;",
        ("BUS-S2", "Driver South", "9000000002", 30, route2_id, "driversouth", security.hash_password("DriverSouth123!"))
    )
    bus2_id = cursor.fetchone()[0]

    # Parents
    cursor.execute(
        "INSERT INTO parent (parent_name, phone, address, pickup_point, username, password) VALUES (%s, %s, %s, %s, %s, %s) RETURNING parent_id;",
        ("Parent Alpha", "9111111111", "Alpha St", "Stop Alpha", "parentalpha", security.hash_password("ParentAlpha123!"))
    )
    parent1_id = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO parent (parent_name, phone, address, pickup_point, username, password) VALUES (%s, %s, %s, %s, %s, %s) RETURNING parent_id;",
        ("Parent Beta", "9222222222", "Beta Ave", "Stop Beta", "parentbeta", security.hash_password("ParentBeta123!"))
    )
    parent2_id = cursor.fetchone()[0]

    # Students: Student 1 -> Parent 1 on Route 1 (Bus 1); Student 2 -> Parent 2 on Route 2 (Bus 2)
    cursor.execute(
        "INSERT INTO student (student_name, student_class, parent_id, route_id, fee_paid, fee_balance, transport_status) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING student_id;",
        ("Child Alpha", "5th Grade", parent1_id, route1_id, 1000.0, 0.0, "Active")
    )
    student1_id = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO student (student_name, student_class, parent_id, route_id, fee_paid, fee_balance, transport_status) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING student_id;",
        ("Child Beta", "6th Grade", parent2_id, route2_id, 1000.0, 0.0, "Active")
    )
    student2_id = cursor.fetchone()[0]

    # Attendance
    cursor.execute(
        "INSERT INTO attendance (student_id, bus_id, date, status) VALUES (%s, %s, %s, %s);",
        (student1_id, bus1_id, "2026-11-05", "Present")
    )
    cursor.execute(
        "INSERT INTO attendance (student_id, bus_id, date, status) VALUES (%s, %s, %s, %s);",
        (student2_id, bus2_id, "2026-11-05", "Absent")
    )

    conn.commit()
    cursor.close()
    conn.close()

    yield {
        "admin_id": admin_id,
        "parent1_id": parent1_id,
        "parent2_id": parent2_id,
        "student1_id": student1_id,
        "student2_id": student2_id,
        "bus1_id": bus1_id,
        "bus2_id": bus2_id,
    }

    # 4. Teardown: Drop test database
    try:
        cleanup_conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname="postgres",
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
        )
        cleanup_conn.autocommit = True
        c = cleanup_conn.cursor()
        c.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid();
        """)
        c.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME};")
        c.close()
        cleanup_conn.close()
    except Exception as e:
        print(f"Warning: could not drop test database: {e}")


@pytest.fixture(autouse=True)
def clean_rate_limits():
    reset_all_rate_limits()
    yield
    reset_all_rate_limits()


class TestLivePostgreSQLIntegration:
    def test_live_db_legacy_plaintext_migration(self):
        """Verify that authenticating a legacy plaintext user in real PostgreSQL upgrades password column to bcrypt."""
        # 1. Verify before login it is stored as plaintext
        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("SELECT password FROM admin WHERE USERNAME = 'legacyadmin';")
        stored_before = cur.fetchone()[0]
        cur.close()
        conn.close()
        assert stored_before == "PlaintextSecret123!"

        # 2. Login through the API
        resp = client.post("/api/v1/auth/login", json={"username": "legacyadmin", "password": "PlaintextSecret123!"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

        # 3. Verify in PostgreSQL that the password was replaced with a bcrypt hash
        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("SELECT password FROM admin WHERE USERNAME = 'legacyadmin';")
        stored_after = cur.fetchone()[0]
        cur.close()
        conn.close()

        assert stored_after != "PlaintextSecret123!"
        assert security.is_bcrypt_hash(stored_after)
        assert security.verify_password("PlaintextSecret123!", stored_after)

    def test_live_db_failed_login_does_not_modify_credentials(self):
        """Verify that an incorrect password login does not modify the database."""
        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("SELECT password FROM admin WHERE USERNAME = 'secureadmin';")
        hash_before = cur.fetchone()[0]
        cur.close()
        conn.close()

        resp = client.post("/api/v1/auth/login", json={"username": "secureadmin", "password": "WrongPassword99!"})
        assert resp.status_code == 401

        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("SELECT password FROM admin WHERE USERNAME = 'secureadmin';")
        hash_after = cur.fetchone()[0]
        cur.close()
        conn.close()

        assert hash_before == hash_after

    def test_live_db_password_change_flow(self):
        """Verify that changing password updates the hash in PostgreSQL and allows subsequent login."""
        # Login to get token
        login_resp = client.post("/api/v1/auth/login", json={"username": "secureadmin", "password": "SecureAdmin123!"})
        token = login_resp.json()["access_token"]

        # Change password
        change_resp = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "SecureAdmin123!", "new_password": "UpdatedSecurePass123!"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert change_resp.status_code == 200

        # Login with old password fails
        fail_resp = client.post("/api/v1/auth/login", json={"username": "secureadmin", "password": "SecureAdmin123!"})
        assert fail_resp.status_code == 401

        # Login with new password succeeds
        ok_resp = client.post("/api/v1/auth/login", json={"username": "secureadmin", "password": "UpdatedSecurePass123!"})
        assert ok_resp.status_code == 200

    def test_live_db_object_level_authorization_attendance(self, setup_disposable_database):
        """Verify parent and driver object-level ownership constraints against real PostgreSQL data."""
        data = setup_disposable_database
        student1_id = data["student1_id"]
        student2_id = data["student2_id"]

        # Login as Parent Alpha (Parent 1)
        p1_login = client.post("/api/v1/auth/login", json={"username": "parentalpha", "password": "ParentAlpha123!"})
        p1_token = p1_login.json()["access_token"]

        # Parent 1 querying own child (Student 1) -> 200 OK
        resp_own = client.get(f"/api/v1/attendance/student/{student1_id}", headers={"Authorization": f"Bearer {p1_token}"})
        assert resp_own.status_code == 200
        records = resp_own.json()
        assert len(records) >= 1
        assert records[0]["attendance_status"] == "Present"

        # Parent 1 querying other family's child (Student 2) -> 403 Forbidden
        resp_other = client.get(f"/api/v1/attendance/student/{student2_id}", headers={"Authorization": f"Bearer {p1_token}"})
        assert resp_other.status_code == 403

    def test_live_db_object_level_authorization_change_request(self, setup_disposable_database):
        """Verify parent change request ownership against real PostgreSQL data."""
        data = setup_disposable_database
        student1_id = data["student1_id"]
        student2_id = data["student2_id"]

        p1_login = client.post("/api/v1/auth/login", json={"username": "parentalpha", "password": "ParentAlpha123!"})
        p1_token = p1_login.json()["access_token"]

        # Parent 1 submitting for own child (Student 1) -> 201 Created
        resp_own = client.post(
            "/api/v1/requests",
            json={"student_id": student1_id, "requested_pickup_point": "New Alpha Gate"},
            headers={"Authorization": f"Bearer {p1_token}"},
        )
        assert resp_own.status_code == 201

        # Parent 1 submitting for other child (Student 2) -> 403 Forbidden
        resp_other = client.post(
            "/api/v1/requests",
            json={"student_id": student2_id, "requested_pickup_point": "Malicious Transfer"},
            headers={"Authorization": f"Bearer {p1_token}"},
        )
        assert resp_other.status_code == 403

    def test_live_db_object_level_authorization_tracking(self, setup_disposable_database):
        """Verify bus tracking ownership against real PostgreSQL relations."""
        data = setup_disposable_database
        bus1_id = data["bus1_id"]
        bus2_id = data["bus2_id"]

        p1_login = client.post("/api/v1/auth/login", json={"username": "parentalpha", "password": "ParentAlpha123!"})
        p1_token = p1_login.json()["access_token"]

        # Parent 1 can track Bus 1 (carrying their child) -> 200 OK
        resp_b1 = client.get(f"/api/v1/tracking/bus/{bus1_id}", headers={"Authorization": f"Bearer {p1_token}"})
        assert resp_b1.status_code == 200
        assert resp_b1.json()["bus_id"] == bus1_id

        # Parent 1 cannot track Bus 2 (no children on Bus 2) -> 403 Forbidden
        resp_b2 = client.get(f"/api/v1/tracking/bus/{bus2_id}", headers={"Authorization": f"Bearer {p1_token}"})
        assert resp_b2.status_code == 403

        # Driver North can only track Bus 1 -> 200 OK; Bus 2 -> 403 Forbidden
        d1_login = client.post("/api/v1/auth/login", json={"username": "drivernorth", "password": "DriverNorth123!"})
        d1_token = d1_login.json()["access_token"]

        assert client.get(f"/api/v1/tracking/bus/{bus1_id}", headers={"Authorization": f"Bearer {d1_token}"}).status_code == 200
        assert client.get(f"/api/v1/tracking/bus/{bus2_id}", headers={"Authorization": f"Bearer {d1_token}"}).status_code == 403

