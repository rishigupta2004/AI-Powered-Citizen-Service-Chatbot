import asyncio
import logging
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
from dataclasses import dataclass
import os

from .etl.extractors.service_extractor import ServiceDataExtractor
from .etl.transformers.dimension_transformer import DimensionTransformer
from .etl.transformers.fact_transformer import FactTransformer
from .etl.loaders.dimension_loader import DimensionLoader
from .etl.loaders.fact_loader import FactLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ETLConfig:
    """Configuration for ETL processes"""
    operational_db_config: Dict
    warehouse_db_config: Dict
    batch_size: int = 1000
    max_retries: int = 3
    parallel_workers: int = 4

class DataWarehouseOrchestrator:
    """Main orchestrator for data warehouse ETL processes"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.extractors = {}
        self.transformers = {}
        self.loaders = {}
        self.dimension_lookups = {}
        
    async def initialize(self):
        """Initialize all ETL components"""
        logger.info("Initializing Data Warehouse Orchestrator...")
        
        # Initialize extractors
        self.extractors['service'] = ServiceDataExtractor(self.config.operational_db_config)
        
        # Initialize transformers
        self.transformers['dimension'] = DimensionTransformer()
        self.transformers['fact'] = FactTransformer(self.dimension_lookups)
        
        # Initialize loaders
        self.loaders['dimension'] = DimensionLoader(self.config.warehouse_db_config)
        self.loaders['fact'] = FactLoader(self.config.warehouse_db_config)
        
        logger.info("Data Warehouse Orchestrator initialized successfully")
        
    async def run_full_etl(self, start_date: date = None, end_date: date = None):
        """Run complete ETL process for specified date range"""
        if not start_date:
            start_date = date.today() - timedelta(days=7)
        if not end_date:
            end_date = date.today()
            
        logger.info(f"Starting full ETL process for {start_date} to {end_date}")
        
        try:
            # Step 1: Create database schema if not exists
            await self._setup_warehouse_schema()
            
            # Step 2: Load dimensions (must be done before facts)
            await self._load_all_dimensions(start_date, end_date)
            
            # Step 3: Build dimension lookups
            await self._build_dimension_lookups()
            
            # Step 4: Load facts
            await self._load_all_facts(start_date, end_date)
            
            # Step 5: Refresh materialized views
            await self._refresh_materialized_views()
            
            # Step 6: Update ETL metadata
            await self._update_etl_metadata('full_etl', 'SUCCESS')
            
            logger.info("Full ETL process completed successfully")
            
        except Exception as e:
            logger.error(f"Full ETL process failed: {str(e)}")
            await self._update_etl_metadata('full_etl', 'FAILED', str(e))
            raise
            
    async def run_incremental_etl(self, target_date: date = None):
        """Run incremental ETL for a specific date"""
        if not target_date:
            target_date = date.today()
            
        logger.info(f"Starting incremental ETL for {target_date}")
        
        try:
            # Extract incremental data
            last_extraction = await self._get_last_extraction_time()
            
            # Load only changed dimensions
            await self._load_incremental_dimensions(last_extraction)
            
            # Rebuild lookups for new/changed dimensions
            await self._build_dimension_lookups()
            
            # Load incremental facts
            await self._load_incremental_facts(target_date)
            
            # Refresh materialized views
            await self._refresh_materialized_views()
            
            # Update metadata
            await self._update_etl_metadata('incremental_etl', 'SUCCESS')
            
            logger.info("Incremental ETL completed successfully")
            
        except Exception as e:
            logger.error(f"Incremental ETL failed: {str(e)}")
            await self._update_etl_metadata('incremental_etl', 'FAILED', str(e))
            raise
            
    async def _setup_warehouse_schema(self):
        """Create warehouse schema and tables"""
        logger.info("Setting up warehouse schema...")
        
        schema_file = os.path.join(os.path.dirname(__file__), 'schemas', 'dimensional_schema.sql')
        
        # Read and execute schema creation script
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
                
            # Execute schema creation (this would need proper connection handling)
            loader = self.loaders['dimension']
            await loader.execute_query(schema_sql)
            logger.info("Warehouse schema created successfully")
        else:
            logger.warning("Schema file not found, assuming schema already exists")
            
    async def _load_all_dimensions(self, start_date: date, end_date: date):
        """Load all dimension tables"""
        logger.info("Loading dimension tables...")
        
        dimension_loader = self.loaders['dimension']
        dimension_transformer = self.transformers['dimension']
        
        # 1. Load date dimension
        await dimension_loader.load_date_dimension(start_date, end_date)
        
        # 2. Load service dimension
        service_extractor = self.extractors['service']
        raw_services = await service_extractor.extract(end_date)
        transformed_services = dimension_transformer.transform_service_dimension(raw_services)
        await dimension_loader.load_service_dimension(transformed_services)
        
        # 3. Load other dimensions (static data)
        await self._load_static_dimensions(dimension_transformer, dimension_loader)
        
        logger.info("All dimensions loaded successfully")
        
    async def _load_static_dimensions(self, transformer: DimensionTransformer, 
                                    loader: DimensionLoader):
        """Load static dimension data"""
        
        # Load location dimension
        locations = transformer.transform_location_dimension([])
        await loader.load_simple_dimension('dim_location', locations)
        
        # Load user segment dimension
        user_segments = transformer.transform_user_segment_dimension()
        await loader.load_simple_dimension('dim_user_segment', user_segments)
        
        # Load channel dimension
        channels = transformer.transform_channel_dimension()
        await loader.load_simple_dimension('dim_channel', channels)
        
        # Load content type dimension
        content_types = transformer.transform_content_type_dimension()
        await loader.load_simple_dimension('dim_content_type', content_types)
        
        # Load language dimension
        languages = transformer.transform_language_dimension()
        await loader.load_simple_dimension('dim_language', languages)
        
        logger.info("Static dimensions loaded successfully")
        
    async def _build_dimension_lookups(self):
        """Build lookup dictionaries for dimension keys"""
        logger.info("Building dimension lookups...")
        
        # This would query the warehouse to build lookup tables
        # For now, we'll create simple mappings
        
        # Service lookups
        self.dimension_lookups['services'] = {}
        
        # Location lookups  
        self.dimension_lookups['locations'] = {
            'Delhi': 1,
            'Maharashtra': 2,
            'Karnataka': 3,
            'Unknown': 1
        }
        
        # Channel lookups
        self.dimension_lookups['channels'] = {
            'Web Portal': 1,
            'Mobile App': 2,
            'API': 3,
            'Call Center': 4
        }
        
        # Content type lookups
        self.dimension_lookups['content_types'] = {
            'FAQ': 1,
            'Procedure': 2,
            'Document': 3,
            'Form': 4
        }
        
        # Language lookups
        self.dimension_lookups['languages'] = {
            'en': 1,
            'hi': 2,
            'bn': 3,
            'ta': 4
        }
        
        # User segment lookups (simplified)
        self.dimension_lookups['user_segments'] = {}
        
        # Update fact transformer with lookups
        self.transformers['fact'].dimension_lookups = self.dimension_lookups
        
        logger.info("Dimension lookups built successfully")
        
    async def _load_all_facts(self, start_date: date, end_date: date):
        """Load all fact tables"""
        logger.info("Loading fact tables...")
        
        fact_transformer = self.transformers['fact']
        fact_loader = self.loaders['fact']
        service_extractor = self.extractors['service']
        
        # Get service IDs for fact generation
        services = await service_extractor.extract(end_date)
        service_ids = [s['service_id'] for s in services]
        
        # Generate sample usage facts
        sample_usage = fact_transformer.generate_sample_usage_facts(
            service_ids, (start_date, end_date)
        )
        
        # Transform and load usage facts
        usage_facts = fact_transformer.transform_service_usage_facts(sample_usage)
        await fact_loader.load_service_usage_facts(usage_facts)
        
        # Generate and load data quality facts
        quality_data = self._generate_sample_quality_data(service_ids, end_date)
        quality_facts = fact_transformer.transform_data_quality_facts(quality_data)
        await fact_loader.load_data_quality_facts(quality_facts)
        
        logger.info("All facts loaded successfully")
        
    async def _load_incremental_dimensions(self, last_extraction: datetime):
        """Load only changed dimensions"""
        logger.info("Loading incremental dimensions...")
        
        service_extractor = self.extractors['service']
        dimension_transformer = self.transformers['dimension']
        dimension_loader = self.loaders['dimension']
        
        # Get incremental service data
        incremental_services = await service_extractor.get_incremental_data(last_extraction)
        
        if incremental_services:
            transformed_services = dimension_transformer.transform_service_dimension(incremental_services)
            await dimension_loader.load_service_dimension(transformed_services)
            logger.info(f"Loaded {len(incremental_services)} incremental service records")
        else:
            logger.info("No incremental service data to load")
            
    async def _load_incremental_facts(self, target_date: date):
        """Load incremental facts for target date"""
        logger.info(f"Loading incremental facts for {target_date}")
        
        fact_transformer = self.transformers['fact']
        fact_loader = self.loaders['fact']
        
        # Generate sample data for the target date
        sample_usage = fact_transformer.generate_sample_usage_facts(
            [1, 2, 3], (target_date, target_date)  # Sample service IDs
        )
        
        usage_facts = fact_transformer.transform_service_usage_facts(sample_usage)
        await fact_loader.load_service_usage_facts(usage_facts)
        
        logger.info("Incremental facts loaded successfully")
        
    async def _refresh_materialized_views(self):
        """Refresh all materialized views"""
        logger.info("Refreshing materialized views...")
        
        loader = self.loaders['dimension']
        
        refresh_query = "SELECT dwh.refresh_all_materialized_views()"
        success = await loader.execute_query(refresh_query)
        
        if success:
            logger.info("Materialized views refreshed successfully")
        else:
            logger.error("Failed to refresh materialized views")
            
    async def _get_last_extraction_time(self) -> datetime:
        """Get timestamp of last successful ETL run"""
        # This would query ETL metadata table
        # For now, return yesterday
        return datetime.now() - timedelta(days=1)
        
    async def _update_etl_metadata(self, process_name: str, status: str, 
                                 error_details: str = ""):
        """Update ETL process metadata"""
        loader = self.loaders['dimension']
        await loader.log_etl_process(process_name, status, 
                                   f"ETL process {status.lower()}", 
                                   error_details)
                                   
    def _generate_sample_quality_data(self, service_ids: List[int], 
                                    check_date: date) -> List[Dict]:
        """Generate sample data quality metrics"""
        import random
        
        quality_data = []
        
        sources = ['APISetu', 'Website Scraping', 'Manual Entry']
        
        for service_id in service_ids:
            for source in sources:
                total_records = random.randint(100, 1000)
                valid_records = int(total_records * random.uniform(0.85, 0.98))
                
                quality_record = {
                    'source_name': source,
                    'service_id': service_id,
                    'check_date': check_date,
                    'total_records': total_records,
                    'new_records': random.randint(5, 50),
                    'updated_records': random.randint(1, 20),
                    'valid_records': valid_records,
                    'duplicate_records': random.randint(0, 10),
                    'accuracy_score': random.uniform(0.90, 0.99),
                    'consistency_score': random.uniform(0.85, 0.95),
                    'freshness_hours': random.randint(1, 48),
                    'processing_time': random.randint(10, 300),
                    'error_count': random.randint(0, 5)
                }
                
                quality_data.append(quality_record)
                
        return quality_data
        
    async def close(self):
        """Close all connections and cleanup"""
        logger.info("Closing Data Warehouse Orchestrator...")
        
        for extractor in self.extractors.values():
            if hasattr(extractor, 'close'):
                await extractor.close()
                
        for loader in self.loaders.values():
            if hasattr(loader, 'close'):
                await loader.close()
                
        logger.info("Data Warehouse Orchestrator closed successfully")