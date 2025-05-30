import streamlit as st
import pandas as pd
import sqlite3
import json
import datetime
import uuid

def generate_sharing_token():
    """Generate a unique token for data sharing"""
    return str(uuid.uuid4())

def save_sharing_preferences(conn, preferences):
    """
    Save data sharing preferences to the database
    
    Parameters:
    conn: Database connection
    preferences (dict): Data sharing preferences
    
    Returns:
    bool: Success status
    """
    try:
        cursor = conn.cursor()
        
        # Check if preferences already exist
        cursor.execute("SELECT id FROM sharing_preferences WHERE user_id = ?", (preferences['user_id'],))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing preferences
            cursor.execute(
                """
                UPDATE sharing_preferences
                SET data_elements = ?, anonymization_level = ?, regions_allowed = ?,
                    auto_update = ?, last_updated = ?
                WHERE user_id = ?
                """,
                (
                    json.dumps(preferences['data_elements']),
                    preferences['anonymization_level'],
                    json.dumps(preferences['regions_allowed']),
                    preferences['auto_update'],
                    datetime.datetime.now().isoformat(),
                    preferences['user_id']
                )
            )
        else:
            # Insert new preferences
            cursor.execute(
                """
                INSERT INTO sharing_preferences 
                (user_id, data_elements, anonymization_level, regions_allowed, auto_update, 
                 sharing_token, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    preferences['user_id'],
                    json.dumps(preferences['data_elements']),
                    preferences['anonymization_level'],
                    json.dumps(preferences['regions_allowed']),
                    preferences['auto_update'],
                    generate_sharing_token(),
                    datetime.datetime.now().isoformat(),
                    datetime.datetime.now().isoformat()
                )
            )
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error saving sharing preferences: {e}")
        return False

def get_sharing_preferences(conn, user_id):
    """
    Retrieve data sharing preferences from the database
    
    Parameters:
    conn: Database connection
    user_id (str): User identifier
    
    Returns:
    dict: Data sharing preferences
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT data_elements, anonymization_level, regions_allowed, auto_update, sharing_token
            FROM sharing_preferences
            WHERE user_id = ?
            """,
            (user_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                'user_id': user_id,
                'data_elements': json.loads(result[0]),
                'anonymization_level': result[1],
                'regions_allowed': json.loads(result[2]),
                'auto_update': result[3],
                'sharing_token': result[4]
            }
        else:
            # Return default preferences if not found
            return {
                'user_id': user_id,
                'data_elements': ['aggregated_cases', 'resistance_patterns'],
                'anonymization_level': 'high',
                'regions_allowed': ['global'],
                'auto_update': False
            }
    
    except Exception as e:
        print(f"Error retrieving sharing preferences: {e}")
        return None

def get_shared_datasets(conn):
    """
    Retrieve list of shared datasets available for collaboration
    
    Parameters:
    conn: Database connection
    
    Returns:
    pandas.DataFrame: Available shared datasets
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT sp.id, u.username, sp.data_elements, sp.anonymization_level, 
                   sp.last_updated, sp.sharing_token
            FROM sharing_preferences sp
            JOIN users u ON sp.user_id = u.id
            """
        )
        results = cursor.fetchall()
        
        if results:
            datasets = []
            for row in results:
                data_elements = json.loads(row[2])
                datasets.append({
                    'id': row[0],
                    'provider': row[1],
                    'data_elements': ', '.join(data_elements),
                    'anonymization_level': row[3],
                    'last_updated': row[4],
                    'sharing_token': row[5]
                })
            
            return pd.DataFrame(datasets)
        else:
            return pd.DataFrame(columns=['id', 'provider', 'data_elements', 
                                       'anonymization_level', 'last_updated', 'sharing_token'])
    
    except Exception as e:
        print(f"Error retrieving shared datasets: {e}")
        return pd.DataFrame()

def anonymize_data(df, level='high'):
    """
    Anonymize data based on specified level
    
    Parameters:
    df (pandas.DataFrame): Data to anonymize
    level (str): Anonymization level (low, medium, high)
    
    Returns:
    pandas.DataFrame: Anonymized data
    """
    anonymized_df = df.copy()
    
    # Identify PII columns (adjust based on your actual data)
    pii_columns = [col for col in df.columns if any(x in col.lower() for x in 
                  ['name', 'id', 'address', 'phone', 'email', 'dob', 'birth'])]
    
    # Apply anonymization based on level
    if level == 'high':
        # Remove all PII
        anonymized_df = anonymized_df.drop(columns=pii_columns, errors='ignore')
        
        # Aggregate data to higher level
        if 'location' in anonymized_df.columns:
            # Keep only region/state level, remove specific locations
            anonymized_df['location'] = anonymized_df['location'].apply(
                lambda x: x.split(',')[-1].strip() if isinstance(x, str) and ',' in x else x
            )
        
    elif level == 'medium':
        # Hash identifiers instead of removing
        for col in pii_columns:
            if col in anonymized_df.columns:
                anonymized_df[col] = anonymized_df[col].apply(
                    lambda x: hash(str(x)) if x is not None else None
                )
    
    elif level == 'low':
        # Only remove direct identifiers like name, phone, email
        direct_pii = [col for col in pii_columns if any(x in col.lower() for x in 
                      ['name', 'phone', 'email'])]
        anonymized_df = anonymized_df.drop(columns=direct_pii, errors='ignore')
    
    return anonymized_df

def prepare_collaborative_dataset(conn, sharing_token):
    """
    Prepare a dataset for sharing based on sharing preferences
    
    Parameters:
    conn: Database connection
    sharing_token (str): Token identifying sharing preferences
    
    Returns:
    pandas.DataFrame: Prepared dataset for sharing
    """
    try:
        cursor = conn.cursor()
        
        # Get sharing preferences
        cursor.execute(
            """
            SELECT user_id, data_elements, anonymization_level, regions_allowed
            FROM sharing_preferences
            WHERE sharing_token = ?
            """,
            (sharing_token,)
        )
        result = cursor.fetchone()
        
        if not result:
            return None
        
        user_id, data_elements_json, anonymization_level, regions_allowed_json = result
        data_elements = json.loads(data_elements_json)
        regions_allowed = json.loads(regions_allowed_json)
        
        # Prepare datasets based on requested elements
        datasets = []
        
        if 'aggregated_cases' in data_elements:
            # Get aggregated case data
            cases_query = """
            SELECT location, tb_type, COUNT(*) as count, 
                   strftime('%Y-%m', diagnosis_date) as month
            FROM tb_cases
            GROUP BY location, tb_type, month
            """
            cases_df = pd.read_sql(cases_query, conn)
            
            # Apply region filtering if not global
            if 'global' not in regions_allowed:
                cases_df = cases_df[cases_df['location'].isin(regions_allowed)]
            
            if not cases_df.empty:
                datasets.append(('aggregated_cases', cases_df))
        
        if 'resistance_patterns' in data_elements:
            # Get resistance pattern data
            resistance_query = """
            SELECT resistance_pattern, COUNT(*) as count, location
            FROM tb_cases
            GROUP BY resistance_pattern, location
            """
            resistance_df = pd.read_sql(resistance_query, conn)
            
            # Apply region filtering if not global
            if 'global' not in regions_allowed:
                resistance_df = resistance_df[resistance_df['location'].isin(regions_allowed)]
            
            if not resistance_df.empty:
                datasets.append(('resistance_patterns', resistance_df))
        
        if 'treatment_outcomes' in data_elements:
            # Get treatment outcome data
            outcomes_query = """
            SELECT treatment_outcome, tb_type, COUNT(*) as count, location
            FROM tb_cases
            WHERE treatment_outcome IS NOT NULL
            GROUP BY treatment_outcome, tb_type, location
            """
            outcomes_df = pd.read_sql(outcomes_query, conn)
            
            # Apply region filtering if not global
            if 'global' not in regions_allowed:
                outcomes_df = outcomes_df[outcomes_df['location'].isin(regions_allowed)]
            
            if not outcomes_df.empty:
                datasets.append(('treatment_outcomes', outcomes_df))
        
        # Apply anonymization to all datasets
        anonymized_datasets = []
        for name, df in datasets:
            anonymized_df = anonymize_data(df, anonymization_level)
            anonymized_datasets.append((name, anonymized_df))
        
        # For simplicity, we'll combine all datasets into one
        if anonymized_datasets:
            combined_data = pd.concat([df.assign(dataset_type=name) for name, df in anonymized_datasets])
            return combined_data
        else:
            return pd.DataFrame()
    
    except Exception as e:
        print(f"Error preparing collaborative dataset: {e}")
        return None

def record_collaboration_request(conn, requester_id, provider_token, status='pending'):
    """
    Record a collaboration request in the database
    
    Parameters:
    conn: Database connection
    requester_id (str): ID of the user requesting data
    provider_token (str): Sharing token of the data provider
    status (str): Status of the request
    
    Returns:
    bool: Success status
    """
    try:
        cursor = conn.cursor()
        
        # Insert collaboration request
        cursor.execute(
            """
            INSERT INTO collaboration_requests
            (requester_id, provider_token, request_date, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                requester_id,
                provider_token,
                datetime.datetime.now().isoformat(),
                status
            )
        )
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error recording collaboration request: {e}")
        return False

def get_pending_collaboration_requests(conn, user_id):
    """
    Get pending collaboration requests for a user
    
    Parameters:
    conn: Database connection
    user_id (str): User ID
    
    Returns:
    pandas.DataFrame: Pending collaboration requests
    """
    try:
        cursor = conn.cursor()
        
        # Get the user's sharing token
        cursor.execute(
            "SELECT sharing_token FROM sharing_preferences WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return pd.DataFrame()
        
        sharing_token = result[0]
        
        # Get pending requests for this token
        cursor.execute(
            """
            SELECT cr.id, u.username as requester, cr.request_date, cr.status
            FROM collaboration_requests cr
            JOIN users u ON cr.requester_id = u.id
            WHERE cr.provider_token = ? AND cr.status = 'pending'
            """,
            (sharing_token,)
        )
        results = cursor.fetchall()
        
        if results:
            requests = []
            for row in results:
                requests.append({
                    'id': row[0],
                    'requester': row[1],
                    'request_date': row[2],
                    'status': row[3]
                })
            
            return pd.DataFrame(requests)
        else:
            return pd.DataFrame(columns=['id', 'requester', 'request_date', 'status'])
    
    except Exception as e:
        print(f"Error retrieving pending collaboration requests: {e}")
        return pd.DataFrame()

def update_collaboration_request(conn, request_id, status):
    """
    Update the status of a collaboration request
    
    Parameters:
    conn: Database connection
    request_id (int): Request ID
    status (str): New status
    
    Returns:
    bool: Success status
    """
    try:
        cursor = conn.cursor()
        
        # Update request status
        cursor.execute(
            """
            UPDATE collaboration_requests
            SET status = ?, response_date = ?
            WHERE id = ?
            """,
            (
                status,
                datetime.datetime.now().isoformat(),
                request_id
            )
        )
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error updating collaboration request: {e}")
        return False
