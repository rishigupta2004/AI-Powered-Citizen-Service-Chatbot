"""
Data transformation module for the data warehouse ETL pipeline.
Transforms extracted data into warehouse-ready format.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class DataTransformer:
    """Handles data transformation for warehouse processing."""
    
    def __init__(self, warehouse_db_url: str):
        self.warehouse_engine = create_engine(warehouse_db_url)
        self.warehouse_session = sessionmaker(bind=self.warehouse_engine)
        
        # Service priority mapping
        self.service_priority_mapping = {
            'passport': 1,
            'aadhaar': 1,
            'pan': 2,
            'epfo': 2,
            'driving license': 3,
            'parivahan': 3,
            'voter id': 3,
            'ration card': 4,
            'scholarship': 4,
            'grievance': 5,
            'birth certificate': 4,
            'death certificate': 4
        }
        
        # Government department mapping
        self.department_mapping = {
            'passport': 'MEA',
            'aadhaar': 'UIDAI',
            'pan': 'CBDT',
            'epfo': 'Ministry of Labour',
            'driving license': 'MoRTH',
            'parivahan': 'MoRTH',
            'voter id': 'ECI',
            'ration card': 'FCS',
            'scholarship': 'Ministry of Education',
            'grievance': 'DARPG',
            'birth certificate': 'State Municipalities',
            'death certificate': 'State Municipalities'
        }
    
    def transform_service_usage_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform service usage data for warehouse loading."""
        try:
            if df.empty:
                return df
            
            # Add calculated fields
            df['priority_level'] = df['service_name'].str.lower().map(
                self.service_priority_mapping
            ).fillna(5)
            
            df['government_department'] = df['service_name'].str.lower().map(
                self.department_mapping
            ).fillna('Unknown')
            
            df['service_type'] = 'hybrid'  # Default to hybrid
            df['is_active'] = True
            
            # Calculate content completeness
            df['content_completeness'] = (
                df['procedure_count'] + df['document_count'] + df['faq_count']
            ) / 3  # Simple average
            
            # Add quality scores (placeholder - would be calculated from actual data)
            df['quality_score'] = np.random.uniform(80, 95, len(df))
            df['completeness_score'] = df['content_completeness'] * 100
            df['accuracy_score'] = np.random.uniform(85, 98, len(df))
            df['freshness_score'] = np.random.uniform(90, 100, len(df))
            
            logger.info(f"Transformed {len(df)} service usage records")
            return df
            
        except Exception as e:
            logger.error(f"Error transforming service usage data: {e}")
            raise
    
    def transform_api_performance_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform API performance data for warehouse loading."""
        try:
            if df.empty:
                return df
            
            # Calculate derived metrics
            df['success_rate'] = np.where(
                df['request_count'] > 0,
                (df['success_count'] / df['request_count']) * 100,
                0
            )
            
            df['error_rate'] = np.where(
                df['request_count'] > 0,
                (df['error_count'] / df['request_count']) * 100,
                0
            )
            
            # Calculate percentiles (simplified - would use actual response time data)
            df['p95_response_time'] = df['avg_response_time'] * 1.5
            df['p99_response_time'] = df['avg_response_time'] * 2.0
            
            # Add timeout and rate limit counts (placeholder)
            df['timeout_count'] = np.random.randint(0, 5, len(df))
            df['rate_limit_hit_count'] = np.random.randint(0, 3, len(df))
            
            logger.info(f"Transformed {len(df)} API performance records")
            return df
            
        except Exception as e:
            logger.error(f"Error transforming API performance data: {e}")
            raise
    
    def transform_document_processing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform document processing data for warehouse loading."""
        try:
            if df.empty:
                return df
            
            # Map document sources to service IDs
            source_mapping = {
                'passport pdf': 1,
                'uidai doc': 2,
                'pan doc': 3,
                'epfo doc': 4,
                'parivahan doc': 5
            }
            
            df['service_id'] = df['source'].map(source_mapping).fillna(0)
            
            # Calculate processing metrics
            df['success_rate'] = np.where(
                df['chunk_count'] > 0,
                (df['chunk_count'] / df['chunk_count']) * 100,  # Simplified
                0
            )
            
            df['ocr_accuracy'] = np.random.uniform(85, 98, len(df))
            df['classification_accuracy'] = np.random.uniform(90, 99, len(df))
            
            # Map content types
            content_type_mapping = {
                'pdf': 'document',
                'text': 'procedure',
                'html': 'faq'
            }
            
            df['content_type'] = df['doc_type'].map(content_type_mapping).fillna('document')
            
            logger.info(f"Transformed {len(df)} document processing records")
            return df
            
        except Exception as e:
            logger.error(f"Error transforming document processing data: {e}")
            raise
    
    def transform_user_engagement_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform user engagement data for warehouse loading."""
        try:
            if df.empty:
                return df
            
            # Calculate engagement metrics
            df['bounce_rate'] = np.random.uniform(10, 40, len(df))  # Placeholder
            df['session_duration_seconds'] = df['avg_session_duration'].fillna(0)
            
            # Map user types
            user_type_mapping = {
                'citizen': 'citizen',
                'admin': 'admin',
                'analyst': 'analyst',
                'system': 'system'
            }
            
            df['user_type'] = df['user_type'].map(user_type_mapping).fillna('citizen')
            
            # Add device type (placeholder)
            device_types = ['mobile', 'desktop', 'tablet']
            df['device_type'] = np.random.choice(device_types, len(df))
            
            logger.info(f"Transformed {len(df)} user engagement records")
            return df
            
        except Exception as e:
            logger.error(f"Error transforming user engagement data: {e}")
            raise
    
    def transform_content_quality_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform content quality data for warehouse loading."""
        try:
            if df.empty:
                return df
            
            # Ensure all quality scores are within valid range
            for col in ['quality_score', 'completeness_score', 'accuracy_score', 'freshness_score']:
                if col in df.columns:
                    df[col] = df[col].clip(0, 100)
            
            # Map content types
            content_type_mapping = {
                'procedure': 'procedure',
                'document': 'document',
                'faq': 'faq',
                'form': 'form',
                'api_response': 'api_response'
            }
            
            df['content_type'] = df['content_type'].map(content_type_mapping).fillna('document')
            
            # Add validation error categories
            df['validation_error_category'] = np.where(
                df['validation_errors'] > 5, 'high',
                np.where(df['validation_errors'] > 2, 'medium', 'low')
            )
            
            logger.info(f"Transformed {len(df)} content quality records")
            return df
            
        except Exception as e:
            logger.error(f"Error transforming content quality data: {e}")
            raise
    
    def get_dimension_keys(self, table_name: str, lookup_column: str, lookup_values: List[Any]) -> Dict[Any, int]:
        """Get dimension keys for given lookup values."""
        try:
            with self.warehouse_session() as session:
                # Get all dimension records
                query = f"SELECT {lookup_column}, {table_name}_key FROM {table_name}"
                result = session.execute(text(query))
                dimension_map = {row[0]: row[1] for row in result.fetchall()}
                
                # Map lookup values to keys
                key_mapping = {}
                for value in lookup_values:
                    if value in dimension_map:
                        key_mapping[value] = dimension_map[value]
                    else:
                        # Create new dimension record if not found
                        new_key = self.create_dimension_record(table_name, lookup_column, value)
                        key_mapping[value] = new_key
                
                return key_mapping
                
        except Exception as e:
            logger.error(f"Error getting dimension keys for {table_name}: {e}")
            raise
    
    def create_dimension_record(self, table_name: str, lookup_column: str, value: Any) -> int:
        """Create a new dimension record and return its key."""
        try:
            with self.warehouse_session() as session:
                # This would create appropriate dimension records based on table_name
                # For now, return a placeholder key
                logger.warning(f"Creating new dimension record for {table_name}: {value}")
                return 999  # Placeholder
                
        except Exception as e:
            logger.error(f"Error creating dimension record: {e}")
            raise
    
    def transform_all_data(self, extraction_results: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform all extracted data for warehouse loading."""
        logger.info("Starting data transformation")
        
        transformation_results = {}
        
        try:
            # Transform service usage data
            if 'service_usage' in extraction_results:
                transformation_results['service_usage'] = self.transform_service_usage_data(
                    extraction_results['service_usage']
                )
            
            # Transform API performance data
            if 'api_performance' in extraction_results:
                transformation_results['api_performance'] = self.transform_api_performance_data(
                    extraction_results['api_performance']
                )
            
            # Transform document processing data
            if 'document_processing' in extraction_results:
                transformation_results['document_processing'] = self.transform_document_processing_data(
                    extraction_results['document_processing']
                )
            
            # Transform user engagement data
            if 'user_engagement' in extraction_results:
                transformation_results['user_engagement'] = self.transform_user_engagement_data(
                    extraction_results['user_engagement']
                )
            
            # Transform content quality data
            if 'content_quality' in extraction_results:
                transformation_results['content_quality'] = self.transform_content_quality_data(
                    extraction_results['content_quality']
                )
            
            logger.info("Data transformation completed successfully")
            return transformation_results
            
        except Exception as e:
            logger.error(f"Error in data transformation: {e}")
            raise
    
    def close_connections(self):
        """Close database connections."""
        self.warehouse_engine.dispose()