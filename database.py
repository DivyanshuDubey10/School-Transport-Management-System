import psycopg2
import os
from dotenv import load_dotenv
import security

load_dotenv()

def connect_database():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "stms_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )
    return connection

def initialize_database():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS admin (
                       admin_id SERIAL PRIMARY KEY,
                       USERNAME VARCHAR(255) NOT NULL UNIQUE,
                       password VARCHAR(255) NOT NULL,
                       full_name VARCHAR(255) NOT NULL
                    )
                   """)
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    if admin is None:
        hashed_pw = security.hash_password("admin123")
        cursor.execute(
            """
                       INSERT INTO admin (USERNAME, password, full_name)
                       VALUES(%s, %s, %s)
            """,
            ("admin", hashed_pw, "Administrator"),
        )
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS parent (
                       parent_id SERIAL PRIMARY KEY,
                       parent_name VARCHAR(255) NOT NULL UNIQUE,
                       phone VARCHAR(50) NOT NULL UNIQUE,
                       address TEXT NOT NULL,
                       pickup_point VARCHAR(255) NOT NULL,
                       username VARCHAR(255) NOT NULL,
                       password VARCHAR(255) NOT NULL
                    )
                   """)
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS route (
                        route_id SERIAL PRIMARY KEY,
                        route_name VARCHAR(255) NOT NULL
                    )
                    """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS bus (
                       bus_id SERIAL PRIMARY KEY,
                       bus_number VARCHAR(100) NOT NULL UNIQUE,
                       driver_name VARCHAR(255) NOT NULL,
                       driver_phone VARCHAR(50) NOT NULL UNIQUE,
                       capacity INTEGER NOT NULL,
                       route_id INTEGER,
                       FOREIGN KEY (route_id) REFERENCES route(route_id)
                   )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS student (
                        student_id SERIAL PRIMARY KEY,
                        student_name VARCHAR(255) NOT NULL,
                        student_class VARCHAR(50) NOT NULL,
                        parent_id INTEGER NOT NULL,
                        route_id INTEGER NOT NULL,
                        fee_status VARCHAR(50) NOT NULL,
                        fee_paid DECIMAL DEFAULT 0.0,
                        fee_balance DECIMAL DEFAULT 0.0,
                        FOREIGN KEY (parent_id) REFERENCES parent(parent_id),
                        FOREIGN KEY (route_id) REFERENCES route(route_id)
                    )
                    """)
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
