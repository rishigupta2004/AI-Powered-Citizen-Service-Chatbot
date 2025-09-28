"""
Data loading module for the data warehouse ETL pipeline.
Loads transformed data into warehouse tables.
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)

class DataLoader:
    """Handles data loading into warehouse tables."""
    
    def __init__(self, warehouse_db_url: str):
        self.warehouse_engine = create_engine(warehouse_db_url)
        self.warehouse_session = sessionmaker(bind=self.warehouse_engine)
    
    def load_service_dimension(self, df: pd.DataFrame) -> None:
        """Load data into service_dim table."""
        try:
            if df.empty:
                return
            
            with self.warehouse_session() as session:
                # Prepare data for insertion
                service_data = []
                for _, row in df.iterrows():
                    service_data.append({
                        'service_id': row['service_id'],
                        'service_name': row['service_name'],
                        'category': row['category'],
                        'description': row.get('description', ''),
                        'government_department': row['government_department'],
                        'service_type': row['service_type'],
                        'priority_level': row['priority_level'],
                        'is_active': row['is_active'],
                        'created_at': row.get('service_created_at', datetime.now()),
                        'updated_at': datetime.now()
                    })
                
                # Use upsert to handle duplicates
                stmt = insert(text("""
                    INSERT INTO service_dim 
                    (service_id, service_name, category, description, government_department, 
                     service_type, priority_level, is_active, created_at, updated_at)
                    VALUES (:service_id, :service_name, :category, :description, :government_department,
                            :service_type, :priority_level, :is_active, :created_at, :updated_at)
                    ON CONFLICT (service_id) 
                    DO UPDATE SET
                        service_name = EXCLUDED.service_name,
                        category = EXCLUDED.category,
                        description = EXCLUDED.description,
                        government_department = EXCLUDED.government_department,
                        service_type = EXCLUDED.service_type,
                        priority_level = EXCLUDED.priority_level,
                        is_active = EXCLUDED.is_active,
                        updated_at = EXCLUDED.updated_at
                """))
                
                session.execute(stmt, service_data)
                session.commit()
                
            logger.info(f"Loaded {len(service_data)} records into service_dim")
            
        except Exception as e:
            logger.error(f"Error loading service dimension data: {e}")
            raise
    
    def load_service_usage_fact(self, df: pd.DataFrame) -> None:
        """Load data into service_usage_fact table."""
        try:
            if df.empty:
                return
            
            with self.warehouse_session() as session:
                # Get dimension keys
                service_keys = self.get_service_keys(df['service_id'].unique())
                date_keys = self.get_date_keys([datetime.now().date()])
                
                # Prepare fact data
                fact_data = []
                for _, row in df.iterrows():
                    fact_data.append({
                        'date_key': date_keys[datetime.now().date()],
                        'service_key': service_keys.get(row['service_id'], 1),
                        'usage_count': 1,
                        'success_count': 1,  # Simplified
                        'error_count': 0,
                        'response_time_ms': 500,  # Placeholder
                        'created_at': datetime.now()
                    })
                
                # Insert fact data
                stmt = text("""
                    INSERT INTO service_usage_fact 
                    (date_key, service_key, usage_count, success_count, error_count, 
                     response_time_ms, created_at)
                    VALUES (:date_key, :service_key, :usage_count, :success_count, :error_count,
                            :response_time_ms, :created_at)
                """)
                
                session.execute(stmt, fact_data)
                session.commit()
                
            logger.info(f"Loaded {len(fact_data)} records into service_usage_fact")
            
        except Exception as e:
            logger.error(f"Error loading service usage fact data: {e}")
            raise
    
    def load_api_performance_fact(self, df: pd.DataFrame) -> None:
        """Load data into api_performance_fact table."""
        try:
            if df.empty:
                return
            
            with self.warehouse_session() as session:
                # Get dimension keys
                service_keys = self.get_service_keys(df['service_id'].unique())
                date_keys = self.get_date_keys([datetime.now().date()])
                endpoint_keys = self.get_endpoint_keys(df['endpoint'].unique())
                
                # Prepare fact data
                fact_data = []
                for _, row in df.iterrows():
                    fact_data.append({
                        'date_key': date_keys[datetime.now().date()],
                        'service_key': service_keys.get(row['service_id'], 1),
                        'endpoint_key': endpoint_keys.get(row['endpoint'], 1),
                        'request_count': row['request_count'],
                        'success_count': row['success_count'],
                        'error_count': row['error_count'],
                        'avg_response_time_ms': row['avg_response_time'],
                        'max_response_time_ms': row['max_response_time'],
                        'min_response_time_ms': row['min_response_time'],
                        'p95_response_time_ms': row.get('p95_response_time', row['avg_response_time'] * 1.5),
                        'p99_response_time_ms': row.get('p99_response_time', row['avg_response_time'] * 2.0),
                        'timeout_count': row.get('timeout_count', 0),
                        'rate_limit_hit_count': row.get('rate_limit_hit_count', 0),
                        'created_at': datetime.now()
                    })
                
                # Insert fact data
                stmt = text("""
                    INSERT INTO api_performance_fact 
                    (date_key, service_key, endpoint_key, request_count, success_count, error_count,
                     avg_response_time_ms, max_response_time_ms, min_response_time_ms,
                     p95_response_time_ms, p99_response_time_ms, timeout_count, rate_limit_hit_count, created_at)
                    VALUES (:date_key, :service_key, :endpoint_key, :request_count, :success_count, :error_count,
                            :avg_response_time_ms, :max_response_time_ms, :min_response_time_ms,
                            :p95_response_time_ms, :p99_response_time_ms, :timeout_count, :rate_limit_hit_count, :created_at)
                """)
                
                session.execute(stmt, fact_data)
                session.commit()
                
            logger.info(f"Loaded {len(fact_data)} records into api_performance_fact")
            
        except Exception as e:
            logger.error(f"Error loading API performance fact data: {e}")
            raise
    
    def load_content_quality_fact(self, df: pd.DataFrame) -> None:
        """Load data into content_quality_fact table."""
        try:
            if df.empty:
                return
            
            with self.warehouse_session() as session:
                # Get dimension keys
                service_keys = self.get_service_keys(df['service_id'].unique())
                date_keys = self.get_date_keys([datetime.now().date()])
                content_type_keys = self.get_content_type_keys(df['content_type'].unique())
                language_keys = self.get_language_keys(df['language'].unique())
                
                # Prepare fact data
                fact_data = []
                for _, row in df.iterrows():
                    fact_data.append({
                        'date_key': date_keys[datetime.now().date()],
                        'service_key': service_keys.get(row['service_id'], 1),
                        'content_type_key': content_type_keys.get(row['content_type'], 1),
                        'language_key': language_keys.get(row['language'], 1),
                        'quality_score': row['quality_score'],
                        'completeness_score': row['completeness_score'],
                        'accuracy_score': row['accuracy_score'],
                        'freshness_score': row['freshness_score'],
                        'validation_errors': row.get('validation_errors', 0),
                        'content_length': row.get('content_length', 0),
                        'word_count': row.get('word_count', 0),
                        'created_at': datetime.now()
                    })
                
                # Insert fact data
                stmt = text("""
                    INSERT INTO content_quality_fact 
                    (date_key, service_key, content_type_key, language_key, quality_score,
                     completeness_score, accuracy_score, freshness_score, validation_errors,
                     content_length, word_count, created_at)
                    VALUES (:date_key, :service_key, :content_type_key, :language_key, :quality_score,
                            :completeness_score, :accuracy_score, :freshness_score, :validation_errors,
                            :content_length, :word_count, :created_at)
                """)
                
                session.execute(stmt, fact_data)
                session.commit()
                
            logger.info(f"Loaded {len(fact_data)} records into content_quality_fact")
            
        except Exception as e:
            logger.error(f"Error loading content quality fact data: {e}")
            raise
    
    def load_document_processing_fact(self, df: pd.DataFrame) -> None:
        """Load data into document_processing_fact table."""
        try:
            if df.empty:
                return
            
            with self.warehouse_session() as session:
                # Get dimension keys
                service_keys = self.get_service_keys(df['service_id'].unique())
                date_keys = self.get_date_keys([datetime.now().date()])
                content_type_keys = self.get_content_type_keys(df['content_type'].unique())
                language_keys = self.get_language_keys(df['language'].unique())
                
                # Prepare fact data
                fact_data = []
                for _, row in df.iterrows():
                    fact_data.append({
                        'date_key': date_keys[datetime.now().date()],
                        'service_key': service_keys.get(row['service_id'], 1),
                        'content_type_key': content_type_keys.get(row['content_type'], 1),
                        'language_key': language_keys.get(row['language'], 1),
                        'documents_processed': 1,
                        'successful_extractions': 1 if row['chunk_count'] > 0 else 0,
                        'failed_extractions': 0 if row['chunk_count'] > 0 else 1,
                        'avg_processing_time_ms': row.get('avg_chunk_length', 1000),
                        'ocr_accuracy_score': row.get('ocr_accuracy', 90),
                        'classification_accuracy': row.get('classification_accuracy', 95),
                        'created_at': datetime.now()
                    })
                
                # Insert fact data
                stmt = text("""
                    INSERT INTO document_processing_fact 
                    (date_key, service_key, content_type_key, language_key, documents_processed,
                     successful_extractions, failed_extractions, avg_processing_time_ms,
                     ocr_accuracy_score, classification_accuracy, created_at)
                    VALUES (:date_key, :service_key, :content_type_key, :language_key, :documents_processed,
                            :successful_extractions, :failed_extractions, :avg_processing_time_ms,
                            :ocr_accuracy_score, :classification_accuracy, :created_at)
                """)
                
                session.execute(stmt, fact_data)
                session.commit()
                
            logger.info(f"Loaded {len(fact_data)} records into document_processing_fact")
            
        except Exception as e:
            logger.error(f"Error loading document processing fact data: {e}")
            raise
    
    def get_service_keys(self, service_ids: List[int]) -> Dict[int, int]:
        """Get service keys for given service IDs."""
        try:
            with self.warehouse_session() as session:
                query = "SELECT service_id, service_key FROM service_dim WHERE service_id = ANY(:service_ids)"
                result = session.execute(text(query), {'service_ids': service_ids})
                return {row[0]: row[1] for row in result.fetchall()}
        except Exception as e:
            logger.error(f"Error getting service keys: {e}")
            return {}
    
    def get_date_keys(self, dates: List[datetime]) -> Dict[datetime, int]:
        """Get date keys for given dates."""
        try:
            with self.warehouse_session() as session:
                date_strings = [d.strftime('%Y-%m-%d') for d in dates]
                query = "SELECT full_date, date_key FROM date_dim WHERE full_date = ANY(:dates)"
                result = session.execute(text(query), {'dates': date_strings})
                return {datetime.strptime(row[0], '%Y-%m-%d').date(): row[1] for row in result.fetchall()}
        except Exception as e:
            logger.error(f"Error getting date keys: {e}")
            return {}
    
    def get_content_type_keys(self, content_types: List[str]) -> Dict[str, int]:
        """Get content type keys for given content types."""
        try:
            with self.warehouse_session() as session:
                query = "SELECT content_type, content_type_key FROM content_type_dim WHERE content_type = ANY(:content_types)"
                result = session.execute(text(query), {'content_types': content_types})
                return {row[0]: row[1] for row in result.fetchall()}
        except Exception as e:
            logger.error(f"Error getting content type keys: {e}")
            return {}
    
    def get_language_keys(self, languages: List[str]) -> Dict[str, int]:
        """Get language keys for given languages."""
        try:
            with self.warehouse_session() as session:
                query = "SELECT language_code, language_key FROM language_dim WHERE language_code = ANY(:languages)"
                result = session.execute(text(query), {'languages': languages})
                return {row[0]: row[1] for row in result.fetchall()}
        except Exception as e:
            logger.error(f"Error getting language keys: {e}")
            return {}
    
    def get_endpoint_keys(self, endpoints: List[str]) -> Dict[str, int]:
        """Get endpoint keys for given endpoints."""
        try:
            with self.warehouse_session() as session:
                query = "SELECT endpoint_name, endpoint_key FROM endpoint_dim WHERE endpoint_name = ANY(:endpoints)"
                result = session.execute(text(query), {'endpoints': endpoints})
                return {row[0]: row[1] for row in result.fetchall()}
        except Exception as e:
            logger.error(f"Error getting endpoint keys: {e}")
            return {}
    
    def load_all_data(self, transformation_results: Dict[str, pd.DataFrame]) -> None:
        """Load all transformed data into warehouse tables."""
        logger.info("Starting data loading")
        
        try:
            # Load dimension data first
            if 'service_usage' in transformation_results:
                self.load_service_dimension(transformation_results['service_usage'])
            
            # Load fact data
            if 'service_usage' in transformation_results:
                self.load_service_usage_fact(transformation_results['service_usage'])
            
            if 'api_performance' in transformation_results:
                self.load_api_performance_fact(transformation_results['api_performance'])
            
            if 'content_quality' in transformation_results:
                self.load_content_quality_fact(transformation_results['content_quality'])
            
            if 'document_processing' in transformation_results:
                self.load_document_processing_fact(transformation_results['document_processing'])
            
            logger.info("Data loading completed successfully")
            
        except Exception as e:
            logger.error(f"Error in data loading: {e}")
            raise
    
    def close_connections(self):
        """Close database connections."""
        self.warehouse_engine.dispose()