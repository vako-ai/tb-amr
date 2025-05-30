import streamlit as st
import pandas as pd
import json
import datetime
import uuid
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import decision_support
import utils
from db_manager import get_connection

def show():
    """Display the clinical decision support page"""
    st.title("Clinical Decision Support for DR-TB")
    
    # Connect to the PostgreSQL database
    conn = get_connection()
    
    # Introduction with visual appeal
    st.markdown("""
    <div style="padding: 10px; border-radius: 10px; background-color: #f0f2f6;">
        <h3 style="color: #1E3A8A;">Welcome to the AI-Powered Clinical Decision Support</h3>
        <p>This module provides evidence-based treatment recommendations, genomic analysis, and patient monitoring tools to support clinical decision-making for drug-resistant tuberculosis.</p>
        <p><em>Features include genomic sequencing integration, treatment outcome prediction, and personalized regimen recommendations.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs([
        "Treatment Recommendation", 
        "Genomic Analysis",
        "Patient History", 
        "Adverse Reaction Checker"
    ])
    
    with tab1:
        show_treatment_recommendation(conn)
    
    with tab2:
        show_genomic_analysis()
    
    with tab3:
        show_patient_history(conn)
    
    with tab4:
        show_adverse_reaction_checker()
    
    # Close database connection
    conn.close()

def show_treatment_recommendation(conn):
    """Display treatment recommendation interface"""
    st.header("Treatment Recommendation")
    st.write("Enter patient details to receive treatment recommendations based on resistance patterns.")
    
    # Patient information form
    with st.form("patient_info_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_id = st.text_input("Patient ID")
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=60.0, step=0.1)
        
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            hiv_status = st.selectbox("HIV Status", ["Negative", "Positive", "Unknown"])
            diabetes = st.selectbox("Diabetes", ["No", "Yes", "Unknown"])
        
        with col3:
            kidney_function = st.selectbox("Kidney Function", ["Normal", "Impaired", "Unknown"])
            liver_function = st.selectbox("Liver Function", ["Normal", "Impaired", "Unknown"])
            pregnant = st.selectbox("Pregnant", ["No", "Yes", "N/A", "Unknown"])
        
        st.subheader("TB Resistance Profile")
        
        # Organize resistance checkboxes in columns
        resistance_col1, resistance_col2, resistance_col3 = st.columns(3)
        
        with resistance_col1:
            rif_resistant = st.checkbox("Rifampicin (RIF) Resistant")
            inh_resistant = st.checkbox("Isoniazid (INH) Resistant")
            pza_resistant = st.checkbox("Pyrazinamide (PZA) Resistant")
        
        with resistance_col2:
            emb_resistant = st.checkbox("Ethambutol (EMB) Resistant")
            fq_resistant = st.checkbox("Fluoroquinolone (FQ) Resistant")
            ami_resistant = st.checkbox("Aminoglycoside (AMI/KAN/CAP) Resistant")
        
        with resistance_col3:
            lzd_resistant = st.checkbox("Linezolid (LZD) Resistant")
            bdq_resistant = st.checkbox("Bedaquiline (BDQ) Resistant")
            cfz_resistant = st.checkbox("Clofazimine (CFZ) Resistant")
        
        additional_notes = st.text_area("Additional Notes", height=100)
        
        submitted = st.form_submit_button("Generate Recommendation")
        
        if submitted:
            if not patient_id:
                st.error("Patient ID is required.")
            else:
                # Prepare resistance data
                resistance_data = {
                    "RIF": rif_resistant,
                    "INH": inh_resistant,
                    "PZA": pza_resistant,
                    "EMB": emb_resistant,
                    "FQ": fq_resistant,
                    "AMI": ami_resistant,
                    "LZD": lzd_resistant,
                    "BDQ": bdq_resistant,
                    "CFZ": cfz_resistant
                }
                
                # Determine TB type based on resistance profile
                tb_type = decision_support.determine_tb_type(resistance_data)
                
                # Create patient data dictionary
                patient_data = {
                    "patient_id": patient_id,
                    "age": age,
                    "weight": weight,
                    "gender": gender,
                    "hiv_status": hiv_status,
                    "diabetes": diabetes,
                    "kidney_function": kidney_function,
                    "liver_function": liver_function,
                    "pregnant": pregnant,
                    "resistance_data": resistance_data,
                    "tb_type": tb_type,
                    "additional_notes": additional_notes,
                    "last_updated": datetime.datetime.now().isoformat()
                }
                
                # Generate treatment recommendation
                recommendation = decision_support.generate_regimen_recommendation(patient_data)
                
                # Save patient data to the database
                decision_support.save_patient_data(patient_data, conn)
                
                # Log the activity
                user_id = utils.get_user_id(st.session_state.username, conn)
                if user_id:
                    utils.log_activity(
                        conn, 
                        user_id, 
                        "Treatment Recommendation", 
                        {"patient_id": patient_id, "tb_type": tb_type}
                    )
                
                # Display the recommendation
                display_treatment_recommendation(tb_type, recommendation)

def display_treatment_recommendation(tb_type, recommendation):
    """Display the treatment recommendation"""
    st.success(f"Recommendation generated for: {tb_type}")
    
    # TB type description
    st.markdown(f"**TB Type Description**: {utils.get_tb_type_description(tb_type)}")
    
    # Recommended drugs
    st.subheader("Recommended Regimen")
    
    if "first_line" in recommendation["regimen"]:
        st.write("**First-line drugs:**")
        for drug in recommendation["regimen"]["first_line"]:
            st.markdown(f"- {drug}")
    
    if "alternatives" in recommendation["regimen"]:
        st.write("**Alternative/Additional drugs (if needed):**")
        for drug in recommendation["regimen"]["alternatives"]:
            st.markdown(f"- {drug}")
    
    st.write(f"**Recommended duration:** {recommendation['regimen'].get('duration', 'Not specified')}")
    st.write(f"**Notes:** {recommendation['regimen'].get('notes', 'None')}")
    
    # Patient-specific adjustments
    if recommendation["patient_specific_adjustments"]:
        st.subheader("Patient-Specific Adjustments")
        for adjustment in recommendation["patient_specific_adjustments"]:
            st.markdown(f"- {adjustment}")
    
    # Drug interactions
    if recommendation["drug_interactions"]:
        st.subheader("Potential Drug Interactions")
        for interaction in recommendation["drug_interactions"]:
            st.markdown(f"- {interaction}")
    
    # Monitoring recommendations
    if recommendation["monitoring_recommendations"]:
        st.subheader("Monitoring Recommendations")
        for monitoring in recommendation["monitoring_recommendations"]:
            st.markdown(f"- {monitoring}")
    
    # Disclaimer
    st.info("This recommendation is provided as a decision support tool. The final treatment decision should be made by qualified healthcare professionals based on patient-specific factors and local guidelines.")

def show_patient_history(conn):
    """Display patient history interface"""
    st.header("Patient Treatment History")
    
    patient_id = st.text_input("Enter Patient ID to view history", key="history_patient_id")
    
    if patient_id:
        patient_data = decision_support.get_patient_history(patient_id, conn)
        
        if patient_data:
            # Log the activity
            user_id = utils.get_user_id(st.session_state.username, conn)
            if user_id:
                utils.log_activity(
                    conn, 
                    user_id, 
                    "Patient History Lookup", 
                    {"patient_id": patient_id}
                )
            
            # Display patient info
            st.subheader("Patient Information")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Age:** {patient_data.get('age', 'N/A')}")
                st.write(f"**Gender:** {patient_data.get('gender', 'N/A')}")
            
            with col2:
                st.write(f"**Weight:** {patient_data.get('weight', 'N/A')} kg")
                st.write(f"**HIV Status:** {patient_data.get('hiv_status', 'N/A')}")
            
            with col3:
                st.write(f"**TB Type:** {patient_data.get('tb_type', 'N/A')}")
                last_updated = patient_data.get('last_updated', '')
                if last_updated:
                    try:
                        formatted_date = datetime.datetime.fromisoformat(last_updated).strftime("%Y-%m-%d %H:%M")
                        st.write(f"**Last Updated:** {formatted_date}")
                    except:
                        st.write(f"**Last Updated:** {last_updated}")
            
            # Display resistance pattern
            st.subheader("Resistance Pattern")
            
            resistance_data = patient_data.get('resistance_data', {})
            if resistance_data:
                resistance_items = []
                for drug, is_resistant in resistance_data.items():
                    if is_resistant:
                        resistance_items.append(f"- {drug}")
                
                if resistance_items:
                    st.write("**Resistant to:**")
                    for item in resistance_items:
                        st.markdown(item)
                else:
                    st.write("No resistance detected")
            else:
                st.write("No resistance data available")
            
            # Display additional notes
            if 'additional_notes' in patient_data and patient_data['additional_notes']:
                st.subheader("Additional Notes")
                st.write(patient_data['additional_notes'])
            
            # Option to generate a new recommendation
            if st.button("Generate New Recommendation"):
                recommendation = decision_support.generate_regimen_recommendation(patient_data)
                display_treatment_recommendation(patient_data.get('tb_type', 'Unknown'), recommendation)
        
        else:
            st.warning(f"No history found for patient ID: {patient_id}")
    
    else:
        st.info("Enter a patient ID to view treatment history")

def show_genomic_analysis():
    """Display genomic analysis interface for TB samples"""
    st.header("Genomic Sequencing Analysis")
    
    st.markdown("""
    <div style="padding: 10px; border-radius: 10px; background-color: #e6f3ff; margin-bottom: 20px;">
        <h4 style="color: #0066cc;">Genomic Data Integration</h4>
        <p>This module integrates whole genome sequencing (WGS) data to identify drug resistance mutations 
        and predict phenotypic resistance. Upload genomic data or search the database for existing sequences.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Two options: upload new genomic data or analyze existing data
    option = st.radio(
        "Select Option",
        ["Upload New Genomic Data", "Analyze Existing Samples"]
    )
    
    if option == "Upload New Genomic Data":
        st.subheader("Upload Genomic Data")
        
        # Sample information
        col1, col2 = st.columns(2)
        
        with col1:
            sample_id = st.text_input("Sample ID")
            source_lab = st.text_input("Source Laboratory")
            
        with col2:
            patient_id = st.text_input("Patient ID (optional)")
            collection_date = st.date_input("Collection Date")
        
        # File upload options
        file_type = st.selectbox(
            "File Type",
            ["FASTQ", "FASTA", "VCF", "BAM", "MTBseq Output", "Other"]
        )
        
        uploaded_file = st.file_uploader(f"Upload {file_type} file", type=["fastq", "fasta", "vcf", "bam", "txt", "csv"])
        
        if st.button("Process Genomic Data") and uploaded_file is not None:
            st.info("Processing genomic data... This may take a few minutes.")
            
            # Simulated progress bar for genomic analysis
            progress_bar = st.progress(0)
            for i in range(100):
                # Update progress bar
                progress_bar.progress(i + 1)
                # Simulate processing delay
                if i % 20 == 0:
                    status_text = st.empty()
                    if i == 0:
                        status_text.text("Reading sequence data...")
                    elif i == 20:
                        status_text.text("Aligning to reference genome...")
                    elif i == 40:
                        status_text.text("Calling variants...")
                    elif i == 60:
                        status_text.text("Identifying resistance mutations...")
                    elif i == 80:
                        status_text.text("Generating resistance report...")
            
            # Display genomic analysis results
            st.success("Genomic analysis complete!")
            
            # Sample results
            show_genomic_results()
    
    else:  # Analyze Existing Samples
        st.subheader("Analyze Existing Genomic Samples")
        
        # Search for samples
        search_term = st.text_input("Search by Sample ID or Patient ID")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.date_input(
                "Date Range",
                value=(datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()),
                help="Filter by collection date range"
            )
        
        with col2:
            resistance_type = st.multiselect(
                "Resistance Type",
                ["RR-TB", "MDR-TB", "Pre-XDR-TB", "XDR-TB", "Other"]
            )
        
        with col3:
            source = st.selectbox(
                "Source Laboratory",
                ["All", "National Reference Lab", "Regional Lab 1", "Regional Lab 2", "Partner Lab"]
            )
        
        if st.button("Search Genomic Database"):
            # Simulated results found message
            st.success("8 matching genomic samples found")
            
            # Simulated sample list as a dataframe
            sample_data = {
                "Sample ID": ["TB001-WGS", "TB045-WGS", "TB078-WGS", "TB092-WGS", "TB103-WGS", 
                             "TB154-WGS", "TB201-WGS", "TB256-WGS"],
                "Patient ID": ["P-10045", "P-10872", "P-11204", "P-11309", "P-11427", 
                              "P-11583", "P-11804", "P-12015"],
                "Collection Date": ["2023-06-12", "2023-07-18", "2023-08-29", "2023-09-10", 
                                  "2023-10-05", "2023-11-22", "2024-01-15", "2024-02-28"],
                "Resistance Type": ["MDR-TB", "RR-TB", "MDR-TB", "XDR-TB", "MDR-TB", 
                                  "Pre-XDR-TB", "RR-TB", "MDR-TB"],
                "Source": ["National Reference Lab", "Regional Lab 1", "Regional Lab 2", 
                          "National Reference Lab", "Partner Lab", "Regional Lab 1", 
                          "Regional Lab 2", "National Reference Lab"]
            }
            
            samples_df = pd.DataFrame(sample_data)
            st.dataframe(samples_df, use_container_width=True)
            
            # Option to select samples for analysis
            selected_samples = st.multiselect("Select samples for detailed analysis", samples_df["Sample ID"])
            
            if selected_samples and st.button("Analyze Selected Samples"):
                # Show genomic results for selected samples
                st.subheader(f"Genomic Analysis Results for {len(selected_samples)} samples")
                
                # Simulated progress bar for genomic comparison
                progress_bar = st.progress(0)
                for i in range(100):
                    # Update progress bar
                    progress_bar.progress(i + 1)
                    # Simulate processing delay
                    if i == 50:
                        st.text("Comparing resistance mutations across samples...")
                
                show_genomic_results()

def show_genomic_results():
    """Display genomic analysis results"""
    # Sample tabs for different aspects of genomic analysis
    result_tabs = st.tabs([
        "Resistance Mutations", 
        "Phylogenetic Analysis", 
        "Treatment Implications"
    ])
    
    with result_tabs[0]:  # Resistance Mutations
        st.markdown("### Identified Resistance Mutations")
        
        # Create a table with resistance-conferring mutations
        mutations_data = {
            "Gene": ["rpoB", "katG", "inhA promoter", "embB", "pncA", "gyrA", "rrs"],
            "Mutation": ["S450L", "S315T", "-15C>T", "M306I", "Q10P", "D94G", "A1401G"],
            "Resistance To": ["Rifampicin", "Isoniazid", "Isoniazid (low-level)", 
                           "Ethambutol", "Pyrazinamide", "Fluoroquinolones", 
                           "Amikacin, Kanamycin, Capreomycin"],
            "Confidence": ["High", "High", "High", "Moderate", "High", "High", "High"],
            "Literature Support": ["Strong", "Strong", "Strong", "Moderate", "Strong", "Strong", "Strong"]
        }
        
        mutations_df = pd.DataFrame(mutations_data)
        st.dataframe(mutations_df, use_container_width=True)
        
        # Circular genome visualization with mutations
        st.markdown("### Genome Map with Resistance Mutations")
        
        # Create a circular plot to visualize mutations on the TB genome
        # For simplicity, we're creating a sample circular plot
        fig = go.Figure()
        
        # TB genome size is approximately 4.4 million base pairs
        genome_size = 4400000
        
        # Create a circle as the genome backbone
        theta = np.linspace(0, 2*np.pi, 1000)
        radius = 1
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name='TB Genome',
            line=dict(color='gray', width=2)
        ))
        
        # Add gene locations as colored segments
        gene_locations = {
            'rpoB': 0.3,    # Position in radians
            'katG': 1.0,
            'inhA': 1.5,
            'embB': 2.0,
            'pncA': 2.5,
            'gyrA': 3.5,
            'rrs': 5.0
        }
        
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'cyan']
        
        for i, (gene, pos) in enumerate(gene_locations.items()):
            # Draw a marker at the gene position
            x_pos = 1.1 * np.cos(pos)
            y_pos = 1.1 * np.sin(pos)
            
            fig.add_trace(go.Scatter(
                x=[x_pos], y=[y_pos],
                mode='markers+text',
                marker=dict(color=colors[i], size=15),
                text=gene,
                textposition="middle right",
                name=gene
            ))
        
        # Update layout
        fig.update_layout(
            title='TB Genome Map with Resistance Mutations',
            xaxis=dict(
                range=[-1.5, 1.5],
                zeroline=False,
                showgrid=False,
                showticklabels=False
            ),
            yaxis=dict(
                range=[-1.5, 1.5],
                zeroline=False,
                showgrid=False,
                showticklabels=False
            ),
            width=700,
            height=700,
            showlegend=True
        )
        
        st.plotly_chart(fig)
    
    with result_tabs[1]:  # Phylogenetic Analysis
        st.markdown("### Phylogenetic Analysis")
        st.write("""
        This analysis shows the genetic relationship of this sample to other TB strains in the database,
        helping to identify transmission clusters and evolutionary patterns.
        """)
        
        # Create a dendrogram for phylogenetic tree visualization
        lineages = ['Lineage 1', 'Lineage 2', 'Lineage 2.2.1 (Beijing)', 'Lineage 2.2.1.1', 
                   'Lineage 2.2.1.2', 'Current Sample', 'Lineage 2.2.2', 'Lineage 3', 
                   'Lineage 4', 'Lineage 4.1.2']
        
        # Create distance matrix (sample values)
        n = len(lineages)
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                # Generate some distance values
                if i == 5 or j == 5:  # Current sample
                    if i == 2 or j == 2 or i == 3 or j == 3 or i == 4 or j == 4:
                        # Close to Beijing family
                        distances[i, j] = distances[j, i] = np.random.uniform(0.01, 0.05)
                    else:
                        distances[i, j] = distances[j, i] = np.random.uniform(0.1, 0.5)
                else:
                    distances[i, j] = distances[j, i] = np.random.uniform(0.05, 0.5)
        
        # Create the dendrogram
        fig = px.imshow(distances, 
                        x=lineages,
                        y=lineages,
                        color_continuous_scale='Viridis',
                        title='Genetic Distance Matrix')
        st.plotly_chart(fig, use_container_width=True)
        
        # Add a phylogenetic tree visualization
        st.image("https://via.placeholder.com/800x400?text=Phylogenetic+Tree+Visualization", 
                caption="Phylogenetic tree showing relationship to other TB strains")
    
    with result_tabs[2]:  # Treatment Implications
        st.markdown("### Treatment Implications Based on Genomic Data")
        
        # Resistance profile
        st.subheader("Predicted Resistance Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### Phenotypic Resistance Predictions
            
            | Drug | Prediction | Confidence |
            | ---- | ---------- | ---------- |
            | Rifampicin | Resistant | 99% |
            | Isoniazid | Resistant | 99% |
            | Pyrazinamide | Resistant | 95% |
            | Ethambutol | Resistant | 90% |
            | Fluoroquinolones | Resistant | 99% |
            | Bedaquiline | Susceptible | 99% |
            | Linezolid | Susceptible | 99% |
            | Clofazimine | Susceptible | 95% |
            | Cycloserine | Susceptible | 95% |
            """)
        
        with col2:
            # Create a radar chart for resistance prediction confidences
            drugs = ['Rifampicin', 'Isoniazid', 'Pyrazinamide', 'Ethambutol', 'Fluoroquinolones', 
                    'Bedaquiline', 'Linezolid', 'Clofazimine']
            resistance_confidences = [0.99, 0.99, 0.95, 0.90, 0.99, 0.01, 0.01, 0.05]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=resistance_confidences,
                theta=drugs,
                fill='toself',
                name='Resistance Probability'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                title="Drug Resistance Probability"
            )
            
            st.plotly_chart(fig)
        
        # Treatment recommendation
        st.subheader("Genomics-Guided Treatment Recommendation")
        
        st.markdown("""
        Based on the genomic profile, this is an **XDR-TB** case with resistance to:
        - First-line drugs (rifampicin, isoniazid, pyrazinamide, ethambutol)
        - Fluoroquinolones
        
        **Recommended Treatment Regimen:**
        - Bedaquiline: 400mg once daily for 2 weeks, then 200mg 3 times per week
        - Linezolid: 600mg once daily
        - Clofazimine: 100mg once daily
        - Cycloserine: 500mg twice daily
        - Delamanid: 100mg twice daily
        
        **Duration:** 18-20 months
        
        **Special Monitoring Required:**
        - Monthly ECG for QT interval monitoring (bedaquiline, clofazimine, and delamanid)
        - Regular complete blood count for linezolid toxicity
        - Visual and neurological assessment for linezolid side effects
        """)
        
        st.warning("""
        This is a genomics-based prediction. Consider confirmatory phenotypic drug susceptibility 
        testing where available. Treatment should be adjusted based on patient response and toxicity.
        """)

def show_adverse_reaction_checker():
    """Display adverse reaction checker interface"""
    st.header("Adverse Reaction Checker")
    st.write("Check for potential drug adverse reactions based on patient symptoms")
    
    # Current drugs
    st.subheader("Current Medication")
    
    # Create drug selection with checkboxes
    drug_cols = st.columns(3)
    
    all_drugs = [
        "Isoniazid", "Rifampicin", "Pyrazinamide", "Ethambutol", 
        "Levofloxacin", "Moxifloxacin", "Bedaquiline", "Linezolid",
        "Clofazimine", "Cycloserine", "Delamanid", "Amikacin",
        "Ethionamide", "Para-aminosalicylic acid"
    ]
    
    selected_drugs = []
    
    for i, drug in enumerate(all_drugs):
        col_idx = i % 3
        with drug_cols[col_idx]:
            if st.checkbox(drug):
                selected_drugs.append(drug)
    
    # Reported symptoms
    st.subheader("Reported Symptoms")
    
    # List of common TB drug side effects
    all_symptoms = [
        "Nausea", "Vomiting", "Diarrhea", "Abdominal pain",
        "Headache", "Dizziness", "Fatigue", "Skin rash",
        "Itching", "Jaundice", "Joint pain", "Numbness/tingling",
        "Visual changes", "Hearing loss", "Psychiatric symptoms",
        "Liver function abnormalities", "Kidney function abnormalities",
        "QT prolongation", "Orange/red body fluids", "Skin discoloration"
    ]
    
    # Create symptom selection with checkboxes
    symptom_cols = st.columns(2)
    
    reported_symptoms = []
    
    for i, symptom in enumerate(all_symptoms):
        col_idx = i % 2
        with symptom_cols[col_idx]:
            if st.checkbox(symptom):
                reported_symptoms.append(symptom)
    
    # Check for adverse reactions
    if st.button("Check for Adverse Reactions") and selected_drugs and reported_symptoms:
        potential_reactions = decision_support.check_for_adverse_reactions(reported_symptoms, selected_drugs)
        
        if potential_reactions:
            st.subheader("Potential Adverse Drug Reactions")
            
            for drug, symptoms in potential_reactions.items():
                st.markdown(f"**{drug}** may be causing:")
                for symptom in symptoms:
                    st.markdown(f"- {symptom}")
                
                # Suggest management
                st.markdown("**Suggested Management:**")
                
                if drug == "Isoniazid" and "Numbness/tingling" in symptoms:
                    st.markdown("- Consider pyridoxine (vitamin B6) supplementation")
                elif drug == "Ethambutol" and "Visual changes" in symptoms:
                    st.markdown("- Stop drug immediately and refer for ophthalmologic evaluation")
                elif drug == "Linezolid" and ("Numbness/tingling" in symptoms or "Visual changes" in symptoms):
                    st.markdown("- Consider dose reduction or temporary discontinuation")
                elif "Liver function abnormalities" in symptoms or "Jaundice" in symptoms:
                    st.markdown("- Monitor liver function closely, consider temporary discontinuation if severe")
                elif "Skin rash" in symptoms or "Itching" in symptoms:
                    st.markdown("- Assess severity; minor rash may be managed symptomatically, severe rash may require drug discontinuation")
                else:
                    st.markdown("- Symptomatic management and close monitoring")
                
                st.markdown("---")
            
            st.info("Consult with a specialist for comprehensive management. This tool provides guidance but does not replace clinical judgment.")
        else:
            st.success("No clear association between the reported symptoms and current medications was found.")
            st.write("This doesn't mean the symptoms aren't drug-related. Continue to monitor the patient and consider other possible causes.")
