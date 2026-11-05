import os
import sys
import psycopg2
from dotenv import load_dotenv

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

load_dotenv(dotenv_path=os.path.join(BACKEND_DIR, '.env'))
load_dotenv()

import security
from database import connect_database


def reset_to_clean_development():
    """
    Clears all demo/seed data in local development environments only.
    Strictly prohibited in production or staging environments.
    """
    env = os.getenv("ENVIRONMENT", "development").strip().lower()
    if env in ("production", "staging"):
        raise RuntimeError(
            f"FATAL: Database reset is strictly forbidden in {env.upper()} environment! Operation aborted."
        )

    # Require explicit confirmation flag
    if "--confirm-destructive-reset" not in sys.argv:
        print("ERROR: reset_db.py is a destructive command.")
        print("To proceed in development, you must pass the exact flag: --confirm-destructive-reset")
        sys.exit(1)

    # If running interactively in terminal, require typing exact confirmation phrase
    if sys.stdin.isatty():
        confirmation = input("WARNING: This will erase all data. Type 'CONFIRM DESTRUCTIVE RESET' to proceed: ")
        if confirmation.strip() != "CONFIRM DESTRUCTIVE RESET":
            print("Reset cancelled. No data was modified.")
            sys.exit(0)

    conn = connect_database()
    cursor = conn.cursor()
    try:
        print("Truncating development tables...")
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
        print("Database reset successfully to clean development slate.")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    reset_to_clean_development()

