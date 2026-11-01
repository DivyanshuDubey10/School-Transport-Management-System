import os
import psycopg2
from dotenv import load_dotenv
import security

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


def connect_database():
    """
    Connect to PostgreSQL using either:
    1. DATABASE_URL (standard on Railway, Render, Supabase, Neon, Heroku)
    2. Discrete DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD environment variables.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "stms_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )


def initialize_database():
    """
    Creates all necessary schema tables if they do not exist,
    and sets up default test credentials (admin, parent, driver)
    so the app can be immediately tested online.
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
                route_id INTEGER REFERENCES route(route_id) ON DELETE SET NULL,
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
                parent_id INTEGER NOT NULL REFERENCES parent(parent_id) ON DELETE CASCADE,
                route_id INTEGER REFERENCES route(route_id) ON DELETE SET NULL,
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
                student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
                requested_pickup_point VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'Pending'
            );
        """)

        # 7. Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
                bus_id INTEGER NOT NULL REFERENCES bus(bus_id) ON DELETE CASCADE,
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

        # -------------------------------------------------------------------
        # Default Test Accounts for Testing/Portfolio Access
        # -------------------------------------------------------------------

        # A. Default Admin (admin / admin123)
        cursor.execute("SELECT admin_id FROM admin LIMIT 1;")
        if not cursor.fetchone():
            default_admin_user = os.getenv("DEFAULT_ADMIN_USER", "admin")
            default_admin_pass = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
            hashed_admin = security.hash_password(default_admin_pass)
            cursor.execute(
                """
                INSERT INTO admin (USERNAME, password, full_name)
                VALUES (%s, %s, %s);
                """,
                (default_admin_user, hashed_admin, "System Administrator"),
            )

        # B. Sample Route
        cursor.execute("SELECT route_id FROM route LIMIT 1;")
        route_row = cursor.fetchone()
        if not route_row:
            cursor.execute(
                "INSERT INTO route (route_name) VALUES (%s) RETURNING route_id;",
                ("North Route - Purana Bazar",),
            )
            route_id = cursor.fetchone()[0]
        else:
            route_id = route_row[0]

        # C. Default Driver & Bus (driver1 / driver123)
        cursor.execute("SELECT bus_id FROM bus LIMIT 1;")
        bus_row = cursor.fetchone()
        if not bus_row:
            hashed_driver = security.hash_password("driver123")
            cursor.execute(
                """
                INSERT INTO bus (bus_number, driver_name, driver_phone, capacity, route_id, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING bus_id;
                """,
                ("DL 1P 1001", "Rajesh Sharma", "9876543210", 40, route_id, "driver1", hashed_driver),
            )
            bus_id = cursor.fetchone()[0]
        else:
            bus_id = bus_row[0]

        # D. Default Parent (parent1 / parent123)
        cursor.execute("SELECT parent_id FROM parent WHERE username = 'parent1' LIMIT 1;")
        parent_row = cursor.fetchone()
        if not parent_row:
            hashed_parent = security.hash_password("parent123")
            cursor.execute(
                """
                INSERT INTO parent (parent_name, phone, address, pickup_point, username, password)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING parent_id;
                """,
                ("Rahul Sharma", "9876543200", "42, Purana Bazar, New Delhi", "Purana Bazar Chowk", "parent1", hashed_parent),
            )
            parent_id = cursor.fetchone()[0]
        else:
            parent_id = parent_row[0]

        # E. Sample Student linked to parent1 and the route
        cursor.execute("SELECT student_id FROM student LIMIT 1;")
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO student (student_name, student_class, parent_id, route_id, transport_status, fee_status, fee_paid, fee_balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                ("Aarav Sharma", "Class 5A", parent_id, route_id, "Active", "Paid", 1500.0, 0.0),
            )

        conn.commit()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized with test credentials successfully.")
