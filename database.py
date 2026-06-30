import sqlite3


def connect_database():
    connection = sqlite3.connect("database.db")
    return connection


def initialize_database():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS admin (
                       admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       USERNAME TEXT NOT NULL UNIQUE,
                       password TEXT NOT NULL,
                       full_name TEXT NOT NULL
                    )
                   """)
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    if admin is None:
        cursor.execute(
            """
                       INSERT INTO admin (USERNAME, password, full_name)
                       VALUES(?, ?, ?)
        """,
            ("admin", "admin123", "Administrator"),
        )
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS parent (
                       parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       parent_name TEXT NOT NULL UNIQUE,
                       phone NUMBER NOT NULL UNIQUE,
                       address TEXT NOT NULL,
                       username TEXT NOT NULL,
                       password TEXT NOT NULL
                    )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS student (
                        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_name TEXT NOT NULL,
                        student_class TEXT NOT NULL,
                        parent_id INTEGER NOT NULL,
                        phone TEXT NOT NULL UNIQUE,
                        address TEXT NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,

                        FOREIGN KEY (parent_id) REFERENCES parent(parent_id)
                    );
                    """)
    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
