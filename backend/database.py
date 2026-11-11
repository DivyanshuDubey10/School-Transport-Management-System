import os
import datetime
from typing import Optional
import psycopg2
from dotenv import load_dotenv
import security

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


def get_database_url() -> Optional[str]:
    """
    Finds the PostgreSQL connection URL from environment variables,
    accounting for case variations (DATABASE_URL vs database_url)
    and common provider names (Neon, Render, Supabase).
    """
    candidate_keys = [
        "DATABASE_URL",
        "database_url",
        "Database_Url",
        "POSTGRES_URL",
        "postgres_url",
        "NEON_DATABASE_URL",
        "neon_database_url",
        "DB_URL",
        "db_url",
    ]
    for key in candidate_keys:
        val = os.getenv(key)
        if val and val.strip():
            return val.strip()

    # Search all env vars case-insensitively
    for k, v in os.environ.items():
        if k.lower() in ("database_url", "postgres_url", "neon_database_url", "db_url", "neon_url"):
            if v and v.strip():
                return v.strip()

    # Check for any environment variable whose value begins with postgresql:// or postgres://
    for k, v in os.environ.items():
        if isinstance(v, str) and (v.strip().startswith("postgresql://") or v.strip().startswith("postgres://")):
            return v.strip()

    return None


def connect_database():
    """
    Connect to PostgreSQL using either:
    1. DATABASE_URL (standard on Render, Neon, Supabase, Railway)
    2. Discrete DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD environment variables.
    """
    database_url = get_database_url()
    if database_url:
        # Standardize postgres:// prefix to postgresql:// for psycopg2
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # Ensure sslmode=require for cloud-hosted databases (Neon, Render, Supabase)
        if "sslmode=" not in database_url and ("neon.tech" in database_url or "render.com" in database_url or "supabase.co" in database_url):
            sep = "&" if "?" in database_url else "?"
            database_url = f"{database_url}{sep}sslmode=require"

        return psycopg2.connect(database_url)

    # Fallback to discrete parameters (local development)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "stms_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )


def run_alembic_migrations():
    """Applies all Alembic migrations to the current database."""
    try:
        from alembic.config import Config
        from alembic import command
        alembic_ini_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
        if os.path.exists(alembic_ini_path):
            cfg = Config(alembic_ini_path)
            command.upgrade(cfg, "head")
    except Exception as e:
        # If running in an environment without alembic CLI or during testing, log or re-raise
        print(f"Notice: alembic migration execution: {e}")


def initialize_database():
    """
    Creates all necessary schema tables if they do not exist,
    applies all Alembic migrations, and sets up default test credentials
    (admin, parent, driver) linked to the default school.
    Safe to run repeatedly (idempotent).
    """
    conn = connect_database()
    cursor = conn.cursor()

    try:
        # 1. Admin table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                admin_id SERIAL PRIMARY KEY,
                USERNAME VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL
            );
        """)

        # 2. Parent table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parent (
                parent_id SERIAL PRIMARY KEY,
                parent_name VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                address TEXT NOT NULL,
                pickup_point VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
        """)

        # 3. Route table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS route (
                route_id SERIAL PRIMARY KEY,
                route_name VARCHAR(255) NOT NULL
            );
        """)

        # 4. Bus table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bus (
                bus_id SERIAL PRIMARY KEY,
                bus_number VARCHAR(100) NOT NULL UNIQUE,
                driver_name VARCHAR(255) NOT NULL,
                driver_phone VARCHAR(50) NOT NULL,
                capacity INTEGER NOT NULL,
                route_id INTEGER,
                username VARCHAR(255) UNIQUE,
                password VARCHAR(255)
            );
        """)

        # 5. Student table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                student_id SERIAL PRIMARY KEY,
                student_name VARCHAR(255) NOT NULL,
                student_class VARCHAR(50) NOT NULL,
                parent_id INTEGER NOT NULL,
                route_id INTEGER,
                transport_status VARCHAR(50) DEFAULT 'Active',
                fee_status VARCHAR(50) DEFAULT 'Pending',
                fee_paid DECIMAL DEFAULT 0.0,
                fee_balance DECIMAL DEFAULT 0.0
            );
        """)

        # 6. Transport change request table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transport_change_request (
                request_id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                requested_pickup_point VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'Pending'
            );
        """)

        # 7. Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                bus_id INTEGER NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(50) NOT NULL,
                UNIQUE (student_id, date)
            );
        """)

        # 8. User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                setting_id SERIAL PRIMARY KEY,
                user_type VARCHAR(50) NOT NULL,
                user_id INTEGER NOT NULL,
                setting_key VARCHAR(255) NOT NULL,
                setting_value VARCHAR(255),
                UNIQUE(user_type, user_id, setting_key)
            );
        """)

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    # Apply all Alembic migrations up to head (adding school, multi-tenancy columns, composite FKs, etc.)
    run_alembic_migrations()

    # Reconnect to seed default data with dynamic school_id resolution
    conn = connect_database()
    cursor = conn.cursor()
    try:
        # Dynamically resolve default school_id
        cursor.execute("SELECT school_id FROM school WHERE LOWER(school_code) = 'default' LIMIT 1;")
        school_row = cursor.fetchone()
        default_school_id = school_row[0] if school_row else 1

        # -------------------------------------------------------------------
        # Default Test Accounts for Testing/Portfolio Access
        # -------------------------------------------------------------------

        # A. Default Admin (admin / admin123)
        hashed_admin = security.hash_password("admin123")
        cursor.execute("SELECT admin_id FROM admin WHERE school_id = %s AND LOWER(USERNAME) = 'admin';", (default_school_id,))
        admin_row = cursor.fetchone()
        if not admin_row:
            cursor.execute(
                """
                INSERT INTO admin (school_id, USERNAME, password, full_name)
                VALUES (%s, %s, %s, %s);
                """,
                (default_school_id, "admin", hashed_admin, "System Administrator"),
            )
        else:
            cursor.execute("UPDATE admin SET password = %s WHERE school_id = %s AND LOWER(USERNAME) = 'admin';", (hashed_admin, default_school_id))

        # B. Routes
        cursor.execute("SELECT route_id FROM route WHERE school_id = %s AND route_name = %s LIMIT 1;", (default_school_id, "North Route - Purana Bazar"))
        r1_row = cursor.fetchone()
        if not r1_row:
            cursor.execute("INSERT INTO route (school_id, route_name) VALUES (%s, %s) RETURNING route_id;", (default_school_id, "North Route - Purana Bazar"))
            route_id_1 = cursor.fetchone()[0]
        else:
            route_id_1 = r1_row[0]

        cursor.execute("SELECT route_id FROM route WHERE school_id = %s AND route_name = %s LIMIT 1;", (default_school_id, "South Route - Sector 14 & Ring Road"))
        r2_row = cursor.fetchone()
        if not r2_row:
            cursor.execute("INSERT INTO route (school_id, route_name) VALUES (%s, %s) RETURNING route_id;", (default_school_id, "South Route - Sector 14 & Ring Road"))
            route_id_2 = cursor.fetchone()[0]
        else:
            route_id_2 = r2_row[0]

        # C. Drivers & Buses
        hashed_driver = security.hash_password("driver123")
        cursor.execute("SELECT bus_id FROM bus WHERE school_id = %s AND LOWER(username) = 'driver';", (default_school_id,))
        b1_row = cursor.fetchone()
        if not b1_row:
            cursor.execute(
                """
                INSERT INTO bus (school_id, bus_number, driver_name, driver_phone, capacity, route_id, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING bus_id;
                """,
                (default_school_id, "DL 1P 1001", "Rajesh Sharma", "9876543210", 40, route_id_1, "driver", hashed_driver),
            )
            bus_id_1 = cursor.fetchone()[0]
        else:
            bus_id_1 = b1_row[0]
            cursor.execute("UPDATE bus SET password = %s, route_id = %s WHERE school_id = %s AND LOWER(username) = 'driver';", (hashed_driver, route_id_1, default_school_id))

        cursor.execute("SELECT bus_id FROM bus WHERE school_id = %s AND LOWER(username) = 'driver1';", (default_school_id,))
        b2_row = cursor.fetchone()
        if not b2_row:
            cursor.execute(
                """
                INSERT INTO bus (school_id, bus_number, driver_name, driver_phone, capacity, route_id, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING bus_id;
                """,
                (default_school_id, "DL 1P 1002", "Suresh Kumar", "9876543211", 35, route_id_2, "driver1", hashed_driver),
            )
            bus_id_2 = cursor.fetchone()[0]
        else:
            bus_id_2 = b2_row[0]
            cursor.execute("UPDATE bus SET password = %s, route_id = %s WHERE school_id = %s AND LOWER(username) = 'driver1';", (hashed_driver, route_id_2, default_school_id))

        # D. Parents
        hashed_parent = security.hash_password("parent123")
        cursor.execute("SELECT parent_id FROM parent WHERE school_id = %s AND LOWER(username) = 'parent';", (default_school_id,))
        p1_row = cursor.fetchone()
        if not p1_row:
            cursor.execute(
                """
                INSERT INTO parent (school_id, parent_name, phone, address, pickup_point, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING parent_id;
                """,
                (default_school_id, "Sharma Family", "9876543200", "42, Purana Bazar, New Delhi", "Purana Bazar Chowk", "parent", hashed_parent),
            )
            parent_id_1 = cursor.fetchone()[0]
        else:
            parent_id_1 = p1_row[0]
            cursor.execute("UPDATE parent SET password = %s WHERE school_id = %s AND LOWER(username) = 'parent';", (hashed_parent, default_school_id))

        cursor.execute("SELECT parent_id FROM parent WHERE school_id = %s AND LOWER(username) = 'parent1';", (default_school_id,))
        p2_row = cursor.fetchone()
        if not p2_row:
            cursor.execute(
                """
                INSERT INTO parent (school_id, parent_name, phone, address, pickup_point, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING parent_id;
                """,
                (default_school_id, "Verma Family", "9876543201", "15, Sector 14, New Delhi", "Sector 14 Metro Station", "parent1", hashed_parent),
            )
            parent_id_2 = cursor.fetchone()[0]
        else:
            parent_id_2 = p2_row[0]
            cursor.execute("UPDATE parent SET password = %s WHERE school_id = %s AND LOWER(username) = 'parent1';", (hashed_parent, default_school_id))

        # E. Students
        cursor.execute("SELECT student_id FROM student WHERE school_id = %s AND student_name = %s LIMIT 1;", (default_school_id, "Aarav Sharma"))
        s1 = cursor.fetchone()
        if not s1:
            cursor.execute(
                """
                INSERT INTO student (school_id, student_name, student_class, parent_id, route_id, transport_status, fee_status, fee_paid, fee_balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING student_id;
                """,
                (default_school_id, "Aarav Sharma", "Class 5A", parent_id_1, route_id_1, "Active", "Paid", 1500.0, 0.0),
            )
            s1_id = cursor.fetchone()[0]
        else:
            s1_id = s1[0]

        cursor.execute("SELECT student_id FROM student WHERE school_id = %s AND student_name = %s LIMIT 1;", (default_school_id, "Diya Sharma"))
        s2 = cursor.fetchone()
        if not s2:
            cursor.execute(
                """
                INSERT INTO student (school_id, student_name, student_class, parent_id, route_id, transport_status, fee_status, fee_paid, fee_balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING student_id;
                """,
                (default_school_id, "Diya Sharma", "Class 8B", parent_id_1, route_id_1, "Active", "Pending", 1000.0, 500.0),
            )
            s2_id = cursor.fetchone()[0]
        else:
            s2_id = s2[0]

        cursor.execute("SELECT student_id FROM student WHERE school_id = %s AND student_name = %s LIMIT 1;", (default_school_id, "Kabir Verma"))
        s3 = cursor.fetchone()
        if not s3:
            cursor.execute(
                """
                INSERT INTO student (school_id, student_name, student_class, parent_id, route_id, transport_status, fee_status, fee_paid, fee_balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING student_id;
                """,
                (default_school_id, "Kabir Verma", "Class 6C", parent_id_2, route_id_2, "Active", "Paid", 1500.0, 0.0),
            )
            s3_id = cursor.fetchone()[0]
        else:
            s3_id = s3[0]

        # F. Sample Attendance
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        for (sid, bid) in [(s1_id, bus_id_1), (s2_id, bus_id_1), (s3_id, bus_id_2)]:
            cursor.execute(
                """
                INSERT INTO attendance (school_id, student_id, bus_id, date, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (school_id, student_id, date) DO NOTHING;
                """,
                (default_school_id, sid, bid, today, "Present"),
            )
            cursor.execute(
                """
                INSERT INTO attendance (school_id, student_id, bus_id, date, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (school_id, student_id, date) DO NOTHING;
                """,
                (default_school_id, sid, bid, yesterday, "Present"),
            )

        # G. Sample Transport Change Request
        cursor.execute("SELECT request_id FROM transport_change_request WHERE school_id = %s LIMIT 1;", (default_school_id,))
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO transport_change_request (school_id, student_id, requested_pickup_point, status)
                VALUES (%s, %s, %s, %s);
                """,
                (default_school_id, s2_id, "Community Center Gate 2", "Pending"),
            )

        # H. Seed Route Stops for North and South Routes if not present
        cursor.execute("SELECT COUNT(*) FROM route_stop WHERE school_id = %s;", (default_school_id,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO route_stop (school_id, route_id, sequence, stop_name, latitude, longitude, stop_type, geofence_radius_m)
                VALUES
                    (%s, %s, 1, 'School Main Campus', 28.6139, 77.2090, 'school', 80),
                    (%s, %s, 2, 'Purana Bazar Chowk', 28.6190, 77.2150, 'stop', 50),
                    (%s, %s, 3, 'Old Market Crossing', 28.6250, 77.2210, 'stop', 50),
                    (%s, %s, 1, 'School South Gate', 28.6130, 77.2080, 'school', 80),
                    (%s, %s, 2, 'Sector 14 Metro Station', 28.6010, 77.1990, 'stop', 50),
                    (%s, %s, 3, 'Ring Road Junction', 28.5910, 77.1900, 'stop', 50);
            """, (default_school_id, route_id_1, default_school_id, route_id_1, default_school_id, route_id_1,
                  default_school_id, route_id_2, default_school_id, route_id_2, default_school_id, route_id_2))

        # I. Initialize Bus Live Location records for seed buses
        for bid in [bus_id_1, bus_id_2]:
            cursor.execute("""
                INSERT INTO bus_live_location (bus_id, school_id, status, is_stale)
                VALUES (%s, %s, 'Idle', FALSE)
                ON CONFLICT (bus_id) DO NOTHING;
            """, (bid, default_school_id))

        conn.commit()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized with test credentials successfully.")
