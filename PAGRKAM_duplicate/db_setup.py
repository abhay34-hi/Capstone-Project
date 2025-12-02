import sqlite3

DB_NAME = 'pgrkam_portal.db'

def create_db_connection():
    """Creates a connection to the SQLite database file."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_tables():
    """Creates the 'users' and 'applications' tables with required fields."""
    conn = create_db_connection()
    c = conn.cursor()
    try:
        # 1. USERS TABLE (Stores registration and login data)
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                mobile_number TEXT UNIQUE NOT NULL,
                email TEXT,
                user_type TEXT,
                first_name TEXT,
                last_name TEXT,
                gender TEXT,
                education TEXT,
                district TEXT
            )
        """)

        # 2. APPLICATIONS TABLE (Stores job application history)
        c.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                app_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                job_title TEXT NOT NULL,
                department TEXT,
                status TEXT DEFAULT 'Submitted',
                date_applied DATE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        print("✅ Database tables 'users' and 'applications' created successfully.")
    except sqlite3.Error as e:
        print(f"Database error during table creation: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # Running this script creates the database file and tables.
    create_tables()