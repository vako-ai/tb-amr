import os
import streamlit as st
from pathlib import Path
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
import pandas as pd
import json
from datetime import datetime

def get_database_url():
    """Get the database URL from environment variables"""
    return os.environ.get('DATABASE_URL')

def get_connection():
    """
    Create a connection to the PostgreSQL database
    
    Returns:
    connection: PostgreSQL connection object
    """
    try:
        conn = psycopg2.connect(get_database_url())
        return conn
    except psycopg2.Error as e:
        st.error(f"Database connection error: {e}")
        return None

def initialize_database(db_path=None):
    """
    Initialize the PostgreSQL database with required tables
    
    Returns:
    bool: Success status
    """
    try:
        # Connect to the database
        conn = get_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP NOT NULL,
            last_login TIMESTAMP
        )
        """)
        
        # Create TB cases table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_cases (
            id SERIAL PRIMARY KEY,
            patient_id TEXT,
            age INTEGER,
            gender TEXT,
            location TEXT,
            diagnosis_date TIMESTAMP,
            tb_type TEXT,
            resistance_pattern TEXT,
            treatment_regimen TEXT,
            treatment_start_date TIMESTAMP,
            treatment_end_date TIMESTAMP,
            treatment_outcome TEXT,
            hiv_status TEXT,
            comorbidities TEXT,
            created_by INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        """)
        
        # Create resistance patterns table for detailed drug resistance data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resistance_details (
            id SERIAL PRIMARY KEY,
            case_id INTEGER,
            drug_name TEXT,
            is_resistant BOOLEAN,
            test_method TEXT,
            test_date TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES tb_cases (id)
        )
        """)
        
        # Create patients table for clinical decision support
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            patient_id TEXT UNIQUE,
            data JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP
        )
        """)
        
        # Create sharing preferences table for global collaboration
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sharing_preferences (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            data_elements JSONB,
            anonymization_level TEXT,
            regions_allowed JSONB,
            auto_update BOOLEAN DEFAULT FALSE,
            sharing_token TEXT UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Create collaboration requests table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS collaboration_requests (
            id SERIAL PRIMARY KEY,
            requester_id INTEGER,
            provider_token TEXT,
            request_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            response_date TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (requester_id) REFERENCES users (id),
            FOREIGN KEY (provider_token) REFERENCES sharing_preferences (sharing_token)
        )
        """)
        
        # Create activity log table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            activity_type TEXT,
            details JSONB,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Create models table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id SERIAL PRIMARY KEY,
            name TEXT,
            description TEXT,
            model_type TEXT,
            created_by INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            metrics JSONB,
            is_active BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        """)
        
        # Create genomic data table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS genomic_data (
            id SERIAL PRIMARY KEY,
            patient_id TEXT,
            case_id INTEGER,
            sequence_data JSONB,
            mutations JSONB,
            analysis_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            analysis_method TEXT,
            FOREIGN KEY (case_id) REFERENCES tb_cases (id)
        )
        """)
        
        # Create research publications table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_publications (
            id SERIAL PRIMARY KEY,
            title TEXT,
            authors JSONB,
            publication_date TIMESTAMP,
            journal TEXT,
            abstract TEXT,
            url TEXT,
            keywords JSONB,
            related_data_ids JSONB
        )
        """)
        
        conn.commit()
        conn.close()
        
        return True
    
    except psycopg2.Error as e:
        print(f"Database initialization error: {e}")
        return False

def check_table_exists(conn, table_name):
    """
    Check if a table exists in the database
    
    Parameters:
    conn: Database connection
    table_name (str): Name of the table to check
    
    Returns:
    bool: True if the table exists, False otherwise
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
        """, (table_name,))
        result = cursor.fetchone()
        return result[0]
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False

def execute_query(conn, query, params=None):
    """
    Execute a SQL query on the database
    
    Parameters:
    conn: Database connection
    query (str): SQL query to execute
    params (tuple): Query parameters (optional)
    
    Returns:
    bool: Success status
    """
    try:
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        return True
    
    except psycopg2.Error as e:
        print(f"Query execution error: {e}")
        return False

def fetch_data(conn, query, params=None):
    """
    Fetch data from the database using a query
    
    Parameters:
    conn: Database connection
    query (str): SQL query to execute
    params (tuple): Query parameters (optional)
    
    Returns:
    list: Query results as a list of tuples
    """
    try:
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor.fetchall()
    
    except psycopg2.Error as e:
        print(f"Data fetch error: {e}")
        return []

def get_table_columns(conn, table_name):
    """
    Get the column names of a table
    
    Parameters:
    conn: Database connection
    table_name (str): Name of the table
    
    Returns:
    list: List of column names
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = %s
        """, (table_name,))
        columns = cursor.fetchall()
        return [column[0] for column in columns]
    
    except psycopg2.Error as e:
        print(f"Error getting table columns: {e}")
        return []

def execute_script(conn, script_path):
    """
    Execute a SQL script file
    
    Parameters:
    conn: Database connection
    script_path (str): Path to the SQL script file
    
    Returns:
    bool: Success status
    """
    try:
        with open(script_path, 'r') as f:
            script = f.read()
        
        cursor = conn.cursor()
        cursor.execute(script)
        conn.commit()
        return True
    
    except (psycopg2.Error, IOError) as e:
        print(f"Script execution error: {e}")
        return False

def backup_database(schema_name='public', output_dir=None):
    """
    Create a backup of the database schema
    
    Parameters:
    schema_name (str): Name of the schema to backup (default: 'public')
    output_dir (str): Directory to save the backup file
    
    Returns:
    bool: Success status
    """
    try:
        if not output_dir:
            output_dir = '.'
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(output_dir, f'tb_resistance_hub_backup_{timestamp}.sql')
        
        # Get connection parameters from DATABASE_URL
        db_url = get_database_url()
        
        # Use pg_dump to create backup
        os.system(f'pg_dump --schema={schema_name} --file={backup_file} {db_url}')
        
        return True
    
    except Exception as e:
        print(f"Database backup error: {e}")
        return False

def get_sqlalchemy_engine():
    """
    Get SQLAlchemy engine for the PostgreSQL database
    
    Returns:
    sqlalchemy.engine.Engine: SQLAlchemy engine object
    """
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        return None

def dataframe_to_database(df, table_name, if_exists='append'):
    """
    Save a pandas DataFrame to the database
    
    Parameters:
    df (pandas.DataFrame): DataFrame to save
    table_name (str): Name of the target table
    if_exists (str): How to behave if the table exists ('fail', 'replace', 'append')
    
    Returns:
    bool: Success status
    """
    try:
        engine = get_sqlalchemy_engine()
        if engine:
            df.to_sql(table_name, engine, if_exists=if_exists, index=False)
            return True
        return False
    except Exception as e:
        print(f"Error saving DataFrame to database: {e}")
        return False

def query_to_dataframe(query, params=None):
    """
    Execute a query and return the result as a pandas DataFrame
    
    Parameters:
    query (str): SQL query to execute
    params (tuple): Query parameters (optional)
    
    Returns:
    pandas.DataFrame: Query results as a DataFrame
    """
    try:
        conn = get_connection()
        if not conn:
            return pd.DataFrame()
            
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
            
        conn.close()
        return df
    except Exception as e:
        print(f"Error executing query to DataFrame: {e}")
        return pd.DataFrame()