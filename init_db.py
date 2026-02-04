import sqlite3
import os

DB_FILE = "notes.db"

# Optional: delete existing database for a fresh start
# if os.path.exists(DB_FILE):
#     os.remove(DB_FILE)

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign keys

# Execute schema.sql to create tables
with open("schema.sql", "r") as f:
    conn.executescript(f.read())

conn.commit()
conn.close()

print(f"Database '{DB_FILE}' initialized successfully.")
