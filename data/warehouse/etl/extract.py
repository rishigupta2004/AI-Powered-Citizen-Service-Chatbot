"""
Data extraction module for the data warehouse ETL pipeline.
Extracts data from operational database and external sources.
"""

import pandas as pd
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.config import APISETU_KEY
from backend.app.db import engine as op_engine

logger = logging.getLogger(__name__)

class DataExtractor:
    """Handles data extraction from various sources for warehouse processing."""
    
    def __init__(self, operational_db_url: str, warehouse_db_url: str):
        self.op_engine = create_engine(operational_db_url)
        self.warehouse_engine = create_engine(warehouse_db_url)
        self.op_session = sessionmaker(bind=self.op_engine)
        self.warehouse_session = sessionmaker(bind=self.warehouse_engine)
    
    def extract_service_usage_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract service usage data from operational database."""
        try:
            query = """
            SELECT 
                s.service_id,
                s.name as service_name,
                s.category,
                s.created_at as service_created_at,
                COUNT(DISTINCT p.procedure_id) as procedure_count,
                COUNT(DISTINCT d.doc_id) as document_count,
                COUNT(DISTINCT f.faq_id) as faq_count,
                CURRENT_DATE as extraction_date
            FROM services s
            LEFT JOIN procedures p ON s.service_id = p.service_id
            LEFT JOIN documents d ON s.service_id = d.service_id
            LEFT JOIN faqs f ON s.service_id = f.faq_id
            WHERE s.created_at BETWEEN :start_date AND :end_date
            GROUP BY s.service_id, s.name, s.category, s.created_at
            """
            
            with self.op_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date,
                    'end_date': end_date
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Extracted {len(df)} service usage records")
            return df
            
        except Exception as e:
            logger.error(f"Error extracting service usage data: {e}")
            raise
    
    def extract_api_logs_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract API logs data for performance analysis."""
        try:
            # This would extract from API logs table if it exists
            # For now, return empty DataFrame with expected structure
            query = """
            SELECT 
                service_id,
                endpoint,
                COUNT(*) as request_count,
                AVG(response_time_ms) as avg_response_time,
                MAX(response_time_ms) as max_response_time,
                MIN(response_time_ms) as min_response_time,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
                CURRENT_DATE as extraction_date
            FROM api_logs
            WHERE created_at BETWEEN :start_date AND :end_date
            GROUP BY service_id, endpoint
            """
            
            with self.op_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date,
                    'end_date': end_date
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Extracted {len(df)} API performance records")
            return df
            
        except Exception as e:
            logger.warning(f"API logs table not found or error: {e}")
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=[
                'service_id', 'endpoint', 'request_count', 'avg_response_time',
                'max_response_time', 'min_response_time', 'success_count',
                'error_count', 'extraction_date'
            ])
    
    def extract_document_processing_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract document processing data from document store."""
        try:
            query = """
            SELECT 
                d.id as document_id,
                d.source,
                d.language,
                d.doc_type,
                d.created_at,
                COUNT(dc.id) as chunk_count,
                AVG(LENGTH(dc.content)) as avg_chunk_length,
                MAX(dc.created_at) as last_processed_at
            FROM documents d
            LEFT JOIN document_chunks dc ON d.id = dc.document_id
            WHERE d.created_at BETWEEN :start_date AND :end_date
            GROUP BY d.id, d.source, d.language, d.doc_type, d.created_at
            """
            
            with self.op_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date,
                    'end_date': end_date
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Extracted {len(df)} document processing records")
            return df
            
        except Exception as e:
            logger.error(f"Error extracting document processing data: {e}")
            raise
    
    def extract_user_engagement_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract user engagement data from user logs."""
        try:
            # This would extract from user engagement logs if they exist
            # For now, return empty DataFrame with expected structure
            query = """
            SELECT 
                u.user_id,
                u.user_type,
                u.region,
                u.language_preference,
                COUNT(ul.session_id) as session_count,
                AVG(ul.session_duration) as avg_session_duration,
                SUM(ul.page_views) as total_page_views,
                SUM(ul.search_queries) as total_search_queries,
                CURRENT_DATE as extraction_date
            FROM users u
            LEFT JOIN user_logs ul ON u.user_id = ul.user_id
            WHERE ul.created_at BETWEEN :start_date AND :end_date
            GROUP BY u.user_id, u.user_type, u.region, u.language_preference
            """
            
            with self.op_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date,
                    'end_date': end_date
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Extracted {len(df)} user engagement records")
            return df
            
        except Exception as e:
            logger.warning(f"User logs table not found or error: {e}")
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=[
                'user_id', 'user_type', 'region', 'language_preference',
                'session_count', 'avg_session_duration', 'total_page_views',
                'total_search_queries', 'extraction_date'
            ])
    
    def extract_content_quality_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract content quality metrics from content validation logs."""
        try:
            # This would extract from content quality logs if they exist
            # For now, return empty DataFrame with expected structure
            query = """
            SELECT 
                service_id,
                content_type,
                language,
                quality_score,
                completeness_score,
                accuracy_score,
                freshness_score,
                validation_errors,
                content_length,
                word_count,
                created_at
            FROM content_quality_logs
            WHERE created_at BETWEEN :start_date AND :end_date
            """
            
            with self.op_session() as session:
                result = session.execute(text(query), {
                    'start_date': start_date,
                    'end_date': end_date
                })
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Extracted {len(df)} content quality records")
            return df
            
        except Exception as e:
            logger.warning(f"Content quality logs table not found or error: {e}")
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=[
                'service_id', 'content_type', 'language', 'quality_score',
                'completeness_score', 'accuracy_score', 'freshness_score',
                'validation_errors', 'content_length', 'word_count', 'created_at'
            ])
    
    def extract_all_data(self, start_date: datetime, end_date: datetime) -> Dict[str, pd.DataFrame]:
        """Extract all data sources for warehouse processing."""
        logger.info(f"Starting data extraction from {start_date} to {end_date}")
        
        extraction_results = {}
        
        try:
            # Extract service usage data
            extraction_results['service_usage'] = self.extract_service_usage_data(start_date, end_date)
            
            # Extract API performance data
            extraction_results['api_performance'] = self.extract_api_logs_data(start_date, end_date)
            
            # Extract document processing data
            extraction_results['document_processing'] = self.extract_document_processing_data(start_date, end_date)
            
            # Extract user engagement data
            extraction_results['user_engagement'] = self.extract_user_engagement_data(start_date, end_date)
            
            # Extract content quality data
            extraction_results['content_quality'] = self.extract_content_quality_data(start_date, end_date)
            
            logger.info("Data extraction completed successfully")
            return extraction_results
            
        except Exception as e:
            logger.error(f"Error in data extraction: {e}")
            raise
    
    def get_date_key(self, date: datetime) -> int:
        """Get date key for warehouse date dimension."""
        return int(date.timestamp())
    
    def close_connections(self):
        """Close database connections."""
        self.op_engine.dispose()
        self.warehouse_engine.dispose()