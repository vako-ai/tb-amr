import streamlit as st
import pandas as pd
import psycopg2
import hashlib
import json
from datetime import datetime
import os
import io
import re
import base64
from db_manager import get_connection

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

def create_connection(db_path=None):
    """Create a database connection to PostgreSQL"""
    # Now we use the get_connection function from db_manager.py
    return get_connection()

def get_user_id(username, conn):
    """Get user ID from username"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        st.error(f"Error getting user ID: {e}")
        return None

def format_datetime(dt_str):
    """Format datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str

def sanitize_filename(filename):
    """Sanitize a filename to remove invalid characters"""
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    return sanitized

def validate_date_format(date_str):
    """Validate if string is in valid date format"""
    try:
        if date_str:
            pd.to_datetime(date_str)
            return True
        return False
    except:
        return False

def encrypt_patient_id(patient_id):
    """Encrypt patient ID for privacy"""
    if not patient_id:
        return ""
    return hashlib.sha256(str(patient_id).encode()).hexdigest()[:10]

def anonymize_patient_data(patient_data):
    """Anonymize patient data by removing PII"""
    if not patient_data:
        return {}
    
    # Create a copy to avoid modifying the original
    anonymized = patient_data.copy()
    
    # Fields to remove
    pii_fields = ['name', 'full_name', 'address', 'phone', 'email', 'social_security', 'ssn', 'national_id']
    
    # Remove PII fields
    for field in pii_fields:
        if field in anonymized:
            del anonymized[field]
    
    # Hash patient ID
    if 'patient_id' in anonymized:
        anonymized['patient_id'] = encrypt_patient_id(anonymized['patient_id'])
    
    return anonymized

def format_resistance_pattern(pattern):
    """Format resistance pattern for display"""
    if not pattern or pattern == "Susceptible":
        return "Susceptible (No resistance)"
    
    # Split the pattern by "+" if it contains it
    if "+" in pattern:
        drugs = pattern.split("+")
        formatted_drugs = []
        
        # Common drug abbreviations and their full names
        drug_names = {
            "INH": "Isoniazid",
            "RIF": "Rifampicin",
            "PZA": "Pyrazinamide",
            "EMB": "Ethambutol",
            "SM": "Streptomycin",
            "FQ": "Fluoroquinolones",
            "AMI": "Amikacin",
            "KAN": "Kanamycin",
            "CAP": "Capreomycin",
            "ETH": "Ethionamide",
            "PAS": "Para-aminosalicylic acid",
            "BDQ": "Bedaquiline",
            "DLM": "Delamanid",
            "LZD": "Linezolid",
            "CFZ": "Clofazimine"
        }
        
        for drug in drugs:
            drug = drug.strip()
            if drug in drug_names:
                formatted_drugs.append(f"{drug} ({drug_names[drug]})")
            else:
                formatted_drugs.append(drug)
        
        return "Resistant to: " + ", ".join(formatted_drugs)
    
    return f"Resistant to: {pattern}"

def get_tb_type_description(tb_type):
    """Get description for TB type"""
    descriptions = {
        "Drug-susceptible TB": "TB that is susceptible to first-line drugs",
        "INH-resistant TB": "TB resistant to isoniazid but susceptible to rifampicin",
        "RR-TB": "Rifampicin-resistant TB",
        "MDR-TB": "TB resistant to at least isoniazid and rifampicin",
        "XDR-TB": "TB resistant to isoniazid, rifampicin, at least one fluoroquinolone, and at least one second-line injectable drug",
    }
    
    return descriptions.get(tb_type, "")

def log_activity(conn, user_id, activity_type, details=None):
    """Log user activity in the database"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO activity_log 
            (user_id, activity_type, details, timestamp)
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                activity_type,
                json.dumps(details) if details else None,
                datetime.now()
            )
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging activity: {e}")
        return False

def get_recent_activities(conn, limit=10):
    """Get recent activities from the log"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT al.id, u.username, al.activity_type, al.details, al.timestamp
            FROM activity_log al
            JOIN users u ON al.user_id = u.id
            ORDER BY al.timestamp DESC
            LIMIT %s
            """,
            (limit,)
        )
        results = cursor.fetchall()
        
        activities = []
        for row in results:
            # In PostgreSQL, datetime objects are returned directly
            timestamp = row[4]
            if isinstance(timestamp, str):
                timestamp = format_datetime(timestamp)
            elif isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
            activities.append({
                'id': row[0],
                'username': row[1],
                'activity_type': row[2],
                'details': json.loads(row[3]) if row[3] and isinstance(row[3], str) else row[3],
                'timestamp': timestamp
            })
        
        return activities
    except Exception as e:
        print(f"Error getting recent activities: {e}")
        return []

def generate_export_filename(prefix, export_format):
    """Generate a filename for data export"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{export_format}"

def validate_api_url(url):
    """Validate if a URL is properly formatted"""
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url) is not None

def get_download_link(content, filename, text="Download file"):
    """Generate a download link for file content"""
    if isinstance(content, str):
        content = content.encode()
    
    b64 = base64.b64encode(content).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href
