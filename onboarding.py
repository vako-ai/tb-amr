import streamlit as st
import json
from datetime import datetime

def initialize_onboarding():
    """Initialize onboarding state variables if they don't exist"""
    if 'onboarding_complete' not in st.session_state:
        st.session_state.onboarding_complete = False
    
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    
    if 'show_onboarding' not in st.session_state:
        st.session_state.show_onboarding = False
    
    if 'onboarding_preferences' not in st.session_state:
        st.session_state.onboarding_preferences = {
            "role": "",
            "primary_interests": [],
            "data_focus": "",
            "experience_level": "",
            "preferred_pages": []
        }

def save_onboarding_preferences(user_id, preferences):
    """
    Save onboarding preferences to the database
    
    Parameters:
    user_id (int): User ID
    preferences (dict): User preferences
    """
    from db_manager import get_connection, execute_query
    
    conn = get_connection()
    if conn:
        try:
            # Convert preferences to JSON
            preferences_json = json.dumps(preferences)
            
            # Check if preferences already exist
            query = """
            SELECT id FROM user_preferences 
            WHERE user_id = %s
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                # Update existing preferences
                query = """
                UPDATE user_preferences 
                SET preferences = %s, last_updated = %s
                WHERE user_id = %s
                """
                execute_query(conn, query, (preferences_json, datetime.now(), user_id))
            else:
                # Insert new preferences
                query = """
                INSERT INTO user_preferences (user_id, preferences, created_at)
                VALUES (%s, %s, %s)
                """
                execute_query(conn, query, (user_id, preferences_json, datetime.now()))
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving onboarding preferences: {e}")
            if conn:
                conn.close()
            return False
    
    return False

def get_onboarding_preferences(user_id):
    """
    Get onboarding preferences from the database
    
    Parameters:
    user_id (int): User ID
    
    Returns:
    dict: User preferences
    """
    from db_manager import get_connection, fetch_data
    
    conn = get_connection()
    if conn:
        try:
            query = """
            SELECT preferences FROM user_preferences 
            WHERE user_id = %s
            """
            
            result = fetch_data(conn, query, (user_id,))
            conn.close()
            
            if result and result[0]:
                return json.loads(result[0][0])
            
        except Exception as e:
            print(f"Error getting onboarding preferences: {e}")
            if conn:
                conn.close()
    
    return None

def ensure_preferences_table():
    """Ensure the user_preferences table exists in the database"""
    from db_manager import get_connection, execute_query
    
    conn = get_connection()
    if conn:
        try:
            # Create user_preferences table if it doesn't exist
            query = """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                preferences JSONB,
                created_at TIMESTAMP NOT NULL,
                last_updated TIMESTAMP,
                UNIQUE(user_id)
            )
            """
            execute_query(conn, query)
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error ensuring preferences table: {e}")
            if conn:
                conn.close()
            return False
    
    return False

def start_onboarding():
    """Start the onboarding process"""
    st.session_state.onboarding_step = 0
    st.session_state.show_onboarding = True
    st.session_state.onboarding_complete = False

def end_onboarding():
    """End the onboarding process"""
    st.session_state.show_onboarding = False
    st.session_state.onboarding_complete = True
    
    # Save preferences to database if user is logged in
    if st.session_state.authenticated and 'user_id' in st.session_state:
        save_onboarding_preferences(
            st.session_state.user_id, 
            st.session_state.onboarding_preferences
        )

def next_step():
    """Go to the next onboarding step"""
    st.session_state.onboarding_step += 1

def previous_step():
    """Go to the previous onboarding step"""
    st.session_state.onboarding_step = max(0, st.session_state.onboarding_step - 1)

def skip_onboarding():
    """Skip the onboarding process"""
    st.session_state.show_onboarding = False
    st.session_state.onboarding_complete = True

def user_role_step():
    """Onboarding step for user role selection"""
    st.markdown("### What best describes your role?")
    
    roles = [
        "Healthcare Provider (Clinician/Nurse)",
        "Public Health Official",
        "TB Program Manager",
        "Laboratory Professional",
        "Researcher/Scientist",
        "Data Analyst",
        "Policy Maker",
        "Other"
    ]
    
    selected_role = st.selectbox(
        "Select your role",
        roles,
        index=0 if not st.session_state.onboarding_preferences["role"] else 
              roles.index(st.session_state.onboarding_preferences["role"])
    )
    
    st.session_state.onboarding_preferences["role"] = selected_role
    
    if st.button("Next", key="user_role_next"):
        next_step()

def interests_step():
    """Onboarding step for primary interests"""
    st.markdown("### What are your primary interests in TB data?")
    
    interests = [
        "Monitoring drug resistance patterns",
        "Clinical decision support for patient treatment",
        "Tracking treatment outcomes",
        "Surveillance and epidemiology",
        "Policy development",
        "Research and analysis",
        "Data sharing and collaboration"
    ]
    
    selected_interests = st.multiselect(
        "Select your interests (choose up to 3)",
        interests,
        default=st.session_state.onboarding_preferences["primary_interests"]
    )
    
    if len(selected_interests) > 3:
        st.warning("Please select no more than 3 primary interests")
    else:
        st.session_state.onboarding_preferences["primary_interests"] = selected_interests
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", key="interests_prev"):
            previous_step()
    
    with col2:
        next_disabled = len(selected_interests) > 3 or len(selected_interests) == 0
        if st.button("Next", key="interests_next", disabled=next_disabled):
            next_step()

def data_focus_step():
    """Onboarding step for data focus"""
    st.markdown("### What geographical scope are you most interested in?")
    
    data_focus_options = [
        "Local/District Level",
        "State/Province Level",
        "National Level",
        "Regional (Multiple Countries)",
        "Global",
        "Not specific"
    ]
    
    data_focus = st.radio(
        "Select your primary geographical focus",
        data_focus_options,
        index=0 if not st.session_state.onboarding_preferences["data_focus"] else 
               data_focus_options.index(st.session_state.onboarding_preferences["data_focus"])
    )
    
    st.session_state.onboarding_preferences["data_focus"] = data_focus
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", key="data_focus_prev"):
            previous_step()
    
    with col2:
        if st.button("Next", key="data_focus_next"):
            next_step()

def experience_level_step():
    """Onboarding step for experience level"""
    st.markdown("### How would you describe your experience with TB data systems?")
    
    experience_options = [
        "Beginner - New to TB data and analytics",
        "Intermediate - Some experience with TB data",
        "Advanced - Regularly work with TB data and analytics",
        "Expert - Specialized in TB data systems and analysis"
    ]
    
    experience = st.select_slider(
        "Select your experience level",
        options=experience_options,
        value=st.session_state.onboarding_preferences["experience_level"] or experience_options[0]
    )
    
    st.session_state.onboarding_preferences["experience_level"] = experience
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", key="experience_prev"):
            previous_step()
    
    with col2:
        if st.button("Next", key="experience_next"):
            next_step()

def preferred_pages_step():
    """Onboarding step for preferred pages"""
    st.markdown("### Which features are you most interested in?")
    
    pages = [
        "Dashboard - Overview of TB resistance data and trends",
        "Clinical Decision Support - Treatment recommendations and patient management",
        "Data Import/Export - Managing and exchanging TB data",
        "Global Collaboration - Sharing and comparing data internationally",
        "Analytics - In-depth analysis and visualization of TB data"
    ]
    
    selected_pages = st.multiselect(
        "Select the features you'll use most frequently",
        pages,
        default=st.session_state.onboarding_preferences["preferred_pages"]
    )
    
    st.session_state.onboarding_preferences["preferred_pages"] = selected_pages
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", key="pages_prev"):
            previous_step()
    
    with col2:
        if st.button("Complete Setup", key="pages_complete"):
            next_step()

def onboarding_summary():
    """Show onboarding summary and complete setup"""
    st.markdown("### Your Personalized Setup")
    
    prefs = st.session_state.onboarding_preferences
    
    st.markdown(f"**Role:** {prefs['role']}")
    
    st.markdown("**Primary Interests:**")
    for interest in prefs['primary_interests']:
        st.markdown(f"- {interest}")
    
    st.markdown(f"**Geographical Focus:** {prefs['data_focus']}")
    st.markdown(f"**Experience Level:** {prefs['experience_level']}")
    
    st.markdown("**Preferred Features:**")
    for page in prefs['preferred_pages']:
        page_name = page.split(" - ")[0]
        st.markdown(f"- {page_name}")
    
    st.markdown("---")
    
    st.markdown("""
    Based on your preferences, we've customized your experience. You can always 
    update these preferences in your user settings.
    """)
    
    if st.button("Previous", key="summary_prev"):
        previous_step()
    
    if st.button("Start Using TB Resistance Hub", key="summary_complete"):
        end_onboarding()

def welcome_back_info():
    """Show personalized welcome back message based on preferences"""
    if ('user_id' in st.session_state and 
        st.session_state.authenticated and 
        st.session_state.onboarding_complete):
        
        # Get stored preferences
        prefs = st.session_state.onboarding_preferences
        
        # Personalized welcome back message
        if "primary_interests" in prefs and prefs["primary_interests"]:
            # Get first interest
            main_interest = prefs["primary_interests"][0]
            
            # Show relevant info based on interest
            if "resistance patterns" in main_interest.lower():
                st.info(f"📊 Welcome back! New resistance pattern data is available in the Analytics section.")
            
            elif "clinical decision" in main_interest.lower():
                st.info(f"🩺 Welcome back! Check out the Clinical Decision Support module for the latest treatment guidelines.")
            
            elif "treatment outcomes" in main_interest.lower():
                st.info(f"📈 Welcome back! New treatment outcome reports are available in the Dashboard.")
            
            elif "surveillance" in main_interest.lower():
                st.info(f"🔍 Welcome back! Recent surveillance data has been updated in the Analytics section.")
            
            elif "research" in main_interest.lower():
                st.info(f"🧪 Welcome back! New research opportunities are available in the Global Collaboration area.")
            
            elif "data sharing" in main_interest.lower():
                st.info(f"🌐 Welcome back! Check out new collaboration requests in the Global Collaboration module.")
            
            else:
                st.info(f"👋 Welcome back to the TB Resistance Hub!")
        else:
            st.info(f"👋 Welcome back to the TB Resistance Hub!")

def show_onboarding():
    """Show the appropriate onboarding step"""
    ensure_preferences_table()
    
    # If the user has closed the onboarding overlay, don't show it
    if not st.session_state.show_onboarding:
        return
    
    # Create a overlay-like container for onboarding
    with st.container():
        # Add styling to make it look like an overlay
        st.markdown("""
        <style>
        .onboarding-overlay {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border-left: 5px solid #3498DB;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='onboarding-overlay'>", unsafe_allow_html=True)
        
        # Header
        st.markdown("## Welcome to TB Resistance Hub")
        st.markdown("Let's personalize your experience to better meet your needs.")
        
        # Option to skip onboarding
        if st.button("Skip Setup", key="skip_onboarding"):
            skip_onboarding()
            st.rerun()
        
        # Show appropriate step
        if st.session_state.onboarding_step == 0:
            user_role_step()
        elif st.session_state.onboarding_step == 1:
            interests_step()
        elif st.session_state.onboarding_step == 2:
            data_focus_step()
        elif st.session_state.onboarding_step == 3:
            experience_level_step()
        elif st.session_state.onboarding_step == 4:
            preferred_pages_step()
        elif st.session_state.onboarding_step == 5:
            onboarding_summary()
        else:
            end_onboarding()
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_feature_tour(page):
    """Show feature tour for specific page"""
    # Feature tours for different pages
    tours = {
        "Consolidated Dashboard": [
            "Use the tabs at the top to navigate between different features.",
            "The Overview tab shows key metrics and geographical distribution.",
            "The Analytics tab provides in-depth resistance trend analysis.",
            "The Clinical Support tab helps with treatment decisions.",
            "The Data Management tab allows you to import and export data.",
            "The Collaboration tab connects you with global research opportunities.",
            "The Medical Search tab provides smart search with autocomplete for TB terminology."
        ],
        "Dashboard": [
            "The Dashboard provides an overview of key TB resistance metrics.",
            "Use the visualizations to explore trends and patterns in TB data.",
            "Click on charts to drill down into specific data points."
        ],
        "Clinical Decision Support": [
            "This module helps with treatment decisions for TB patients.",
            "Enter patient details and resistance patterns to get regimen recommendations.",
            "Review treatment guidelines and clinical notes for different TB types."
        ],
        "Data Import/Export": [
            "Import TB data from various sources including CSV, Excel, and APIs.",
            "Export data for reports and further analysis.",
            "Configure data validation rules and mappings."
        ],
        "Global Collaboration": [
            "Connect with other TB programs and researchers globally.",
            "Share anonymized data and insights with partner organizations.",
            "Access research opportunities and collaborative projects."
        ],
        "Analytics": [
            "Perform in-depth analysis of TB resistance patterns.",
            "Create custom visualizations and reports.",
            "Track key performance indicators for TB programs."
        ],
        "User Management": [
            "Manage user accounts and access permissions.",
            "Configure user roles and responsibilities.",
            "Review user activity logs."
        ]
    }
    
    if page in tours:
        # Create expander for feature tour
        with st.sidebar.expander("Feature Tour", expanded=False):
            st.markdown(f"### {page} Features")
            for i, feature in enumerate(tours[page]):
                st.markdown(f"{i+1}. {feature}")
            
            if st.button("Close Tour", key="close_tour"):
                pass

def inject_help_buttons():
    """Add help buttons to the sidebar"""
    # Add help button to sidebar
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Restart Tour", key="restart_tour"):
                start_onboarding()
                st.rerun()
        
        with col2:
            if st.button("❓ Get Help", key="get_help"):
                st.session_state.show_help = True
                st.rerun()

def show_help_modal():
    """Show help modal with resources and guidance"""
    if 'show_help' in st.session_state and st.session_state.show_help:
        # Create a overlay-like container for help
        with st.container():
            # Add styling to make it look like a modal
            st.markdown("""
            <style>
            .help-modal {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
                border-left: 5px solid #16A085;
                position: relative;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='help-modal'>", unsafe_allow_html=True)
            
            # Header
            st.markdown("## Help & Resources")
            
            # Help topics
            st.markdown("### Frequently Asked Questions")
            
            with st.expander("How do I import data?"):
                st.markdown("""
                To import data:
                1. Navigate to the Data Import/Export page
                2. Select the data source (CSV, Excel, API)
                3. Follow the import wizard to map fields and validate data
                4. Review the import summary and confirm
                """)
            
            with st.expander("How do I update my preferences?"):
                st.markdown("""
                To update your preferences:
                1. Click on your username in the top right
                2. Select "Settings" from the dropdown
                3. Update your preferences
                4. Click "Save Changes"
                """)
            
            with st.expander("What do the different TB types mean?"):
                st.markdown("""
                - **Drug-susceptible TB**: Responds to first-line TB drugs
                - **INH-resistant TB**: Resistant to isoniazid
                - **RR-TB**: Rifampicin-resistant tuberculosis
                - **MDR-TB**: Multi-drug resistant tuberculosis (resistant to at least INH and RIF)
                - **XDR-TB**: Extensively drug-resistant tuberculosis (MDR-TB plus resistance to a fluoroquinolone and at least one second-line injectable)
                """)
            
            st.markdown("### Getting Support")
            
            st.markdown("""
            For additional help:
            - Review the user guide in the Documentation section
            - Contact technical support at support@tbresistancehub.org
            - Join the monthly webinar for users (first Tuesday of each month)
            """)
            
            # Close button
            if st.button("Close", key="close_help"):
                st.session_state.show_help = False
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

def load_user_preferences():
    """Load user preferences from database if available"""
    if (st.session_state.authenticated and 
        'user_id' in st.session_state and 
        st.session_state.user_id):
        
        # Get preferences from database
        prefs = get_onboarding_preferences(st.session_state.user_id)
        
        # Update session state if preferences exist
        if prefs:
            st.session_state.onboarding_preferences = prefs
            st.session_state.onboarding_complete = True