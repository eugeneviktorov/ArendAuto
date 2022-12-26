import sqlite3

conn = sqlite3.connect('base.db')
cursor = conn.cursor()

cursor.execute("INSERT INTO admins (login, password) VALUES (?,?)", ("admin", "admin"))
conn.commit()