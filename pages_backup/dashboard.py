import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import utils
import data_processor
import analytics
from db_manager import get_connection

def show():
    """Display the dashboard page"""
    st.title("TB Resistance Hub Dashboard")
    
    # Connect to the PostgreSQL database
    conn = get_connection()
    
    # Load data for analytics
    tb_data = analytics.load_tb_data(conn)
    
    # Display key metrics
    st.subheader("Key Metrics")
    
    if not tb_data.empty:
        metrics = analytics.calculate_key_metrics(tb_data)
        trends = analytics.get_recent_trends(tb_data)
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total DR-TB Cases", 
                value=metrics['total_cases'],
                delta=trends.get('case_change_percentage')
            )
            
        with col2:
            st.metric(
                label="Treatment Success Rate", 
                value=f"{metrics.get('treatment_success_rate', 0)}%",
                delta=None
            )
            
        with col3:
            st.metric(
                label="MDR-TB Percentage", 
                value=f"{metrics.get('mdr_tb_percentage', 0)}%",
                delta=None
            )
            
        with col4:
            st.metric(
                label="Avg Treatment Duration", 
                value=f"{metrics.get('avg_treatment_duration_days', 0)} days",
                delta=None
            )
    else:
        st.info("No data available. Import data using the Data Import/Export module.")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    user_id = utils.get_user_id(st.session_state.username, conn)
    if user_id:
        activities = utils.get_recent_activities(conn)
        
        if activities:
            activity_df = pd.DataFrame(activities)
            st.dataframe(
                activity_df[['username', 'activity_type', 'timestamp']],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No recent activities found.")
    
    # Visualizations
    st.subheader("TB Resistance Overview")
    
    if not tb_data.empty:
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs([
            "Resistance Trends", 
            "Geographical Distribution", 
            "Treatment Outcomes"
        ])
        
        with tab1:
            st.plotly_chart(
                analytics.create_resistance_trend_chart(tb_data),
                use_container_width=True
            )
        
        with tab2:
            st.plotly_chart(
                analytics.create_geo_distribution_chart(tb_data),
                use_container_width=True
            )
        
        with tab3:
            st.plotly_chart(
                analytics.create_treatment_outcomes_chart(tb_data),
                use_container_width=True
            )
        
        # Top resistance patterns
        st.subheader("Top Resistance Patterns")
        top_patterns = analytics.get_top_resistance_patterns(tb_data)
        
        if not top_patterns.empty:
            fig = px.pie(
                top_patterns, 
                values='count', 
                names='pattern',
                title='Distribution of Resistance Patterns',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No resistance pattern data available.")
    else:
        st.info("No data available for visualizations. Import data using the Data Import/Export module.")
    
    # Close database connection
    conn.close()
