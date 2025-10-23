import os
import psycopg2
from psycopg2 import sql
import time

# Read environment variables
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Retry until DB is ready
for i in range(10):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("✅ Connected to PostgreSQL!")
        break
    except Exception as e:
        print("⏳ Waiting for PostgreSQL to start...", e)
        time.sleep(3)
else:
    raise Exception("❌ Could not connect to the database after several attempts.")

cur = conn.cursor()

# ✅ Create table with a UNIQUE constraint
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(50),
    UNIQUE (name, email)
);
""")

# ✅ Insert record safely (no duplicates)
cur.execute("""
    INSERT INTO users (name, email)
    VALUES (%s, %s)
    ON CONFLICT (name, email) DO NOTHING
    RETURNING id;
""", ("Alice", "alice@example.com"))

result = cur.fetchone()

if result:
    user_id = result[0]
    print(f"🎉 New user inserted with id = {user_id}")
else:
    print("ℹ️ User already exists, skipping insert.")

conn.commit()

# ✅ Retrieve all records
cur.execute("SELECT * FROM users;")
records = cur.fetchall()
print("\n📋 Users in Database:")
for row in records:
    print(f"{row[0]} — {row[1]} ({row[2]})")

cur.close()
conn.close()
