import mysql.connector  
import bcrypt

DB_CONFIG = {
    "host": "localhost",
    "user": "root",          
    "password": "",          
    "database": "saku"  
}

def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                task_text TEXT NOT NULL,
                due_date DATE,
                is_completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        return conn
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return None

def add_user(username, password):
    conn = connect_db()
    if not conn:
        return False
    
    try:
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                      (username, hashed_password))
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False  
    except Exception as e:
        print(f"Error adding user: {e}")
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = connect_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user['user_id']
        return None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None
    finally:
        conn.close()
        
def get_user_id(username, password):
    conn = connect_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def get_task_id(user_id):
    conn = connect_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT task_id FROM tasks WHERE user_id=%s ORDER BY task_id DESC LIMIT 1", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def save_task(user_id, task_text, due_date, is_completed=0):
    conn = connect_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (user_id, task_text, due_date, is_completed) VALUES (%s, %s, %s, %s)",
            (user_id, task_text, due_date, is_completed)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def delete_task(task_id):
    conn = connect_db()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def update_task_details(task_id, new_text, due_date, is_completed):
    conn = connect_db()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET task_text = %s, due_date = %s, is_completed = %s WHERE task_id = %s",
            (new_text, due_date, is_completed, task_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_user_tasks(user_id):
    conn = connect_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT task_id, task_text, due_date, is_completed FROM tasks WHERE user_id = %s",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()