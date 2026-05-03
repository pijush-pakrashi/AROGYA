import sqlite3

conn = sqlite3.connect('arogya.db')
c = conn.cursor()
try:
    c.execute("ALTER TABLE users ADD COLUMN city VARCHAR(100) DEFAULT ''")
    c.execute("ALTER TABLE users ADD COLUMN address TEXT DEFAULT ''")
    conn.commit()
    print("Columns added successfully")
except Exception as e:
    print("Error or columns already exist:", e)
conn.close()
