import sqlite3

username = input("Masukkan username baru: ")
password = input("Masukkan password: ")

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

try:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    print(f"User '{username}' berhasil ditambahkan.")
except sqlite3.IntegrityError:
    print(f"User '{username}' sudah ada.")
finally:
    conn.close()
