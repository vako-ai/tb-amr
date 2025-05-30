import streamlit as st
import pandas as pd
import os
import io
import datetime
import data_loader
import data_processor
import utils
from db_manager import get_connection

def show():
    """Display the data import/export page"""
    st.title("Data Import/Export")
    
    # Connect to the PostgreSQL database
    conn = get_connection()
    
    # Create tabs for import and export
    tab1, tab2 = st.tabs(["Import Data", "Export Data"])
    
    with tab1:
        show_import_interface(conn)
    
    with tab2:
        show_export_interface(conn)
    
    # Close database connection
    conn.close()

def show_import_interface(conn):
    """Display data import interface"""
    st.header("Import TB Resistance Data")
    
    import_method = st.radio(
        "Select Import Method",
        ["File Upload", "API Connection"]
    )
    
    if import_method == "File Upload":
        show_file_upload(conn)
    else:
        show_api_import(conn)

def show_file_upload(conn):
    """Display file upload interface"""
    st.subheader("Upload Data File")
    
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["csv", "xlsx", "xls", "json"]
    )
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        # Load data based on file type
        if file_extension == "csv":
            df, error = data_loader.load_csv_data(uploaded_file)
        elif file_extension in ["xlsx", "xls"]:
            df, error = data_loader.load_excel_data(uploaded_file)
        elif file_extension == "json":
            df, error = data_loader.load_json_data(uploaded_file)
        else:
            df, error = None, "Unsupported file format"
        
        if error:
            st.error(f"Error loading file: {error}")
        elif df is not None:
            process_imported_data(df, conn, source=f"File: {uploaded_file.name}")
        else:
            st.error("Failed to load data from file")

def show_api_import(conn):
    """Display API import interface"""
    st.subheader("Import Data from API")
    
    api_url = st.text_input("API Endpoint URL")
    
    # API authentication (optional)
    use_auth = st.checkbox("API requires authentication")
    api_key = None
    
    if use_auth:
        auth_method = st.radio("Authentication Method", ["API Key", "Bearer Token"])
        api_key = st.text_input("Enter API Key/Token", type="password")
    
    if st.button("Connect to API") and api_url:
        if not utils.validate_api_url(api_url):
            st.error("Invalid API URL format. Please enter a valid URL.")
        else:
            with st.spinner("Connecting to API..."):
                df, error = data_loader.load_api_data(api_url, api_key)
                
                if error:
                    st.error(f"Error connecting to API: {error}")
                elif df is not None:
                    process_imported_data(df, conn, source=f"API: {api_url}")
                else:
                    st.error("Failed to load data from API")

def process_imported_data(df, conn, source):
    """Process and import data into the database"""
    st.subheader("Data Preview")
    st.dataframe(df.head(), use_container_width=True)
    
    st.write(f"Total rows: {len(df)}")
    st.write(f"Columns: {', '.join(df.columns)}")
    
    # Data mapping
    st.subheader("Data Mapping")
    
    # Get required columns for TB cases
    required_columns = [
        "patient_id", "age", "gender", "location", "diagnosis_date", 
        "tb_type", "resistance_pattern", "treatment_regimen", 
        "treatment_start_date", "treatment_end_date", "treatment_outcome"
    ]
    
    # Create mapping from source columns to required columns
    mapping = {}
    st.write("Map your data columns to TB Resistance Hub fields:")
    
    # Split the mapping into columns
    col1, col2 = st.columns(2)
    
    for i, req_col in enumerate(required_columns):
        column = col1 if i < len(required_columns) // 2 else col2
        with column:
            mapping[req_col] = st.selectbox(
                f"Map to '{req_col}'",
                options=[""] + list(df.columns),
                key=f"map_{req_col}"
            )
    
    # Process and save data
    if st.button("Import Data"):
        # Check if at least essential fields are mapped
        essential_fields = ["patient_id", "diagnosis_date", "tb_type", "resistance_pattern"]
        missing_essential = [field for field in essential_fields if not mapping.get(field)]
        
        if missing_essential:
            st.error(f"Please map the following essential fields: {', '.join(missing_essential)}")
        else:
            # Create new DataFrame with mapped columns
            mapped_df = pd.DataFrame()
            
            for tb_hub_col, source_col in mapping.items():
                if source_col:
                    mapped_df[tb_hub_col] = df[source_col]
                else:
                    mapped_df[tb_hub_col] = None
            
            # Preprocess the data
            processed_df = data_processor.preprocess_tb_data(mapped_df)
            
            # Additional processing for resistance patterns if needed
            if "resistance_pattern" in processed_df.columns:
                # Check for drug resistance columns and extract resistance pattern if needed
                drug_columns = [col for col in processed_df.columns if 
                               ('resistant' in col.lower() or 'resistance' in col.lower()) 
                               and col != 'resistance_pattern']
                
                if drug_columns and processed_df['resistance_pattern'].isnull().any():
                    processed_df = data_processor.extract_resistance_patterns(processed_df, drug_columns)
            
            # Check for tb_type and categorize if needed
            if "tb_type" in processed_df.columns and processed_df['tb_type'].isnull().any():
                if "resistance_pattern" in processed_df.columns:
                    processed_df = data_processor.categorize_tb_type(processed_df)
            
            # Add metadata
            user_id = utils.get_user_id(st.session_state.username, conn)
            current_time = datetime.datetime.now().isoformat()
            
            processed_df['created_by'] = user_id
            processed_df['created_at'] = current_time
            processed_df['updated_at'] = current_time
            
            # Save to database
            try:
                processed_df.to_sql('tb_cases', conn, if_exists='append', index=False)
                
                # Log the activity
                if user_id:
                    utils.log_activity(
                        conn, 
                        user_id, 
                        "Data Import", 
                        {"source": source, "rows": len(processed_df)}
                    )
                
                st.success(f"Successfully imported {len(processed_df)} records")
            except Exception as e:
                st.error(f"Error saving data to database: {e}")

def show_export_interface(conn):
    """Display data export interface"""
    st.header("Export TB Resistance Data")
    
    # Get available tables
    tables, error = data_loader.get_database_tables(conn)
    
    if error:
        st.error(f"Error retrieving database tables: {error}")
    elif not tables:
        st.info("No data available for export")
    else:
        # Filter out system tables
        data_tables = [table for table in tables if not table.startswith("pg_") and not table.startswith("information_schema")]
        
        if not data_tables:
            st.info("No data tables available for export")
        else:
            # Select table to export
            selected_table = st.selectbox(
                "Select data to export",
                options=data_tables
            )
            
            # Export format
            export_format = st.radio(
                "Export Format",
                ["csv", "json", "excel"]
            )
            
            # Data filtering options
            st.subheader("Filter Data (Optional)")
            
            # Get table schema
            schema, schema_error = data_loader.get_table_schema(selected_table, conn)
            
            if schema_error:
                st.error(f"Error retrieving table schema: {schema_error}")
            else:
                # Create filter options based on schema
                filters = {}
                
                # Example: simple filtering for the tb_cases table
                if selected_table == "tb_cases":
                    # Filter by location
                    try:
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT DISTINCT location FROM {selected_table} WHERE location IS NOT NULL")
                        locations = [row[0] for row in cursor.fetchall() if row[0]]
                        
                        if locations:
                            filters["location"] = st.multiselect(
                                "Filter by Location",
                                options=locations
                            )
                    except:
                        pass
                    
                    # Filter by TB type
                    try:
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT DISTINCT tb_type FROM {selected_table} WHERE tb_type IS NOT NULL")
                        tb_types = [row[0] for row in cursor.fetchall() if row[0]]
                        
                        if tb_types:
                            filters["tb_type"] = st.multiselect(
                                "Filter by TB Type",
                                options=tb_types
                            )
                    except:
                        pass
                    
                    # Filter by date range if diagnosis_date exists
                    try:
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT MIN(diagnosis_date), MAX(diagnosis_date) FROM {selected_table} WHERE diagnosis_date IS NOT NULL")
                        date_range = cursor.fetchone()
                        
                        if date_range and date_range[0] and date_range[1]:
                            try:
                                min_date = datetime.datetime.fromisoformat(date_range[0])
                                max_date = datetime.datetime.fromisoformat(date_range[1])
                                
                                date_filter = st.date_input(
                                    "Filter by Diagnosis Date Range",
                                    value=(min_date.date(), max_date.date())
                                )
                                
                                if len(date_filter) == 2:
                                    filters["date_range"] = (
                                        date_filter[0].isoformat(),
                                        date_filter[1].isoformat()
                                    )
                            except:
                                pass
                    except:
                        pass
            
            # Export button
            if st.button("Export Data"):
                # Build SQL query with filters
                query = f"SELECT * FROM {selected_table}"
                
                where_clauses = []
                params = []
                
                if selected_table == "tb_cases":
                    if "location" in filters and filters["location"]:
                        placeholders = ", ".join(["?"] * len(filters["location"]))
                        where_clauses.append(f"location IN ({placeholders})")
                        params.extend(filters["location"])
                    
                    if "tb_type" in filters and filters["tb_type"]:
                        placeholders = ", ".join(["?"] * len(filters["tb_type"]))
                        where_clauses.append(f"tb_type IN ({placeholders})")
                        params.extend(filters["tb_type"])
                    
                    if "date_range" in filters:
                        where_clauses.append("diagnosis_date BETWEEN ? AND ?")
                        params.extend(filters["date_range"])
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
                
                # Execute query
                try:
                    df = pd.read_sql(query, conn, params=params)
                    
                    if df.empty:
                        st.warning("No data matches the selected filters")
                    else:
                        # Export data
                        if export_format == "csv":
                            csv = df.to_csv(index=False)
                            filename = f"{selected_table}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            
                            st.download_button(
                                "Download CSV",
                                data=csv,
                                file_name=filename,
                                mime="text/csv"
                            )
                        
                        elif export_format == "json":
                            json_str = df.to_json(orient="records")
                            filename = f"{selected_table}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            
                            st.download_button(
                                "Download JSON",
                                data=json_str,
                                file_name=filename,
                                mime="application/json"
                            )
                        
                        elif export_format == "excel":
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                df.to_excel(writer, sheet_name=selected_table, index=False)
                            
                            filename = f"{selected_table}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                            
                            st.download_button(
                                "Download Excel",
                                data=output.getvalue(),
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        # Log the activity
                        user_id = utils.get_user_id(st.session_state.username, conn)
                        if user_id:
                            utils.log_activity(
                                conn, 
                                user_id, 
                                "Data Export", 
                                {"table": selected_table, "format": export_format, "rows": len(df)}
                            )
                
                except Exception as e:
                    st.error(f"Error exporting data: {e}")
