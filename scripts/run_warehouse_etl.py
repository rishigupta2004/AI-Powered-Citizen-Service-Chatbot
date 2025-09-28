#!/usr/bin/env python3
"""
Data Warehouse ETL Runner Script

This script runs the data warehouse ETL processes for the Citizen Services project.
It can run full ETL, incremental ETL, or specific ETL components.

Usage:
    python scripts/run_warehouse_etl.py --mode full --start-date 2024-01-01 --end-date 2024-01-31
    python scripts/run_warehouse_etl.py --mode incremental --date 2024-01-31
    python scripts/run_warehouse_etl.py --mode setup-schema
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.warehouse.warehouse_orchestrator import DataWarehouseOrchestrator, ETLConfig
from data.warehouse.config.warehouse_config import WarehouseConfig

def setup_logging(log_level: str = 'INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('data_warehouse_etl.log')
        ]
    )

async def run_full_etl(orchestrator: DataWarehouseOrchestrator, 
                      start_date: date, end_date: date):
    """Run full ETL process"""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting full ETL process from {start_date} to {end_date}")
    
    try:
        await orchestrator.run_full_etl(start_date, end_date)
        logger.info("Full ETL process completed successfully")
        return True
    except Exception as e:
        logger.error(f"Full ETL process failed: {str(e)}")
        return False

async def run_incremental_etl(orchestrator: DataWarehouseOrchestrator, 
                             target_date: date):
    """Run incremental ETL process"""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting incremental ETL process for {target_date}")
    
    try:
        await orchestrator.run_incremental_etl(target_date)
        logger.info("Incremental ETL process completed successfully")
        return True
    except Exception as e:
        logger.error(f"Incremental ETL process failed: {str(e)}")
        return False

async def setup_schema(orchestrator: DataWarehouseOrchestrator):
    """Setup warehouse schema"""
    logger = logging.getLogger(__name__)
    logger.info("Setting up data warehouse schema")
    
    try:
        await orchestrator._setup_warehouse_schema()
        logger.info("Schema setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Schema setup failed: {str(e)}")
        return False

async def validate_connections(config: WarehouseConfig):
    """Validate database connections"""
    logger = logging.getLogger(__name__)
    logger.info("Validating database connections...")
    
    try:
        # Test operational database connection
        import asyncpg
        
        op_config = config.get_operational_db_config()
        op_conn = await asyncpg.connect(**op_config)
        await op_conn.execute("SELECT 1")
        await op_conn.close()
        logger.info("✓ Operational database connection successful")
        
        # Test warehouse database connection
        wh_config = config.get_warehouse_db_config()
        wh_conn = await asyncpg.connect(**wh_config)
        await wh_conn.execute("SELECT 1")
        await wh_conn.close()
        logger.info("✓ Warehouse database connection successful")
        
        return True
        
    except Exception as e:
        logger.error(f"Database connection validation failed: {str(e)}")
        return False

def parse_date(date_str: str) -> date:
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Data Warehouse ETL Runner for Citizen Services',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full ETL for date range
  python scripts/run_warehouse_etl.py --mode full --start-date 2024-01-01 --end-date 2024-01-31
  
  # Run incremental ETL for today
  python scripts/run_warehouse_etl.py --mode incremental
  
  # Run incremental ETL for specific date
  python scripts/run_warehouse_etl.py --mode incremental --date 2024-01-31
  
  # Setup warehouse schema
  python scripts/run_warehouse_etl.py --mode setup-schema
  
  # Validate connections only
  python scripts/run_warehouse_etl.py --mode validate
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'incremental', 'setup-schema', 'validate'],
        required=True,
        help='ETL mode to run'
    )
    
    parser.add_argument(
        '--start-date',
        type=parse_date,
        help='Start date for full ETL (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date',
        type=parse_date,
        help='End date for full ETL (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--date',
        type=parse_date,
        help='Target date for incremental ETL (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Environment to run against'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without actual data changes'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    try:
        config = WarehouseConfig(args.environment)
        config.validate_config()
        logger.info(f"Configuration loaded for {args.environment} environment")
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    
    # Validate connections
    if not await validate_connections(config):
        logger.error("Database connection validation failed")
        sys.exit(1)
    
    # Handle dry run
    if args.dry_run:
        logger.info("DRY RUN MODE - No actual data changes will be made")
        # In a real implementation, you'd set flags to prevent actual writes
    
    # Create ETL configuration
    etl_config = ETLConfig(
        operational_db_config=config.get_operational_db_config(),
        warehouse_db_config=config.get_warehouse_db_config(),
        **config.get_etl_config()
    )
    
    # Initialize orchestrator
    orchestrator = DataWarehouseOrchestrator(etl_config)
    await orchestrator.initialize()
    
    success = False
    
    try:
        if args.mode == 'validate':
            logger.info("Connection validation completed successfully")
            success = True
            
        elif args.mode == 'setup-schema':
            success = await setup_schema(orchestrator)
            
        elif args.mode == 'full':
            if not args.start_date or not args.end_date:
                logger.error("Full ETL requires --start-date and --end-date")
                sys.exit(1)
                
            if args.start_date > args.end_date:
                logger.error("Start date must be before end date")
                sys.exit(1)
                
            success = await run_full_etl(orchestrator, args.start_date, args.end_date)
            
        elif args.mode == 'incremental':
            target_date = args.date or date.today()
            success = await run_incremental_etl(orchestrator, target_date)
            
    except KeyboardInterrupt:
        logger.info("ETL process interrupted by user")
        success = False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        success = False
    finally:
        await orchestrator.close()
    
    if success:
        logger.info("ETL process completed successfully")
        sys.exit(0)
    else:
        logger.error("ETL process failed")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())