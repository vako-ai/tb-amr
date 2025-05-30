import pandas as pd
import numpy as np
import streamlit as st
import sqlite3
import json
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import pickle
import os

# Drug resistance regimen guidelines
REGIMEN_GUIDELINES = {
    "Drug-susceptible TB": {
        "first_line": ["Isoniazid", "Rifampicin", "Pyrazinamide", "Ethambutol"],
        "duration": "6 months",
        "notes": "Standard 6-month regimen. Ethambutol may be omitted in certain cases."
    },
    "INH-resistant TB": {
        "first_line": ["Rifampicin", "Pyrazinamide", "Ethambutol", "Levofloxacin"],
        "duration": "6-9 months",
        "notes": "Consider extending treatment to 9 months for extensive disease."
    },
    "RR-TB": {
        "first_line": ["Bedaquiline", "Linezolid", "Levofloxacin", "Clofazimine", "Cycloserine"],
        "duration": "9-12 months",
        "notes": "Modified shorter MDR-TB regimen may be used if criteria are met."
    },
    "MDR-TB": {
        "first_line": ["Bedaquiline", "Linezolid", "Levofloxacin", "Clofazimine", "Cycloserine"],
        "alternatives": ["Delamanid", "Meropenem", "Amikacin", "Ethionamide", "Para-aminosalicylic acid"],
        "duration": "18-24 months",
        "notes": "Regimen should include at least 4 likely effective drugs."
    },
    "XDR-TB": {
        "first_line": ["Bedaquiline", "Linezolid", "Delamanid", "Clofazimine", "Cycloserine", "Meropenem", "Amoxicillin-clavulanate"],
        "duration": "18-24 months",
        "notes": "Individualized regimen essential. Consider surgical options if localized disease."
    }
}

# Side effects data
DRUG_SIDE_EFFECTS = {
    "Isoniazid": ["Peripheral neuropathy", "Hepatitis", "Rash"],
    "Rifampicin": ["Orange-colored bodily fluids", "Hepatitis", "Flu-like syndrome", "Drug interactions"],
    "Pyrazinamide": ["Hepatitis", "Hyperuricemia", "Arthralgias"],
    "Ethambutol": ["Optic neuritis", "Visual disturbances", "Hyperuricemia"],
    "Levofloxacin": ["Tendinopathy", "QT prolongation", "GI disturbances", "CNS effects"],
    "Moxifloxacin": ["QT prolongation", "Tendinopathy", "GI disturbances", "CNS effects"],
    "Bedaquiline": ["QT prolongation", "Hepatitis", "Headache"],
    "Linezolid": ["Peripheral neuropathy", "Optic neuritis", "Bone marrow suppression", "Lactic acidosis"],
    "Clofazimine": ["Skin discoloration", "QT prolongation", "Abdominal pain"],
    "Cycloserine": ["Neuropsychiatric effects", "Seizures", "Suicidal ideation"],
    "Delamanid": ["QT prolongation", "Nausea", "Vomiting"],
    "Meropenem": ["Diarrhea", "Nausea", "Headache", "Infusion site reactions"],
    "Amikacin": ["Ototoxicity", "Nephrotoxicity", "Vestibular toxicity"],
    "Ethionamide": ["GI intolerance", "Hepatitis", "Hypothyroidism"],
    "Para-aminosalicylic acid": ["GI intolerance", "Hepatitis", "Hypothyroidism"]
}

def get_drug_interactions(drugs):
    """
    Returns potential drug interactions for a given set of drugs
    
    Parameters:
    drugs (list): List of drug names
    
    Returns:
    list: List of potential drug interactions
    """
    interactions = []
    
    # Check for specific drug interactions
    if "Rifampicin" in drugs:
        interactions.append("Rifampicin decreases levels of many drugs through CYP induction (anticoagulants, anticonvulsants, methadone, etc.)")
    
    if "Bedaquiline" in drugs and ("Moxifloxacin" in drugs or "Levofloxacin" in drugs or "Clofazimine" in drugs):
        interactions.append("Multiple QT-prolonging drugs (Bedaquiline, fluoroquinolones, Clofazimine) - increased risk of arrhythmias")
    
    if "Linezolid" in drugs and "Isoniazid" in drugs:
        interactions.append("Linezolid and Isoniazid - increased risk of neuropathy and CNS effects")
    
    return interactions

def determine_tb_type(resistance_data):
    """
    Determines TB type based on resistance data
    
    Parameters:
    resistance_data (dict): Dictionary containing resistance information
    
    Returns:
    str: TB type classification
    """
    if not resistance_data.get("RIF", False) and not resistance_data.get("INH", False):
        return "Drug-susceptible TB"
    
    if resistance_data.get("RIF", False) and resistance_data.get("INH", False):
        if (resistance_data.get("FQ", False) and 
            (resistance_data.get("AMI", False) or 
             resistance_data.get("KAN", False) or 
             resistance_data.get("CAP", False))):
            return "XDR-TB"
        else:
            return "MDR-TB"
    
    if resistance_data.get("RIF", False):
        return "RR-TB"
    
    if resistance_data.get("INH", False):
        return "INH-resistant TB"
    
    return "Other resistance"

def generate_regimen_recommendation(patient_data):
    """
    Generates treatment regimen recommendations based on patient data
    
    Parameters:
    patient_data (dict): Dictionary containing patient information
    
    Returns:
    dict: Recommended regimen and additional information
    """
    tb_type = patient_data.get("tb_type", "Drug-susceptible TB")
    
    # Get base regimen from guidelines
    regimen = REGIMEN_GUIDELINES.get(tb_type, REGIMEN_GUIDELINES["Drug-susceptible TB"]).copy()
    
    # Adjust regimen based on patient characteristics
    patient_age = patient_data.get("age", 30)
    patient_weight = patient_data.get("weight", 60)
    hiv_status = patient_data.get("hiv_status", "Negative")
    kidney_function = patient_data.get("kidney_function", "Normal")
    liver_function = patient_data.get("liver_function", "Normal")
    
    recommendations = {
        "regimen": regimen,
        "patient_specific_adjustments": [],
        "monitoring_recommendations": [],
        "drug_interactions": []
    }
    
    # Age-specific adjustments
    if patient_age > 65:
        recommendations["patient_specific_adjustments"].append("Consider dose reduction for elderly patient")
    
    # Weight-based dosing
    if patient_weight < 50:
        recommendations["patient_specific_adjustments"].append(f"Adjust dosing for low body weight ({patient_weight} kg)")
    
    # HIV considerations
    if hiv_status == "Positive":
        recommendations["patient_specific_adjustments"].append("Consider drug interactions with antiretroviral therapy")
        recommendations["monitoring_recommendations"].append("Close monitoring for immune reconstitution inflammatory syndrome (IRIS)")
    
    # Kidney function
    if kidney_function != "Normal":
        if "Ethambutol" in regimen.get("first_line", []):
            recommendations["patient_specific_adjustments"].append("Adjust Ethambutol dosing for impaired kidney function")
        if "Amikacin" in regimen.get("first_line", []) or "Amikacin" in regimen.get("alternatives", []):
            recommendations["patient_specific_adjustments"].append("Consider avoiding aminoglycosides due to kidney function")
    
    # Liver function
    if liver_function != "Normal":
        recommendations["patient_specific_adjustments"].append("Close monitoring of liver function tests weekly")
        if "Pyrazinamide" in regimen.get("first_line", []):
            recommendations["patient_specific_adjustments"].append("Consider omitting Pyrazinamide in severe liver disease")
    
    # Get drug interactions
    recommendations["drug_interactions"] = get_drug_interactions(regimen.get("first_line", []))
    
    # Add standard monitoring
    recommendations["monitoring_recommendations"].extend([
        "Regular sputum cultures to monitor treatment response",
        "Monthly clinical evaluation for side effects",
        "Baseline and periodic liver and kidney function tests"
    ])
    
    return recommendations

def check_for_adverse_reactions(reported_symptoms, current_drugs):
    """
    Checks for potential adverse drug reactions based on reported symptoms
    
    Parameters:
    reported_symptoms (list): List of symptoms reported by patient
    current_drugs (list): List of drugs in current regimen
    
    Returns:
    dict: Potential adverse reactions by drug
    """
    potential_reactions = {}
    
    for drug in current_drugs:
        if drug in DRUG_SIDE_EFFECTS:
            matching_symptoms = [s for s in reported_symptoms if s in DRUG_SIDE_EFFECTS[drug]]
            if matching_symptoms:
                potential_reactions[drug] = matching_symptoms
    
    return potential_reactions

def save_patient_data(patient_data, conn):
    """
    Saves patient data to the database
    
    Parameters:
    patient_data (dict): Patient information
    conn: Database connection
    
    Returns:
    bool: Success status
    """
    try:
        cursor = conn.cursor()
        
        # Convert dictionary to JSON for storage
        patient_json = json.dumps(patient_data)
        
        # Check if patient already exists
        cursor.execute(
            "SELECT id FROM patients WHERE patient_id = ?", 
            (patient_data.get("patient_id"),)
        )
        existing_patient = cursor.fetchone()
        
        if existing_patient:
            # Update existing patient
            cursor.execute(
                """
                UPDATE patients 
                SET data = ?, last_updated = ?
                WHERE patient_id = ?
                """,
                (patient_json, datetime.now().isoformat(), patient_data.get("patient_id"))
            )
        else:
            # Insert new patient
            cursor.execute(
                """
                INSERT INTO patients (patient_id, data, created_at, last_updated)
                VALUES (?, ?, ?, ?)
                """,
                (
                    patient_data.get("patient_id"),
                    patient_json,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                )
            )
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error saving patient data: {e}")
        return False

def get_patient_history(patient_id, conn):
    """
    Retrieves patient history from the database
    
    Parameters:
    patient_id (str): Patient identifier
    conn: Database connection
    
    Returns:
    dict: Patient data
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT data FROM patients WHERE patient_id = ?", 
            (patient_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        else:
            return None
    
    except Exception as e:
        print(f"Error retrieving patient history: {e}")
        return None
