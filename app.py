"""
TB Resistance Hub - Main Streamlit Application

A comprehensive platform for tuberculosis antimicrobial resistance analysis,
clinical decision support, and global collaboration.

Copyright (c) 2025 TB Antimicrobial Resistance (TB-AMR) Project Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import streamlit as st
import os
from pathlib import Path
import auth
import db_manager
from db_manager import get_connection
from utils import initialize_session_state
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import onboarding
from analytics import load_tb_data, create_resistance_trend_chart, create_geo_distribution_chart, create_treatment_outcomes_chart, create_drug_resistance_heatmap
from data_processor import preprocess_tb_data, extract_resistance_patterns, categorize_tb_type
from decision_support import generate_regimen_recommendation
from global_collaboration import get_shared_datasets, anonymize_data
import datetime
import medical_search

# Set page configuration with modern settings
st.set_page_config(
    page_title="TB Resistance Hub",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a more modern look
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #2C3E50;
        --secondary-color: #3498DB;
        --accent-color: #16A085;
        --background-color: #F8F9FA;
        --text-color: #2C3E50;
    }
    
    /* Background and text */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid var(--secondary-color);
        padding-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.4rem;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--primary-color);
    }
    
    .css-1d391kg .css-xazyk {
        color: white;
    }
    
    /* Cards for metrics */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--secondary-color);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--accent-color);
        transform: translateY(-2px);
    }
    
    /* Info boxes */
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #3498DB;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 0 4px 4px 0;
    }
    
    /* Dashboard sections */
    .dashboard-section {
        margin-bottom: 2rem;
    }
    
    /* Tables */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
        background-color: white;
        border-radius: 5px;
        overflow: hidden;
        box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
    }
    
    .dataframe th {
        background-color: var(--secondary-color);
        color: white;
        padding: 10px;
        text-align: left;
    }
    
    .dataframe td {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
    
    .dataframe tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    .dataframe tr:hover {
        background-color: #e9ecef;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f1f3f5;
        border-radius: 4px 4px 0 0;
        color: var(--text-color);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: var(--secondary-color);
        border-top: 4px solid var(--secondary-color);
    }
</style>
""", unsafe_allow_html=True)

# Function to display the consolidated dashboard
def show_consolidated_dashboard():
    st.title("TB Resistance Hub Dashboard")
    
    try:
        # Get database connection
        conn = get_connection()
        
        # Load and preprocess TB data
        tb_data = load_tb_data(conn)
        if tb_data is None or tb_data.empty:
            st.error("No TB data available. Please seed the database with demonstration data.")
            return
            
        processed_data = preprocess_tb_data(tb_data)
        
        # Create tabs for different sections
        tabs = st.tabs(["Overview", "Analytics", "Clinical Support", "Data Management", "Collaboration", "Medical Search"])
        
        # Overview Tab
        with tabs[0]:
            st.header("TB Resistance Overview")
            
            # Key metrics in 4 columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>Total Cases</h3>
                    <h2 style="color: #3498DB;">{}</h2>
                    <p>Recorded TB cases</p>
                </div>
                """.format(len(processed_data)), unsafe_allow_html=True)
                
            with col2:
                mdr_count = len(processed_data[processed_data['tb_type'] == 'MDR-TB'])
                st.markdown("""
                <div class="metric-card">
                    <h3>MDR-TB Cases</h3>
                    <h2 style="color: #E74C3C;">{}</h2>
                    <p>Multi-drug resistant cases</p>
                </div>
                """.format(mdr_count), unsafe_allow_html=True)
                
            with col3:
                success_count = len(processed_data[processed_data['treatment_outcome'].isin(['Cured', 'Treatment Completed'])])
                success_rate = int((success_count / len(processed_data)) * 100)
                st.markdown("""
                <div class="metric-card">
                    <h3>Treatment Success</h3>
                    <h2 style="color: #2ECC71;">{:.0f}%</h2>
                    <p>Treatment success rate</p>
                </div>
                """.format(success_rate), unsafe_allow_html=True)
                
            with col4:
                recent_count = len(processed_data[processed_data['diagnosis_date'] > datetime.datetime.now() - datetime.timedelta(days=90)])
                st.markdown("""
                <div class="metric-card">
                    <h3>Recent Cases</h3>
                    <h2 style="color: #F39C12;">{}</h2>
                    <p>Cases in past 90 days</p>
                </div>
                """.format(recent_count), unsafe_allow_html=True)
            
            # Treatment outcomes chart
            st.subheader("Treatment Outcomes by TB Type")
            outcomes_chart = create_treatment_outcomes_chart(processed_data)
            st.plotly_chart(outcomes_chart, use_container_width=True)
            
            # Geographical distribution
            st.subheader("Geographical Distribution of TB Cases")
            geo_chart = create_geo_distribution_chart(processed_data)
            st.plotly_chart(geo_chart, use_container_width=True)
            
        # Analytics Tab
        with tabs[1]:
            st.header("TB Resistance Analytics")
            
            # Resistance trends over time
            st.subheader("Resistance Trends Over Time")
            trends_chart = create_resistance_trend_chart(processed_data)
            st.plotly_chart(trends_chart, use_container_width=True)
            
            # Drug resistance heatmap
            st.subheader("Drug Resistance Patterns")
            heatmap = create_drug_resistance_heatmap(processed_data)
            st.plotly_chart(heatmap, use_container_width=True)
            
            # Top resistance patterns
            st.subheader("Top Resistance Patterns")
            # Extract resistance patterns from data
            resistance_cols = [col for col in processed_data.columns if 'resistance' in col.lower()]
            if resistance_cols:
                resistance_patterns = extract_resistance_patterns(processed_data, resistance_cols)
                # Display top patterns
                pattern_counts = processed_data['resistance_pattern'].value_counts().reset_index()
                pattern_counts.columns = ['Pattern', 'Count']
                pattern_counts = pattern_counts.head(10)
                st.dataframe(pattern_counts, use_container_width=True)
            else:
                st.write("Resistance pattern data not available.")
        
        # Clinical Support Tab
        with tabs[2]:
            st.header("Clinical Decision Support")
            
            # Patient information form
            st.subheader("Treatment Recommendation Generator")
            
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("Patient Age", min_value=1, max_value=120, value=45)
                gender = st.selectbox("Gender", ["Male", "Female"])
                weight = st.number_input("Weight (kg)", min_value=20, max_value=200, value=70)
                
            with col2:
                resistance_pattern = st.selectbox(
                    "Resistance Pattern",
                    ["None", "INH", "RIF", "INH+RIF", "INH+RIF+EMB", "INH+RIF+EMB+PZA", "INH+RIF+FQ+SLID"]
                )
                hiv_status = st.selectbox("HIV Status", ["Negative", "Positive", "Unknown"])
                comorbidities = st.multiselect(
                    "Comorbidities",
                    ["None", "Diabetes", "Hypertension", "COPD", "Renal disease", "Liver disease"]
                )
            
            if st.button("Generate Recommendation"):
                # Create patient data dictionary
                patient_data = {
                    "age": age,
                    "gender": gender,
                    "weight": weight,
                    "resistance_pattern": resistance_pattern,
                    "hiv_status": hiv_status,
                    "comorbidities": comorbidities
                }
                
                # Generate recommendation
                recommendation = generate_regimen_recommendation(patient_data)
                
                # Display recommendation in a nice format
                st.markdown("### Recommended Treatment Regimen")
                st.markdown(f"**TB Type Classification:** {recommendation.get('tb_type', 'Not classified')}")
                
                st.markdown("**Recommended Drugs:**")
                for drug in recommendation.get('recommended_drugs', []):
                    st.markdown(f"- {drug}")
                
                st.markdown("**Treatment Duration:**")
                st.markdown(f"{recommendation.get('duration', 'Not specified')}")
                
                st.markdown("**Special Considerations:**")
                for note in recommendation.get('notes', []):
                    st.markdown(f"- {note}")
        
        # Data Management Tab
        with tabs[3]:
            st.header("Data Import/Export")
            
            sub_tabs = st.tabs(["Import Data", "Export Data", "Database Tables"])
            
            with sub_tabs[0]:
                st.subheader("Import TB Data")
                
                import_option = st.selectbox(
                    "Select Import Source",
                    ["CSV File", "Excel File", "API"]
                )
                
                if import_option == "CSV File":
                    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
                    if uploaded_file is not None:
                        st.success("File uploaded successfully. Click 'Process Data' to continue.")
                        if st.button("Process Data"):
                            st.info("Processing data... This would import the CSV into the database.")
                
                elif import_option == "Excel File":
                    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
                    if uploaded_file is not None:
                        st.success("File uploaded successfully. Click 'Process Data' to continue.")
                        if st.button("Process Data"):
                            st.info("Processing data... This would import the Excel file into the database.")
                
                elif import_option == "API":
                    api_url = st.text_input("API URL")
                    api_key = st.text_input("API Key (if required)", type="password")
                    if st.button("Connect to API"):
                        if api_url:
                            st.info("Connecting to API... This would fetch data from the API and import it into the database.")
                        else:
                            st.error("Please enter a valid API URL")
            
            with sub_tabs[1]:
                st.subheader("Export TB Data")
                
                export_format = st.selectbox(
                    "Export Format",
                    ["CSV", "Excel", "JSON"]
                )
                
                export_table = st.selectbox(
                    "Select Table to Export",
                    ["tb_cases", "users", "user_preferences"]
                )
                
                include_fields = st.multiselect(
                    "Fields to Include (leave empty for all)",
                    ["patient_id", "age", "gender", "location", "diagnosis_date", 
                     "tb_type", "treatment_outcome", "resistance_pattern"]
                )
                
                if st.button("Export Data"):
                    st.success(f"Exporting {export_table} as {export_format}...")
                    # This would trigger the export functionality
                    st.download_button(
                        label=f"Download {export_format} File",
                        data="Sample export data",
                        file_name=f"tb_data_export.{export_format.lower()}",
                        mime="text/csv"
                    )
            
            with sub_tabs[2]:
                st.subheader("Database Tables")
                
                # Display a sample of the TB cases table
                st.write("Sample TB Cases Data")
                st.dataframe(processed_data.head(10), use_container_width=True)
        
        # Collaboration Tab
        with tabs[4]:
            st.header("Global Collaboration")
            
            st.subheader("Research Opportunities")
            
            # Sample research opportunities
            opportunities = [
                {
                    "title": "Multi-center study on XDR-TB treatment outcomes",
                    "organization": "WHO Collaborative Research Network",
                    "deadline": "2025-06-30",
                    "description": "Looking for collaborators to contribute data on XDR-TB cases for a multi-center analysis of treatment outcomes."
                },
                {
                    "title": "Genomic surveillance of TB drug resistance",
                    "organization": "International TB Research Consortium",
                    "deadline": "2025-07-15",
                    "description": "Seeking partners for a global genomic surveillance project tracking the emergence of new resistance patterns."
                },
                {
                    "title": "AI-driven prediction of TB treatment outcomes",
                    "organization": "Global Health AI Initiative",
                    "deadline": "2025-08-01",
                    "description": "Collaborators needed to contribute data for training machine learning models to predict treatment outcomes."
                }
            ]
            
            for idx, opp in enumerate(opportunities):
                with st.expander(f"{opp['title']} - {opp['organization']}"):
                    st.write(f"**Deadline:** {opp['deadline']}")
                    st.write(opp['description'])
                    if st.button("Express Interest", key=f"interest_{idx}"):
                        st.success("Interest registered. The organization will contact you for next steps.")
            
            st.subheader("Data Sharing")
            
            # Data sharing options
            st.write("Share your TB resistance data with the global community")
            
            sharing_level = st.select_slider(
                "Select data anonymization level",
                options=["High (fully anonymized)", "Medium (limited identifiers)", "Low (minimal anonymization)"]
            )
            
            sharing_scope = st.multiselect(
                "Data elements to share",
                ["Resistance patterns", "Treatment outcomes", "Demographic data", "Clinical data", "Genomic data"]
            )
            
            if st.button("Prepare Data for Sharing"):
                if sharing_scope:
                    st.info("Preparing data for sharing with selected anonymization level...")
                    # This would trigger the data sharing preparation
                    
                    # Show sample of anonymized data
                    anonymized_sample = anonymize_data(processed_data.head(5), level=sharing_level.split()[0].lower())
                    st.write("Sample of anonymized data:")
                    st.dataframe(anonymized_sample, use_container_width=True)
                    
                    # Generate sharing token
                    st.success("Data prepared for sharing. Use the following token for reference:")
                    st.code("TB-SHARE-" + os.urandom(4).hex().upper())
                else:
                    st.error("Please select at least one data element to share")
            
            st.subheader("Available Shared Datasets")
            
            # Display available shared datasets
            shared_data = get_shared_datasets(conn)
            if shared_data is not None and not shared_data.empty:
                st.dataframe(shared_data, use_container_width=True)
            else:
                st.info("No shared datasets available at this time")
                
                # Sample shared datasets for demonstration
                sample_datasets = pd.DataFrame({
                    "Dataset Name": ["Global XDR-TB Registry", "MDR-TB Treatment Outcomes", "TB Drug Susceptibility Survey"],
                    "Organization": ["WHO", "TB Alliance", "CDC"],
                    "Records": [2500, 1800, 3200],
                    "Last Updated": ["2025-03-15", "2025-02-28", "2025-04-01"]
                })
                
                st.write("Sample available datasets:")
                st.dataframe(sample_datasets, use_container_width=True)
                
        # Medical Search Tab
        with tabs[5]:
            # Display the medical search interface
            medical_search.show_search_interface()
        
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        import traceback
        st.error(traceback.format_exc())

# Initialize PostgreSQL database
db_manager.initialize_database()

# Initialize session state variables
initialize_session_state()

# Initialize onboarding state
onboarding.initialize_onboarding()

# Authentication
auth.login_widget()

# Only show the main app if user is authenticated
if st.session_state.authenticated:
    # Load user preferences if available
    onboarding.load_user_preferences()
    
    # Show onboarding if it's the user's first login
    if not st.session_state.onboarding_complete and not st.session_state.show_onboarding:
        st.session_state.show_onboarding = True
        
    # Display onboarding overlay if needed
    if st.session_state.show_onboarding:
        onboarding.show_onboarding()
        
    # Show welcome back message with personalized tips
    if st.session_state.onboarding_complete:
        onboarding.welcome_back_info()
        
    # Show help modal if requested
    onboarding.show_help_modal()
    st.sidebar.title("TB Resistance Hub")
    
    # User info in sidebar
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    st.sidebar.write(f"Role: {st.session_state.user_role}")
    
    # Display the consolidated dashboard
    show_consolidated_dashboard()
    
    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_session_state()
        st.rerun()
    
    # Add feature tour for consolidated dashboard
    onboarding.show_feature_tour("Consolidated Dashboard")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("TB Resistance Hub v1.0")
    
    # Add help buttons
    onboarding.inject_help_buttons()