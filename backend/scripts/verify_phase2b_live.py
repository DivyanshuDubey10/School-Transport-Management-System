import os
import sys
import uuid
import datetime
import requests
import psycopg2

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Connect to database directly for state inspection
import database
import security


def run_live_verification():
    print("=" * 70)
    print("NEOYATRA PHASE 2B — LIVE END-TO-END VERIFICATION")
    print(f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print("=" * 70)

    results = []

    def record(category: str, test_name: str, passed: bool, detail: str = ""):
        status_str = "PASSED" if passed else "FAILED"
        print(f"[{status_str}] {category} :: {test_name} - {detail}")
        results.append({
            "category": category,
            "name": test_name,
            "passed": passed,
            "detail": detail
        })

    # -----------------------------------------------------------------------
    # 1. DRIVER WORKFLOW
    # -----------------------------------------------------------------------
    print("\n--- 1. Testing Complete Driver Workflow ---")
    
    # Clean any lingering active trips on bus 12 before testing
    conn = database.connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE trips SET status = 'completed', ended_at = NOW() WHERE status = 'active';")
    conn.commit()
    cur.close()
    conn.close()

    # Step 1: Log in as driver
    login_payload = {
        "username": "driver",
        "password": "driver123",
        "school_code": "DEFAULT",
        "user_type": "driver"
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    driver_login_ok = (r.status_code == 200)
    driver_token = ""
    driver_bus_id = None
    school_id = None
    if driver_login_ok:
        data = r.json()
        driver_token = data.get("access_token")
        driver_bus_id = data.get("user_id")
        school_id = data.get("school_id")
    record(
        "Driver Workflow",
        "1. Driver Login & Tenant Context",
        driver_login_ok and driver_bus_id == 12 and school_id == 1,
        f"HTTP {r.status_code}, bus_id={driver_bus_id}, school_id={school_id}"
    )

    driver_headers = {"Authorization": f"Bearer {driver_token}"}

    # Step 2: Start Trip
    start_payload = {"bus_id": driver_bus_id}
    r = requests.post(f"{BASE_URL}/tracking/trip/start", json=start_payload, headers=driver_headers)
    start_ok = (r.status_code == 200 and r.json().get("status") == "started")
    trip_id = r.json().get("trip_id") if start_ok else None
    record(
        "Driver Workflow",
        "2. Start Trip",
        start_ok and trip_id is not None,
        f"HTTP {r.status_code}, trip_id={trip_id}"
    )

    # Step 3: Send canonical telemetry events (consecutive updates)
    ev_uuid1 = str(uuid.uuid4())
    ev1_payload = {
        "client_event_id": ev_uuid1,
        "trip_id": trip_id,
        "bus_id": driver_bus_id,
        "trip_sequence_number": 1,
        "latitude": 28.6145,
        "longitude": 77.2095,
        "speed_kmh": 25.0,
        "bearing_degrees": 45.0,
        "accuracy_metres": 8.0,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "next_stop": "Purana Bazar Chowk"
    }
    r1 = requests.post(f"{BASE_URL}/tracking/event", json=ev1_payload, headers=driver_headers)
    ev1_ok = (r1.status_code == 200 and r1.json().get("accepted") is True)
    record(
        "Driver Workflow",
        "3. Telemetry Event 1 Ingestion",
        ev1_ok,
        f"HTTP {r1.status_code}, accepted={r1.json().get('accepted')}"
    )

    ev_uuid2 = str(uuid.uuid4())
    ev2_payload = {
        "client_event_id": ev_uuid2,
        "trip_id": trip_id,
        "bus_id": driver_bus_id,
        "trip_sequence_number": 2,
        "latitude": 28.6180,
        "longitude": 77.2140,
        "speed_kmh": 30.0,
        "bearing_degrees": 50.0,
        "accuracy_metres": 9.0,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "next_stop": "Purana Bazar Chowk"
    }
    r2 = requests.post(f"{BASE_URL}/tracking/event", json=ev2_payload, headers=driver_headers)

    ev_uuid3 = str(uuid.uuid4())
    ev3_payload = {
        "client_event_id": ev_uuid3,
        "trip_id": trip_id,
        "bus_id": driver_bus_id,
        "trip_sequence_number": 3,
        "latitude": 28.6220,
        "longitude": 77.2180,
        "speed_kmh": 35.0,
        "bearing_degrees": 55.0,
        "accuracy_metres": 7.5,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "next_stop": "Old Market Crossing"
    }
    r3 = requests.post(f"{BASE_URL}/tracking/event", json=ev3_payload, headers=driver_headers)
    record(
        "Driver Workflow",
        "4. Consecutive Telemetry Stream (Events 2 & 3)",
        r2.status_code == 200 and r3.status_code == 200,
        f"Ev2: HTTP {r2.status_code}, Ev3: HTTP {r3.status_code}"
    )

    # Step 4: Verify Database Storage and Live Location State
    conn = database.connect_database()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM bus_telemetry_events WHERE trip_id = %s;", (trip_id,))
    stored_events_count = cur.fetchone()[0]

    cur.execute("""
        SELECT latitude, longitude, speed_kmh, status, accuracy_metres, gps_quality, is_stale, last_trip_sequence
        FROM bus_live_location WHERE bus_id = %s;
    """, (driver_bus_id,))
    live_row = cur.fetchone()
    cur.close()
    conn.close()

    live_verified = (
        stored_events_count == 3 and
        live_row is not None and
        abs(live_row[0] - 28.6220) < 0.0001 and
        abs(live_row[1] - 77.2180) < 0.0001 and
        live_row[3] == "In Transit" and
        live_row[6] is False and
        live_row[7] == 3
    )
    record(
        "Driver Workflow",
        "5. PostgreSQL Live State & Telemetry Storage Verification",
        live_verified,
        f"Events stored: {stored_events_count}, Live: lat={live_row[0]}, lng={live_row[1]}, status={live_row[3]}, seq={live_row[7]}"
    )

    # -----------------------------------------------------------------------
    # 2. PARENT WORKFLOW
    # -----------------------------------------------------------------------
    print("\n--- 2. Testing Parent Workflow ---")

    # Step 1: Parent logs in
    parent_login_payload = {
        "username": "parent",
        "password": "parent123",
        "school_code": "DEFAULT",
        "user_type": "parent"
    }
    r_parent_login = requests.post(f"{BASE_URL}/auth/login", json=parent_login_payload)
    parent_login_ok = (r_parent_login.status_code == 200)
    parent_token = r_parent_login.json().get("access_token") if parent_login_ok else ""
    parent_headers = {"Authorization": f"Bearer {parent_token}"}
    record(
        "Parent Workflow",
        "1. Parent Login",
        parent_login_ok,
        f"HTTP {r_parent_login.status_code}, parent_id={r_parent_login.json().get('user_id')}"
    )

    # Step 2: Parent tracks assigned bus (Bus 12)
    r_track = requests.get(f"{BASE_URL}/tracking/bus/12", headers=parent_headers)
    track_ok = (r_track.status_code == 200)
    track_data = r_track.json() if track_ok else {}
    coords_match = (
        abs(track_data.get("latitude", 0) - 28.6220) < 0.0001 and
        abs(track_data.get("longitude", 0) - 77.2180) < 0.0001
    )
    record(
        "Parent Workflow",
        "2. Retrieve Assigned Bus Location & Accuracy",
        track_ok and coords_match,
        f"HTTP {r_track.status_code}, lat={track_data.get('latitude')}, lng={track_data.get('longitude')}, acc={track_data.get('accuracy_metres')}m, quality={track_data.get('gps_quality')}"
    )

    # Step 3: Stop Trip from driver
    r_stop = requests.post(f"{BASE_URL}/tracking/trip/stop", json={"bus_id": driver_bus_id}, headers=driver_headers)
    stop_ok = (r_stop.status_code == 200 and r_stop.json().get("status") == "stopped")
    summary = r_stop.json().get("summary", {}) if stop_ok else {}
    record(
        "Driver Workflow",
        "6. Stop Trip & Atomic Distance Summary",
        stop_ok and summary.get("total_events") == 3,
        f"HTTP {r_stop.status_code}, distance_km={summary.get('distance_km')}, events={summary.get('total_events')}"
    )

    # Step 4: Parent checks bus state after trip stopped (should be Idle)
    r_track_after = requests.get(f"{BASE_URL}/tracking/bus/12", headers=parent_headers)
    idle_ok = (r_track_after.status_code == 200 and r_track_after.json().get("status") == "Idle")
    record(
        "Parent Workflow",
        "3. Parent Views Completed/Idle Trip State",
        idle_ok,
        f"HTTP {r_track_after.status_code}, status={r_track_after.json().get('status')}"
    )

    # Step 5: Parent attempts to track unassigned bus (Bus 13 belongs to Kabir Verma / Parent 2)
    r_unauth = requests.get(f"{BASE_URL}/tracking/bus/13", headers=parent_headers)
    record(
        "Parent Workflow",
        "4. Parent Forbidden From Tracking Unassigned Bus (BOLA)",
        r_unauth.status_code == 403,
        f"HTTP {r_unauth.status_code} (Expected 403)"
    )

    # -----------------------------------------------------------------------
    # 3. ADMIN WORKFLOW
    # -----------------------------------------------------------------------
    print("\n--- 3. Testing Administrator Workflow ---")

    admin_login_payload = {
        "username": "admin",
        "password": "admin123",
        "school_code": "DEFAULT",
        "user_type": "admin"
    }
    r_admin_login = requests.post(f"{BASE_URL}/auth/login", json=admin_login_payload)
    admin_login_ok = (r_admin_login.status_code == 200)
    admin_token = r_admin_login.json().get("access_token") if admin_login_ok else ""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    record(
        "Admin Workflow",
        "1. Admin Login",
        admin_login_ok,
        f"HTTP {r_admin_login.status_code}, admin_id={r_admin_login.json().get('user_id')}"
    )

    # Admin fleet overview
    r_fleet = requests.get(f"{BASE_URL}/tracking/fleet", headers=admin_headers)
    fleet_ok = (r_fleet.status_code == 200)
    fleet_buses = r_fleet.json().get("buses", []) if fleet_ok else []
    fleet_bus_ids = [b["bus_id"] for b in fleet_buses]
    record(
        "Admin Workflow",
        "2. Fleet Map Multi-Bus Overview",
        fleet_ok and (12 in fleet_bus_ids and 13 in fleet_bus_ids),
        f"HTTP {r_fleet.status_code}, total_buses={len(fleet_buses)}, bus_ids={fleet_bus_ids}"
    )

    # Non-admin rejected from fleet overview
    r_fleet_parent = requests.get(f"{BASE_URL}/tracking/fleet", headers=parent_headers)
    record(
        "Admin Workflow",
        "3. Parent Forbidden From Admin Fleet Endpoint",
        r_fleet_parent.status_code == 403,
        f"HTTP {r_fleet_parent.status_code} (Expected 403)"
    )

    # -----------------------------------------------------------------------
    # 4. GPS & CONCURRENCY BEHAVIOR
    # -----------------------------------------------------------------------
    print("\n--- 4. Testing GPS Edge Cases & Concurrency Behavior ---")

    # Start a fresh trip on Bus 12 for edge-case testing
    r_start2 = requests.post(f"{BASE_URL}/tracking/trip/start", json={"bus_id": 12}, headers=driver_headers)
    trip2_id = r_start2.json().get("trip_id")

    # A. Duplicate event UUID on same trip (idempotent acceptance)
    test_uuid = str(uuid.uuid4())
    ev_dup1 = {
        "client_event_id": test_uuid,
        "trip_id": trip2_id,
        "bus_id": 12,
        "trip_sequence_number": 1,
        "latitude": 28.6145,
        "longitude": 77.2095,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    r_ev_orig = requests.post(f"{BASE_URL}/tracking/event", json=ev_dup1, headers=driver_headers)
    r_ev_dup = requests.post(f"{BASE_URL}/tracking/event", json=ev_dup1, headers=driver_headers)
    record(
        "GPS & Concurrency",
        "1. Duplicate Event UUID (Idempotency Acceptance)",
        r_ev_dup.status_code == 200 and r_ev_dup.json().get("accepted") is True and "duplicate" in r_ev_dup.json().get("status"),
        f"HTTP {r_ev_dup.status_code}, status={r_ev_dup.json().get('status')}"
    )

    # B. Reused UUID across different trips (rejection)
    requests.post(f"{BASE_URL}/tracking/trip/stop", json={"bus_id": 12}, headers=driver_headers)
    r_start3 = requests.post(f"{BASE_URL}/tracking/trip/start", json={"bus_id": 12}, headers=driver_headers)
    trip3_id = r_start3.json().get("trip_id")

    ev_cross_trip = {
        "client_event_id": test_uuid,  # Reused from trip 2
        "trip_id": trip3_id,
        "bus_id": 12,
        "trip_sequence_number": 1,
        "latitude": 28.6145,
        "longitude": 77.2095,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    r_cross_trip = requests.post(f"{BASE_URL}/tracking/event", json=ev_cross_trip, headers=driver_headers)
    record(
        "GPS & Concurrency",
        "2. Reused UUID Across Trips Rejected (409 Conflict)",
        r_cross_trip.status_code == 409,
        f"HTTP {r_cross_trip.status_code}, detail={r_cross_trip.json().get('detail')}"
    )

    # C. Out-of-order sequence arrival
    # Send seq #5 first
    requests.post(f"{BASE_URL}/tracking/event", json={
        "client_event_id": str(uuid.uuid4()),
        "trip_id": trip3_id,
        "bus_id": 12,
        "trip_sequence_number": 5,
        "latitude": 28.6300,
        "longitude": 77.2300,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }, headers=driver_headers)

    # Send seq #3 second (older event arriving late)
    r_ooo = requests.post(f"{BASE_URL}/tracking/event", json={
        "client_event_id": str(uuid.uuid4()),
        "trip_id": trip3_id,
        "bus_id": 12,
        "trip_sequence_number": 3,
        "latitude": 28.6180,
        "longitude": 77.2150,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }, headers=driver_headers)

    # Check live location did NOT regress to seq #3
    r_live_ooo = requests.get(f"{BASE_URL}/tracking/bus/12", headers=driver_headers)
    live_lat = r_live_ooo.json().get("latitude", 0)
    record(
        "GPS & Concurrency",
        "3. Out-Of-Order Event Handled Without Live Location Regression",
        r_ooo.status_code == 200 and r_ooo.json().get("out_of_order") is True and abs(live_lat - 28.6300) < 0.0001,
        f"Out-of-order flag={r_ooo.json().get('out_of_order')}, live_lat={live_lat} (held at 28.6300)"
    )

    # D. Coordinates outside service area (Tier 2 Diagnostic Rejection)
    # Testing location far outside Indian subcontinent service area (e.g. Sydney, Australia: -33.8688, 151.2093)
    r_outside = requests.post(f"{BASE_URL}/tracking/event", json={
        "client_event_id": str(uuid.uuid4()),
        "trip_id": trip3_id,
        "bus_id": 12,
        "trip_sequence_number": 6,
        "latitude": -33.8688,  # Sydney, Australia (outside metropolitan bounding box)
        "longitude": 151.2093,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }, headers=driver_headers)
    outside_ok = (
        r_outside.status_code == 200 and
        r_outside.json().get("accepted") is False and
        "service_area" in r_outside.json().get("status")
    )
    record(
        "GPS & Concurrency",
        "4. Coordinates Outside Service Area Hard-Rejected",
        outside_ok,
        f"HTTP {r_outside.status_code}, accepted={r_outside.json().get('accepted')}, note={r_outside.json().get('status')}"
    )

    # E. Impossible coordinates (lat > 90) -> HTTP 422
    r_impossible = requests.post(f"{BASE_URL}/tracking/event", json={
        "client_event_id": str(uuid.uuid4()),
        "trip_id": trip3_id,
        "bus_id": 12,
        "trip_sequence_number": 7,
        "latitude": 98.5000,  # Impossible
        "longitude": 77.2000,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }, headers=driver_headers)
    record(
        "GPS & Concurrency",
        "5. Impossible Coordinates Rejected (HTTP 422)",
        r_impossible.status_code == 422,
        f"HTTP {r_impossible.status_code}"
    )

    # F. Poor GPS accuracy (> 100m)
    r_poor = requests.post(f"{BASE_URL}/tracking/event", json={
        "client_event_id": str(uuid.uuid4()),
        "trip_id": trip3_id,
        "bus_id": 12,
        "trip_sequence_number": 8,
        "latitude": 28.6310,
        "longitude": 77.2310,
        "accuracy_metres": 150.0,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }, headers=driver_headers)
    r_live_poor = requests.get(f"{BASE_URL}/tracking/bus/12", headers=driver_headers)
    poor_quality = r_live_poor.json().get("gps_quality")
    record(
        "GPS & Concurrency",
        "6. Degraded/Poor GPS Accuracy Categorization",
        r_poor.status_code == 200 and poor_quality == "poor",
        f"HTTP {r_poor.status_code}, quality={poor_quality}"
    )

    # G. Two simultaneous trip-start requests (duplicate active trip prevention)
    r_dup_start = requests.post(f"{BASE_URL}/tracking/trip/start", json={"bus_id": 12}, headers=driver_headers)
    record(
        "GPS & Concurrency",
        "7. Duplicate Active Trip Blocked (HTTP 409)",
        r_dup_start.status_code == 409,
        f"HTTP {r_dup_start.status_code}, detail={r_dup_start.json().get('detail')}"
    )

    # H. Stop trip 3
    requests.post(f"{BASE_URL}/tracking/trip/stop", json={"bus_id": 12}, headers=driver_headers)

    # I. GPS event sent to stopped trip -> rejected
    r_post_stop = requests.post(f"{BASE_URL}/tracking/event", json={
        "client_event_id": str(uuid.uuid4()),
        "trip_id": trip3_id,
        "bus_id": 12,
        "trip_sequence_number": 9,
        "latitude": 28.6315,
        "longitude": 77.2315,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }, headers=driver_headers)
    record(
        "GPS & Concurrency",
        "8. Ingestion After Trip Stopped Rejected (HTTP 409 Conflict/Inactive)",
        r_post_stop.status_code in (404, 409),
        f"HTTP {r_post_stop.status_code}, detail={r_post_stop.json().get('detail')}"
    )

    # -----------------------------------------------------------------------
    # 5. MULTI-TENANT & SECURITY VERIFICATION
    # -----------------------------------------------------------------------
    print("\n--- 5. Testing Multi-Tenant & Security Controls ---")

    # Seed School 2 (Beta School) in database to verify tenant boundaries
    conn = database.connect_database()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO school (school_code, school_name, is_active)
        VALUES ('BETA_TEST', 'Beta Test Academy', TRUE)
        ON CONFLICT (LOWER(school_code)) DO NOTHING
        RETURNING school_id;
    """)
    s2_row = cur.fetchone()
    if s2_row:
        school2_id = s2_row[0]
    else:
        cur.execute("SELECT school_id FROM school WHERE LOWER(school_code) = 'beta_test';")
        school2_id = cur.fetchone()[0]

    # Seed Admin for School 2
    cur.execute("""
        INSERT INTO admin (school_id, USERNAME, password, full_name)
        VALUES (%s, 'admin_beta', %s, 'Admin Beta')
        ON CONFLICT DO NOTHING
        RETURNING admin_id;
    """, (school2_id, security.hash_password("beta123")))
    
    # Seed Bus for School 2
    cur.execute("""
        INSERT INTO bus (school_id, bus_number, driver_name, driver_phone, capacity, username, password)
        VALUES (%s, 'DL 2P 9999', 'Driver Beta', '9999999999', 40, 'driver_beta', %s)
        ON CONFLICT DO NOTHING
        RETURNING bus_id;
    """, (school2_id, security.hash_password("beta123")))
    b2_row = cur.fetchone()
    if b2_row:
        bus2_id = b2_row[0]
    else:
        cur.execute("SELECT bus_id FROM bus WHERE school_id = %s LIMIT 1;", (school2_id,))
        bus2_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # Login as Admin Beta (School 2)
    r_beta_login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin_beta",
        "password": "beta123",
        "school_code": "BETA_TEST",
        "user_type": "admin"
    })
    beta_token = r_beta_login.json().get("access_token")
    beta_headers = {"Authorization": f"Bearer {beta_token}"}

    # Verify Admin Beta only sees School 2 buses in fleet
    r_beta_fleet = requests.get(f"{BASE_URL}/tracking/fleet", headers=beta_headers)
    beta_fleet = r_beta_fleet.json().get("buses", [])
    beta_bus_ids = [b["bus_id"] for b in beta_fleet]
    record(
        "Security & Multi-Tenancy",
        "1. School B Cannot Retrieve School A Fleet",
        12 not in beta_bus_ids and 13 not in beta_bus_ids and bus2_id in beta_bus_ids,
        f"School B Fleet bus_ids={beta_bus_ids} (School A buses 12, 13 absent)"
    )

    # Driver A attempts to send telemetry to School 2's bus
    r_cross_telemetry = requests.post(f"{BASE_URL}/tracking/event", json={
        "client_event_id": str(uuid.uuid4()),
        "trip_id": 999,
        "bus_id": bus2_id,  # Belongs to School 2
        "trip_sequence_number": 1,
        "latitude": 28.6145,
        "longitude": 77.2095,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }, headers=driver_headers)
    record(
        "Security & Multi-Tenancy",
        "2. Driver A Forbidden From Accessing School B Bus",
        r_cross_telemetry.status_code == 403,
        f"HTTP {r_cross_telemetry.status_code} (Expected 403 Forbidden)"
    )

    # Suspended school account login rejection
    conn = database.connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE school SET is_active = FALSE WHERE school_id = %s;", (school2_id,))
    conn.commit()
    cur.close()
    conn.close()

    r_susp_login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin_beta",
        "password": "beta123",
        "school_code": "BETA_TEST",
        "user_type": "admin"
    })
    record(
        "Security & Multi-Tenancy",
        "3. Inactive/Suspended School Login Rejected",
        r_susp_login.status_code == 401,
        f"HTTP {r_susp_login.status_code}, detail={r_susp_login.json().get('detail')}"
    )

    # Clean up test school
    conn = database.connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM bus WHERE school_id = %s;", (school2_id,))
    cur.execute("DELETE FROM admin WHERE school_id = %s;", (school2_id,))
    cur.execute("DELETE FROM school WHERE school_id = %s;", (school2_id,))
    conn.commit()
    cur.close()
    conn.close()

    # -----------------------------------------------------------------------
    # SUMMARY REPORT
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("LIVE VERIFICATION SUMMARY")
    print("=" * 70)
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    print(f"Total Checks: {total} | Passed: {passed} | Failed: {failed}")
    print("=" * 70)
    return passed == total


if __name__ == "__main__":
    success = run_live_verification()
    sys.exit(0 if success else 1)
