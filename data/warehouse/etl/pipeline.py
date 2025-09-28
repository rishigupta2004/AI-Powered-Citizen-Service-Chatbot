"""
Main ETL pipeline orchestrator for the data warehouse.
Coordinates extraction, transformation, and loading processes.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from .extract import DataExtractor
from .transform import DataTransformer
from .load import DataLoader

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ETLPipeline:
    """Main ETL pipeline orchestrator."""
    
    def __init__(self, 
                 operational_db_url: str = None,
                 warehouse_db_url: str = None):
        """
        Initialize ETL pipeline with database connections.
        
        Args:
            operational_db_url: URL for operational database
            warehouse_db_url: URL for warehouse database
        """
        self.operational_db_url = operational_db_url or os.getenv("OPERATIONAL_DATABASE_URL")
        self.warehouse_db_url = warehouse_db_url or os.getenv("WAREHOUSE_DATABASE_URL")
        
        if not self.operational_db_url or not self.warehouse_db_url:
            raise ValueError("Database URLs must be provided or set in environment variables")
        
        # Initialize ETL components
        self.extractor = DataExtractor(self.operational_db_url, self.warehouse_db_url)
        self.transformer = DataTransformer(self.warehouse_db_url)
        self.loader = DataLoader(self.warehouse_db_url)
        
        logger.info("ETL Pipeline initialized successfully")
    
    def run_full_pipeline(self, 
                         start_date: datetime = None, 
                         end_date: datetime = None) -> Dict[str, Any]:
        """
        Run the complete ETL pipeline.
        
        Args:
            start_date: Start date for data extraction (default: yesterday)
            end_date: End date for data extraction (default: today)
        
        Returns:
            Dictionary containing pipeline execution results
        """
        try:
            # Set default dates if not provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=1)
            if not end_date:
                end_date = datetime.now()
            
            logger.info(f"Starting ETL pipeline from {start_date} to {end_date}")
            
            # Step 1: Extract data
            logger.info("Step 1: Extracting data from operational database")
            extraction_results = self.extractor.extract_all_data(start_date, end_date)
            
            # Step 2: Transform data
            logger.info("Step 2: Transforming data for warehouse format")
            transformation_results = self.transformer.transform_all_data(extraction_results)
            
            # Step 3: Load data
            logger.info("Step 3: Loading data into warehouse tables")
            self.loader.load_all_data(transformation_results)
            
            # Step 4: Update aggregated tables
            logger.info("Step 4: Updating aggregated tables")
            self.update_aggregated_tables()
            
            # Step 5: Data quality validation
            logger.info("Step 5: Running data quality validation")
            quality_results = self.validate_data_quality()
            
            # Prepare results
            results = {
                'status': 'success',
                'start_date': start_date,
                'end_date': end_date,
                'extraction_counts': {k: len(v) for k, v in extraction_results.items()},
                'transformation_counts': {k: len(v) for k, v in transformation_results.items()},
                'quality_results': quality_results,
                'execution_time': datetime.now(),
                'errors': []
            }
            
            logger.info("ETL pipeline completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'execution_time': datetime.now()
            }
        finally:
            # Clean up connections
            self.cleanup()
    
    def run_incremental_pipeline(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Run incremental ETL pipeline for recent data.
        
        Args:
            hours_back: Number of hours to look back for data
        
        Returns:
            Dictionary containing pipeline execution results
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours_back)
        
        logger.info(f"Running incremental ETL pipeline for last {hours_back} hours")
        return self.run_full_pipeline(start_date, end_date)
    
    def run_daily_pipeline(self) -> Dict[str, Any]:
        """Run daily ETL pipeline for yesterday's data."""
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        logger.info("Running daily ETL pipeline")
        return self.run_full_pipeline(start_date, end_date)
    
    def update_aggregated_tables(self) -> None:
        """Update aggregated tables with latest data."""
        try:
            with self.loader.warehouse_session() as session:
                # Update daily service summary
                session.execute("""
                    INSERT INTO daily_service_summary 
                    (date_key, service_key, total_requests, successful_requests, failed_requests,
                     avg_response_time_ms, max_response_time_ms, unique_users, content_updates, avg_quality_score)
                    SELECT 
                        suf.date_key,
                        suf.service_key,
                        SUM(suf.usage_count) as total_requests,
                        SUM(suf.success_count) as successful_requests,
                        SUM(suf.error_count) as failed_requests,
                        AVG(suf.response_time_ms) as avg_response_time_ms,
                        MAX(suf.response_time_ms) as max_response_time_ms,
                        COUNT(DISTINCT suf.user_key) as unique_users,
                        0 as content_updates, -- Placeholder
                        AVG(cqf.quality_score) as avg_quality_score
                    FROM service_usage_fact suf
                    LEFT JOIN content_quality_fact cqf ON suf.service_key = cqf.service_key 
                        AND suf.date_key = cqf.date_key
                    WHERE suf.date_key = EXTRACT(EPOCH FROM CURRENT_DATE)::INTEGER
                    GROUP BY suf.date_key, suf.service_key
                    ON CONFLICT (date_key, service_key) 
                    DO UPDATE SET
                        total_requests = EXCLUDED.total_requests,
                        successful_requests = EXCLUDED.successful_requests,
                        failed_requests = EXCLUDED.failed_requests,
                        avg_response_time_ms = EXCLUDED.avg_response_time_ms,
                        max_response_time_ms = EXCLUDED.max_response_time_ms,
                        unique_users = EXCLUDED.unique_users,
                        avg_quality_score = EXCLUDED.avg_quality_score,
                        updated_at = CURRENT_TIMESTAMP
                """)
                
                # Update weekly content analytics
                session.execute("""
                    INSERT INTO weekly_content_analytics 
                    (week_key, service_key, content_type_key, language_key, total_content_items,
                     new_content_items, updated_content_items, avg_quality_score, multilingual_coverage,
                     completeness_percentage, avg_processing_time_ms)
                    SELECT 
                        EXTRACT(YEAR FROM dd.full_date) * 100 + EXTRACT(WEEK FROM dd.full_date) as week_key,
                        cqf.service_key,
                        cqf.content_type_key,
                        cqf.language_key,
                        COUNT(*) as total_content_items,
                        COUNT(*) as new_content_items, -- Simplified
                        0 as updated_content_items, -- Placeholder
                        AVG(cqf.quality_score) as avg_quality_score,
                        COUNT(DISTINCT cqf.language_key) * 100.0 / COUNT(*) as multilingual_coverage,
                        AVG(cqf.completeness_score) as completeness_percentage,
                        AVG(dpf.avg_processing_time_ms) as avg_processing_time_ms
                    FROM content_quality_fact cqf
                    JOIN date_dim dd ON cqf.date_key = dd.date_key
                    LEFT JOIN document_processing_fact dpf ON cqf.service_key = dpf.service_key 
                        AND cqf.date_key = dpf.date_key
                    WHERE dd.full_date >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY week_key, cqf.service_key, cqf.content_type_key, cqf.language_key
                    ON CONFLICT (week_key, service_key, content_type_key, language_key)
                    DO UPDATE SET
                        total_content_items = EXCLUDED.total_content_items,
                        new_content_items = EXCLUDED.new_content_items,
                        avg_quality_score = EXCLUDED.avg_quality_score,
                        multilingual_coverage = EXCLUDED.multilingual_coverage,
                        completeness_percentage = EXCLUDED.completeness_percentage,
                        avg_processing_time_ms = EXCLUDED.avg_processing_time_ms
                """)
                
                session.commit()
                logger.info("Aggregated tables updated successfully")
                
        except Exception as e:
            logger.error(f"Error updating aggregated tables: {e}")
            raise
    
    def validate_data_quality(self) -> Dict[str, Any]:
        """Validate data quality in the warehouse."""
        try:
            quality_results = {}
            
            with self.loader.warehouse_session() as session:
                # Check for missing dimension keys
                missing_service_keys = session.execute("""
                    SELECT COUNT(*) FROM service_usage_fact suf
                    LEFT JOIN service_dim sd ON suf.service_key = sd.service_key
                    WHERE sd.service_key IS NULL
                """).scalar()
                
                # Check for data completeness
                incomplete_records = session.execute("""
                    SELECT COUNT(*) FROM content_quality_fact
                    WHERE quality_score IS NULL OR completeness_score IS NULL
                """).scalar()
                
                # Check for data freshness
                stale_data = session.execute("""
                    SELECT COUNT(*) FROM service_usage_fact
                    WHERE created_at < CURRENT_DATE - INTERVAL '7 days'
                """).scalar()
                
                quality_results = {
                    'missing_service_keys': missing_service_keys,
                    'incomplete_records': incomplete_records,
                    'stale_data_records': stale_data,
                    'overall_quality_score': max(0, 100 - (missing_service_keys + incomplete_records + stale_data))
                }
                
            logger.info(f"Data quality validation completed: {quality_results}")
            return quality_results
            
        except Exception as e:
            logger.error(f"Error validating data quality: {e}")
            return {'error': str(e)}
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and statistics."""
        try:
            with self.loader.warehouse_session() as session:
                # Get record counts
                service_count = session.execute("SELECT COUNT(*) FROM service_dim").scalar()
                usage_count = session.execute("SELECT COUNT(*) FROM service_usage_fact").scalar()
                quality_count = session.execute("SELECT COUNT(*) FROM content_quality_fact").scalar()
                
                # Get last update time
                last_update = session.execute("""
                    SELECT MAX(created_at) FROM service_usage_fact
                """).scalar()
                
                return {
                    'service_count': service_count,
                    'usage_records': usage_count,
                    'quality_records': quality_count,
                    'last_update': last_update,
                    'status': 'healthy'
                }
                
        except Exception as e:
            logger.error(f"Error getting pipeline status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def cleanup(self) -> None:
        """Clean up database connections."""
        try:
            self.extractor.close_connections()
            self.transformer.close_connections()
            self.loader.close_connections()
            logger.info("Pipeline cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Convenience function for running the pipeline
def run_etl_pipeline(start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
    """
    Convenience function to run the ETL pipeline.
    
    Args:
        start_date: Start date for data extraction
        end_date: End date for data extraction
    
    Returns:
        Dictionary containing pipeline execution results
    """
    pipeline = ETLPipeline()
    return pipeline.run_full_pipeline(start_date, end_date)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the pipeline
    results = run_etl_pipeline()
    print(f"ETL Pipeline Results: {results}")