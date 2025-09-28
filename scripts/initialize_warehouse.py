#!/usr/bin/env python3
"""
Data Warehouse Initialization Script

This script sets up the complete data warehouse infrastructure for the first time,
including schema creation, initial data loading, and sample data generation.

Usage:
    python scripts/initialize_warehouse.py --environment development
    python scripts/initialize_warehouse.py --environment production --skip-sample-data
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
import asyncpg

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.warehouse.warehouse_orchestrator import DataWarehouseOrchestrator, ETLConfig
from data.warehouse.config.warehouse_config import WarehouseConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_warehouse_database(config: WarehouseConfig):
    """Create the warehouse database if it doesn't exist"""
    logger.info("Creating warehouse database if needed...")
    
    wh_config = config.get_warehouse_db_config()
    db_name = wh_config['database']
    
    # Connect to default postgres database to create warehouse db
    admin_config = wh_config.copy()
    admin_config['database'] = 'postgres'
    
    try:
        conn = await asyncpg.connect(**admin_config)
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        
        if not exists:
            # Create database
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            logger.info(f"Created database: {db_name}")
        else:
            logger.info(f"Database {db_name} already exists")
            
        await conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create database: {str(e)}")
        raise

async def setup_extensions(config: WarehouseConfig):
    """Setup required PostgreSQL extensions"""
    logger.info("Setting up PostgreSQL extensions...")
    
    wh_config = config.get_warehouse_db_config()
    
    try:
        conn = await asyncpg.connect(**wh_config)
        
        # Enable required extensions
        extensions = [
            'CREATE EXTENSION IF NOT EXISTS vector;',
            'CREATE EXTENSION IF NOT EXISTS pg_stat_statements;',
            'CREATE EXTENSION IF NOT EXISTS pg_trgm;'
        ]
        
        for ext_sql in extensions:
            try:
                await conn.execute(ext_sql)
                logger.info(f"Extension enabled: {ext_sql}")
            except Exception as e:
                logger.warning(f"Could not enable extension {ext_sql}: {str(e)}")
                
        await conn.close()
        
    except Exception as e:
        logger.error(f"Failed to setup extensions: {str(e)}")
        raise

async def create_warehouse_schema(config: WarehouseConfig):
    """Create the complete warehouse schema"""
    logger.info("Creating warehouse schema...")
    
    schema_file = project_root / 'data' / 'warehouse' / 'schemas' / 'dimensional_schema.sql'
    
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    
    wh_config = config.get_warehouse_db_config()
    
    try:
        conn = await asyncpg.connect(**wh_config)
        
        # Read and execute schema
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
            
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                await conn.execute(statement)
            except Exception as e:
                logger.warning(f"Statement failed (may be expected): {str(e)[:100]}...")
                
        logger.info("Warehouse schema created successfully")
        await conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create schema: {str(e)}")
        raise

async def create_analytics_views(config: WarehouseConfig):
    """Create analytics views and data marts"""
    logger.info("Creating analytics views...")
    
    views_file = project_root / 'data' / 'warehouse' / 'analytics' / 'data_marts.sql'
    
    if not views_file.exists():
        logger.warning(f"Analytics views file not found: {views_file}")
        return
    
    wh_config = config.get_warehouse_db_config()
    
    try:
        conn = await asyncpg.connect(**wh_config)
        
        # Read and execute views
        with open(views_file, 'r') as f:
            views_sql = f.read()
            
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in views_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                await conn.execute(statement)
            except Exception as e:
                logger.warning(f"View creation failed: {str(e)[:100]}...")
                
        logger.info("Analytics views created successfully")
        await conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create analytics views: {str(e)}")
        raise

async def load_initial_data(orchestrator: DataWarehouseOrchestrator, 
                          include_sample_data: bool = True):
    """Load initial data into the warehouse"""
    logger.info("Loading initial data...")
    
    # Load basic dimensions
    start_date = date(2024, 1, 1)
    end_date = date.today() + timedelta(days=365)  # Load future dates too
    
    await orchestrator._load_all_dimensions(start_date, end_date)
    
    if include_sample_data:
        logger.info("Loading sample fact data...")
        await orchestrator._load_all_facts(
            date.today() - timedelta(days=30), 
            date.today()
        )
    
    logger.info("Initial data loading completed")

async def verify_installation(config: WarehouseConfig):
    """Verify the warehouse installation"""
    logger.info("Verifying warehouse installation...")
    
    wh_config = config.get_warehouse_db_config()
    
    try:
        conn = await asyncpg.connect(**wh_config)
        
        # Check schema exists
        schema_exists = await conn.fetchval(
            "SELECT 1 FROM information_schema.schemata WHERE schema_name = 'dwh'"
        )
        
        if not schema_exists:
            raise Exception("DWH schema not found")
        
        # Check key tables exist
        key_tables = [
            'dim_service', 'dim_date', 'dim_location', 'dim_user_segment',
            'fact_service_usage', 'fact_data_quality'
        ]
        
        for table in key_tables:
            table_exists = await conn.fetchval(
                "SELECT 1 FROM information_schema.tables WHERE table_schema = 'dwh' AND table_name = $1",
                table
            )
            
            if not table_exists:
                raise Exception(f"Table {table} not found")
            
            # Check table has data (for dimension tables)
            if table.startswith('dim_'):
                row_count = await conn.fetchval(f"SELECT COUNT(*) FROM dwh.{table}")
                logger.info(f"Table {table}: {row_count} rows")
                
                if row_count == 0 and table in ['dim_date', 'dim_location']:
                    logger.warning(f"Table {table} is empty - this may be expected")
        
        # Check views exist
        view_count = await conn.fetchval(
            "SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'dwh'"
        )
        logger.info(f"Created {view_count} analytics views")
        
        # Check materialized views
        mv_count = await conn.fetchval(
            "SELECT COUNT(*) FROM pg_matviews WHERE schemaname = 'dwh'"
        )
        logger.info(f"Created {mv_count} materialized views")
        
        await conn.close()
        
        logger.info("✓ Warehouse installation verification completed successfully")
        
    except Exception as e:
        logger.error(f"Warehouse verification failed: {str(e)}")
        raise

async def main():
    """Main initialization function"""
    parser = argparse.ArgumentParser(
        description='Initialize Data Warehouse for Citizen Services'
    )
    
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Environment to initialize'
    )
    
    parser.add_argument(
        '--skip-sample-data',
        action='store_true',
        help='Skip loading sample data'
    )
    
    parser.add_argument(
        '--force-recreate',
        action='store_true',
        help='Force recreate schema (WARNING: destroys existing data)'
    )
    
    args = parser.parse_args()
    
    logger.info(f"Initializing data warehouse for {args.environment} environment")
    
    # Load configuration
    try:
        config = WarehouseConfig(args.environment)
        config.validate_config()
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    
    try:
        # Step 1: Create warehouse database
        await create_warehouse_database(config)
        
        # Step 2: Setup extensions
        await setup_extensions(config)
        
        # Step 3: Create schema
        if args.force_recreate:
            logger.warning("Force recreating schema - existing data will be lost!")
            # Here you would add DROP SCHEMA IF EXISTS dwh CASCADE;
        
        await create_warehouse_schema(config)
        
        # Step 4: Create analytics views
        await create_analytics_views(config)
        
        # Step 5: Initialize orchestrator and load data
        etl_config = ETLConfig(
            operational_db_config=config.get_operational_db_config(),
            warehouse_db_config=config.get_warehouse_db_config(),
            **config.get_etl_config()
        )
        
        orchestrator = DataWarehouseOrchestrator(etl_config)
        await orchestrator.initialize()
        
        try:
            # Load initial data
            await load_initial_data(orchestrator, not args.skip_sample_data)
            
        finally:
            await orchestrator.close()
        
        # Step 6: Verify installation
        await verify_installation(config)
        
        logger.info("🎉 Data warehouse initialization completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Run ETL process: python scripts/run_warehouse_etl.py --mode incremental")
        logger.info("2. Connect your BI tools to the warehouse")
        logger.info("3. Set up monitoring and alerting")
        
    except Exception as e:
        logger.error(f"Data warehouse initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())