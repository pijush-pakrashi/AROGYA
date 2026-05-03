import sqlite3

conn = sqlite3.connect('arogya.db')
c = conn.cursor()
try:
    c.execute("ALTER TABLE users ADD COLUMN age INTEGER")
    conn.commit()
    print("Column 'age' added successfully")
except Exception as e:
    print("Error or column already exists:", e)
conn.close()
