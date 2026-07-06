import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()
cursor.execute("PRAGMA table_info(student)")

for column in cursor.fetchall():
    print(column)
    
connection.close()