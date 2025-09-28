from .base_loader import BaseLoader
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class FactLoader(BaseLoader):
    """Load data into fact tables"""
    
    def __init__(self, connection_config: Dict):
        super().__init__(connection_config)
        
    async def load_service_usage_facts(self, transformed_data: List[Dict]) -> bool:
        """Load service usage facts with incremental processing"""
        self.start_load()
        
        try:
            if not transformed_data:
                logger.info("No service usage facts to load")
                return True
                
            # Batch insert with conflict resolution
            inserted = await self.bulk_insert('fact_service_usage', transformed_data, 'IGNORE')
            
            logger.info(f"Loaded {inserted} service usage fact records")
            
            await self.log_etl_process(
                'load_service_usage_facts',
                'SUCCESS',
                f"Loaded {inserted} fact records"
            )
            
            self.end_load('load_service_usage_facts')
            return True
            
        except Exception as e:
            logger.error(f"Failed to load service usage facts: {str(e)}")
            await self.log_etl_process(
                'load_service_usage_facts',
                'FAILED',
                error_details=str(e)
            )
            return False
            
    async def load_data_quality_facts(self, transformed_data: List[Dict]) -> bool:
        """Load data quality facts"""
        self.start_load()
        
        try:
            if not transformed_data:
                logger.info("No data quality facts to load")
                return True
                
            inserted = await self.bulk_insert('fact_data_quality', transformed_data, 'IGNORE')
            
            logger.info(f"Loaded {inserted} data quality fact records")
            
            await self.log_etl_process(
                'load_data_quality_facts',
                'SUCCESS',
                f"Loaded {inserted} fact records"
            )
            
            self.end_load('load_data_quality_facts')
            return True
            
        except Exception as e:
            logger.error(f"Failed to load data quality facts: {str(e)}")
            await self.log_etl_process(
                'load_data_quality_facts',
                'FAILED',
                error_details=str(e)
            )
            return False
            
    async def load_content_analytics_facts(self, transformed_data: List[Dict]) -> bool:
        """Load content analytics facts"""
        self.start_load()
        
        try:
            if not transformed_data:
                logger.info("No content analytics facts to load")
                return True
                
            inserted = await self.bulk_insert('fact_content_analytics', transformed_data, 'IGNORE')
            
            logger.info(f"Loaded {inserted} content analytics fact records")
            
            await self.log_etl_process(
                'load_content_analytics_facts',
                'SUCCESS',
                f"Loaded {inserted} fact records"
            )
            
            self.end_load('load_content_analytics_facts')
            return True
            
        except Exception as e:
            logger.error(f"Failed to load content analytics facts: {str(e)}")
            await self.log_etl_process(
                'load_content_analytics_facts',
                'FAILED',
                error_details=str(e)
            )
            return False
            
    async def aggregate_daily_facts(self, target_date: str) -> bool:
        """Aggregate facts for a specific date"""
        self.start_load()
        
        try:
            # Aggregate service usage by service and date
            aggregation_query = """
            INSERT INTO dwh.fact_service_usage_daily_agg 
            (service_key, date_key, total_queries, total_successes, 
             avg_response_time, total_documents, avg_satisfaction)
            SELECT 
                service_key,
                date_key,
                SUM(query_count) as total_queries,
                SUM(success_count) as total_successes,
                AVG(avg_response_time_ms) as avg_response_time,
                SUM(total_documents_served) as total_documents,
                AVG(satisfaction_score) as avg_satisfaction
            FROM dwh.fact_service_usage
            WHERE date_key = $1
            GROUP BY service_key, date_key
            ON CONFLICT (service_key, date_key) DO UPDATE SET
                total_queries = EXCLUDED.total_queries,
                total_successes = EXCLUDED.total_successes,
                avg_response_time = EXCLUDED.avg_response_time,
                total_documents = EXCLUDED.total_documents,
                avg_satisfaction = EXCLUDED.avg_satisfaction,
                updated_at = CURRENT_TIMESTAMP
            """
            
            date_key = int(target_date.replace('-', ''))
            success = await self.execute_query(aggregation_query, date_key)
            
            if success:
                logger.info(f"Successfully aggregated facts for date {target_date}")
                
                await self.log_etl_process(
                    'aggregate_daily_facts',
                    'SUCCESS',
                    f"Aggregated facts for {target_date}"
                )
            else:
                raise Exception("Aggregation query failed")
                
            self.end_load('aggregate_daily_facts')
            return success
            
        except Exception as e:
            logger.error(f"Failed to aggregate daily facts: {str(e)}")
            await self.log_etl_process(
                'aggregate_daily_facts',
                'FAILED',
                error_details=str(e)
            )
            return False
            
    async def cleanup_old_facts(self, retention_days: int = 365) -> bool:
        """Clean up old fact records beyond retention period"""
        self.start_load()
        
        try:
            # Calculate cutoff date
            cutoff_query = """
            DELETE FROM dwh.fact_service_usage 
            WHERE created_at < CURRENT_DATE - INTERVAL '%s days'
            """
            
            success = await self.execute_query(cutoff_query % retention_days)
            
            if success:
                logger.info(f"Cleaned up fact records older than {retention_days} days")
                
                await self.log_etl_process(
                    'cleanup_old_facts',
                    'SUCCESS',
                    f"Cleaned records older than {retention_days} days"
                )
            else:
                raise Exception("Cleanup query failed")
                
            self.end_load('cleanup_old_facts')
            return success
            
        except Exception as e:
            logger.error(f"Failed to cleanup old facts: {str(e)}")
            await self.log_etl_process(
                'cleanup_old_facts',
                'FAILED',
                error_details=str(e)
            )
            return False