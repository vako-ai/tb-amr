import streamlit as st
import hashlib
import os
import datetime
import db_manager
from db_manager import get_connection

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Verify user credentials against the database"""
    try:
        conn = get_connection()
        if not conn:
            return False, None
            
        cursor = conn.cursor()
        
        # Get the user from the database
        cursor.execute("SELECT password_hash, role FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result is None:
            conn.close()
            return False, None
        
        stored_hash, role = result
        computed_hash = hash_password(password)
        
        # Update last login time
        if stored_hash == computed_hash:
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE username = %s",
                (datetime.datetime.now(), username)
            )
            conn.commit()
            conn.close()
            return True, role
        else:
            conn.close()
            return False, None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False, None

def create_user(username, password, role="user"):
    """Create a new user in the database"""
    try:
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone() is not None:
            conn.close()
            return False, "Username already exists"
        
        # Create the new user with timestamp
        current_time = datetime.datetime.now()
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at, last_login) VALUES (%s, %s, %s, %s, %s)",
            (username, password_hash, role, current_time, current_time)
        )
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False, str(e)

def login_widget():
    """Display the login form and handle authentication"""
    if not st.session_state.authenticated:
        st.title("TB Resistance Hub")
        st.subheader("Login")
        
        # Create a form for login
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if username and password:
                    authenticated, role = verify_user(username, password)
                    if authenticated:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = role
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
        
        # Check if we need to create the initial admin user
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                conn.close()
                
                if user_count == 0:
                    st.info("No users found. Creating default admin user: admin/admin123")
                    success, message = create_user("admin", "admin123", "admin")
                    if success:
                        st.info("Please login with the default credentials and change the password immediately.")
                    else:
                        st.error(f"Error creating admin user: {message}")
            else:
                st.error("Database connection failed. Could not check for existing users.")
                # Initialize the database
                if db_manager.initialize_database():
                    st.info("Database initialized. Refresh the page to continue.")
        except Exception as e:
            st.error(f"Database initialization error: {e}")
