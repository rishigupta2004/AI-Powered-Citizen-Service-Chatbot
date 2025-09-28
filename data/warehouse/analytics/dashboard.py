"""
Analytics dashboard for data warehouse.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import sqlalchemy
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)

class WarehouseDashboard:
    """Streamlit dashboard for data warehouse analytics."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
    
    def run(self):
        """Run the Streamlit dashboard."""
        st.set_page_config(
            page_title="Citizen Services Data Warehouse",
            page_icon="🏛️",
            layout="wide"
        )
        
        st.title("🏛️ Citizen Services Data Warehouse Analytics")
        st.markdown("---")
        
        # Sidebar for filters
        self._render_sidebar()
        
        # Main dashboard content
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🔍 Service Analytics", "👥 User Analytics", 
            "📄 Content Analytics", "⚡ System Performance"
        ])
        
        with tab1:
            self._render_overview()
        
        with tab2:
            self._render_service_analytics()
        
        with tab3:
            self._render_user_analytics()
        
        with tab4:
            self._render_content_analytics()
        
        with tab5:
            self._render_system_performance()
    
    def _render_sidebar(self):
        """Render sidebar with filters."""
        st.sidebar.title("Filters")
        
        # Date range filter
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=30),
                max_value=date.today()
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=date.today(),
                max_value=date.today()
            )
        
        # Service filter
        services = self._get_services()
        selected_services = st.sidebar.multiselect(
            "Services",
            options=services,
            default=services
        )
        
        # Language filter
        languages = self._get_languages()
        selected_languages = st.sidebar.multiselect(
            "Languages",
            options=languages,
            default=languages
        )
        
        # Store filters in session state
        st.session_state.filters = {
            'start_date': start_date,
            'end_date': end_date,
            'services': selected_services,
            'languages': selected_languages
        }
    
    def _get_services(self) -> List[str]:
        """Get list of available services."""
        try:
            query = "SELECT DISTINCT service_name FROM dim_service WHERE is_active = true ORDER BY service_name"
            result = pd.read_sql(query, self.engine)
            return result['service_name'].tolist()
        except Exception as e:
            logger.error(f"Failed to get services: {e}")
            return []
    
    def _get_languages(self) -> List[str]:
        """Get list of available languages."""
        try:
            query = "SELECT DISTINCT language_name FROM dim_language WHERE is_supported = true ORDER BY language_name"
            result = pd.read_sql(query, self.engine)
            return result['language_name'].tolist()
        except Exception as e:
            logger.error(f"Failed to get languages: {e}")
            return []
    
    def _render_overview(self):
        """Render overview dashboard."""
        st.header("📊 Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_queries = self._get_total_queries()
            st.metric("Total Queries", f"{total_queries:,}")
        
        with col2:
            success_rate = self._get_success_rate()
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col3:
            avg_response_time = self._get_avg_response_time()
            st.metric("Avg Response Time", f"{avg_response_time:.0f}ms")
        
        with col4:
            unique_users = self._get_unique_users()
            st.metric("Unique Users", f"{unique_users:,}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Query Volume Over Time")
            query_volume_data = self._get_query_volume_data()
            if not query_volume_data.empty:
                fig = px.line(
                    query_volume_data, 
                    x='date', 
                    y='query_count',
                    title="Daily Query Volume"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Service Distribution")
            service_dist_data = self._get_service_distribution()
            if not service_dist_data.empty:
                fig = px.pie(
                    service_dist_data,
                    values='query_count',
                    names='service_name',
                    title="Queries by Service"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_service_analytics(self):
        """Render service analytics dashboard."""
        st.header("🔍 Service Analytics")
        
        # Service performance table
        st.subheader("Service Performance")
        service_performance = self._get_service_performance()
        if not service_performance.empty:
            st.dataframe(service_performance, use_container_width=True)
        
        # Service trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Service Usage Trends")
            service_trends = self._get_service_trends()
            if not service_trends.empty:
                fig = px.line(
                    service_trends,
                    x='date',
                    y='query_count',
                    color='service_name',
                    title="Service Usage Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Response Time by Service")
            response_times = self._get_response_times_by_service()
            if not response_times.empty:
                fig = px.bar(
                    response_times,
                    x='service_name',
                    y='avg_response_time',
                    title="Average Response Time by Service"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_user_analytics(self):
        """Render user analytics dashboard."""
        st.header("👥 User Analytics")
        
        # User metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_users = self._get_total_users()
            st.metric("Total Users", f"{total_users:,}")
        
        with col2:
            active_users = self._get_active_users()
            st.metric("Active Users (30 days)", f"{active_users:,}")
        
        with col3:
            avg_queries_per_user = self._get_avg_queries_per_user()
            st.metric("Avg Queries per User", f"{avg_queries_per_user:.1f}")
        
        # User engagement charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("User Activity Over Time")
            user_activity = self._get_user_activity()
            if not user_activity.empty:
                fig = px.line(
                    user_activity,
                    x='date',
                    y='unique_users',
                    title="Daily Active Users"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("User Type Distribution")
            user_types = self._get_user_type_distribution()
            if not user_types.empty:
                fig = px.pie(
                    user_types,
                    values='user_count',
                    names='user_type',
                    title="Users by Type"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_content_analytics(self):
        """Render content analytics dashboard."""
        st.header("📄 Content Analytics")
        
        # Content metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_content = self._get_total_content()
            st.metric("Total Content Items", f"{total_content:,}")
        
        with col2:
            content_views = self._get_content_views()
            st.metric("Total Content Views", f"{content_views:,}")
        
        with col3:
            avg_view_duration = self._get_avg_view_duration()
            st.metric("Avg View Duration", f"{avg_view_duration:.1f}s")
        
        # Content performance
        st.subheader("Top Performing Content")
        top_content = self._get_top_content()
        if not top_content.empty:
            st.dataframe(top_content, use_container_width=True)
        
        # Content type distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Content Type Distribution")
            content_types = self._get_content_type_distribution()
            if not content_types.empty:
                fig = px.pie(
                    content_types,
                    values='count',
                    names='content_type',
                    title="Content by Type"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Content Views Over Time")
            content_views_trend = self._get_content_views_trend()
            if not content_views_trend.empty:
                fig = px.line(
                    content_views_trend,
                    x='date',
                    y='view_count',
                    title="Daily Content Views"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_system_performance(self):
        """Render system performance dashboard."""
        st.header("⚡ System Performance")
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_response_time = self._get_avg_response_time()
            st.metric("Avg Response Time", f"{avg_response_time:.0f}ms")
        
        with col2:
            error_rate = self._get_error_rate()
            st.metric("Error Rate", f"{error_rate:.2f}%")
        
        with col3:
            throughput = self._get_throughput()
            st.metric("Throughput", f"{throughput:.0f} req/min")
        
        with col4:
            uptime = self._get_uptime()
            st.metric("Uptime", f"{uptime:.2f}%")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Response Time Trends")
            response_time_trend = self._get_response_time_trend()
            if not response_time_trend.empty:
                fig = px.line(
                    response_time_trend,
                    x='date',
                    y='avg_response_time',
                    title="Average Response Time Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Error Rate Trends")
            error_rate_trend = self._get_error_rate_trend()
            if not error_rate_trend.empty:
                fig = px.line(
                    error_rate_trend,
                    x='date',
                    y='error_rate',
                    title="Error Rate Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Data retrieval methods
    def _get_total_queries(self) -> int:
        """Get total number of queries."""
        try:
            query = """
            SELECT COUNT(*) as total_queries
            FROM fct_service_queries sq
            JOIN dim_date d ON sq.date_key = d.date_key
            WHERE d.full_date BETWEEN :start_date AND :end_date
            """
            result = pd.read_sql(
                query, 
                self.engine, 
                params=st.session_state.filters
            )
            return result['total_queries'].iloc[0]
        except Exception as e:
            logger.error(f"Failed to get total queries: {e}")
            return 0
    
    def _get_success_rate(self) -> float:
        """Get query success rate."""
        try:
            query = """
            SELECT 
                COUNT(*) FILTER (WHERE success_flag = true) * 100.0 / COUNT(*) as success_rate
            FROM fct_service_queries sq
            JOIN dim_date d ON sq.date_key = d.date_key
            WHERE d.full_date BETWEEN :start_date AND :end_date
            """
            result = pd.read_sql(
                query, 
                self.engine, 
                params=st.session_state.filters
            )
            return result['success_rate'].iloc[0]
        except Exception as e:
            logger.error(f"Failed to get success rate: {e}")
            return 0.0
    
    def _get_avg_response_time(self) -> float:
        """Get average response time."""
        try:
            query = """
            SELECT AVG(response_time_ms) as avg_response_time
            FROM fct_service_queries sq
            JOIN dim_date d ON sq.date_key = d.date_key
            WHERE d.full_date BETWEEN :start_date AND :end_date
            AND response_time_ms IS NOT NULL
            """
            result = pd.read_sql(
                query, 
                self.engine, 
                params=st.session_state.filters
            )
            return result['avg_response_time'].iloc[0] or 0.0
        except Exception as e:
            logger.error(f"Failed to get average response time: {e}")
            return 0.0
    
    def _get_unique_users(self) -> int:
        """Get number of unique users."""
        try:
            query = """
            SELECT COUNT(DISTINCT user_key) as unique_users
            FROM fct_service_queries sq
            JOIN dim_date d ON sq.date_key = d.date_key
            WHERE d.full_date BETWEEN :start_date AND :end_date
            AND user_key IS NOT NULL
            """
            result = pd.read_sql(
                query, 
                self.engine, 
                params=st.session_state.filters
            )
            return result['unique_users'].iloc[0]
        except Exception as e:
            logger.error(f"Failed to get unique users: {e}")
            return 0
    
    def _get_query_volume_data(self) -> pd.DataFrame:
        """Get query volume data over time."""
        try:
            query = """
            SELECT 
                d.full_date as date,
                COUNT(*) as query_count
            FROM fct_service_queries sq
            JOIN dim_date d ON sq.date_key = d.date_key
            WHERE d.full_date BETWEEN :start_date AND :end_date
            GROUP BY d.full_date
            ORDER BY d.full_date
            """
            return pd.read_sql(query, self.engine, params=st.session_state.filters)
        except Exception as e:
            logger.error(f"Failed to get query volume data: {e}")
            return pd.DataFrame()
    
    def _get_service_distribution(self) -> pd.DataFrame:
        """Get service distribution data."""
        try:
            query = """
            SELECT 
                s.service_name,
                COUNT(*) as query_count
            FROM fct_service_queries sq
            JOIN dim_service s ON sq.service_key = s.service_key
            JOIN dim_date d ON sq.date_key = d.date_key
            WHERE d.full_date BETWEEN :start_date AND :end_date
            GROUP BY s.service_name
            ORDER BY query_count DESC
            """
            return pd.read_sql(query, self.engine, params=st.session_state.filters)
        except Exception as e:
            logger.error(f"Failed to get service distribution: {e}")
            return pd.DataFrame()
    
    # Additional data retrieval methods would be implemented here...
    def _get_service_performance(self) -> pd.DataFrame:
        """Get service performance data."""
        return pd.DataFrame()
    
    def _get_service_trends(self) -> pd.DataFrame:
        """Get service usage trends."""
        return pd.DataFrame()
    
    def _get_response_times_by_service(self) -> pd.DataFrame:
        """Get response times by service."""
        return pd.DataFrame()
    
    def _get_total_users(self) -> int:
        """Get total number of users."""
        return 0
    
    def _get_active_users(self) -> int:
        """Get number of active users."""
        return 0
    
    def _get_avg_queries_per_user(self) -> float:
        """Get average queries per user."""
        return 0.0
    
    def _get_user_activity(self) -> pd.DataFrame:
        """Get user activity data."""
        return pd.DataFrame()
    
    def _get_user_type_distribution(self) -> pd.DataFrame:
        """Get user type distribution."""
        return pd.DataFrame()
    
    def _get_total_content(self) -> int:
        """Get total content items."""
        return 0
    
    def _get_content_views(self) -> int:
        """Get total content views."""
        return 0
    
    def _get_avg_view_duration(self) -> float:
        """Get average view duration."""
        return 0.0
    
    def _get_top_content(self) -> pd.DataFrame:
        """Get top performing content."""
        return pd.DataFrame()
    
    def _get_content_type_distribution(self) -> pd.DataFrame:
        """Get content type distribution."""
        return pd.DataFrame()
    
    def _get_content_views_trend(self) -> pd.DataFrame:
        """Get content views trend."""
        return pd.DataFrame()
    
    def _get_error_rate(self) -> float:
        """Get error rate."""
        return 0.0
    
    def _get_throughput(self) -> float:
        """Get throughput."""
        return 0.0
    
    def _get_uptime(self) -> float:
        """Get uptime percentage."""
        return 100.0
    
    def _get_response_time_trend(self) -> pd.DataFrame:
        """Get response time trend."""
        return pd.DataFrame()
    
    def _get_error_rate_trend(self) -> pd.DataFrame:
        """Get error rate trend."""
        return pd.DataFrame()

def main():
    """Main function to run the dashboard."""
    import os
    
    # Get database URL from environment
    database_url = os.getenv(
        'WAREHOUSE_DATABASE_URL', 
        'postgresql://user:password@localhost/citizen_services_warehouse'
    )
    
    # Create and run dashboard
    dashboard = WarehouseDashboard(database_url)
    dashboard.run()

if __name__ == "__main__":
    main()