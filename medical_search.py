import streamlit as st
import pandas as pd
import json
from fuzzywuzzy import process
import db_manager

# Medical terminology categories
CATEGORIES = {
    'tb_types': 'TB Types',
    'drugs': 'Medications',
    'side_effects': 'Side Effects',
    'diagnostic_terms': 'Diagnostic Terms',
    'resistance_patterns': 'Resistance Patterns'
}

# Base medical terminology dictionary
MEDICAL_TERMS = {
    'tb_types': [
        {'term': 'Drug-susceptible TB', 'definition': 'TB that is susceptible to first-line anti-TB drugs.'},
        {'term': 'INH-resistant TB', 'definition': 'TB resistant to isoniazid but susceptible to rifampicin.'},
        {'term': 'RR-TB', 'definition': 'Rifampicin-resistant tuberculosis.'},
        {'term': 'MDR-TB', 'definition': 'Multi-drug resistant tuberculosis (resistant to at least INH and RIF).'},
        {'term': 'XDR-TB', 'definition': 'Extensively drug-resistant tuberculosis (MDR-TB plus resistance to fluoroquinolones and at least one second-line injectable).'},
        {'term': 'TDR-TB', 'definition': 'Totally drug-resistant tuberculosis (resistant to all first and second-line anti-TB drugs).'},
        {'term': 'Pulmonary TB', 'definition': 'TB disease affecting the lungs.'},
        {'term': 'Extrapulmonary TB', 'definition': 'TB disease affecting organs other than the lungs.'},
        {'term': 'Latent TB', 'definition': 'TB infection without active disease.'}
    ],
    'drugs': [
        {'term': 'Isoniazid (INH)', 'definition': 'First-line bactericidal anti-TB drug that inhibits mycolic acid synthesis.'},
        {'term': 'Rifampicin (RIF)', 'definition': 'First-line bactericidal anti-TB drug that inhibits bacterial RNA synthesis.'},
        {'term': 'Ethambutol (EMB)', 'definition': 'First-line bacteriostatic anti-TB drug that inhibits arabinosyl transferase.'},
        {'term': 'Pyrazinamide (PZA)', 'definition': 'First-line anti-TB drug that disrupts membrane transport and energy production.'},
        {'term': 'Streptomycin (SM)', 'definition': 'Injectable aminoglycoside antibiotic used as a second-line anti-TB drug.'},
        {'term': 'Fluoroquinolones', 'definition': 'Class of antibiotics including levofloxacin and moxifloxacin used for MDR-TB.'},
        {'term': 'Bedaquiline', 'definition': 'Novel anti-TB drug that inhibits mycobacterial ATP synthase.'},
        {'term': 'Delamanid', 'definition': 'Nitroimidazole anti-TB drug that inhibits mycolic acid biosynthesis.'},
        {'term': 'Linezolid', 'definition': 'Oxazolidinone antibiotic used for drug-resistant TB.'},
        {'term': 'Clofazimine', 'definition': 'Riminophenazine anti-leprosy drug also used for drug-resistant TB.'},
        {'term': 'Cycloserine', 'definition': 'Second-line anti-TB drug that inhibits cell wall synthesis.'}
    ],
    'side_effects': [
        {'term': 'Hepatotoxicity', 'definition': 'Liver damage that can be caused by anti-TB drugs like INH, RIF, and PZA.'},
        {'term': 'Peripheral neuropathy', 'definition': 'Nerve damage in extremities, common with INH.'},
        {'term': 'Optic neuritis', 'definition': 'Inflammation of the optic nerve, associated with EMB.'},
        {'term': 'Ototoxicity', 'definition': 'Damage to the inner ear affecting hearing, associated with aminoglycosides.'},
        {'term': 'QT prolongation', 'definition': 'Delay in heart ventricle repolarization, associated with bedaquiline, fluoroquinolones.'},
        {'term': 'Arthralgia', 'definition': 'Joint pain, common with PZA.'},
        {'term': 'Hyperuricemia', 'definition': 'Elevated uric acid levels, associated with PZA.'},
        {'term': 'Gastrointestinal disturbance', 'definition': 'Nausea, vomiting, diarrhea, common with many anti-TB drugs.'},
        {'term': 'Myelosuppression', 'definition': 'Decreased production of blood cells, associated with linezolid.'},
        {'term': 'Skin discoloration', 'definition': 'Skin pigmentation changes, associated with clofazimine.'}
    ],
    'diagnostic_terms': [
        {'term': 'Acid-fast bacilli (AFB)', 'definition': 'Bacteria that retain certain dyes after being washed with acid solutions, characteristic of mycobacteria.'},
        {'term': 'AFB smear microscopy', 'definition': 'Examination of sputum or other specimens for acid-fast bacilli using microscopy.'},
        {'term': 'Culture', 'definition': 'Laboratory growth of mycobacteria from patient specimens.'},
        {'term': 'GeneXpert MTB/RIF', 'definition': 'Rapid molecular test that detects M. tuberculosis and rifampicin resistance.'},
        {'term': 'Line probe assay (LPA)', 'definition': 'Molecular test that detects mutations associated with drug resistance.'},
        {'term': 'Drug susceptibility testing (DST)', 'definition': 'Laboratory tests to determine if TB bacteria are susceptible to anti-TB drugs.'},
        {'term': 'Interferon-Gamma Release Assay (IGRA)', 'definition': 'Blood test that measures immune response to TB bacteria.'},
        {'term': 'Tuberculin Skin Test (TST)', 'definition': 'Skin test that measures immune response to TB bacteria.'},
        {'term': 'Chest X-ray', 'definition': 'Radiographic examination of the chest to detect TB-related abnormalities.'},
        {'term': 'Computed Tomography (CT)', 'definition': 'Advanced imaging technique for detailed visualization of TB lesions.'},
        {'term': 'Whole Genome Sequencing (WGS)', 'definition': 'Complete genetic analysis of TB bacteria to determine lineage and resistance patterns.'}
    ],
    'resistance_patterns': [
        {'term': 'INH resistance', 'definition': 'Resistance to isoniazid, often associated with mutations in katG and inhA genes.'},
        {'term': 'RIF resistance', 'definition': 'Resistance to rifampicin, primarily associated with mutations in the rpoB gene.'},
        {'term': 'EMB resistance', 'definition': 'Resistance to ethambutol, associated with mutations in embB gene.'},
        {'term': 'PZA resistance', 'definition': 'Resistance to pyrazinamide, associated with mutations in pncA gene.'},
        {'term': 'Fluoroquinolone resistance', 'definition': 'Resistance to fluoroquinolones, associated with mutations in gyrA and gyrB genes.'},
        {'term': 'Injectable resistance', 'definition': 'Resistance to injectable agents, associated with mutations in rrs and eis promoter regions.'},
        {'term': 'INH+RIF (MDR)', 'definition': 'Resistance to both isoniazid and rifampicin, defining MDR-TB.'},
        {'term': 'INH+RIF+FQ+SLID (XDR)', 'definition': 'Resistance to isoniazid, rifampicin, fluoroquinolones, and second-line injectables, defining XDR-TB.'},
        {'term': 'Primary resistance', 'definition': 'Drug resistance in patients who have never received TB treatment.'},
        {'term': 'Acquired resistance', 'definition': 'Drug resistance developed during TB treatment.'}
    ]
}

def save_medical_terms_to_db():
    """Save medical terminology to database if not already present"""
    conn = db_manager.get_connection()
    if not conn:
        st.error("Could not connect to database")
        return False
    
    try:
        # Check if terminology table exists
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_terminology (
            id SERIAL PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            term VARCHAR(255) NOT NULL,
            definition TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, term)
        )
        """)
        conn.commit()
        
        # Check if we already have terms in the database
        cursor.execute("SELECT COUNT(*) FROM medical_terminology")
        count = cursor.fetchone()[0]
        
        # If no terms exist, insert the default ones
        if count == 0:
            for category, terms in MEDICAL_TERMS.items():
                for term_data in terms:
                    cursor.execute(
                        "INSERT INTO medical_terminology (category, term, definition) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (category, term_data['term'], term_data['definition'])
                    )
            conn.commit()
            st.success("Medical terminology database initialized")
        
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error initializing medical terminology: {e}")
        if conn:
            conn.close()
        return False

def get_medical_terms(category=None, search_term=None):
    """
    Get medical terms from the database
    
    Parameters:
    category (str): Optional category to filter terms
    search_term (str): Optional search term to filter results
    
    Returns:
    pandas.DataFrame: Matching medical terms
    """
    conn = db_manager.get_connection()
    if not conn:
        st.error("Could not connect to database")
        return pd.DataFrame()
    
    try:
        query = "SELECT id, category, term, definition FROM medical_terminology"
        params = []
        
        where_clauses = []
        if category:
            where_clauses.append("category = %s")
            params.append(category)
        
        if search_term:
            # Use ILIKE for case-insensitive partial matching
            where_clauses.append("(term ILIKE %s OR definition ILIKE %s)")
            search_pattern = f"%{search_term}%"
            params.append(search_pattern)
            params.append(search_pattern)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY category, term"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    except Exception as e:
        st.error(f"Error retrieving medical terms: {e}")
        if conn:
            conn.close()
        return pd.DataFrame()

def add_medical_term(category, term, definition):
    """
    Add a new medical term to the database
    
    Parameters:
    category (str): Term category
    term (str): The medical term
    definition (str): Definition of the term
    
    Returns:
    bool: Success status
    """
    if not category or not term or not definition:
        return False
    
    conn = db_manager.get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO medical_terminology (category, term, definition) VALUES (%s, %s, %s) ON CONFLICT (category, term) DO UPDATE SET definition = %s",
            (category, term, definition, definition)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error adding medical term: {e}")
        if conn:
            conn.close()
        return False

def get_term_suggestions(partial_term, limit=10):
    """
    Get suggestions for autocomplete based on partial term
    
    Parameters:
    partial_term (str): Partial term to match
    limit (int): Maximum number of suggestions to return
    
    Returns:
    list: List of matching terms
    """
    if not partial_term or len(partial_term) < 2:
        return []
    
    # Get all terms from the database
    df = get_medical_terms()
    if df.empty:
        return []
    
    # Create a list of all terms
    all_terms = df['term'].tolist()
    
    # Use fuzzy matching to find closest matches
    matches = process.extractBests(partial_term, all_terms, limit=limit, score_cutoff=60)
    
    # Return just the matched terms
    return [match[0] for match in matches]

def search_medical_terms(search_text):
    """
    Search medical terms by text
    
    Parameters:
    search_text (str): Text to search for
    
    Returns:
    pandas.DataFrame: Matching medical terms
    """
    if not search_text or len(search_text) < 2:
        return pd.DataFrame()
    
    return get_medical_terms(search_term=search_text)

def show_search_interface():
    """Display smart search interface with autocomplete"""
    st.header("Medical Terminology Search")
    
    # Initialize medical terms database if needed
    save_medical_terms_to_db()
    
    # Create session state for search text if it doesn't exist
    if 'search_text' not in st.session_state:
        st.session_state.search_text = ""
    
    # Create session state for suggestions
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []
    
    # Function to update suggestions
    def update_suggestions():
        if len(st.session_state.search_text) >= 2:
            st.session_state.suggestions = get_term_suggestions(st.session_state.search_text)
        else:
            st.session_state.suggestions = []
    
    # Function to select suggestion
    def select_suggestion(suggestion):
        st.session_state.search_text = suggestion
        st.session_state.suggestions = []
    
    # Search box with custom styling for autocomplete
    st.markdown("""
    <style>
    .suggestion-item {
        padding: 8px 16px;
        border-bottom: 1px solid #e0e0e0;
        cursor: pointer;
    }
    .suggestion-item:hover {
        background-color: #f5f5f5;
    }
    .suggestions-box {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-top: 5px;
        max-height: 200px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_text = st.text_input(
            "Search for medical terms",
            value=st.session_state.search_text,
            key="search_input",
            on_change=update_suggestions
        )
        st.session_state.search_text = search_text
    
    with col2:
        category_filter = st.selectbox(
            "Category",
            ["All Categories"] + list(CATEGORIES.values()),
            index=0
        )
    
    # Display suggestions
    if st.session_state.suggestions:
        suggestion_html = '<div class="suggestions-box">'
        for suggestion in st.session_state.suggestions:
            suggestion_html += f'<div class="suggestion-item" onclick="document.getElementById(\'search_input\').value=\'{suggestion}\'; document.getElementById(\'search_button\').click();">{suggestion}</div>'
        suggestion_html += '</div>'
        st.markdown(suggestion_html, unsafe_allow_html=True)
    
    # Search button
    if st.button("Search", key="search_button") or st.session_state.search_text:
        # Map category display name back to key
        category_key = None
        if category_filter != "All Categories":
            for key, value in CATEGORIES.items():
                if value == category_filter:
                    category_key = key
                    break
        
        # Perform search
        results = search_medical_terms(st.session_state.search_text)
        
        # Apply category filter if selected
        if category_key:
            results = results[results['category'] == category_key]
        
        if not results.empty:
            st.subheader(f"Search Results ({len(results)} terms found)")
            
            # Group results by category
            for category_key, category_name in CATEGORIES.items():
                category_results = results[results['category'] == category_key]
                if not category_results.empty:
                    with st.expander(f"{category_name} ({len(category_results)} terms)", expanded=True):
                        for _, row in category_results.iterrows():
                            st.markdown(f"**{row['term']}**: {row['definition']}")
        else:
            st.info("No matching terms found. Try a different search term or category.")
    
    # Add new term section (for admin users only)
    if 'user_role' in st.session_state and st.session_state.user_role == 'admin':
        st.markdown("---")
        st.subheader("Add New Medical Term")
        
        with st.form("add_term_form"):
            new_category = st.selectbox(
                "Category",
                list(CATEGORIES.items()),
                format_func=lambda x: x[1]
            )
            new_term = st.text_input("Term")
            new_definition = st.text_area("Definition")
            
            submit_button = st.form_submit_button("Add Term")
            
            if submit_button:
                if new_term and new_definition:
                    success = add_medical_term(new_category[0], new_term, new_definition)
                    if success:
                        st.success(f"Term '{new_term}' added successfully.")
                    else:
                        st.error("Failed to add term. Please try again.")
                else:
                    st.warning("Please enter both term and definition.")