import sqlite3
from datetime import datetime

DB_NAME = 'pgrkam_portal.db'

# --- 1. CONNECTION HELPER ---
def get_db_connection():
    """Returns a connection object to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name (like a dictionary)
    return conn

# --- 2. USER REGISTRATION ---
def add_user(data):
    """Inserts a new user record into the database."""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("""
            INSERT INTO users (
                username, password, mobile_number, email, user_type, 
                first_name, last_name, gender, education, district
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['username'], data['password'], data['mobile'], data['email'], 
            data['user_type'], data['first_name'], data['last_name'], data['gender'], 
            data['education'], data['district']
        ))
        conn.commit()
        return True, "Registration successful."
    
    except sqlite3.IntegrityError:
        return False, "Error: Username or Mobile number already exists."
    except sqlite3.Error as e:
        return False, f"Database error during registration: {e}"
    finally:
        conn.close()

# --- 3. USER LOGIN VERIFICATION ---
def verify_login(username, password):
    """Checks credentials and returns user data if valid."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    
    conn.close()
    
    if user:
        # Return user info as a dictionary (due to conn.row_factory)
        return True, dict(user) 
    else:
        return False, None

# --- 4. SAVE APPLICATION HISTORY ---
def save_application(user_id, job_title, department):
    """Records a submitted job application."""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("""
            INSERT INTO applications (user_id, job_title, department, date_applied)
            VALUES (?, ?, ?, ?)
        """, (
            user_id, job_title, department, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return True, "Application saved."
    except sqlite3.Error as e:
        return False, f"Error saving application: {e}"
    finally:
        conn.close()

# --- 5. RETRIEVE APPLICATION STATUS ---
def get_applications_by_username(username):
    """Retrieves all application records for a given username."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # First, find the user's ID
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_row = c.fetchone()
    
    if user_row:
        user_id = user_row['id']
        c.execute("SELECT job_title, department, status, date_applied FROM applications WHERE user_id = ?", (user_id,))
        apps = c.fetchall()
        
        # Convert list of rows to list of dictionaries
        result = [dict(row) for row in apps]
        conn.close()
        return result
    
    conn.close()
    return []