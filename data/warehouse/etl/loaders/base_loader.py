from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
import asyncpg
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseLoader(ABC):
    """Base class for all data loaders"""
    
    def __init__(self, connection_config: Dict, schema: str = "dwh"):
        self.connection_config = connection_config
        self.schema = schema
        self.db_pool = None
        self.load_stats = {
            'records_inserted': 0,
            'records_updated': 0,
            'records_failed': 0,
            'start_time': None,
            'end_time': None
        }
        
    async def _get_connection(self):
        """Get database connection pool"""
        if not self.db_pool:
            self.db_pool = await asyncpg.create_pool(**self.connection_config)
        return self.db_pool
        
    def start_load(self):
        """Mark start of load process"""
        self.load_stats['start_time'] = datetime.now()
        self.load_stats['records_inserted'] = 0
        self.load_stats['records_updated'] = 0
        self.load_stats['records_failed'] = 0
        
    def end_load(self, process_name: str):
        """Mark end of load process"""
        self.load_stats['end_time'] = datetime.now()
        duration = (self.load_stats['end_time'] - 
                   self.load_stats['start_time']).total_seconds()
                   
        logger.info(f"Load process '{process_name}' completed in {duration:.2f}s")
        logger.info(f"Inserted: {self.load_stats['records_inserted']}, "
                   f"Updated: {self.load_stats['records_updated']}, "
                   f"Failed: {self.load_stats['records_failed']}")
                   
    @abstractmethod
    async def load(self, data: List[Dict], **kwargs) -> bool:
        """Load data into target table"""
        pass
        
    async def bulk_insert(self, table_name: str, data: List[Dict], 
                         conflict_resolution: str = "IGNORE") -> int:
        """Perform bulk insert with conflict resolution"""
        if not data:
            return 0
            
        pool = await self._get_connection()
        
        # Get column names from first record
        columns = list(data[0].keys())
        column_list = ", ".join(columns)
        placeholders = ", ".join(f"${i+1}" for i in range(len(columns)))
        
        # Build the INSERT statement
        if conflict_resolution == "IGNORE":
            query = f"""
            INSERT INTO {self.schema}.{table_name} ({column_list})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
            """
        elif conflict_resolution == "UPDATE":
            # For upsert, assume first column is the key
            key_column = columns[0]
            update_columns = ", ".join(f"{col} = EXCLUDED.{col}" for col in columns[1:])
            query = f"""
            INSERT INTO {self.schema}.{table_name} ({column_list})
            VALUES ({placeholders})
            ON CONFLICT ({key_column}) DO UPDATE SET {update_columns}
            """
        else:
            query = f"""
            INSERT INTO {self.schema}.{table_name} ({column_list})
            VALUES ({placeholders})
            """
            
        inserted_count = 0
        async with pool.acquire() as conn:
            async with conn.transaction():
                for record in data:
                    try:
                        values = [record[col] for col in columns]
                        await conn.execute(query, *values)
                        inserted_count += 1
                    except Exception as e:
                        logger.error(f"Failed to insert record into {table_name}: {str(e)}")
                        self.load_stats['records_failed'] += 1
                        continue
                        
        self.load_stats['records_inserted'] += inserted_count
        return inserted_count
        
    async def execute_query(self, query: str, *args) -> bool:
        """Execute a query with parameters"""
        pool = await self._get_connection()
        
        try:
            async with pool.acquire() as conn:
                await conn.execute(query, *args)
            return True
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return False
            
    async def fetch_existing_records(self, table_name: str, 
                                   key_column: str, 
                                   key_values: List) -> Dict:
        """Fetch existing records for comparison"""
        if not key_values:
            return {}
            
        pool = await self._get_connection()
        placeholders = ", ".join(f"${i+1}" for i in range(len(key_values)))
        query = f"SELECT * FROM {self.schema}.{table_name} WHERE {key_column} IN ({placeholders})"
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *key_values)
            
        return {row[key_column]: dict(row) for row in rows}
        
    async def log_etl_process(self, process_name: str, status: str, 
                            message: str = "", error_details: str = ""):
        """Log ETL process execution"""
        pool = await self._get_connection()
        
        duration = 0
        if (self.load_stats['start_time'] and self.load_stats['end_time']):
            duration = int((self.load_stats['end_time'] - 
                          self.load_stats['start_time']).total_seconds())
            
        query = """
        INSERT INTO dwh.etl_log 
        (process_name, status, message, error_details, records_processed, processing_time_seconds)
        VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        total_processed = (self.load_stats['records_inserted'] + 
                          self.load_stats['records_updated'] + 
                          self.load_stats['records_failed'])
        
        async with pool.acquire() as conn:
            await conn.execute(query, process_name, status, message, 
                             error_details, total_processed, duration)
                             
    async def close(self):
        """Close database connections"""
        if self.db_pool:
            await self.db_pool.close()