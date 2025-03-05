import sqlite3

# Creăm/conectăm baza de date
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Ștergem tabelele vechi dacă există (opțional, pentru resetare completă)
cursor.execute("DROP TABLE IF EXISTS attendance")
cursor.execute("DROP TABLE IF EXISTS employees")

# Creăm tabela pentru angajați
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nume TEXT NOT NULL,
    email TEXT NOT NULL,
    departament TEXT,
    data_angajarii TEXT,
    detalii TEXT
)
""")

# Creăm tabela pentru pontaj
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time_in TEXT,
    time_out TEXT,
    FOREIGN KEY (user_id) REFERENCES employees(id)
)
""")

conn.commit()
conn.close()

print("✅ Baza de date a fost creată cu tabelele employees și attendance.")
