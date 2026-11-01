import os
import psycopg2
from dotenv import load_dotenv
import security
from database import connect_database


def reset_to_clean_production():
    """
    Clears all demo/seed data (students, parents, buses, routes, attendance, change requests, user settings)
    and ensures a clean default administrator account exists for production use.
    """
    conn = connect_database()
    cursor = conn.cursor()
    try:
        print("Truncating seed tables...")
        cursor.execute("TRUNCATE TABLE transport_change_request CASCADE;")
        cursor.execute("TRUNCATE TABLE attendance CASCADE;")
        cursor.execute("TRUNCATE TABLE student CASCADE;")
        cursor.execute("TRUNCATE TABLE parent CASCADE;")
        cursor.execute("TRUNCATE TABLE bus CASCADE;")
        cursor.execute("TRUNCATE TABLE route CASCADE;")
        cursor.execute("TRUNCATE TABLE user_settings CASCADE;")

        cursor.execute("SELECT admin_id FROM admin LIMIT 1;")
        if not cursor.fetchone():
            default_user = os.getenv("DEFAULT_ADMIN_USER", "admin")
            default_pass = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
            hashed_pw = security.hash_password(default_pass)
            cursor.execute(
                "INSERT INTO admin (USERNAME, password, full_name) VALUES (%s, %s, %s);",
                (default_user, hashed_pw, "System Administrator"),
            )
        conn.commit()
        print("Database reset successfully to clean production slate.")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    reset_to_clean_production()

