import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import json

def preprocess_tb_data(df):
    """
    Preprocesses TB data for analysis
    
    Parameters:
    df (pandas.DataFrame): Raw TB data
    
    Returns:
    pandas.DataFrame: Processed TB data
    """
    # Make a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Convert date columns to datetime if they exist
    date_columns = [col for col in processed_df.columns if 'date' in col.lower()]
    for col in date_columns:
        try:
            processed_df[col] = pd.to_datetime(processed_df[col], errors='coerce')
        except:
            pass
    
    # Handle missing values
    for col in processed_df.columns:
        if processed_df[col].dtype == 'object':
            processed_df[col] = processed_df[col].fillna('Unknown')
        else:
            processed_df[col] = processed_df[col].fillna(0)
    
    # Standardize column names (lowercase, replace spaces with underscores)
    processed_df.columns = [col.lower().replace(' ', '_') for col in processed_df.columns]
    
    return processed_df

def extract_resistance_patterns(df, drug_columns):
    """
    Extracts resistance patterns from drug resistance columns
    
    Parameters:
    df (pandas.DataFrame): TB data
    drug_columns (list): List of columns containing drug resistance info
    
    Returns:
    pandas.DataFrame: DataFrame with resistance patterns
    """
    pattern_df = df.copy()
    
    # Create a new column for resistance pattern
    pattern_df['resistance_pattern'] = ''
    
    # Generate resistance pattern string
    for idx, row in pattern_df.iterrows():
        resistant_drugs = []
        for drug in drug_columns:
            if row[drug] == 1 or row[drug] == 'Resistant' or row[drug] == 'Yes':
                drug_name = drug.replace('_resistant', '').replace('_resistance', '')
                resistant_drugs.append(drug_name.upper())
        
        pattern_df.at[idx, 'resistance_pattern'] = '+'.join(resistant_drugs) if resistant_drugs else 'Susceptible'
    
    return pattern_df

def categorize_tb_type(df):
    """
    Categorizes TB cases based on resistance patterns
    
    Parameters:
    df (pandas.DataFrame): TB data with resistance patterns
    
    Returns:
    pandas.DataFrame: DataFrame with TB type categorization
    """
    categorized_df = df.copy()
    
    # Define TB type based on resistance pattern
    def determine_tb_type(row):
        pattern = row['resistance_pattern'].upper()
        
        if pattern == 'SUSCEPTIBLE':
            return 'Drug-susceptible TB'
        elif 'RIF' in pattern and 'INH' in pattern:
            if 'FQ' in pattern and ('AMI' in pattern or 'KAN' in pattern or 'CAP' in pattern):
                return 'XDR-TB'
            else:
                return 'MDR-TB'
        elif 'RIF' in pattern:
            return 'RR-TB'
        elif 'INH' in pattern:
            return 'INH-resistant TB'
        else:
            return 'Other resistance'
    
    categorized_df['tb_type'] = categorized_df.apply(determine_tb_type, axis=1)
    
    return categorized_df

def calculate_resistance_metrics(conn):
    """
    Calculates resistance metrics from the database
    
    Parameters:
    conn: SQLite database connection
    
    Returns:
    dict: Dictionary containing resistance metrics
    """
    try:
        # Get TB cases data
        cases_query = """
        SELECT 
            tb_type, 
            COUNT(*) as count,
            strftime('%Y-%m', diagnosis_date) as month
        FROM 
            tb_cases 
        GROUP BY 
            tb_type, month
        ORDER BY 
            month
        """
        cases_df = pd.read_sql(cases_query, conn)
        
        # Get treatment outcomes
        outcomes_query = """
        SELECT 
            tb_type, 
            treatment_outcome,
            COUNT(*) as count
        FROM 
            tb_cases 
        WHERE 
            treatment_outcome IS NOT NULL
        GROUP BY 
            tb_type, treatment_outcome
        """
        outcomes_df = pd.read_sql(outcomes_query, conn)
        
        # Calculate success rates
        success_rates = {}
        for tb_type in outcomes_df['tb_type'].unique():
            type_data = outcomes_df[outcomes_df['tb_type'] == tb_type]
            success = type_data[type_data['treatment_outcome'].isin(['Cured', 'Treatment Completed'])]['count'].sum()
            total = type_data['count'].sum()
            success_rates[tb_type] = (success / total * 100) if total > 0 else 0
        
        # Prepare time series data
        time_series = {}
        for tb_type in cases_df['tb_type'].unique():
            type_data = cases_df[cases_df['tb_type'] == tb_type]
            time_series[tb_type] = dict(zip(type_data['month'], type_data['count']))
        
        # Compile metrics
        metrics = {
            'success_rates': success_rates,
            'time_series': time_series,
            'total_cases': cases_df['count'].sum(),
            'mdr_cases': cases_df[cases_df['tb_type'] == 'MDR-TB']['count'].sum(),
            'xdr_cases': cases_df[cases_df['tb_type'] == 'XDR-TB']['count'].sum()
        }
        
        return metrics
    
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return {}

def generate_geographical_distribution(conn):
    """
    Generates geographical distribution data from the database
    
    Parameters:
    conn: SQLite database connection
    
    Returns:
    pandas.DataFrame: Geographical distribution data
    """
    try:
        query = """
        SELECT 
            location, 
            tb_type, 
            COUNT(*) as count
        FROM 
            tb_cases 
        GROUP BY 
            location, tb_type
        """
        geo_df = pd.read_sql(query, conn)
        
        # Pivot the data for easier visualization
        pivot_df = geo_df.pivot(index='location', columns='tb_type', values='count').fillna(0)
        
        return pivot_df.reset_index()
    
    except Exception as e:
        print(f"Error generating geographical distribution: {e}")
        return pd.DataFrame()
