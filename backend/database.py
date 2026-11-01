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
    and ensures default admin credentials exist for first login.
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

        cursor.execute("SELECT admin_id FROM admin LIMIT 1;")
        admin = cursor.fetchone()
        if admin is None:
            default_admin_user = os.getenv("DEFAULT_ADMIN_USER", "admin")
            default_admin_pass = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
            hashed_pw = security.hash_password(default_admin_pass)
            cursor.execute(
                """
                INSERT INTO admin (USERNAME, password, full_name)
                VALUES (%s, %s, %s);
                """,
                (default_admin_user, hashed_pw, "System Administrator"),
            )

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

        conn.commit()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
