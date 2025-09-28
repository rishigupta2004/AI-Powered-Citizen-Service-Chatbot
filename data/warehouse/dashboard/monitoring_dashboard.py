"""
Data Warehouse Monitoring Dashboard

A simple web-based dashboard for monitoring the data warehouse health,
ETL processes, and key metrics.

Run with: python -m streamlit run data/warehouse/dashboard/monitoring_dashboard.py
"""

import streamlit as st
import asyncio
import asyncpg
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data.warehouse.config.warehouse_config import WarehouseConfig

# Page configuration
st.set_page_config(
    page_title="Citizen Services Data Warehouse Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache configuration
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_warehouse_config():
    """Get warehouse configuration"""
    return WarehouseConfig('development')

@st.cache_data(ttl=300)
async def get_db_connection():
    """Get database connection"""
    config = get_warehouse_config()
    wh_config = config.get_warehouse_db_config()
    return await asyncpg.connect(**wh_config)

# Data fetching functions
@st.cache_data(ttl=300)
def fetch_etl_status():
    """Fetch ETL process status"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _fetch():
            conn = await get_db_connection()
            query = """
            SELECT 
                process_name,
                status,
                message,
                records_processed,
                processing_time_seconds,
                created_at
            FROM dwh.etl_log 
            ORDER BY created_at DESC 
            LIMIT 20
            """
            rows = await conn.fetch(query)
            await conn.close()
            return [dict(row) for row in rows]
        
        return loop.run_until_complete(_fetch())
    except Exception as e:
        st.error(f"Error fetching ETL status: {str(e)}")
        return []

@st.cache_data(ttl=300)
def fetch_service_performance():
    """Fetch service performance metrics"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _fetch():
            conn = await get_db_connection()
            query = """
            SELECT * FROM dwh.dm_service_performance_monthly 
            WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
            AND month >= EXTRACT(MONTH FROM CURRENT_DATE) - 2
            ORDER BY year DESC, month DESC, total_queries DESC
            LIMIT 50
            """
            rows = await conn.fetch(query)
            await conn.close()
            return pd.DataFrame([dict(row) for row in rows])
        
        return loop.run_until_complete(_fetch())
    except Exception as e:
        st.error(f"Error fetching service performance: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_daily_operations():
    """Fetch daily operations summary"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _fetch():
            conn = await get_db_connection()
            query = """
            SELECT * FROM dwh.dm_daily_operations 
            WHERE full_date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY full_date DESC
            """
            rows = await conn.fetch(query)
            await conn.close()
            return pd.DataFrame([dict(row) for row in rows])
        
        return loop.run_until_complete(_fetch())
    except Exception as e:
        st.error(f"Error fetching daily operations: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_data_quality():
    """Fetch data quality metrics"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _fetch():
            conn = await get_db_connection()
            query = """
            SELECT * FROM dwh.dm_data_quality_sources 
            WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
            AND month >= EXTRACT(MONTH FROM CURRENT_DATE) - 1
            ORDER BY overall_quality_score DESC
            """
            rows = await conn.fetch(query)
            await conn.close()
            return pd.DataFrame([dict(row) for row in rows])
        
        return loop.run_until_complete(_fetch())
    except Exception as e:
        st.error(f"Error fetching data quality: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_performance_alerts():
    """Fetch performance alerts"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _fetch():
            conn = await get_db_connection()
            query = "SELECT * FROM dwh.dm_performance_alerts ORDER BY alert_severity"
            rows = await conn.fetch(query)
            await conn.close()
            return pd.DataFrame([dict(row) for row in rows])
        
        return loop.run_until_complete(_fetch())
    except Exception as e:
        st.error(f"Error fetching performance alerts: {str(e)}")
        return pd.DataFrame()

# Dashboard UI
def main():
    """Main dashboard function"""
    
    # Header
    st.title("🏛️ Citizen Services Data Warehouse Dashboard")
    st.markdown("Monitor your data warehouse health, ETL processes, and service performance")
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Environment info
    config = get_warehouse_config()
    st.sidebar.info(f"Environment: {config.environment}")
    st.sidebar.info(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🔄 ETL Status", 
        "🎯 Service Performance", 
        "📈 Operations", 
        "🔍 Data Quality"
    ])
    
    with tab1:
        show_overview()
    
    with tab2:
        show_etl_status()
    
    with tab3:
        show_service_performance()
    
    with tab4:
        show_operations()
    
    with tab5:
        show_data_quality()

def show_overview():
    """Show dashboard overview"""
    st.header("📊 Data Warehouse Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch basic metrics
    daily_ops = fetch_daily_operations()
    if not daily_ops.empty:
        latest_day = daily_ops.iloc[0]
        
        with col1:
            st.metric(
                "Total Daily Queries",
                f"{latest_day['total_daily_queries']:,}",
                delta=None
            )
        
        with col2:
            st.metric(
                "Success Rate",
                f"{latest_day['daily_success_rate']:.1f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                "Avg Satisfaction",
                f"{latest_day['daily_avg_satisfaction']:.2f}/5",
                delta=None
            )
        
        with col4:
            st.metric(
                "Active Services",
                f"{latest_day['active_services']}",
                delta=None
            )
    
    # Performance alerts
    alerts = fetch_performance_alerts()
    if not alerts.empty:
        st.subheader("🚨 Performance Alerts")
        
        critical_alerts = alerts[alerts['alert_severity'] == 'Critical']
        warning_alerts = alerts[alerts['alert_severity'] == 'Warning']
        
        if not critical_alerts.empty:
            st.error(f"🔴 {len(critical_alerts)} Critical Alerts")
            for _, alert in critical_alerts.head(3).iterrows():
                st.error(f"**{alert['service_name']}**: {alert['alert_type']}")
        
        if not warning_alerts.empty:
            st.warning(f"🟡 {len(warning_alerts)} Warning Alerts")
            for _, alert in warning_alerts.head(3).iterrows():
                st.warning(f"**{alert['service_name']}**: {alert['alert_type']}")
    
    # Recent ETL status
    etl_status = fetch_etl_status()
    if etl_status:
        st.subheader("🔄 Recent ETL Activities")
        
        recent_etl = etl_status[:5]
        for etl in recent_etl:
            status_icon = "✅" if etl['status'] == 'SUCCESS' else "❌"
            st.write(f"{status_icon} **{etl['process_name']}** - {etl['message']} ({etl['created_at'].strftime('%H:%M:%S')})")

def show_etl_status():
    """Show ETL process status"""
    st.header("🔄 ETL Process Status")
    
    etl_data = fetch_etl_status()
    if not etl_data:
        st.warning("No ETL status data available")
        return
    
    # Convert to DataFrame
    etl_df = pd.DataFrame(etl_data)
    
    # ETL success rate
    success_rate = (etl_df['status'] == 'SUCCESS').mean() * 100
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("ETL Success Rate", f"{success_rate:.1f}%")
    
    with col2:
        avg_processing_time = etl_df['processing_time_seconds'].mean()
        st.metric("Avg Processing Time", f"{avg_processing_time:.1f}s")
    
    # ETL status chart
    status_counts = etl_df['status'].value_counts()
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="ETL Process Status Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent ETL processes
    st.subheader("Recent ETL Processes")
    
    display_df = etl_df[['process_name', 'status', 'records_processed', 'processing_time_seconds', 'created_at']].copy()
    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    st.dataframe(
        display_df,
        column_config={
            "process_name": "Process",
            "status": "Status",
            "records_processed": "Records",
            "processing_time_seconds": "Time (s)",
            "created_at": "Timestamp"
        },
        use_container_width=True
    )

def show_service_performance():
    """Show service performance metrics"""
    st.header("🎯 Service Performance")
    
    perf_data = fetch_service_performance()
    if perf_data.empty:
        st.warning("No service performance data available")
        return
    
    # Top performing services
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Services by Usage")
        top_services = perf_data.nlargest(10, 'total_queries')
        fig = px.bar(
            top_services,
            x='total_queries',
            y='service_name',
            orientation='h',
            title="Most Used Services"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top Services by Satisfaction")
        top_satisfaction = perf_data.nlargest(10, 'avg_satisfaction')
        fig = px.bar(
            top_satisfaction,
            x='avg_satisfaction',
            y='service_name',
            orientation='h',
            title="Highest Satisfaction Services"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Service category performance
    if 'service_category' in perf_data.columns:
        st.subheader("Performance by Category")
        category_perf = perf_data.groupby('service_category').agg({
            'total_queries': 'sum',
            'avg_satisfaction': 'mean',
            'success_rate_percent': 'mean'
        }).reset_index()
        
        fig = px.scatter(
            category_perf,
            x='total_queries',
            y='avg_satisfaction',
            size='success_rate_percent',
            hover_data=['service_category'],
            title="Service Category Performance"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed service table
    st.subheader("Detailed Service Performance")
    
    display_columns = [
        'service_name', 'service_category', 'total_queries', 
        'success_rate_percent', 'avg_satisfaction', 'satisfaction_rating'
    ]
    
    if all(col in perf_data.columns for col in display_columns):
        st.dataframe(
            perf_data[display_columns],
            column_config={
                "service_name": "Service",
                "service_category": "Category", 
                "total_queries": "Queries",
                "success_rate_percent": "Success Rate (%)",
                "avg_satisfaction": "Satisfaction",
                "satisfaction_rating": "Rating"
            },
            use_container_width=True
        )

def show_operations():
    """Show daily operations metrics"""
    st.header("📈 Daily Operations")
    
    ops_data = fetch_daily_operations()
    if ops_data.empty:
        st.warning("No operations data available")
        return
    
    # Convert date column
    ops_data['full_date'] = pd.to_datetime(ops_data['full_date'])
    
    # Daily trends
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            ops_data,
            x='full_date',
            y='total_daily_queries',
            title="Daily Query Volume Trend"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            ops_data,
            x='full_date',
            y='daily_avg_satisfaction',
            title="Daily Satisfaction Trend"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Success rate and response time
    col3, col4 = st.columns(2)
    
    with col3:
        fig = px.line(
            ops_data,
            x='full_date',
            y='daily_success_rate',
            title="Daily Success Rate (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        fig = px.line(
            ops_data,
            x='full_date',
            y='daily_avg_response_time',
            title="Daily Avg Response Time (ms)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance by day of week
    if 'day_name' in ops_data.columns:
        st.subheader("Performance by Day of Week")
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ops_data['day_name'] = pd.Categorical(ops_data['day_name'], categories=day_order, ordered=True)
        
        day_stats = ops_data.groupby('day_name').agg({
            'total_daily_queries': 'mean',
            'daily_avg_satisfaction': 'mean',
            'daily_success_rate': 'mean'
        }).reset_index()
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Avg Queries', 'Avg Satisfaction', 'Avg Success Rate'),
            specs=[[{'secondary_y': False}, {'secondary_y': False}, {'secondary_y': False}]]
        )
        
        fig.add_trace(
            go.Bar(x=day_stats['day_name'], y=day_stats['total_daily_queries'], name='Queries'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=day_stats['day_name'], y=day_stats['daily_avg_satisfaction'], name='Satisfaction'),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(x=day_stats['day_name'], y=day_stats['daily_success_rate'], name='Success Rate'),
            row=1, col=3
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def show_data_quality():
    """Show data quality metrics"""
    st.header("🔍 Data Quality")
    
    quality_data = fetch_data_quality()
    if quality_data.empty:
        st.warning("No data quality metrics available")
        return
    
    # Overall quality score
    avg_quality = quality_data['overall_quality_score'].mean()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Quality Score", f"{avg_quality:.1f}%")
    
    with col2:
        excellent_sources = (quality_data['quality_rating'] == 'Excellent').sum()
        st.metric("Excellent Sources", f"{excellent_sources}")
    
    with col3:
        poor_sources = (quality_data['quality_rating'] == 'Poor').sum()
        st.metric("Poor Quality Sources", f"{poor_sources}")
    
    # Quality by source type
    if 'source_type' in quality_data.columns:
        st.subheader("Quality by Source Type")
        
        source_quality = quality_data.groupby('source_type').agg({
            'overall_quality_score': 'mean',
            'avg_completeness': 'mean',
            'avg_accuracy': 'mean',
            'avg_consistency': 'mean'
        }).reset_index()
        
        fig = px.bar(
            source_quality,
            x='source_type',
            y='overall_quality_score',
            title="Quality Score by Source Type"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Quality trends
    quality_metrics = quality_data[['source_name', 'overall_quality_score', 'avg_completeness', 'avg_accuracy', 'avg_consistency']].copy()
    
    st.subheader("Quality Metrics by Source")
    st.dataframe(
        quality_metrics,
        column_config={
            "source_name": "Source",
            "overall_quality_score": "Overall (%)",
            "avg_completeness": "Completeness",
            "avg_accuracy": "Accuracy", 
            "avg_consistency": "Consistency"
        },
        use_container_width=True
    )
    
    # Quality distribution
    fig = px.histogram(
        quality_data,
        x='overall_quality_score',
        nbins=20,
        title="Quality Score Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()