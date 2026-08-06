import re

with open('dal.py', 'r') as f:
    content = f.read()

# Replace import sqlite3 with import psycopg2
content = content.replace('import sqlite3\n', 'import psycopg2\n')

# Replace ? with %s
# Be careful: only replace ? if they are not in comments, but in this file, ? is only used in SQL statements.
content = content.replace('?', '%s')

with open('dal.py', 'w') as f:
    f.write(content)

print("dal.py updated.")
