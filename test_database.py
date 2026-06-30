from database import connect_database

connection = connect_database()
cursor = connection.cursor()

cursor.execute("SELECT * FROM admin")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()