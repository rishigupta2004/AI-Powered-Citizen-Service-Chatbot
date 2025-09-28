"""
Analytics and reporting module for the data warehouse.
Provides business intelligence queries and report generation.
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

logger = logging.getLogger(__name__)

class AnalyticsReporter:
    """Handles analytics and reporting for the data warehouse."""
    
    def __init__(self, warehouse_db_url: str):
        self.warehouse_engine = create_engine(warehouse_db_url)
        self.warehouse_session = sessionmaker(bind=self.warehouse_engine)
    
    def get_service_performance_summary(self, 
                                      start_date: datetime = None, 
                                      end_date: datetime = None) -> pd.DataFrame:
        """Get service performance summary for the given date range."""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            query = """
            SELECT 
                s.service_name,
                s.category,
                s.priority_level,
                s.government_department,
                dss.date_key,
                dd.full_date,
                dss.total_requests,
                dss.successful_requests,
                dss.failed_requests,
                dss.success_rate,
                dss.avg_response_time_ms,
                dss.unique_users,
                dss.avg_quality_score
            FROM daily_service_summary dss
            JOIN service_dim s ON dss.service_key = s.service_key
            JOIN date_dim dd ON dss.date_key = dd.date_key
            WHERE dd.full_date BETWEEN :start_date AND :end_date
            AND s.is_active = TRUE
            ORDER BY dss.total_requests DESC, dss.success_rate DESC
            """
            
            with self.warehouse_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date.date(),
                    'end_date': end_date.date()
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Retrieved service performance summary: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error getting service performance summary: {e}")
            raise
    
    def get_top_performing_services(self, 
                                   days: int = 30, 
                                   limit: int = 10) -> pd.DataFrame:
        """Get top performing services by usage and success rate."""
        try:
            query = """
            SELECT 
                s.service_name,
                s.category,
                s.government_department,
                SUM(dss.total_requests) as total_requests,
                AVG(dss.success_rate) as avg_success_rate,
                AVG(dss.avg_response_time_ms) as avg_response_time,
                SUM(dss.unique_users) as total_unique_users,
                AVG(dss.avg_quality_score) as avg_quality_score
            FROM daily_service_summary dss
            JOIN service_dim s ON dss.service_key = s.service_key
            JOIN date_dim dd ON dss.date_key = dd.date_key
            WHERE dd.full_date >= CURRENT_DATE - INTERVAL :days DAY
            AND s.is_active = TRUE
            GROUP BY s.service_key, s.service_name, s.category, s.government_department
            ORDER BY total_requests DESC, avg_success_rate DESC
            LIMIT :limit
            """
            
            with self.warehouse_session() as session:
                result = session.execute(text(query), {
                    'days': days,
                    'limit': limit
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Retrieved top {len(df)} performing services")
            return df
            
        except Exception as e:
            logger.error(f"Error getting top performing services: {e}")
            raise
    
    def get_content_quality_trends(self, 
                                  start_date: datetime = None, 
                                  end_date: datetime = None) -> pd.DataFrame:
        """Get content quality trends over time."""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            query = """
            SELECT 
                s.service_name,
                ctd.content_type,
                ctd.sub_type,
                ld.language_name,
                cqf.quality_score,
                cqf.completeness_score,
                cqf.accuracy_score,
                cqf.freshness_score,
                cqf.validation_errors,
                dd.full_date
            FROM content_quality_fact cqf
            JOIN service_dim s ON cqf.service_key = s.service_key
            JOIN content_type_dim ctd ON cqf.content_type_key = ctd.content_type_key
            JOIN language_dim ld ON cqf.language_key = ld.language_key
            JOIN date_dim dd ON cqf.date_key = dd.date_key
            WHERE dd.full_date BETWEEN :start_date AND :end_date
            ORDER BY dd.full_date DESC, cqf.quality_score DESC
            """
            
            with self.warehouse_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date.date(),
                    'end_date': end_date.date()
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Retrieved content quality trends: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error getting content quality trends: {e}")
            raise
    
    def get_api_performance_metrics(self, 
                                   start_date: datetime = None, 
                                   end_date: datetime = None) -> pd.DataFrame:
        """Get API performance metrics for the given date range."""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=7)
            if not end_date:
                end_date = datetime.now()
            
            query = """
            SELECT 
                s.service_name,
                ed.endpoint_name,
                ed.endpoint_url,
                dd.full_date,
                apf.request_count,
                apf.success_count,
                apf.error_count,
                apf.avg_response_time_ms,
                apf.p95_response_time_ms,
                apf.p99_response_time_ms,
                apf.timeout_count,
                apf.rate_limit_hit_count,
                CASE WHEN apf.request_count > 0 
                     THEN (apf.error_count::DECIMAL / apf.request_count) * 100 
                     ELSE 0 END as error_rate
            FROM api_performance_fact apf
            JOIN service_dim s ON apf.service_key = s.service_key
            JOIN endpoint_dim ed ON apf.endpoint_key = ed.endpoint_key
            JOIN date_dim dd ON apf.date_key = dd.date_key
            WHERE dd.full_date BETWEEN :start_date AND :end_date
            ORDER BY apf.request_count DESC, apf.avg_response_time_ms ASC
            """
            
            with self.warehouse_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date.date(),
                    'end_date': end_date.date()
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Retrieved API performance metrics: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error getting API performance metrics: {e}")
            raise
    
    def get_user_engagement_metrics(self, 
                                   start_date: datetime = None, 
                                   end_date: datetime = None) -> pd.DataFrame:
        """Get user engagement metrics for the given date range."""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            query = """
            SELECT 
                s.service_name,
                ud.user_type,
                rd.state_name,
                rd.region_type,
                ld.language_name,
                dd.full_date,
                uef.session_count,
                uef.page_views,
                uef.search_queries,
                uef.successful_completions,
                uef.session_duration_seconds,
                uef.bounce_rate
            FROM user_engagement_fact uef
            JOIN service_dim s ON uef.service_key = s.service_key
            JOIN user_dim ud ON uef.user_key = ud.user_key
            LEFT JOIN region_dim rd ON uef.region_key = rd.region_key
            LEFT JOIN language_dim ld ON ud.language_preference = ld.language_code
            JOIN date_dim dd ON uef.date_key = dd.date_key
            WHERE dd.full_date BETWEEN :start_date AND :end_date
            ORDER BY uef.session_count DESC, uef.page_views DESC
            """
            
            with self.warehouse_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date.date(),
                    'end_date': end_date.date()
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Retrieved user engagement metrics: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error getting user engagement metrics: {e}")
            raise
    
    def get_multilingual_coverage_report(self) -> pd.DataFrame:
        """Get multilingual coverage report across all services."""
        try:
            query = """
            SELECT 
                s.service_name,
                s.category,
                ld.language_name,
                ld.script,
                COUNT(cqf.content_type_key) as content_items,
                AVG(cqf.quality_score) as avg_quality_score,
                AVG(cqf.completeness_score) as avg_completeness_score
            FROM content_quality_fact cqf
            JOIN service_dim s ON cqf.service_key = s.service_key
            JOIN language_dim ld ON cqf.language_key = ld.language_key
            WHERE s.is_active = TRUE
            GROUP BY s.service_key, s.service_name, s.category, ld.language_key, ld.language_name, ld.script
            ORDER BY s.service_name, content_items DESC
            """
            
            with self.warehouse_session() as session:
                result = session.execute(text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Retrieved multilingual coverage report: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error getting multilingual coverage report: {e}")
            raise
    
    def get_data_quality_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive data quality dashboard metrics."""
        try:
            with self.warehouse_session() as session:
                # Overall data quality metrics
                quality_metrics = session.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        AVG(quality_score) as avg_quality_score,
                        AVG(completeness_score) as avg_completeness_score,
                        AVG(accuracy_score) as avg_accuracy_score,
                        AVG(freshness_score) as avg_freshness_score,
                        SUM(validation_errors) as total_validation_errors
                    FROM content_quality_fact
                    WHERE date_key >= EXTRACT(EPOCH FROM CURRENT_DATE - INTERVAL '30 days')::INTEGER
                """).fetchone()
                
                # Service-wise quality breakdown
                service_quality = session.execute("""
                    SELECT 
                        s.service_name,
                        AVG(cqf.quality_score) as avg_quality_score,
                        COUNT(*) as content_items,
                        SUM(cqf.validation_errors) as total_errors
                    FROM content_quality_fact cqf
                    JOIN service_dim s ON cqf.service_key = s.service_key
                    WHERE cqf.date_key >= EXTRACT(EPOCH FROM CURRENT_DATE - INTERVAL '30 days')::INTEGER
                    GROUP BY s.service_key, s.service_name
                    ORDER BY avg_quality_score DESC
                """).fetchall()
                
                # Language-wise quality breakdown
                language_quality = session.execute("""
                    SELECT 
                        ld.language_name,
                        COUNT(*) as content_items,
                        AVG(cqf.quality_score) as avg_quality_score,
                        AVG(cqf.completeness_score) as avg_completeness_score
                    FROM content_quality_fact cqf
                    JOIN language_dim ld ON cqf.language_key = ld.language_key
                    WHERE cqf.date_key >= EXTRACT(EPOCH FROM CURRENT_DATE - INTERVAL '30 days')::INTEGER
                    GROUP BY ld.language_key, ld.language_name
                    ORDER BY avg_quality_score DESC
                """).fetchall()
                
                # Data freshness metrics
                freshness_metrics = session.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '1 day' THEN 1 END) as recent_records,
                        COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as weekly_records,
                        COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as monthly_records
                    FROM service_usage_fact
                """).fetchone()
                
                dashboard = {
                    'overall_metrics': {
                        'total_records': quality_metrics[0],
                        'avg_quality_score': float(quality_metrics[1]) if quality_metrics[1] else 0,
                        'avg_completeness_score': float(quality_metrics[2]) if quality_metrics[2] else 0,
                        'avg_accuracy_score': float(quality_metrics[3]) if quality_metrics[3] else 0,
                        'avg_freshness_score': float(quality_metrics[4]) if quality_metrics[4] else 0,
                        'total_validation_errors': quality_metrics[5]
                    },
                    'service_quality': [
                        {
                            'service_name': row[0],
                            'avg_quality_score': float(row[1]) if row[1] else 0,
                            'content_items': row[2],
                            'total_errors': row[3]
                        } for row in service_quality
                    ],
                    'language_quality': [
                        {
                            'language_name': row[0],
                            'content_items': row[1],
                            'avg_quality_score': float(row[2]) if row[2] else 0,
                            'avg_completeness_score': float(row[3]) if row[3] else 0
                        } for row in language_quality
                    ],
                    'freshness_metrics': {
                        'total_records': freshness_metrics[0],
                        'recent_records': freshness_metrics[1],
                        'weekly_records': freshness_metrics[2],
                        'monthly_records': freshness_metrics[3],
                        'freshness_percentage': (freshness_metrics[1] / freshness_metrics[0] * 100) if freshness_metrics[0] > 0 else 0
                    }
                }
                
            logger.info("Retrieved data quality dashboard metrics")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting data quality dashboard: {e}")
            raise
    
    def generate_executive_summary(self, days: int = 30) -> Dict[str, Any]:
        """Generate executive summary report for the given period."""
        try:
            with self.warehouse_session() as session:
                # Key performance indicators
                kpis = session.execute("""
                    SELECT 
                        SUM(dss.total_requests) as total_requests,
                        AVG(dss.success_rate) as avg_success_rate,
                        AVG(dss.avg_response_time_ms) as avg_response_time,
                        SUM(dss.unique_users) as total_unique_users,
                        AVG(dss.avg_quality_score) as avg_quality_score
                    FROM daily_service_summary dss
                    JOIN date_dim dd ON dss.date_key = dd.date_key
                    WHERE dd.full_date >= CURRENT_DATE - INTERVAL :days DAY
                """, {'days': days}).fetchone()
                
                # Top services by usage
                top_services = session.execute("""
                    SELECT 
                        s.service_name,
                        SUM(dss.total_requests) as total_requests,
                        AVG(dss.success_rate) as avg_success_rate
                    FROM daily_service_summary dss
                    JOIN service_dim s ON dss.service_key = s.service_key
                    JOIN date_dim dd ON dss.date_key = dd.date_key
                    WHERE dd.full_date >= CURRENT_DATE - INTERVAL :days DAY
                    GROUP BY s.service_key, s.service_name
                    ORDER BY total_requests DESC
                    LIMIT 5
                """, {'days': days}).fetchall()
                
                # Content quality trends
                quality_trends = session.execute("""
                    SELECT 
                        dd.full_date,
                        AVG(cqf.quality_score) as avg_quality_score,
                        COUNT(*) as content_items
                    FROM content_quality_fact cqf
                    JOIN date_dim dd ON cqf.date_key = dd.date_key
                    WHERE dd.full_date >= CURRENT_DATE - INTERVAL :days DAY
                    GROUP BY dd.full_date
                    ORDER BY dd.full_date
                """, {'days': days}).fetchall()
                
                # Multilingual coverage
                multilingual_coverage = session.execute("""
                    SELECT 
                        COUNT(DISTINCT ld.language_key) as supported_languages,
                        COUNT(*) as total_content_items
                    FROM content_quality_fact cqf
                    JOIN language_dim ld ON cqf.language_key = ld.language_key
                    JOIN date_dim dd ON cqf.date_key = dd.date_key
                    WHERE dd.full_date >= CURRENT_DATE - INTERVAL :days DAY
                """, {'days': days}).fetchone()
                
                summary = {
                    'period_days': days,
                    'generated_at': datetime.now().isoformat(),
                    'key_performance_indicators': {
                        'total_requests': kpis[0] or 0,
                        'avg_success_rate': float(kpis[1]) if kpis[1] else 0,
                        'avg_response_time_ms': float(kpis[2]) if kpis[2] else 0,
                        'total_unique_users': kpis[3] or 0,
                        'avg_quality_score': float(kpis[4]) if kpis[4] else 0
                    },
                    'top_services': [
                        {
                            'service_name': row[0],
                            'total_requests': row[1],
                            'avg_success_rate': float(row[2]) if row[2] else 0
                        } for row in top_services
                    ],
                    'quality_trends': [
                        {
                            'date': row[0].isoformat(),
                            'avg_quality_score': float(row[1]) if row[1] else 0,
                            'content_items': row[2]
                        } for row in quality_trends
                    ],
                    'multilingual_coverage': {
                        'supported_languages': multilingual_coverage[0] or 0,
                        'total_content_items': multilingual_coverage[1] or 0
                    }
                }
                
            logger.info("Generated executive summary report")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            raise
    
    def export_report_to_json(self, report_data: Dict[str, Any], filename: str = None) -> str:
        """Export report data to JSON file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"citizen_services_report_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting report to JSON: {e}")
            raise
    
    def close_connections(self):
        """Close database connections."""
        self.warehouse_engine.dispose()