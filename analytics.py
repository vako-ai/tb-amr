import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import datetime, timedelta
import io
import base64
from db_manager import get_sqlalchemy_engine

def load_tb_data(conn):
    """
    Load TB data from the database for analytics
    
    Parameters:
    conn: PostgreSQL database connection
    
    Returns:
    pandas.DataFrame: TB data for analysis
    """
    try:
        # Use SQLAlchemy engine for pandas compatibility
        engine = get_sqlalchemy_engine()
        query = "SELECT * FROM tb_cases"
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        print(f"Error loading TB data: {e}")
        return pd.DataFrame()

def create_resistance_trend_chart(df):
    """
    Create a trend chart of resistance patterns over time
    
    Parameters:
    df (pandas.DataFrame): DataFrame with TB data
    
    Returns:
    plotly.graph_objects.Figure: Trend chart
    """
    # Ensure diagnosis_date is datetime
    if 'diagnosis_date' in df.columns:
        df['diagnosis_date'] = pd.to_datetime(df['diagnosis_date'])
        df['month'] = df['diagnosis_date'].dt.strftime('%Y-%m')
        
        # Group data by month and TB type
        monthly_data = df.groupby(['month', 'tb_type']).size().reset_index(name='count')
        
        # Create line chart using Plotly
        fig = px.line(
            monthly_data, 
            x='month', 
            y='count', 
            color='tb_type',
            markers=True,
            title='TB Resistance Trends Over Time',
            labels={'month': 'Month', 'count': 'Number of Cases', 'tb_type': 'TB Type'}
        )
        
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Number of Cases',
            legend_title='TB Type',
            hovermode='x unified'
        )
        
        return fig
    else:
        # Create empty figure if data is not available
        fig = go.Figure()
        fig.update_layout(
            title='TB Resistance Trends Over Time (No Data Available)',
            xaxis_title='Month',
            yaxis_title='Number of Cases'
        )
        return fig

def create_geo_distribution_chart(df):
    """
    Create a geographical distribution chart of TB cases
    
    Parameters:
    df (pandas.DataFrame): DataFrame with TB data
    
    Returns:
    plotly.graph_objects.Figure: Geographical distribution chart
    """
    if 'location' in df.columns and 'tb_type' in df.columns and not df.empty:
        # Group data by location and TB type
        geo_data = df.groupby(['location', 'tb_type']).size().reset_index(name='count')
        
        # Create bar chart using Plotly
        fig = px.bar(
            geo_data, 
            x='location', 
            y='count', 
            color='tb_type',
            title='Geographical Distribution of TB Cases',
            labels={'location': 'Location', 'count': 'Number of Cases', 'tb_type': 'TB Type'}
        )
        
        fig.update_layout(
            xaxis_title='Location',
            yaxis_title='Number of Cases',
            legend_title='TB Type',
            xaxis={'categoryorder':'total descending'}
        )
        
        return fig
    else:
        # Create empty figure if data is not available
        fig = go.Figure()
        fig.update_layout(
            title='Geographical Distribution of TB Cases (No Data Available)',
            xaxis_title='Location',
            yaxis_title='Number of Cases'
        )
        return fig

def create_treatment_outcomes_chart(df):
    """
    Create a chart showing treatment outcomes by TB type
    
    Parameters:
    df (pandas.DataFrame): DataFrame with TB data
    
    Returns:
    plotly.graph_objects.Figure: Treatment outcomes chart
    """
    if 'treatment_outcome' in df.columns and 'tb_type' in df.columns and not df.empty:
        # Remove rows with null treatment outcomes
        df_filtered = df[df['treatment_outcome'].notna()]
        
        if not df_filtered.empty:
            # Group data by TB type and treatment outcome
            outcome_data = df_filtered.groupby(['tb_type', 'treatment_outcome']).size().reset_index(name='count')
            
            # Create grouped bar chart using Plotly
            fig = px.bar(
                outcome_data, 
                x='tb_type', 
                y='count', 
                color='treatment_outcome',
                title='Treatment Outcomes by TB Type',
                labels={'tb_type': 'TB Type', 'count': 'Number of Cases', 'treatment_outcome': 'Outcome'}
            )
            
            fig.update_layout(
                xaxis_title='TB Type',
                yaxis_title='Number of Cases',
                legend_title='Treatment Outcome',
                barmode='group'
            )
            
            return fig
    
    # Create empty figure if data is not available
    fig = go.Figure()
    fig.update_layout(
        title='Treatment Outcomes by TB Type (No Data Available)',
        xaxis_title='TB Type',
        yaxis_title='Number of Cases'
    )
    return fig

def create_drug_resistance_heatmap(df):
    """
    Create a heatmap showing resistance to different drugs
    
    Parameters:
    df (pandas.DataFrame): DataFrame with TB data
    
    Returns:
    plotly.graph_objects.Figure: Drug resistance heatmap
    """
    # Check if resistance data columns exist
    resistance_cols = [col for col in df.columns if ('resistant' in col.lower() or 'resistance' in col.lower()) and col != 'resistance_pattern']
    
    if resistance_cols and not df.empty:
        # Create a pivot table for resistance patterns
        resistance_data = df[resistance_cols].apply(pd.value_counts).fillna(0)
        
        # Create heatmap using Plotly
        fig = px.imshow(
            resistance_data,
            labels=dict(x="Drug", y="Resistance Status", color="Count"),
            x=resistance_data.columns,
            y=resistance_data.index,
            aspect="auto",
            title='Drug Resistance Patterns'
        )
        
        fig.update_layout(
            xaxis_title='Drug',
            yaxis_title='Resistance Status',
        )
        
        return fig
    else:
        # Create empty figure if data is not available
        fig = go.Figure()
        fig.update_layout(
            title='Drug Resistance Patterns (No Data Available)',
            xaxis_title='Drug',
            yaxis_title='Resistance Status'
        )
        return fig

def calculate_key_metrics(df):
    """
    Calculate key metrics from TB data
    
    Parameters:
    df (pandas.DataFrame): DataFrame with TB data
    
    Returns:
    dict: Key metrics
    """
    metrics = {}
    
    if not df.empty:
        # Total cases
        metrics['total_cases'] = len(df)
        
        # Cases by TB type
        if 'tb_type' in df.columns:
            tb_type_counts = df['tb_type'].value_counts().to_dict()
            for tb_type, count in tb_type_counts.items():
                metrics[f'{tb_type}_count'] = count
            
            # Calculate MDR-TB percentage
            if 'MDR-TB' in tb_type_counts:
                metrics['mdr_tb_percentage'] = round(tb_type_counts.get('MDR-TB', 0) / metrics['total_cases'] * 100, 2)
            else:
                metrics['mdr_tb_percentage'] = 0
        
        # Treatment success rate
        if 'treatment_outcome' in df.columns:
            success_outcomes = ['Cured', 'Treatment Completed']
            success_count = df[df['treatment_outcome'].isin(success_outcomes)].shape[0]
            completed_cases = df[df['treatment_outcome'].notna()].shape[0]
            
            if completed_cases > 0:
                metrics['treatment_success_rate'] = round(success_count / completed_cases * 100, 2)
            else:
                metrics['treatment_success_rate'] = 0
        
        # Calculate average treatment duration
        if 'treatment_start_date' in df.columns and 'treatment_end_date' in df.columns:
            df['treatment_start_date'] = pd.to_datetime(df['treatment_start_date'], errors='coerce')
            df['treatment_end_date'] = pd.to_datetime(df['treatment_end_date'], errors='coerce')
            
            # Calculate duration for rows with valid dates
            valid_duration = df.dropna(subset=['treatment_start_date', 'treatment_end_date'])
            
            if not valid_duration.empty:
                duration = (valid_duration['treatment_end_date'] - valid_duration['treatment_start_date']).dt.days
                metrics['avg_treatment_duration_days'] = round(duration.mean(), 1)
            else:
                metrics['avg_treatment_duration_days'] = 0
    else:
        # Default metrics if data is empty
        metrics = {
            'total_cases': 0,
            'mdr_tb_percentage': 0,
            'treatment_success_rate': 0,
            'avg_treatment_duration_days': 0
        }
    
    return metrics

def get_recent_trends(df):
    """
    Get recent trends in TB data
    
    Parameters:
    df (pandas.DataFrame): DataFrame with TB data
    
    Returns:
    dict: Recent trends information
    """
    trends = {}
    
    if not df.empty and 'diagnosis_date' in df.columns:
        df['diagnosis_date'] = pd.to_datetime(df['diagnosis_date'], errors='coerce')
        
        # Filter for data with valid dates
        df_dates = df.dropna(subset=['diagnosis_date'])
        
        if not df_dates.empty:
            # Get last 6 months of data
            today = datetime.now()
            six_months_ago = today - timedelta(days=180)
            
            recent_df = df_dates[df_dates['diagnosis_date'] >= six_months_ago]
            previous_df = df_dates[(df_dates['diagnosis_date'] >= six_months_ago - timedelta(days=180)) & 
                                  (df_dates['diagnosis_date'] < six_months_ago)]
            
            # Calculate trend metrics
            recent_count = len(recent_df)
            previous_count = len(previous_df)
            
            if previous_count > 0:
                case_change_pct = round((recent_count - previous_count) / previous_count * 100, 2)
            else:
                case_change_pct = 0
            
            trends['recent_cases'] = recent_count
            trends['case_change_percentage'] = case_change_pct
            
            # Calculate MDR-TB trends if tb_type exists
            if 'tb_type' in df.columns:
                recent_mdr = recent_df[recent_df['tb_type'] == 'MDR-TB'].shape[0]
                previous_mdr = previous_df[previous_df['tb_type'] == 'MDR-TB'].shape[0]
                
                if previous_mdr > 0:
                    mdr_change_pct = round((recent_mdr - previous_mdr) / previous_mdr * 100, 2)
                else:
                    mdr_change_pct = 0 if recent_mdr == 0 else 100
                
                trends['recent_mdr_cases'] = recent_mdr
                trends['mdr_change_percentage'] = mdr_change_pct
    
    if not trends:
        # Default trends if data is insufficient
        trends = {
            'recent_cases': 0,
            'case_change_percentage': 0,
            'recent_mdr_cases': 0,
            'mdr_change_percentage': 0
        }
    
    return trends

def get_top_resistance_patterns(df, top_n=5):
    """
    Get the top resistance patterns from the data
    
    Parameters:
    df (pandas.DataFrame): DataFrame with TB data
    top_n (int): Number of top patterns to return
    
    Returns:
    pandas.DataFrame: Top resistance patterns
    """
    if not df.empty and 'resistance_pattern' in df.columns:
        # Count patterns
        pattern_counts = df['resistance_pattern'].value_counts().reset_index()
        pattern_counts.columns = ['pattern', 'count']
        
        # Calculate percentage
        pattern_counts['percentage'] = round(pattern_counts['count'] / pattern_counts['count'].sum() * 100, 2)
        
        # Get top patterns
        top_patterns = pattern_counts.head(top_n)
        return top_patterns
    else:
        return pd.DataFrame(columns=['pattern', 'count', 'percentage'])

def generate_report(df, conn, report_type='summary'):
    """
    Generate a report based on TB data
    
    Parameters:
    df (pandas.DataFrame): DataFrame with TB data
    conn: PostgreSQL database connection (not used directly, kept for backward compatibility)
    report_type (str): Type of report to generate
    
    Returns:
    str: HTML report content
    """
    if not df.empty:
        # Calculate metrics
        metrics = calculate_key_metrics(df)
        trends = get_recent_trends(df)
        
        # Generate report HTML
        report_html = f"""
        <html>
        <head>
            <title>TB Resistance Hub - {report_type.title()} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #0083B8; }}
                .metric-box {{ 
                    background-color: #f8f9fa; 
                    border: 1px solid #ddd; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px;
                }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #0083B8; }}
                .metric-label {{ font-size: 14px; color: #555; }}
                .trend-up {{ color: #28a745; }}
                .trend-down {{ color: #dc3545; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>TB Resistance Hub - {report_type.title()} Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>Key Metrics</h2>
            <div style="display: flex; flex-wrap: wrap;">
                <div class="metric-box" style="flex: 1; min-width: 200px;">
                    <div class="metric-value">{metrics['total_cases']}</div>
                    <div class="metric-label">Total Cases</div>
                </div>
                <div class="metric-box" style="flex: 1; min-width: 200px;">
                    <div class="metric-value">{metrics.get('mdr_tb_percentage', 0)}%</div>
                    <div class="metric-label">MDR-TB Percentage</div>
                </div>
                <div class="metric-box" style="flex: 1; min-width: 200px;">
                    <div class="metric-value">{metrics.get('treatment_success_rate', 0)}%</div>
                    <div class="metric-label">Treatment Success Rate</div>
                </div>
            </div>
            
            <h2>Recent Trends</h2>
            <div style="display: flex; flex-wrap: wrap;">
                <div class="metric-box" style="flex: 1; min-width: 200px;">
                    <div class="metric-value">{trends.get('recent_cases', 0)}</div>
                    <div class="metric-label">Recent Cases (6 months)</div>
                    <div class="trend {'trend-up' if trends.get('case_change_percentage', 0) >= 0 else 'trend-down'}">
                        {trends.get('case_change_percentage', 0)}% {'increase' if trends.get('case_change_percentage', 0) >= 0 else 'decrease'}
                    </div>
                </div>
                <div class="metric-box" style="flex: 1; min-width: 200px;">
                    <div class="metric-value">{trends.get('recent_mdr_cases', 0)}</div>
                    <div class="metric-label">Recent MDR-TB Cases</div>
                    <div class="trend {'trend-up' if trends.get('mdr_change_percentage', 0) >= 0 else 'trend-down'}">
                        {trends.get('mdr_change_percentage', 0)}% {'increase' if trends.get('mdr_change_percentage', 0) >= 0 else 'decrease'}
                    </div>
                </div>
            </div>
        """
        
        # Add top resistance patterns
        top_patterns = get_top_resistance_patterns(df)
        if not top_patterns.empty:
            report_html += """
            <h2>Top Resistance Patterns</h2>
            <table>
                <tr>
                    <th>Pattern</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            """
            
            for _, row in top_patterns.iterrows():
                report_html += f"""
                <tr>
                    <td>{row['pattern']}</td>
                    <td>{row['count']}</td>
                    <td>{row['percentage']}%</td>
                </tr>
                """
            
            report_html += "</table>"
        
        # Add detailed analysis if required
        if report_type == 'detailed':
            # Add geographical distribution
            report_html += """
            <h2>Geographical Distribution</h2>
            <p>Please refer to the analytics dashboard for interactive visualizations of geographical distribution.</p>
            
            <h2>Recommendations</h2>
            <ul>
                <li>Focus on high-incidence regions for targeted interventions</li>
                <li>Monitor emerging resistance patterns, especially in XDR-TB cases</li>
                <li>Implement antibiotic stewardship programs in areas with rising MDR-TB cases</li>
                <li>Review treatment protocols for cases with lower success rates</li>
            </ul>
            """
        
        # Close HTML document
        report_html += """
        </body>
        </html>
        """
        
        return report_html
    else:
        # Return basic report if no data
        return f"""
        <html>
        <head>
            <title>TB Resistance Hub - {report_type.title()} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #0083B8; }}
            </style>
        </head>
        <body>
            <h1>TB Resistance Hub - {report_type.title()} Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>No Data Available</h2>
            <p>There is currently no data available to generate a report. Please import TB data via the Data Import/Export module.</p>
        </body>
        </html>
        """
