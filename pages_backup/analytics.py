import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import analytics
import io
import json
from db_manager import get_connection

def show():
    """Display the analytics page"""
    st.title("TB Resistance Analytics")
    
    # Connect to the PostgreSQL database
    conn = get_connection()
    
    # Load data for analytics
    tb_data = analytics.load_tb_data(conn)
    
    if tb_data.empty:
        st.info("No data available for analysis. Import data using the Data Import/Export module.")
        conn.close()
        return
    
    # Create sections for different analytics features
    tab1, tab2, tab3, tab4 = st.tabs([
        "Resistance Patterns", 
        "Treatment Outcomes", 
        "Geographical Analysis",
        "Reports"
    ])
    
    with tab1:
        show_resistance_analysis(tb_data, conn)
    
    with tab2:
        show_treatment_analysis(tb_data, conn)
    
    with tab3:
        show_geographical_analysis(tb_data, conn)
    
    with tab4:
        show_report_generation(tb_data, conn)
    
    # Close database connection
    conn.close()

def show_resistance_analysis(tb_data, conn):
    """Display resistance pattern analysis"""
    st.header("Resistance Pattern Analysis")
    
    # Time series of TB types
    st.subheader("TB Resistance Trends Over Time")
    resistance_trend_chart = analytics.create_resistance_trend_chart(tb_data)
    st.plotly_chart(resistance_trend_chart, use_container_width=True)
    
    # Drug resistance heatmap
    st.subheader("Drug Resistance Patterns")
    drug_resistance_heatmap = analytics.create_drug_resistance_heatmap(tb_data)
    st.plotly_chart(drug_resistance_heatmap, use_container_width=True)
    
    # Top resistance patterns
    st.subheader("Top Resistance Patterns")
    top_patterns = analytics.get_top_resistance_patterns(tb_data, top_n=10)
    
    if not top_patterns.empty:
        # Create horizontal bar chart
        fig = px.bar(
            top_patterns,
            y='pattern',
            x='count',
            orientation='h',
            text='percentage',
            labels={'pattern': 'Resistance Pattern', 'count': 'Number of Cases'},
            title='Top Resistance Patterns'
        )
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create data table with resistances
        st.dataframe(
            top_patterns,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No resistance pattern data available")
    
    # Resistance pattern emergence over time
    if 'resistance_pattern' in tb_data.columns and 'diagnosis_date' in tb_data.columns:
        st.subheader("Emergence of Resistance Patterns Over Time")
        
        # Convert diagnosis_date to datetime
        tb_data['diagnosis_date'] = pd.to_datetime(tb_data['diagnosis_date'])
        
        # Get top patterns
        top_n_patterns = top_patterns['pattern'].tolist()[:5]  # Use top 5 patterns
        
        if top_n_patterns:
            # Filter data for top patterns
            filtered_data = tb_data[tb_data['resistance_pattern'].isin(top_n_patterns)]
            
            if not filtered_data.empty:
                # Group by month and pattern
                filtered_data['month'] = filtered_data['diagnosis_date'].dt.strftime('%Y-%m')
                monthly_pattern_data = filtered_data.groupby(['month', 'resistance_pattern']).size().reset_index(name='count')
                
                # Create line chart
                fig = px.line(
                    monthly_pattern_data,
                    x='month',
                    y='count',
                    color='resistance_pattern',
                    markers=True,
                    title='Emergence of Resistance Patterns Over Time',
                    labels={'month': 'Month', 'count': 'Number of Cases', 'resistance_pattern': 'Pattern'}
                )
                
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Number of Cases',
                    legend_title='Resistance Pattern'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough temporal data for resistance pattern analysis")
        else:
            st.info("No significant resistance patterns found")

def show_treatment_analysis(tb_data, conn):
    """Display treatment outcome analysis"""
    st.header("Treatment Outcome Analysis")
    
    # Treatment outcomes by TB type
    st.subheader("Treatment Outcomes by TB Type")
    treatment_outcomes_chart = analytics.create_treatment_outcomes_chart(tb_data)
    st.plotly_chart(treatment_outcomes_chart, use_container_width=True)
    
    # Treatment success rate over time
    if 'treatment_outcome' in tb_data.columns and 'diagnosis_date' in tb_data.columns:
        st.subheader("Treatment Success Rate Over Time")
        
        # Convert dates
        tb_data['diagnosis_date'] = pd.to_datetime(tb_data['diagnosis_date'])
        
        # Filter for cases with treatment outcomes
        outcome_data = tb_data[tb_data['treatment_outcome'].notna()]
        
        if not outcome_data.empty:
            # Define success outcomes
            success_outcomes = ['Cured', 'Treatment Completed']
            
            # Add success indicator
            outcome_data['treatment_success'] = outcome_data['treatment_outcome'].isin(success_outcomes)
            
            # Group by month
            outcome_data['month'] = outcome_data['diagnosis_date'].dt.strftime('%Y-%m')
            
            # Calculate success rate by month
            monthly_success = outcome_data.groupby('month')['treatment_success'].agg(
                ['mean', 'count']
            ).reset_index()
            
            monthly_success['success_rate'] = monthly_success['mean'] * 100
            
            # Create line chart
            fig = px.line(
                monthly_success,
                x='month',
                y='success_rate',
                markers=True,
                title='Treatment Success Rate Over Time',
                labels={'month': 'Month', 'success_rate': 'Success Rate (%)'}
            )
            
            # Add case count as hover data
            fig.update_traces(
                hovertemplate='Month: %{x}<br>Success Rate: %{y:.1f}%<br>Cases: %{customdata}<extra></extra>',
                customdata=monthly_success['count']
            )
            
            fig.update_layout(
                xaxis_title='Month',
                yaxis_title='Success Rate (%)',
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough treatment outcome data for temporal analysis")
    
    # Treatment duration analysis
    if 'treatment_start_date' in tb_data.columns and 'treatment_end_date' in tb_data.columns:
        st.subheader("Treatment Duration Analysis")
        
        # Convert dates
        tb_data['treatment_start_date'] = pd.to_datetime(tb_data['treatment_start_date'], errors='coerce')
        tb_data['treatment_end_date'] = pd.to_datetime(tb_data['treatment_end_date'], errors='coerce')
        
        # Calculate duration
        duration_data = tb_data.dropna(subset=['treatment_start_date', 'treatment_end_date'])
        
        if not duration_data.empty:
            duration_data['treatment_duration_days'] = (
                duration_data['treatment_end_date'] - duration_data['treatment_start_date']
            ).dt.days
            
            # Group by TB type
            if 'tb_type' in duration_data.columns:
                duration_by_type = duration_data.groupby('tb_type')['treatment_duration_days'].agg(
                    ['mean', 'median', 'std', 'count']
                ).reset_index()
                
                # Round values
                for col in ['mean', 'median', 'std']:
                    duration_by_type[col] = duration_by_type[col].round(1)
                
                # Create bar chart for average duration
                fig = px.bar(
                    duration_by_type,
                    x='tb_type',
                    y='mean',
                    error_y='std',
                    title='Average Treatment Duration by TB Type',
                    labels={'tb_type': 'TB Type', 'mean': 'Average Duration (days)'}
                )
                
                fig.update_layout(
                    xaxis_title='TB Type',
                    yaxis_title='Average Duration (days)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display data table
                duration_by_type.columns = ['TB Type', 'Mean (days)', 'Median (days)', 'Std Dev (days)', 'Count']
                
                st.dataframe(
                    duration_by_type,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                # Overall duration stats
                mean_duration = duration_data['treatment_duration_days'].mean()
                median_duration = duration_data['treatment_duration_days'].median()
                
                col1, col2 = st.columns(2)
                col1.metric("Average Treatment Duration", f"{mean_duration:.1f} days")
                col2.metric("Median Treatment Duration", f"{median_duration:.1f} days")
                
                # Create histogram
                fig = px.histogram(
                    duration_data,
                    x='treatment_duration_days',
                    title='Distribution of Treatment Duration',
                    labels={'treatment_duration_days': 'Duration (days)'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough treatment duration data for analysis")

def show_geographical_analysis(tb_data, conn):
    """Display geographical analysis"""
    st.header("Geographical Distribution Analysis")
    
    # Geographical distribution chart
    st.subheader("TB Cases by Location")
    geo_distribution_chart = analytics.create_geo_distribution_chart(tb_data)
    st.plotly_chart(geo_distribution_chart, use_container_width=True)
    
    # More detailed geographical analysis
    if 'location' in tb_data.columns:
        # Distribution of resistance patterns by location
        st.subheader("Resistance Patterns by Location")
        
        if 'resistance_pattern' in tb_data.columns:
            # Get top resistance patterns
            top_patterns = analytics.get_top_resistance_patterns(tb_data, top_n=5)
            top_pattern_list = top_patterns['pattern'].tolist()
            
            # Filter for top patterns and group by location
            if top_pattern_list:
                pattern_by_location = tb_data[tb_data['resistance_pattern'].isin(top_pattern_list)]
                pattern_by_location = pattern_by_location.groupby(['location', 'resistance_pattern']).size().reset_index(name='count')
                
                # Create grouped bar chart
                fig = px.bar(
                    pattern_by_location,
                    x='location',
                    y='count',
                    color='resistance_pattern',
                    title='Top Resistance Patterns by Location',
                    labels={'location': 'Location', 'count': 'Number of Cases', 'resistance_pattern': 'Pattern'}
                )
                
                fig.update_layout(
                    xaxis_title='Location',
                    yaxis_title='Number of Cases',
                    xaxis={'categoryorder': 'total descending'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Treatment success by location
        st.subheader("Treatment Success Rate by Location")
        
        if 'treatment_outcome' in tb_data.columns:
            # Define success outcomes
            success_outcomes = ['Cured', 'Treatment Completed']
            
            # Filter for cases with treatment outcomes
            outcome_data = tb_data[tb_data['treatment_outcome'].notna()]
            
            if not outcome_data.empty:
                # Calculate success rate by location
                outcome_data['treatment_success'] = outcome_data['treatment_outcome'].isin(success_outcomes)
                
                success_by_location = outcome_data.groupby('location')['treatment_success'].agg(
                    ['mean', 'count']
                ).reset_index()
                
                success_by_location['success_rate'] = success_by_location['mean'] * 100
                
                # Only include locations with sufficient data
                min_cases = 5  # Minimum cases for inclusion
                filtered_locations = success_by_location[success_by_location['count'] >= min_cases]
                
                if not filtered_locations.empty:
                    # Create bar chart
                    fig = px.bar(
                        filtered_locations,
                        x='location',
                        y='success_rate',
                        text='count',
                        title='Treatment Success Rate by Location',
                        labels={'location': 'Location', 'success_rate': 'Success Rate (%)', 'count': 'Cases'}
                    )
                    
                    fig.update_traces(textposition='outside')
                    fig.update_layout(
                        xaxis_title='Location',
                        yaxis_title='Success Rate (%)',
                        yaxis=dict(range=[0, 100])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Create data table
                    success_table = filtered_locations.copy()
                    success_table['success_rate'] = success_table['success_rate'].round(1)
                    success_table.columns = ['Location', 'Success Proportion', 'Cases', 'Success Rate (%)']
                    
                    st.dataframe(
                        success_table[['Location', 'Success Rate (%)', 'Cases']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Not enough location-specific treatment outcome data for analysis")
            else:
                st.info("Not enough treatment outcome data for geographical analysis")

def show_report_generation(tb_data, conn):
    """Display report generation options"""
    st.header("TB Resistance Reports")
    
    # Report type selection
    report_type = st.radio(
        "Select Report Type",
        ["Summary Report", "Detailed Analysis Report"]
    )
    
    # Generate report
    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            # Generate HTML report
            report_html = analytics.generate_report(
                tb_data, 
                conn, 
                "detailed" if report_type == "Detailed Analysis Report" else "summary"
            )
            
            # Display report preview
            st.subheader("Report Preview")
            st.components.v1.html(report_html, height=600)
            
            # Download option
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"tb_resistance_{report_type.lower().replace(' ', '_')}_{timestamp}.html"
            
            st.download_button(
                "Download Report",
                data=report_html,
                file_name=report_filename,
                mime="text/html"
            )
    
    # Custom metric tracking
    st.subheader("Track Key Metrics")
    
    # Get key metrics
    metrics = analytics.calculate_key_metrics(tb_data)
    trends = analytics.get_recent_trends(tb_data)
    
    # Display metric selector
    metrics_to_track = st.multiselect(
        "Select Metrics to Track",
        [
            "Total Cases",
            "MDR-TB Percentage",
            "Treatment Success Rate",
            "XDR-TB Cases",
            "Average Treatment Duration"
        ],
        default=["Total Cases", "MDR-TB Percentage", "Treatment Success Rate"]
    )
    
    if metrics_to_track:
        st.subheader("Selected Metrics")
        
        # Create metric dashboard
        cols = st.columns(len(metrics_to_track))
        
        for i, metric in enumerate(metrics_to_track):
            with cols[i]:
                if metric == "Total Cases":
                    st.metric(
                        "Total Cases", 
                        metrics.get('total_cases', 0),
                        delta=f"{trends.get('case_change_percentage', 0)}%"
                    )
                
                elif metric == "MDR-TB Percentage":
                    st.metric(
                        "MDR-TB Percentage", 
                        f"{metrics.get('mdr_tb_percentage', 0)}%",
                        delta=None
                    )
                
                elif metric == "Treatment Success Rate":
                    st.metric(
                        "Success Rate", 
                        f"{metrics.get('treatment_success_rate', 0)}%",
                        delta=None
                    )
                
                elif metric == "XDR-TB Cases":
                    xdr_cases = metrics.get('XDR-TB_count', 0)
                    st.metric(
                        "XDR-TB Cases", 
                        xdr_cases,
                        delta=None
                    )
                
                elif metric == "Average Treatment Duration":
                    st.metric(
                        "Avg Treatment", 
                        f"{metrics.get('avg_treatment_duration_days', 0)} days",
                        delta=None
                    )
        
        # Create metrics export
        if st.button("Export Metrics"):
            # Create metrics dictionary
            export_metrics = {
                "timestamp": datetime.now().isoformat(),
                "metrics": {}
            }
            
            for metric in metrics_to_track:
                if metric == "Total Cases":
                    export_metrics["metrics"]["total_cases"] = metrics.get('total_cases', 0)
                elif metric == "MDR-TB Percentage":
                    export_metrics["metrics"]["mdr_tb_percentage"] = metrics.get('mdr_tb_percentage', 0)
                elif metric == "Treatment Success Rate":
                    export_metrics["metrics"]["treatment_success_rate"] = metrics.get('treatment_success_rate', 0)
                elif metric == "XDR-TB Cases":
                    export_metrics["metrics"]["xdr_tb_cases"] = metrics.get('XDR-TB_count', 0)
                elif metric == "Average Treatment Duration":
                    export_metrics["metrics"]["avg_treatment_duration_days"] = metrics.get('avg_treatment_duration_days', 0)
            
            # Convert to JSON
            metrics_json = json.dumps(export_metrics, indent=2)
            
            # Create download button
            st.download_button(
                "Download Metrics JSON",
                data=metrics_json,
                file_name=f"tb_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
