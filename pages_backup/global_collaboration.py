import streamlit as st
import pandas as pd
import json
import datetime
import global_collaboration
import utils
from db_manager import get_connection

def show():
    """Display the global collaboration page"""
    st.title("Global TB Collaboration Network")
    
    # Introduction with visual appeal
    st.markdown("""
    <div style="padding: 15px; border-radius: 10px; background-color: #f0f7ff; margin-bottom: 20px;">
        <h3 style="color: #2c5282;">International TB Data Sharing Platform</h3>
        <p>This platform facilitates secure, anonymous sharing of TB data across international boundaries to accelerate research and improve treatment outcomes globally.</p>
        <p><em>Features include controlled data sharing, anonymization tools, and collaborative research capabilities.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # World map showing active collaborations
    st.subheader("Global Collaboration Map")
    
    # Create a world map visualization
    import plotly.express as px
    
    # Sample data representing collaboration nodes
    collab_data = pd.DataFrame({
        'country': ['United States', 'India', 'South Africa', 'Brazil', 'China', 
                   'United Kingdom', 'Russia', 'Nigeria', 'Philippines', 'Indonesia'],
        'collaborations': [24, 31, 18, 12, 22, 15, 9, 7, 14, 11],
        'shared_datasets': [18, 25, 12, 8, 16, 13, 5, 3, 9, 7],
        'continent': ['North America', 'Asia', 'Africa', 'South America', 'Asia', 
                     'Europe', 'Europe', 'Africa', 'Asia', 'Asia']
    })
    
    # Create map
    fig = px.scatter_geo(
        collab_data,
        locations="country",
        locationmode="country names",
        size="collaborations",
        color="continent",
        hover_name="country",
        hover_data=["shared_datasets"],
        projection="natural earth",
        title="Active TB Data Sharing Collaborations"
    )
    
    # Adjust layout
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=450
    )
    
    # Display map
    st.plotly_chart(fig, use_container_width=True)
    
    # Key statistics for global collaborations
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Active Collaborations", value="143", delta="12")
    with col2:
        st.metric(label="Participating Countries", value="48", delta="3")
    with col3:
        st.metric(label="Shared Datasets", value="276", delta="24")
    with col4:
        st.metric(label="Research Publications", value="37", delta="5")
    
    # Connect to the PostgreSQL database
    conn = get_connection()
    
    # Create tabs for different collaboration features
    tab1, tab2, tab3, tab4 = st.tabs([
        "Data Sharing Controls", 
        "Available Collaborations", 
        "Collaboration Requests",
        "Research Opportunities"
    ])
    
    with tab1:
        show_sharing_preferences(conn)
    
    with tab2:
        show_available_collaborations(conn)
    
    with tab3:
        show_collaboration_requests(conn)
    
    with tab4:
        show_research_opportunities()
    
    # Close database connection
    conn.close()

def show_sharing_preferences(conn):
    """Display data sharing preferences interface"""
    st.header("Your Data Sharing Preferences")
    
    # Get user ID
    user_id = utils.get_user_id(st.session_state.username, conn)
    
    if not user_id:
        st.error("Unable to retrieve user information")
        return
    
    # Get current sharing preferences
    preferences = global_collaboration.get_sharing_preferences(conn, user_id)
    
    # Display and edit preferences
    with st.form("sharing_preferences_form"):
        st.subheader("Data Elements to Share")
        
        # Data elements selection
        data_elements = [
            "aggregated_cases",
            "resistance_patterns",
            "treatment_outcomes",
            "demographic_data"
        ]
        
        selected_elements = []
        for element in data_elements:
            if st.checkbox(
                element.replace("_", " ").title(),
                value=element in preferences.get('data_elements', [])
            ):
                selected_elements.append(element)
        
        # Anonymization level
        st.subheader("Anonymization Level")
        anonymization_level = st.radio(
            "Select level of data anonymization",
            options=["low", "medium", "high"],
            index=["low", "medium", "high"].index(preferences.get('anonymization_level', 'high')),
            help="Low: Minimal anonymization, Medium: Remove direct identifiers, High: Aggregate data only"
        )
        
        # Geographical regions
        st.subheader("Geographical Regions to Share")
        
        # Get available regions from database
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT location FROM tb_cases WHERE location IS NOT NULL")
            available_regions = [row[0] for row in cursor.fetchall() if row[0]]
        except:
            available_regions = []
        
        if not available_regions:
            available_regions = ["global"]
        
        # Add global option
        if "global" not in available_regions:
            available_regions = ["global"] + available_regions
        
        selected_regions = st.multiselect(
            "Select regions to share data from",
            options=available_regions,
            default=preferences.get('regions_allowed', ['global'])
        )
        
        # Auto-update preference
        auto_update = st.checkbox(
            "Automatically update shared data",
            value=preferences.get('auto_update', False),
            help="Allow collaborators to access your latest data automatically"
        )
        
        # Submit button
        submitted = st.form_submit_button("Save Preferences")
        
        if submitted:
            # Save preferences to database
            updated_preferences = {
                'user_id': user_id,
                'data_elements': selected_elements,
                'anonymization_level': anonymization_level,
                'regions_allowed': selected_regions if selected_regions else ['global'],
                'auto_update': auto_update
            }
            
            success = global_collaboration.save_sharing_preferences(conn, updated_preferences)
            
            if success:
                st.success("Data sharing preferences saved successfully")
                
                # Log the activity
                utils.log_activity(
                    conn, 
                    user_id, 
                    "Updated Sharing Preferences", 
                    {"anonymization_level": anonymization_level}
                )
            else:
                st.error("Failed to save sharing preferences")
    
    # Display current sharing token if available
    if 'sharing_token' in preferences:
        st.subheader("Your Sharing Token")
        st.info(f"Token: {preferences['sharing_token']}")
        st.caption("Share this token with collaborators to allow them to request access to your data")

def show_available_collaborations(conn):
    """Display available collaborations interface"""
    st.header("Available Collaborations")
    
    # Get shared datasets
    shared_datasets = global_collaboration.get_shared_datasets(conn)
    
    if shared_datasets.empty:
        st.info("No shared datasets available for collaboration")
    else:
        # Filter out user's own datasets
        user_id = utils.get_user_id(st.session_state.username, conn)
        if user_id:
            try:
                # Get user's own sharing token
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT sharing_token FROM sharing_preferences WHERE user_id = %s",
                    (user_id,)
                )
                own_token = cursor.fetchone()
                
                if own_token:
                    # Filter out own dataset
                    shared_datasets = shared_datasets[shared_datasets['sharing_token'] != own_token[0]]
            except:
                pass
        
        if shared_datasets.empty:
            st.info("No external shared datasets available for collaboration")
        else:
            # Display available datasets
            st.dataframe(
                shared_datasets[['provider', 'data_elements', 'anonymization_level', 'last_updated']],
                use_container_width=True,
                hide_index=True
            )
            
            # Request collaboration
            st.subheader("Request Collaboration")
            
            selected_provider = st.selectbox(
                "Select provider to collaborate with",
                options=shared_datasets['provider'].tolist()
            )
            
            if selected_provider:
                # Get token for selected provider
                provider_token = shared_datasets[shared_datasets['provider'] == selected_provider]['sharing_token'].iloc[0]
                
                request_purpose = st.text_area(
                    "Purpose of collaboration request",
                    height=100,
                    placeholder="Explain why you want to collaborate with this provider..."
                )
                
                if st.button("Send Collaboration Request"):
                    if not request_purpose:
                        st.error("Please provide a purpose for your collaboration request")
                    else:
                        # Record collaboration request
                        success = global_collaboration.record_collaboration_request(
                            conn, user_id, provider_token
                        )
                        
                        if success:
                            st.success(f"Collaboration request sent to {selected_provider}")
                            
                            # Log the activity
                            utils.log_activity(
                                conn, 
                                user_id, 
                                "Sent Collaboration Request", 
                                {"provider": selected_provider}
                            )
                        else:
                            st.error("Failed to send collaboration request")

def show_collaboration_requests(conn):
    """Display collaboration requests interface"""
    st.header("Manage Collaboration Requests")
    
    # Get user ID
    user_id = utils.get_user_id(st.session_state.username, conn)
    
    if not user_id:
        st.error("Unable to retrieve user information")
        return
    
    # Get pending requests
    pending_requests = global_collaboration.get_pending_collaboration_requests(conn, user_id)
    
    if pending_requests.empty:
        st.info("No pending collaboration requests")
    else:
        # Display pending requests
        st.subheader("Pending Requests")
        st.dataframe(
            pending_requests[['requester', 'request_date']],
            use_container_width=True,
            hide_index=True
        )
        
        # Handle requests
        st.subheader("Respond to Request")
        
        selected_request = st.selectbox(
            "Select request to respond to",
            options=pending_requests['requester'].tolist()
        )
        
        if selected_request:
            # Get request ID
            request_id = pending_requests[pending_requests['requester'] == selected_request]['id'].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Approve Request"):
                    # Update request status
                    success = global_collaboration.update_collaboration_request(
                        conn, request_id, "approved"
                    )
                    
                    if success:
                        st.success(f"Approved collaboration with {selected_request}")
                        
                        # Log the activity
                        utils.log_activity(
                            conn, 
                            user_id, 
                            "Approved Collaboration", 
                            {"requester": selected_request}
                        )
                        
                        # Refresh the page
                        st.rerun()
                    else:
                        st.error("Failed to approve request")
            
            with col2:
                if st.button("Reject Request"):
                    # Update request status
                    success = global_collaboration.update_collaboration_request(
                        conn, request_id, "rejected"
                    )
                    
                    if success:
                        st.success(f"Rejected collaboration with {selected_request}")
                        
                        # Log the activity
                        utils.log_activity(
                            conn, 
                            user_id, 
                            "Rejected Collaboration", 
                            {"requester": selected_request}
                        )
                        
                        # Refresh the page
                        st.rerun()
                    else:
                        st.error("Failed to reject request")
    
    # Show active collaborations
    st.subheader("Active Collaborations")
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.username, cr.request_date, cr.response_date
            FROM collaboration_requests cr
            JOIN users u ON cr.requester_id = u.id
            JOIN sharing_preferences sp ON cr.provider_token = sp.sharing_token
            WHERE sp.user_id = %s AND cr.status = 'approved'
            """,
            (user_id,)
        )
        active_collaborations = cursor.fetchall()
        
        if not active_collaborations:
            st.info("No active collaborations")
        else:
            # Create DataFrame for display
            active_df = pd.DataFrame(
                active_collaborations,
                columns=['Collaborator', 'Request Date', 'Approval Date']
            )
            
            # Format dates
            for date_col in ['Request Date', 'Approval Date']:
                if date_col in active_df.columns:
                    active_df[date_col] = active_df[date_col].apply(utils.format_datetime)
            
            st.dataframe(active_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error retrieving active collaborations: {e}")

def show_research_opportunities():
    """Display research opportunities based on global collaboration data"""
    st.header("Global Research Opportunities")
    
    st.markdown("""
    <div style="padding: 10px; border-radius: 10px; background-color: #e6f3ff; margin-bottom: 20px;">
        <h4 style="color: #0066cc;">International TB Research Network</h4>
        <p>Connect with researchers worldwide to collaborate on TB studies, clinical trials, 
        and publications. Leverage pooled data for greater insights and impact.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Research projects in progress
    st.subheader("Active Research Projects")
    
    # Sample research projects
    research_data = {
        "Project Title": [
            "Multi-country analysis of bedaquiline resistance emergence",
            "AI-based prediction of MDR-TB treatment outcomes",
            "Genomic determinants of TB transmission in high-burden settings",
            "Pharmacokinetic variability in DR-TB regimens",
            "Social determinants of TB treatment adherence"
        ],
        "Lead Institution": [
            "University of California, San Francisco",
            "Indian Council of Medical Research",
            "FIND & Stop TB Partnership",
            "University of Cape Town",
            "London School of Hygiene & Tropical Medicine"
        ],
        "Countries Involved": [
            "USA, South Africa, India, Philippines",
            "India, China, Russia, Brazil",
            "South Africa, Kenya, Vietnam, Peru",
            "South Africa, Uganda, Moldova, Belarus",
            "UK, India, Nigeria, Indonesia, Pakistan"
        ],
        "Participants Needed": [
            "Yes", "No", "Yes", "Yes", "No"
        ],
        "Status": [
            "Enrolling", "Analysis", "Data Collection", "Enrolling", "Writing"
        ]
    }
    
    research_df = pd.DataFrame(research_data)
    st.dataframe(research_df, use_container_width=True)
    
    # Clinical trials
    st.subheader("Upcoming Clinical Trials")
    
    # Tabs for different trial types
    trial_tabs = st.tabs(["Treatment Trials", "Diagnostic Trials", "Vaccine Trials"])
    
    with trial_tabs[0]:  # Treatment trials
        st.markdown("""
        #### Novel Treatment Regimen Trials
        
        | Trial Name | Treatment | Phase | Sites | Enrollment Status |
        | ---------- | --------- | ----- | ----- | ----------------- |
        | SimpliciTB | BPaMZ | Phase 2c/3 | 10 countries | Enrolling |
        | ZeNix | BPaL with varied linezolid | Phase 3 | 7 countries | Complete |
        | TB-PRACTECAL | BPaLM | Phase 2/3 | 4 countries | Complete |
        | endTB | Bedaquiline & Delamanid | Phase 3 | 7 countries | Analysis |
        | BEAT-TB | 4-month regimen | Phase 2 | 3 countries | Planning |
        """)
    
    with trial_tabs[1]:  # Diagnostic trials
        st.markdown("""
        #### TB Diagnostics Evaluation
        
        | Trial Name | Diagnostic Test | Type | Sites | Status |
        | ---------- | --------------- | ---- | ----- | ------ |
        | Xpert XDR Evaluation | Xpert MTB/XDR | PCR | 5 countries | Enrolling |
        | TB-LAMP Study | Loop-mediated isothermal amplification | Molecular | 4 countries | Analysis |
        | TraDIS | Truenat MTB-RIF Dx | POC | 3 countries | Complete |
        | SILVAMP-LAM | Urine LAM test | POC | 2 countries | Enrolling |
        """)
    
    with trial_tabs[2]:  # Vaccine trials
        st.markdown("""
        #### TB Vaccine Development
        
        | Trial Name | Vaccine | Phase | Sites | Status |
        | ---------- | ------- | ----- | ----- | ------ |
        | M72/AS01E | M72/AS01E | Phase 2b | 3 countries | Complete |
        | MTBVAC | MTBVAC | Phase 2a | 2 countries | Enrolling |
        | H56:IC31 | H56:IC31 | Phase 2 | 3 countries | Enrolling |
        | BCG Revaccination | BCG | Phase 2 | 1 country | Complete |
        """)
    
    # Collaboration opportunities
    st.subheader("Join a Collaborative Study")
    
    # Two columns layout for different types of opportunities
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Data Contribution Opportunities")
        
        with st.expander("Global TB Resistance Database"):
            st.markdown("""
            **Institution**: WHO Global TB Program
            
            **Description**: Contribute TB drug resistance data to the global surveillance database. 
            Data will be used for the annual Global TB Report and to monitor progress towards 
            End TB Strategy goals.
            
            **Data Needed**: MDR/XDR-TB cases, resistance patterns, treatment outcomes
            
            **Commitment**: Annual data submission
            
            [**Apply to Join**]
            """)
            
        with st.expander("TB Genomics Consortium"):
            st.markdown("""
            **Institution**: ReSeqTB & CRyPTIC Network
            
            **Description**: Share whole genome sequencing data from TB isolates to improve 
            understanding of resistance mutations and transmission patterns.
            
            **Data Needed**: WGS data, phenotypic DST results, basic clinical data
            
            **Commitment**: Contribution of at least 50 sequences annually
            
            [**Apply to Join**]
            """)
    
    with col2:
        st.markdown("### Research Grant Opportunities")
        
        with st.expander("Multi-Country DR-TB Implementation Research"):
            st.markdown("""
            **Funder**: USAID & Stop TB Partnership
            
            **Description**: Grants for implementation research to improve MDR-TB care 
            delivery in high-burden settings.
            
            **Focus Areas**: 
            - Digital adherence technologies
            - Decentralized MDR-TB care
            - Active case finding strategies
            
            **Funding Range**: $250,000 - $1,000,000
            
            **Deadline**: September 30, 2025
            
            [**View Details**]
            """)
            
        with st.expander("TB Diagnostic Innovation Challenge"):
            st.markdown("""
            **Funder**: Bill & Melinda Gates Foundation
            
            **Description**: Challenge grants for novel TB diagnostic approaches with 
            potential for use in low-resource settings.
            
            **Focus Areas**: 
            - Non-sputum based diagnostics
            - Point-of-care molecular testing
            - AI-enabled screening tools
            
            **Funding Range**: $100,000 - $500,000
            
            **Deadline**: August 15, 2025
            
            [**View Details**]
            """)
    
    # Publication opportunities
    st.subheader("Publication Opportunities")
    
    st.markdown("""
    #### Upcoming Special Issues and Calls for Papers
    
    | Journal | Special Issue Topic | Submission Deadline | Impact Factor |
    | ------- | ------------------ | ------------------- | ------------- |
    | Int J Tuberc Lung Dis | Digital Technologies for TB Care | December 15, 2025 | 2.8 |
    | Journal of Clinical TB | Next Generation Sequencing in Drug Resistance | October 30, 2025 | 3.6 |
    | Lancet Global Health | TB Elimination Strategies | January 31, 2026 | 22.0 |
    | PLoS ONE | TB Data Science | November 15, 2025 | 3.2 |
    
    [**View More Opportunities**]
    """)
    
    # Disclaimer
    st.info("""
    These research opportunities are updated regularly. To participate in any study, 
    you must follow institutional research protocols, obtain necessary approvals, and 
    ensure data sharing complies with all relevant regulations and ethical standards.
    """)
