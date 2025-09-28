"""
ETL Orchestrator for data warehouse operations.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, date
import yaml
import os
from pathlib import Path

from .base_etl import ETLOrchestrator
from .loaders.dimension_loader import (
    ServiceDimensionLoader,
    UserDimensionLoader,
    ContentDimensionLoader,
    QueryTypeDimensionLoader,
    LanguageDimensionLoader
)

logger = logging.getLogger(__name__)

class DataWarehouseOrchestrator:
    """Main orchestrator for data warehouse ETL operations."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.orchestrator = ETLOrchestrator(self.config)
        self._setup_etl_processes()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        return os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'warehouse_config.yaml')
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'source': {
                'url': os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/citizen_services'),
                'echo': False
            },
            'target': {
                'url': os.getenv('WAREHOUSE_DATABASE_URL', 'postgresql://user:password@localhost/citizen_services_warehouse'),
                'echo': False
            },
            'quality': {
                'quality_rules': {
                    'dim_service': {
                        'not_null_service_name': {
                            'type': 'not_null',
                            'column': 'service_name'
                        },
                        'not_null_service_category': {
                            'type': 'not_null',
                            'column': 'service_category'
                        }
                    },
                    'dim_user': {
                        'not_null_user_type': {
                            'type': 'not_null',
                            'column': 'user_type'
                        }
                    }
                }
            }
        }
    
    def _setup_etl_processes(self):
        """Set up all ETL processes."""
        source_config = self.config['source']
        target_config = self.config['target']
        
        # Add dimension loaders
        self.orchestrator.add_etl_process(
            ServiceDimensionLoader(source_config, target_config)
        )
        self.orchestrator.add_etl_process(
            UserDimensionLoader(source_config, target_config)
        )
        self.orchestrator.add_etl_process(
            ContentDimensionLoader(source_config, target_config)
        )
        self.orchestrator.add_etl_process(
            QueryTypeDimensionLoader(source_config, target_config)
        )
        self.orchestrator.add_etl_process(
            LanguageDimensionLoader(source_config, target_config)
        )
        
        logger.info(f"Set up {len(self.orchestrator.etl_processes)} ETL processes")
    
    async def run_dimension_loads(self, **kwargs) -> Dict[str, Any]:
        """Run dimension table loads."""
        logger.info("Starting dimension table loads")
        
        # Set SCD type for dimension loads
        kwargs['scd_type'] = 1  # Type 1 for now
        
        result = await self.orchestrator.run_all(**kwargs)
        
        logger.info(f"Dimension loads completed. Success: {result['overall_success']}")
        return result
    
    async def run_incremental_load(self, start_date: date, end_date: date, **kwargs) -> Dict[str, Any]:
        """Run incremental data load for specified date range."""
        logger.info(f"Starting incremental load from {start_date} to {end_date}")
        
        kwargs.update({
            'start_date': start_date,
            'end_date': end_date,
            'load_type': 'append'
        })
        
        result = await self.orchestrator.run_all(**kwargs)
        
        logger.info(f"Incremental load completed. Success: {result['overall_success']}")
        return result
    
    async def run_full_refresh(self, **kwargs) -> Dict[str, Any]:
        """Run full data warehouse refresh."""
        logger.info("Starting full warehouse refresh")
        
        kwargs.update({
            'load_type': 'replace'
        })
        
        result = await self.orchestrator.run_all(**kwargs)
        
        logger.info(f"Full refresh completed. Success: {result['overall_success']}")
        return result
    
    def get_etl_status(self) -> Dict[str, Any]:
        """Get status of ETL processes."""
        return {
            'total_processes': len(self.orchestrator.etl_processes),
            'process_names': [process.__class__.__name__ for process in self.orchestrator.etl_processes],
            'last_run': None,  # Would be tracked in production
            'status': 'ready'
        }

async def main():
    """Main function for running ETL operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Warehouse ETL Orchestrator')
    parser.add_argument('--operation', choices=['dimensions', 'incremental', 'full_refresh'], 
                       default='dimensions', help='ETL operation to run')
    parser.add_argument('--start-date', type=str, help='Start date for incremental load (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for incremental load (YYYY-MM-DD)')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize orchestrator
    orchestrator = DataWarehouseOrchestrator(args.config)
    
    try:
        if args.operation == 'dimensions':
            result = await orchestrator.run_dimension_loads()
        elif args.operation == 'incremental':
            if not args.start_date or not args.end_date:
                raise ValueError("Start date and end date are required for incremental load")
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
            result = await orchestrator.run_incremental_load(start_date, end_date)
        elif args.operation == 'full_refresh':
            result = await orchestrator.run_full_refresh()
        
        print(f"ETL operation completed successfully: {result}")
        
    except Exception as e:
        logger.error(f"ETL operation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())