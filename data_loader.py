import pandas as pd
import sqlite3
import requests
import json
import os
import io
import streamlit as st

def load_csv_data(file):
    """Load data from a CSV file into a pandas DataFrame"""
    try:
        df = pd.read_csv(file)
        return df, None
    except Exception as e:
        return None, str(e)

def load_excel_data(file):
    """Load data from an Excel file into a pandas DataFrame"""
    try:
        df = pd.read_excel(file)
        return df, None
    except Exception as e:
        return None, str(e)

def load_json_data(file):
    """Load data from a JSON file into a pandas DataFrame"""
    try:
        data = json.load(file)
        df = pd.json_normalize(data)
        return df, None
    except Exception as e:
        return None, str(e)

def load_api_data(api_url, api_key=None):
    """Load data from an API endpoint"""
    try:
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        df = pd.json_normalize(data)
        return df, None
    except Exception as e:
        return None, str(e)

def save_to_database(df, table_name, conn):
    """Save DataFrame to SQLite database table"""
    try:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        return True, None
    except Exception as e:
        return False, str(e)

def get_table_schema(table_name, conn):
    """Get schema information for a specified table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        return schema, None
    except Exception as e:
        return None, str(e)

def export_data(table_name, conn, format_type):
    """Export data from a database table in the specified format"""
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        
        if format_type == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            return output.getvalue(), None
        
        elif format_type == 'json':
            return df.to_json(orient='records'), None
        
        elif format_type == 'excel':
            output = io.BytesIO()
            df.to_excel(output, index=False)
            return output.getvalue(), None
        
        else:
            return None, "Unsupported export format"
            
    except Exception as e:
        return None, str(e)

def get_database_tables(conn):
    """Get a list of tables in the database"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables], None
    except Exception as e:
        return None, str(e)
