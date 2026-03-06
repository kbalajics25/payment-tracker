import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Tuple
import re

DATABASE_PATH = 'database.db'

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username
    Requirements:
    - 3-20 characters
    - Alphanumeric and underscore only
    """
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Username is valid"

def register_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user
    Returns: (success: bool, message: str)
    """
    # Validate username
    valid, msg = validate_username(username)
    if not valid:
        return False, msg
    
    # Validate password
    valid, msg = validate_password(password)
    if not valid:
        return False, msg
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists. Please choose another."
        
        # Hash password and create user
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                      (username, password_hash))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[int], str]:
    """
    Authenticate user credentials
    Returns: (success: bool, user_id: Optional[int], message: str)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        conn.close()
        
        if not user:
            return False, None, "Invalid username or password"
        
        if check_password_hash(user['password_hash'], password):
            return True, user['id'], "Login successful"
        else:
            return False, None, "Invalid username or password"
    except Exception as e:
        return False, None, f"Authentication failed: {str(e)}"

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user information by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, created_at FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        return dict(user) if user else None
    except Exception as e:
        return None

def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
    """Change user password"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current password hash
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "User not found"
        
        # Verify old password
        if not check_password_hash(user['password_hash'], old_password):
            conn.close()
            return False, "Current password is incorrect"
        
        # Validate new password
        valid, msg = validate_password(new_password)
        if not valid:
            conn.close()
            return False, msg
        
        # Update password
        new_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
        
        conn.commit()
        conn.close()
        
        return True, "Password changed successfully"
    except Exception as e:
        return False, f"Password change failed: {str(e)}"