import os
import sys
import uuid
import datetime
import psycopg2
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

ORIGINAL_DB_NAME = os.environ.get("DB_NAME", "stms_db")
TEST_DB_NAME = "neoyatra_test_phase2b"

os.environ["ENVIRONMENT"] = "development"

import database
import security
from dal import db_dal
from main import app
from middleware.rate_limiter import reset_all_rate_limits
from middleware.db_retry import with_psycopg2_retry

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module", autouse=True)
def setup_disposable_database():
    """Create a completely isolated disposable PostgreSQL database for live Phase 2B integration tests."""
    old_db = os.environ.get("DB_NAME", "stms_db")
    os.environ["DB_NAME"] = TEST_DB_NAME

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

    # Apply all Alembic migrations (0001 -> 0005)
    database.initialize_database()

    # Seed test entities across 2 active schools and 1 suspended school
    conn = database.connect_database()
    cursor = conn.cursor()

    # School A
    cursor.execute("""
        INSERT INTO school (school_code, school_name, is_active, timezone)
        VALUES ('SCH_A', 'Alpha Academy', TRUE, 'Asia/Kolkata')
        RETURNING school_id;
    """)
    school_a_id = cursor.fetchone()[0]

    # School B
    cursor.execute("""
        INSERT INTO school (school_code, school_name, is_active, timezone)
        VALUES ('SCH_B', 'Beta High', TRUE, 'Asia/Kolkata')
        RETURNING school_id;
    """)
    school_b_id = cursor.fetchone()[0]

    # Suspended School
    cursor.execute("""
        INSERT INTO school (school_code, school_name, is_active, timezone)
        VALUES ('SCH_SUSP', 'Suspended Institution', FALSE, 'Asia/Kolkata')
        RETURNING school_id;
    """)
    school_susp_id = cursor.fetchone()[0]

    # School A Service Area (Delhi coordinates)
    cursor.execute("""
        INSERT INTO school_service_area (school_id, area_name, bbox_lat_min, bbox_lat_max, bbox_lng_min, bbox_lng_max, is_active)
        VALUES (%s, 'Delhi NCR Metropolitan', 28.4000, 28.9000, 77.0000, 77.5000, TRUE);
    """, (school_a_id,))

    # School A Route & Stops
    cursor.execute("""
        INSERT INTO route (school_id, route_name)
        VALUES (%s, 'Alpha Route 1')
        RETURNING route_id;
    """, (school_a_id,))
    route_a_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO route_stop (school_id, route_id, stop_name, sequence, latitude, longitude, stop_type, geofence_radius_m)
        VALUES
        (%s, %s, 'Alpha School Campus', 1, 28.6139, 77.2090, 'school', 100),
        (%s, %s, 'Alpha Stop 1', 2, 28.6200, 77.2150, 'stop', 50),
        (%s, %s, 'Alpha Stop 2', 3, 28.6300, 77.2250, 'stop', 50);
    """, (school_a_id, route_a_id, school_a_id, route_a_id, school_a_id, route_a_id))

    # School B Route
    cursor.execute("""
        INSERT INTO route (school_id, route_name)
        VALUES (%s, 'Beta Route 1')
        RETURNING route_id;
    """, (school_b_id,))
    route_b_id = cursor.fetchone()[0]

    # School A Bus (with driver credentials)
    cursor.execute("""
        INSERT INTO bus (school_id, bus_number, driver_name, driver_phone, capacity, route_id, username, password)
        VALUES (%s, 'BUS-A1', 'Driver Alpha', '9800000001', 40, %s, 'driver_a', %s)
        RETURNING bus_id;
    """, (school_a_id, route_a_id, security.hash_password("DriverAlpha123!")))
    bus_a_id = cursor.fetchone()[0]

    # School B Bus
    cursor.execute("""
        INSERT INTO bus (school_id, bus_number, driver_name, driver_phone, capacity, route_id, username, password)
        VALUES (%s, 'BUS-B1', 'Driver Beta', '9800000002', 35, %s, 'driver_b', %s)
        RETURNING bus_id;
    """, (school_b_id, route_b_id, security.hash_password("DriverBeta123!")))
    bus_b_id = cursor.fetchone()[0]

    # School A Admin
    cursor.execute("""
        INSERT INTO admin (school_id, USERNAME, password, full_name)
        VALUES (%s, 'admin_a', %s, 'Admin Alpha')
        RETURNING admin_id;
    """, (school_a_id, security.hash_password("AdminAlpha123!")))
    admin_a_id = cursor.fetchone()[0]

    # School B Admin
    cursor.execute("""
        INSERT INTO admin (school_id, USERNAME, password, full_name)
        VALUES (%s, 'admin_b', %s, 'Admin Beta')
        RETURNING admin_id;
    """, (school_b_id, security.hash_password("AdminBeta123!")))
    admin_b_id = cursor.fetchone()[0]

    # Suspended School Admin
    cursor.execute("""
        INSERT INTO admin (school_id, USERNAME, password, full_name)
        VALUES (%s, 'admin_susp', %s, 'Admin Suspended')
        RETURNING admin_id;
    """, (school_susp_id, security.hash_password("AdminSusp123!")))
    admin_susp_id = cursor.fetchone()[0]

    # School A Parent & Student
    cursor.execute("""
        INSERT INTO parent (school_id, parent_name, phone, address, pickup_point, username, password)
        VALUES (%s, 'Parent Alpha', '9811111111', 'Sector 14', 'Alpha Stop 1', 'parent_a', %s)
        RETURNING parent_id;
    """, (school_a_id, security.hash_password("ParentAlpha123!")))
    parent_a_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO student (school_id, student_name, student_class, parent_id, route_id, fee_paid, fee_balance, transport_status)
        VALUES (%s, 'Student Alpha', 'Grade 5', %s, %s, 5000.0, 0.0, 'Active')
        RETURNING student_id;
    """, (school_a_id, parent_a_id, route_a_id))
    student_a_id = cursor.fetchone()[0]

    # School A Retention Policy
    cursor.execute("""
        INSERT INTO retention_policy (school_id, scope, default_days, min_days, max_days, purge_enabled)
        VALUES 
            (%s, 'telemetry_events', 30,  7,  90,  TRUE),
            (%s, 'trips',            365, 90, 730, TRUE),
            (%s, 'audit_logs',        365, 90, 1095, TRUE)
        ON CONFLICT (school_id, scope) DO UPDATE SET purge_enabled = EXCLUDED.purge_enabled;
    """, (school_a_id, school_a_id, school_a_id))

    conn.commit()
    cursor.close()
    conn.close()

    yield {
        "school_a_id": school_a_id,
        "school_b_id": school_b_id,
        "school_susp_id": school_susp_id,
        "bus_a_id": bus_a_id,
        "bus_b_id": bus_b_id,
        "route_a_id": route_a_id,
        "route_b_id": route_b_id,
        "admin_a_id": admin_a_id,
        "admin_b_id": admin_b_id,
        "admin_susp_id": admin_susp_id,
        "parent_a_id": parent_a_id,
        "student_a_id": student_a_id,
    }

    # Teardown: terminate sessions and drop test database
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
        print(f"Warning: could not drop test database {TEST_DB_NAME}: {e}")
    finally:
        os.environ["DB_NAME"] = ORIGINAL_DB_NAME


@pytest.fixture(autouse=True)
def clean_rate_limits():
    reset_all_rate_limits()
    yield
    reset_all_rate_limits()


# ===========================================================================
# 1. Multi-Tenant Authentication & Session Verification
# ===========================================================================
class TestMultiTenantAuthentication:
    def test_login_with_valid_school_code_and_user_type(self):
        resp = client.post("/api/v1/auth/login", json={
            "username": "admin_a",
            "password": "AdminAlpha123!",
            "school_code": "SCH_A",
            "user_type": "admin"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user_type"] == "admin"
        assert data["school_id"] is not None

    def test_login_with_wrong_school_code_rejected(self):
        resp = client.post("/api/v1/auth/login", json={
            "username": "admin_a",
            "password": "AdminAlpha123!",
            "school_code": "SCH_B",  # Admin A does not exist in School B
            "user_type": "admin"
        })
        assert resp.status_code == 401
        assert "Invalid username or password" in resp.json()["detail"]

    def test_login_with_mismatched_user_type_rejected(self):
        resp = client.post("/api/v1/auth/login", json={
            "username": "admin_a",
            "password": "AdminAlpha123!",
            "school_code": "SCH_A",
            "user_type": "driver"  # Mismatched role
        })
        assert resp.status_code == 401

    def test_login_to_suspended_institution_rejected(self):
        resp = client.post("/api/v1/auth/login", json={
            "username": "admin_susp",
            "password": "AdminSusp123!",
            "school_code": "SCH_SUSP",
            "user_type": "admin"
        })
        assert resp.status_code == 401
        assert "inactive" in resp.json()["detail"].lower()

    def test_legacy_token_in_flight_tenant_resolution(self, setup_disposable_database):
        # Create legacy token missing school_id
        admin_a_id = setup_disposable_database["admin_a_id"]
        legacy_token = security.create_access_token({
            "user_id": admin_a_id,
            "user_type": "admin",
            "username": "admin_a"
        })
        # Call fleet tracking which enforces school_id
        resp = client.get("/api/v1/tracking/fleet", headers={"Authorization": f"Bearer {legacy_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "buses" in data


# ===========================================================================
# 2. Cross-Tenant Data Isolation & Security Rejection
# ===========================================================================
class TestCrossTenantDataIsolation:
    def test_admin_cannot_access_other_school_fleet(self, setup_disposable_database):
        admin_b_token = security.create_access_token({
            "user_id": setup_disposable_database["admin_b_id"],
            "user_type": "admin",
            "username": "admin_b",
            "school_id": setup_disposable_database["school_b_id"]
        })
        resp = client.get("/api/v1/tracking/fleet", headers={"Authorization": f"Bearer {admin_b_token}"})
        assert resp.status_code == 200
        buses = resp.json()["buses"]
        # Must only see School B's bus, never School A's bus
        bus_numbers = [b["bus_number"] for b in buses]
        assert "BUS-B1" in bus_numbers
        assert "BUS-A1" not in bus_numbers

    def test_driver_cannot_start_trip_for_other_school_bus(self, setup_disposable_database):
        driver_a_token = security.create_access_token({
            "user_id": setup_disposable_database["bus_a_id"],
            "user_type": "driver",
            "username": "driver_a",
            "bus_id": setup_disposable_database["bus_a_id"],
            "school_id": setup_disposable_database["school_a_id"]
        })
        # Attempt to start trip on School B's bus
        resp = client.post("/api/v1/tracking/trip/start", json={
            "bus_id": setup_disposable_database["bus_b_id"]
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        # Rejected because driver A is only authorized for bus A (403)
        assert resp.status_code == 403

    def test_parent_cannot_track_other_school_bus(self, setup_disposable_database):
        parent_a_token = security.create_access_token({
            "user_id": setup_disposable_database["parent_a_id"],
            "user_type": "parent",
            "username": "parent_a",
            "parent_id": setup_disposable_database["parent_a_id"],
            "school_id": setup_disposable_database["school_a_id"]
        })
        resp = client.get(
            f"/api/v1/tracking/bus/{setup_disposable_database['bus_b_id']}",
            headers={"Authorization": f"Bearer {parent_a_token}"}
        )
        assert resp.status_code == 403


# ===========================================================================
# 3. GPS Trip Lifecycle & Telemetry Ingestion
# ===========================================================================
class TestGpsTripAndTelemetryLifecycle:
    @pytest.fixture(autouse=True)
    def cleanup_active_trips(self, setup_disposable_database):
        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("UPDATE trips SET status = 'completed', ended_at = NOW() WHERE status = 'active';")
        conn.commit()
        cur.close()
        conn.close()
        yield
        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("UPDATE trips SET status = 'completed', ended_at = NOW() WHERE status = 'active';")
        conn.commit()
        cur.close()
        conn.close()

    def test_trip_start_and_telemetry_flow(self, setup_disposable_database):
        driver_a_token = security.create_access_token({
            "user_id": setup_disposable_database["bus_a_id"],
            "user_type": "driver",
            "username": "driver_a",
            "bus_id": setup_disposable_database["bus_a_id"],
            "school_id": setup_disposable_database["school_a_id"]
        })
        bus_id = setup_disposable_database["bus_a_id"]

        # 1. Start Trip
        start_resp = client.post("/api/v1/tracking/trip/start", json={
            "bus_id": bus_id
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert start_resp.status_code == 200
        trip_data = start_resp.json()
        assert trip_data["status"] == "started"
        trip_id = trip_data["trip_id"]

        # 2. Ingest first valid telemetry event
        event_uuid1 = str(uuid.uuid4())
        ev1_resp = client.post("/api/v1/tracking/event", json={
            "client_event_id": event_uuid1,
            "trip_id": trip_id,
            "bus_id": bus_id,
            "trip_sequence_number": 1,
            "latitude": 28.6145,
            "longitude": 77.2095,
            "speed_kmh": 32.5,
            "bearing_degrees": 90.0,
            "accuracy_metres": 8.0,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "next_stop": "Alpha Stop 1"
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert ev1_resp.status_code == 200
        assert ev1_resp.json()["accepted"] is True

        # 3. Verify live bus location updated from PostgreSQL
        live_resp = client.get(f"/api/v1/tracking/bus/{bus_id}", headers={"Authorization": f"Bearer {driver_a_token}"})
        assert live_resp.status_code == 200
        live = live_resp.json()
        assert live["status"] == "In Transit"
        assert abs(live["latitude"] - 28.6145) < 0.0001
        assert live["accuracy_metres"] == 8.0
        assert live["gps_quality"] == "good"

        # 4. Stop Trip
        stop_resp = client.post("/api/v1/tracking/trip/stop", json={
            "bus_id": bus_id
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert stop_resp.status_code == 200
        assert stop_resp.json()["status"] == "stopped"

    def test_duplicate_client_event_id_rejected(self, setup_disposable_database):
        driver_a_token = security.create_access_token({
            "user_id": setup_disposable_database["bus_a_id"],
            "user_type": "driver",
            "username": "driver_a",
            "bus_id": setup_disposable_database["bus_a_id"],
            "school_id": setup_disposable_database["school_a_id"]
        })
        bus_id = setup_disposable_database["bus_a_id"]

        start_resp = client.post("/api/v1/tracking/trip/start", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert start_resp.status_code == 200
        trip_id = start_resp.json()["trip_id"]

        shared_uuid = str(uuid.uuid4())
        # First send on trip 1
        r1 = client.post("/api/v1/tracking/event", json={
            "client_event_id": shared_uuid,
            "trip_id": trip_id,
            "bus_id": bus_id,
            "trip_sequence_number": 1,
            "latitude": 28.6150,
            "longitude": 77.2100,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert r1.status_code == 200

        # Stop trip 1
        client.post("/api/v1/tracking/trip/stop", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})

        # Start trip 2
        start2_resp = client.post("/api/v1/tracking/trip/start", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert start2_resp.status_code == 200
        trip_id2 = start2_resp.json()["trip_id"]

        # Duplicate send on trip 2 with identical client_event_id from trip 1 -> MUST be rejected with 409
        dup_resp = client.post("/api/v1/tracking/event", json={
            "client_event_id": shared_uuid,
            "trip_id": trip_id2,
            "bus_id": bus_id,
            "trip_sequence_number": 1,
            "latitude": 28.6160,
            "longitude": 77.2110,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert dup_resp.status_code == 409
        assert "Reused client_event_id" in dup_resp.json()["detail"]

        client.post("/api/v1/tracking/trip/stop", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})

    def test_out_of_order_sequence_does_not_regress_live_location(self, setup_disposable_database):
        driver_a_token = security.create_access_token({
            "user_id": setup_disposable_database["bus_a_id"],
            "user_type": "driver",
            "username": "driver_a",
            "bus_id": setup_disposable_database["bus_a_id"],
            "school_id": setup_disposable_database["school_a_id"]
        })
        bus_id = setup_disposable_database["bus_a_id"]

        start_resp = client.post("/api/v1/tracking/trip/start", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})
        trip_id = start_resp.json()["trip_id"]

        # Send sequence #5 first
        client.post("/api/v1/tracking/event", json={
            "client_event_id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "bus_id": bus_id,
            "trip_sequence_number": 5,
            "latitude": 28.6250,
            "longitude": 77.2200,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, headers={"Authorization": f"Bearer {driver_a_token}"})

        # Send sequence #3 afterwards (out of order arrival)
        ev_ooo = client.post("/api/v1/tracking/event", json={
            "client_event_id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "bus_id": bus_id,
            "trip_sequence_number": 3,
            "latitude": 28.6180,
            "longitude": 77.2130,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert ev_ooo.status_code == 200
        assert ev_ooo.json()["out_of_order"] is True

        # Verify live location remains at sequence 5 and did NOT regress to sequence 3
        live = client.get(f"/api/v1/tracking/bus/{bus_id}", headers={"Authorization": f"Bearer {driver_a_token}"}).json()
        assert abs(live["latitude"] - 28.6250) < 0.0001

        client.post("/api/v1/tracking/trip/stop", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})

    def test_coordinate_validation_impossible_and_service_area(self, setup_disposable_database):
        driver_a_token = security.create_access_token({
            "user_id": setup_disposable_database["bus_a_id"],
            "user_type": "driver",
            "username": "driver_a",
            "bus_id": setup_disposable_database["bus_a_id"],
            "school_id": setup_disposable_database["school_a_id"]
        })
        bus_id = setup_disposable_database["bus_a_id"]

        # Impossible coordinates (lat > 90) must be rejected with 422
        resp = client.post("/api/v1/tracking/update", json={
            "bus_id": bus_id,
            "latitude": 95.0000,
            "longitude": 77.2000
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert resp.status_code == 422

        # Telemetry event outside school service area must be hard rejected
        start_resp = client.post("/api/v1/tracking/trip/start", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})
        trip_id = start_resp.json()["trip_id"]

        outside_resp = client.post("/api/v1/tracking/event", json={
            "client_event_id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "bus_id": bus_id,
            "trip_sequence_number": 1,
            "latitude": 19.0760,  # Mumbai coordinates, outside School A Delhi NCR bounding box
            "longitude": 72.8777,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert outside_resp.status_code == 200
        assert outside_resp.json()["accepted"] is False
        assert "service_area" in outside_resp.json()["note"].lower() or "service area" in outside_resp.json()["note"].lower()

        client.post("/api/v1/tracking/trip/stop", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})


# ===========================================================================
# 4. Concurrency, Locking & Serialization Retry
# ===========================================================================
class TestConcurrencyAndIntegrity:
    def test_duplicate_active_trip_prevented(self, setup_disposable_database):
        driver_a_token = security.create_access_token({
            "user_id": setup_disposable_database["bus_a_id"],
            "user_type": "driver",
            "username": "driver_a",
            "bus_id": setup_disposable_database["bus_a_id"],
            "school_id": setup_disposable_database["school_a_id"]
        })
        bus_id = setup_disposable_database["bus_a_id"]

        # First trip start succeeds
        r1 = client.post("/api/v1/tracking/trip/start", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert r1.status_code == 200

        # Attempt to start a second trip on the same bus while first is active fails
        r2 = client.post("/api/v1/tracking/trip/start", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})
        assert r2.status_code == 409
        assert "active trip is already in progress" in r2.json()["detail"].lower()

        # Stop active trip
        client.post("/api/v1/tracking/trip/stop", json={"bus_id": bus_id}, headers={"Authorization": f"Bearer {driver_a_token}"})

    def test_serialization_retry_decorator(self):
        attempts = 0

        class MockSerializationError(Exception):
            @property
            def pgcode(self):
                return "40001"

        @with_psycopg2_retry(max_retries=3, base_delay=0.01)
        def simulated_flaky_transaction():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise MockSerializationError("Simulated serialization failure")
            return "SUCCESS"

        result = simulated_flaky_transaction()
        assert result == "SUCCESS"
        assert attempts == 3


# ===========================================================================
# 5. Retention Purge & Historical Preservation
# ===========================================================================
class TestRetentionPurgeAndAudit:
    def test_retention_purge_respects_purge_enabled_flag(self, setup_disposable_database):
        school_id = setup_disposable_database["school_a_id"]
        conn = database.connect_database()
        cur = conn.cursor()

        # Disable purge
        cur.execute("UPDATE retention_policy SET purge_enabled = FALSE WHERE school_id = %s;", (school_id,))
        conn.commit()
        cur.close()
        conn.close()

        purged_when_disabled = db_dal.run_retention_purge()
        assert purged_when_disabled.get("telemetry_events", 0) == 0

        # Re-enable purge
        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("UPDATE retention_policy SET purge_enabled = TRUE WHERE school_id = %s;", (school_id,))
        conn.commit()
        cur.close()
        conn.close()

        purged_when_enabled = db_dal.run_retention_purge()
        assert isinstance(purged_when_enabled, dict)
        assert "telemetry_events" in purged_when_enabled

    def test_audit_log_ip_masking(self, setup_disposable_database):
        school_id = setup_disposable_database["school_a_id"]
        # Seed an old audit entry (>90 days ago) with unmasked IP
        conn = database.connect_database()
        cur = conn.cursor()
        old_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=95)
        cur.execute("""
            INSERT INTO audit_log (school_id, actor_type, actor_id, actor_username, action, ip_address, occurred_at)
            VALUES (%s, 'admin', 1, 'admin_a', 'test.action', '192.168.1.150', %s)
            RETURNING log_id;
        """, (school_id, old_time))
        log_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # Execute masking
        masked_count = db_dal.mask_audit_ips()
        assert masked_count >= 1

        # Verify IP was masked (CIDR network mask /24)
        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("SELECT ip_address, masklen(ip_address) FROM audit_log WHERE log_id = %s;", (log_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        assert row is not None
        assert row[1] == 24
        masked_ip = row[0]
        assert str(masked_ip).startswith("192.168.1.")
