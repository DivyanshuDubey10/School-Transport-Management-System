import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import security
from dal import db_dal
from middleware.rate_limiter import reset_all_rate_limits
from main import app

client = TestClient(app, raise_server_exceptions=False)

# ---------------------------------------------------------------------------
# Test Data & Mock Setup
# ---------------------------------------------------------------------------
HASHED_ADMIN_PW = security.hash_password("AdminSecure123!")
HASHED_PARENT1_PW = security.hash_password("ParentSecure123!")
HASHED_PARENT2_PW = security.hash_password("ParentSecure123!")
HASHED_DRIVER1_PW = security.hash_password("DriverSecure123!")
HASHED_DRIVER2_PW = security.hash_password("DriverSecure123!")

MOCK_ADMIN = (1, "admin", HASHED_ADMIN_PW, "Admin User")
MOCK_LEGACY_ADMIN = (2, "legacyadmin", "PlaintextSecret123!", "Legacy Admin")
MOCK_PARENT1 = (1, "Parent One", "9876543210", "123 Street", "Stop A", "parent1", HASHED_PARENT1_PW)
MOCK_PARENT2 = (2, "Parent Two", "9876543211", "456 Avenue", "Stop B", "parent2", HASHED_PARENT2_PW)
MOCK_BUS1 = (101, "BUS-01", "Driver One", "9876543220", 30, 1, "driver1", HASHED_DRIVER1_PW)
MOCK_BUS2 = (102, "BUS-02", "Driver Two", "9876543221", 30, 2, "driver2", HASHED_DRIVER2_PW)

MOCK_STUDENT1 = (1, "Student One", "5th", 1, 1, 500.0, 0.0, "Active")  # Parent 1, Route 1 (Bus 101)
MOCK_STUDENT2 = (2, "Student Two", "6th", 2, 2, 500.0, 0.0, "Active")  # Parent 2, Route 2 (Bus 102)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Reset rate limiter state and mock DB before each test."""
    reset_all_rate_limits()
    yield
    reset_all_rate_limits()


def get_token(user_type: str, user_id: int, username: str, **kwargs) -> str:
    payload = {"user_type": user_type, "user_id": user_id, "username": username}
    payload.update(kwargs)
    return security.create_access_token(payload)


# ===========================================================================
# Task 1: Public Test Account Endpoint Removal Tests
# ===========================================================================
class TestEndpointRemoval:
    def test_setup_test_accounts_root_get_returns_404(self):
        resp = client.get("/setup-test-accounts")
        assert resp.status_code == 404

    def test_setup_test_accounts_root_post_returns_404(self):
        resp = client.post("/setup-test-accounts")
        assert resp.status_code == 404

    def test_setup_test_accounts_api_v1_get_returns_404(self):
        resp = client.get("/api/v1/setup-test-accounts")
        assert resp.status_code == 404

    def test_setup_test_accounts_api_v1_post_returns_404(self):
        resp = client.post("/api/v1/setup-test-accounts")
        assert resp.status_code == 404

    def test_root_endpoint_does_not_expose_setup_route(self):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "setup_test_accounts" not in data


# ===========================================================================
# Task 2: Authentication & Password Hardening Tests
# ===========================================================================
class TestAuthenticationHardening:
    def test_login_success_with_valid_bcrypt_admin(self, monkeypatch):
        monkeypatch.setattr(db_dal, "get_admin_by_username", lambda u: MOCK_ADMIN if u == "admin" else None)
        monkeypatch.setattr(db_dal, "get_parent_by_username", lambda u: None)
        monkeypatch.setattr(db_dal, "get_driver_by_username", lambda u: None)

        resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "AdminSecure123!"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user_type"] == "admin"
        assert data["user_id"] == 1

    def test_login_failure_with_wrong_password(self, monkeypatch):
        monkeypatch.setattr(db_dal, "get_admin_by_username", lambda u: MOCK_ADMIN if u == "admin" else None)
        monkeypatch.setattr(db_dal, "get_parent_by_username", lambda u: None)
        monkeypatch.setattr(db_dal, "get_driver_by_username", lambda u: None)

        resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "WrongPassword999!"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid username or password."

    def test_login_rejects_previously_hardcoded_bypass_password(self, monkeypatch):
        # Admin password in DB is 'AdminSecure123!', attempt to use old bypass 'admin123' must fail with 401
        monkeypatch.setattr(db_dal, "get_admin_by_username", lambda u: MOCK_ADMIN if u == "admin" else None)
        monkeypatch.setattr(db_dal, "get_parent_by_username", lambda u: None)
        monkeypatch.setattr(db_dal, "get_driver_by_username", lambda u: None)

        resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid username or password."

    def test_login_transparent_legacy_plaintext_migration(self, monkeypatch):
        # User has legacy unhashed password in database
        upgraded_hashes = []
        monkeypatch.setattr(db_dal, "get_admin_by_username", lambda u: MOCK_LEGACY_ADMIN if u == "legacyadmin" else None)
        monkeypatch.setattr(db_dal, "get_parent_by_username", lambda u: None)
        monkeypatch.setattr(db_dal, "get_driver_by_username", lambda u: None)
        monkeypatch.setattr(db_dal, "set_admin_password_hash", lambda uid, h: upgraded_hashes.append((uid, h)) or True)

        resp = client.post("/api/v1/auth/login", json={"username": "legacyadmin", "password": "PlaintextSecret123!"})
        assert resp.status_code == 200
        assert len(upgraded_hashes) == 1
        assert upgraded_hashes[0][0] == 2
        # Verify it upgraded to a valid bcrypt hash
        assert security.is_bcrypt_hash(upgraded_hashes[0][1])

    def test_rate_limiting_lockout_after_multiple_failed_logins(self, monkeypatch):
        monkeypatch.setattr(db_dal, "get_admin_by_username", lambda u: MOCK_ADMIN if u == "admin" else None)
        monkeypatch.setattr(db_dal, "get_parent_by_username", lambda u: None)
        monkeypatch.setattr(db_dal, "get_driver_by_username", lambda u: None)

        # 5 failed attempts: return 401
        for _ in range(5):
            r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "BadPassword1!"})
            assert r.status_code == 401

        # 6th attempt triggers rate limit block (429)
        r6 = client.post("/api/v1/auth/login", json={"username": "admin", "password": "BadPassword1!"})
        assert r6.status_code == 429
        assert "Too many" in r6.json()["detail"]

    def test_password_strength_validator(self):
        # Too short (<8)
        valid, msg = security.validate_password_strength("Short1!")
        assert not valid
        assert "8 characters" in msg

        # Only letters
        valid, msg = security.validate_password_strength("NoNumbersAtAll")
        assert not valid
        assert "letter and one number" in msg

        # Only numbers
        valid, msg = security.validate_password_strength("1234567890")
        assert not valid
        assert "letter and one number" in msg

        # Valid password
        valid, msg = security.validate_password_strength("ValidPassword123")
        assert valid
        assert msg == ""

    def test_change_password_with_incorrect_current_password(self, monkeypatch):
        token = get_token("admin", 1, "admin")
        monkeypatch.setattr(db_dal, "get_admin_by_id", lambda uid: MOCK_ADMIN)

        resp = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "WrongPassword123!", "new_password": "NewStrongPass456!"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400
        assert "Current password is incorrect" in resp.json()["detail"]

    def test_change_password_success(self, monkeypatch):
        token = get_token("admin", 1, "admin")
        saved_hashes = []
        monkeypatch.setattr(db_dal, "get_admin_by_id", lambda uid: MOCK_ADMIN)
        monkeypatch.setattr(db_dal, "set_admin_password_hash", lambda uid, h: saved_hashes.append(h) or True)

        resp = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "AdminSecure123!", "new_password": "NewStrongPass456!"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(saved_hashes) == 1
        assert security.verify_password("NewStrongPass456!", saved_hashes[0])


# ===========================================================================
# Task 3: Broken Object-Level Authorization (BOLA/IDOR) Tests
# ===========================================================================
class TestObjectLevelAuthorization:
    # --- Attendance Ownership ---
    def test_parent_can_view_own_child_attendance(self, monkeypatch):
        token = get_token("parent", 1, "parent1", parent_id=1)
        monkeypatch.setattr(db_dal, "get_student_by_id", lambda student_id=None, *a, **k: MOCK_STUDENT1 if student_id == 1 else None)
        monkeypatch.setattr(db_dal, "get_attendance_history_for_student", lambda student_id=None, *a, **k: [("2026-11-01", "Present")])

        resp = client.get("/api/v1/attendance/student/1", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["attendance_status"] == "Present"

    def test_parent_cannot_view_other_parent_child_attendance(self, monkeypatch):
        # Parent 1 tries to access Student 2 (Parent 2's child) -> MUST FAIL with 403 Forbidden
        token = get_token("parent", 1, "parent1", parent_id=1)
        monkeypatch.setattr(db_dal, "get_student_by_id", lambda student_id=None, *a, **k: MOCK_STUDENT2 if student_id == 2 else None)

        resp = client.get("/api/v1/attendance/student/2", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
        assert "permission" in resp.json()["detail"].lower()

    def test_driver_can_only_view_attendance_for_students_on_their_bus(self, monkeypatch):
        token = get_token("driver", 101, "driver1", bus_id=101)
        monkeypatch.setattr(db_dal, "get_student_by_id", lambda student_id=None, *a, **k: MOCK_STUDENT1 if student_id == 1 else MOCK_STUDENT2)
        monkeypatch.setattr(db_dal, "is_student_on_driver_bus", lambda sid, bid: (sid == 1 and bid == 101))
        monkeypatch.setattr(db_dal, "get_attendance_history_for_student", lambda student_id=None, *a, **k: [("2026-11-01", "Present")])

        # Allowed: Student 1 is on Bus 101
        ok_resp = client.get("/api/v1/attendance/student/1", headers={"Authorization": f"Bearer {token}"})
        assert ok_resp.status_code == 200

        # Forbidden: Student 2 is NOT on Bus 101
        forbidden_resp = client.get("/api/v1/attendance/student/2", headers={"Authorization": f"Bearer {token}"})
        assert forbidden_resp.status_code == 403

    # --- Transport Change Request Ownership ---
    def test_parent_can_create_request_for_own_child(self, monkeypatch):
        token = get_token("parent", 1, "parent1", parent_id=1)
        monkeypatch.setattr(db_dal, "get_student_by_id", lambda sid: MOCK_STUDENT1 if sid == 1 else None)
        monkeypatch.setattr(db_dal, "create_change_request", lambda student_id, new_pickup_point: True)

        resp = client.post(
            "/api/v1/requests",
            json={"student_id": 1, "requested_pickup_point": "New Stop Plaza"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert "submitted successfully" in resp.json()["message"]

    def test_parent_cannot_create_request_for_other_parent_child(self, monkeypatch):
        # Parent 1 tries to submit change request for Student 2 (Parent 2's child) -> MUST FAIL with 403 Forbidden
        token = get_token("parent", 1, "parent1", parent_id=1)
        monkeypatch.setattr(db_dal, "get_student_by_id", lambda sid: MOCK_STUDENT2 if sid == 2 else None)

        resp = client.post(
            "/api/v1/requests",
            json={"student_id": 2, "requested_pickup_point": "Malicious Transfer"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert "own children" in resp.json()["detail"].lower()

    # --- Bus Live Tracking BOLA ---
    def test_parent_can_track_assigned_bus(self, monkeypatch):
        token = get_token("parent", 1, "parent1", parent_id=1)
        monkeypatch.setattr(db_dal, "is_parent_authorized_for_bus", lambda pid, bid: (pid == 1 and bid == 101))
        monkeypatch.setattr(db_dal, "get_bus_by_id", lambda bid: MOCK_BUS1 if bid == 101 else None)
        monkeypatch.setattr(db_dal, "get_all_routes", lambda: [(1, "Route 1"), (2, "Route 2")])

        resp = client.get("/api/v1/tracking/bus/101", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["bus_id"] == 101

    def test_parent_cannot_track_unassigned_bus(self, monkeypatch):
        # Parent 1 tries to track Bus 102 (Student 1 is NOT on Bus 102) -> MUST FAIL with 403 Forbidden
        token = get_token("parent", 1, "parent1", parent_id=1)
        monkeypatch.setattr(db_dal, "is_parent_authorized_for_bus", lambda pid, bid: False)

        resp = client.get("/api/v1/tracking/bus/102", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
        assert "not authorized to track this bus" in resp.json()["detail"]

    def test_driver_cannot_track_other_bus(self, monkeypatch):
        token = get_token("driver", 101, "driver1", bus_id=101)
        resp = client.get("/api/v1/tracking/bus/102", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
        assert "only authorized to track your own assigned bus" in resp.json()["detail"]

    def test_driver_cannot_broadcast_gps_for_other_bus(self, monkeypatch):
        token = get_token("driver", 101, "driver1", bus_id=101)
        resp = client.post(
            "/api/v1/tracking/update",
            json={"bus_id": 102, "latitude": 28.6139, "longitude": 77.2090, "speed": 30.0},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert "only authorized to broadcast locations for your assigned bus" in resp.json()["detail"]

    def test_parent_cannot_broadcast_gps_location(self):
        token = get_token("parent", 1, "parent1", parent_id=1)
        resp = client.post(
            "/api/v1/tracking/update",
            json={"bus_id": 101, "latitude": 28.6139, "longitude": 77.2090},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    def test_fleet_tracking_restricted_to_admin(self, monkeypatch):
        parent_token = get_token("parent", 1, "parent1", parent_id=1)
        driver_token = get_token("driver", 101, "driver1", bus_id=101)
        admin_token = get_token("admin", 1, "admin")

        monkeypatch.setattr(db_dal, "get_all_buses", lambda: [MOCK_BUS1, MOCK_BUS2])
        monkeypatch.setattr(db_dal, "get_all_routes", lambda: [(1, "Route 1"), (2, "Route 2")])

        # Parent: 403 Forbidden
        p_resp = client.get("/api/v1/tracking/fleet", headers={"Authorization": f"Bearer {parent_token}"})
        assert p_resp.status_code == 403

        # Driver: 403 Forbidden
        d_resp = client.get("/api/v1/tracking/fleet", headers={"Authorization": f"Bearer {driver_token}"})
        assert d_resp.status_code == 403

        # Admin: 200 OK
        a_resp = client.get("/api/v1/tracking/fleet", headers={"Authorization": f"Bearer {admin_token}"})
        assert a_resp.status_code == 200
        assert len(a_resp.json()) == 2

    def test_gps_coordinate_validation_bounds(self):
        admin_token = get_token("admin", 1, "admin")

        # Invalid latitude (>90.0)
        resp1 = client.post(
            "/api/v1/tracking/update",
            json={"bus_id": 101, "latitude": 95.0, "longitude": 77.2090},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp1.status_code == 422

        # Invalid longitude (>180.0)
        resp2 = client.post(
            "/api/v1/tracking/update",
            json={"bus_id": 101, "latitude": 28.6139, "longitude": 185.0},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp2.status_code == 422


# ===========================================================================
# Task 4: Production Configuration & Safeguards Tests
# ===========================================================================
class TestProductionSafeguards:
    def test_production_jwt_secret_rejection(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")

        # Insecure default secret must raise RuntimeError
        monkeypatch.setenv("JWT_SECRET", "neoyatra-production-super-secret-jwt-key-2026")
        with pytest.raises(RuntimeError) as exc_info:
            security.get_jwt_secret()
        assert "CRITICAL SECURITY CONFIGURATION ERROR" in str(exc_info.value)

        # Secret too short (<32 chars) must raise RuntimeError
        monkeypatch.setenv("JWT_SECRET", "short_secret_key_123")
        with pytest.raises(RuntimeError):
            security.get_jwt_secret()

        # Secure 32+ character secret succeeds
        secure_key = "a-secure-randomly-generated-key-of-at-least-32-bytes-length"
        monkeypatch.setenv("JWT_SECRET", secure_key)
        assert security.get_jwt_secret() == secure_key

    def test_reset_db_aborts_in_production_and_staging(self, monkeypatch):
        import reset_db

        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(RuntimeError) as exc_p:
            reset_db.reset_to_clean_development()
        assert "strictly forbidden in PRODUCTION" in str(exc_p.value)

        monkeypatch.setenv("ENVIRONMENT", "staging")
        with pytest.raises(RuntimeError) as exc_s:
            reset_db.reset_to_clean_development()
        assert "strictly forbidden in STAGING" in str(exc_s.value)

    def test_reset_db_requires_cli_confirmation_flag(self, monkeypatch):
        import reset_db
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setattr(sys, "argv", ["reset_db.py"])

        with pytest.raises(SystemExit) as exit_code:
            reset_db.reset_to_clean_development()
        assert exit_code.value.code == 1

    def test_global_exception_handler_sanitizes_500_errors(self, monkeypatch):
        # When an unexpected server exception occurs, it must return a generic 500 error
        # without disclosing database internals, queries, or credentials
        admin_token = get_token("admin", 1, "admin")

        def broken_get_all_buses():
            raise Exception("psycopg2.OperationalError: could not connect to server: Connection refused\nIs the server running at localhost:5432?")

        monkeypatch.setattr(db_dal, "get_all_buses", broken_get_all_buses)

        resp = client.get("/api/v1/tracking/fleet", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 500
        data = resp.json()
        assert data["detail"] == "An internal server error occurred. Please contact system support."
        assert "psycopg2" not in str(data)
        assert "5432" not in str(data)

    def test_cors_preflight_whitelisted_origin(self):
        resp = client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert "POST" in resp.headers.get("access-control-allow-methods", "")

    def test_cors_preflight_rejects_unauthorized_origin(self):
        resp = client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "https://malicious-attacker-website.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        # Origin must not be allowed
        assert resp.headers.get("access-control-allow-origin") != "https://malicious-attacker-website.com"
