import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from db_manager import get_connection, get_sqlalchemy_engine, dataframe_to_database

def seed_demo_data():
    """
    Seed the database with demonstration TB case data
    
    This function creates sample demonstration data for the TB Resistance Hub
    to show functionality and visualizations
    """
    print("Starting database seeding with demonstration data...")
    
    # Connect to database
    conn = get_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    # Generate data
    num_cases = 150  # Number of TB cases to generate
    
    # Create date range for diagnoses over the past 2 years
    start_date = datetime.now() - timedelta(days=730)  # 2 years ago
    end_date = datetime.now()
    
    # Generate random dates within range
    diagnosis_dates = [start_date + (end_date - start_date) * random.random() for _ in range(num_cases)]
    
    # TB Types and their approximate distribution
    tb_types = ['Drug-susceptible TB', 'INH-resistant TB', 'RR-TB', 'MDR-TB', 'XDR-TB']
    tb_type_weights = [0.6, 0.15, 0.1, 0.1, 0.05]  # Probabilities of each type
    
    # Locations (countries with high TB burden)
    locations = ['India', 'China', 'Indonesia', 'Philippines', 'Pakistan', 
                'Nigeria', 'Bangladesh', 'South Africa', 'DR Congo', 'Myanmar',
                'United States', 'Russia', 'Ethiopia', 'Vietnam', 'Brazil']
    
    # Treatment outcomes and approximate success rates by TB type
    outcomes = ['Cured', 'Treatment Completed', 'Treatment Failed', 'Lost to Follow-up', 'Died']
    
    # Create outcome probabilities by TB type
    outcome_probabilities = {
        'Drug-susceptible TB': [0.7, 0.15, 0.05, 0.06, 0.04],
        'INH-resistant TB': [0.65, 0.1, 0.1, 0.08, 0.07],
        'RR-TB': [0.55, 0.15, 0.12, 0.1, 0.08],
        'MDR-TB': [0.45, 0.1, 0.2, 0.15, 0.1],
        'XDR-TB': [0.35, 0.1, 0.25, 0.15, 0.15]
    }
    
    # Common resistance patterns
    resistance_patterns = {
        'Drug-susceptible TB': ['None'],
        'INH-resistant TB': ['INH', 'INH+SM'],
        'RR-TB': ['RIF', 'RIF+SM'],
        'MDR-TB': ['INH+RIF', 'INH+RIF+EMB', 'INH+RIF+SM', 'INH+RIF+EMB+SM'],
        'XDR-TB': ['INH+RIF+FQ+SLID', 'INH+RIF+EMB+PZA+FQ+SLID']
    }
    
    # Generate gender distribution
    genders = ['Male', 'Female']
    gender_weights = [0.65, 0.35]  # TB is more common in males
    
    # Generate age distribution (TB affects adults of working age more commonly)
    age_min, age_max = 1, 95
    age_mean, age_std = 45, 18
    
    # HIV status
    hiv_status = ['Positive', 'Negative', 'Unknown']
    hiv_weights = [0.2, 0.7, 0.1]
    
    # Generate treatment durations based on TB type
    treatment_durations = {
        'Drug-susceptible TB': (150, 210),  # 6-7 months
        'INH-resistant TB': (180, 300),     # 6-10 months
        'RR-TB': (270, 365),                # 9-12 months
        'MDR-TB': (450, 600),               # 15-20 months
        'XDR-TB': (540, 730)                # 18-24 months
    }
    
    # Common comorbidities
    comorbidities = ['Diabetes', 'Hypertension', 'COPD', 'Malnutrition', 'Alcohol use disorder', 
                     'Smoking', 'HIV/AIDS', 'Hepatitis', 'Renal disease', 'None']
    
    # Create empty data frame
    data = {
        'patient_id': [f'P{i:06d}' for i in range(1, num_cases + 1)],
        'age': np.round(np.clip(np.random.normal(age_mean, age_std, num_cases), age_min, age_max)).astype(int),
        'gender': np.random.choice(genders, num_cases, p=gender_weights),
        'location': np.random.choice(locations, num_cases),
        'diagnosis_date': diagnosis_dates,
        'tb_type': np.random.choice(tb_types, num_cases, p=tb_type_weights),
        'treatment_outcome': [],
        'hiv_status': np.random.choice(hiv_status, num_cases, p=hiv_weights),
        'comorbidities': [],
        'resistance_pattern': [],
        'treatment_start_date': [],
        'treatment_end_date': []
    }
    
    # Fill in dependent fields
    for i in range(num_cases):
        tb_type = data['tb_type'][i]
        
        # Set resistance pattern based on TB type
        data['resistance_pattern'].append(
            random.choice(resistance_patterns[tb_type])
        )
        
        # Set treatment outcome based on TB type
        data['treatment_outcome'].append(
            np.random.choice(outcomes, p=outcome_probabilities[tb_type])
        )
        
        # Set treatment dates
        # Some percentage of recent diagnoses might still be in treatment
        treatment_start = data['diagnosis_date'][i] + timedelta(days=random.randint(1, 14))
        
        if (datetime.now() - treatment_start).days < 60 or data['treatment_outcome'][i] in ['Lost to Follow-up', 'Died']:
            # Recent diagnosis or early loss - treatment not completed
            data['treatment_end_date'].append(None)
        else:
            # Completed treatment
            min_duration, max_duration = treatment_durations[tb_type]
            duration = random.randint(min_duration, max_duration)
            data['treatment_end_date'].append(treatment_start + timedelta(days=duration))
        
        data['treatment_start_date'].append(treatment_start)
        
        # Set comorbidities (0-3 random comorbidities per patient)
        num_comorbidities = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]
        if num_comorbidities == 0:
            data['comorbidities'].append('None')
        else:
            patient_comorbidities = random.sample([c for c in comorbidities if c != 'None'], num_comorbidities)
            data['comorbidities'].append(', '.join(patient_comorbidities))
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add created_by and created_at fields
    df['created_by'] = 1  # Assuming user ID 1 exists (admin)
    df['created_at'] = datetime.now()
    
    # Save to database
    try:
        print(f"Inserting {num_cases} TB cases into database...")
        
        # Use SQLAlchemy engine for better pandas-to-database integration
        engine = get_sqlalchemy_engine()
        df.to_sql('tb_cases', engine, if_exists='append', index=False)
        
        print("Demonstration data added successfully!")
        return True
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Execute if run directly
if __name__ == "__main__":
    seed_demo_data()