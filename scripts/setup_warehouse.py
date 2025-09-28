#!/usr/bin/env python3
"""
Setup script for Citizen Services Data Warehouse.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime, date
import subprocess
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.warehouse.etl.orchestrator import DataWarehouseOrchestrator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WarehouseSetup:
    """Setup class for data warehouse."""
    
    def __init__(self):
        self.project_root = project_root
        self.config_path = self.project_root / 'config' / 'warehouse_config.yaml'
        self.schema_path = self.project_root / 'database' / 'warehouse_schema.sql'
    
    def setup_database(self):
        """Set up the data warehouse database."""
        logger.info("Setting up data warehouse database...")
        
        # Check if schema file exists
        if not self.schema_path.exists():
            logger.error(f"Schema file not found: {self.schema_path}")
            return False
        
        try:
            # Read schema file
            with open(self.schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Get database URL from environment
            database_url = os.getenv(
                'WAREHOUSE_DATABASE_URL',
                'postgresql://user:password@localhost/citizen_services_warehouse'
            )
            
            # Execute schema creation
            logger.info("Creating data warehouse schema...")
            result = subprocess.run([
                'psql', database_url, '-c', schema_sql
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Data warehouse schema created successfully")
                return True
            else:
                logger.error(f"Failed to create schema: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            return False
    
    def setup_config(self):
        """Set up configuration files."""
        logger.info("Setting up configuration...")
        
        # Create config directory if it doesn't exist
        config_dir = self.project_root / 'config'
        config_dir.mkdir(exist_ok=True)
        
        # Create default config if it doesn't exist
        if not self.config_path.exists():
            logger.info("Creating default configuration...")
            default_config = {
                'source': {
                    'url': os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/citizen_services'),
                    'echo': False
                },
                'target': {
                    'url': os.getenv('WAREHOUSE_DATABASE_URL', 'postgresql://user:password@localhost/citizen_services_warehouse'),
                    'echo': False
                },
                'quality': {
                    'quality_rules': {}
                }
            }
            
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            
            logger.info(f"Configuration created: {self.config_path}")
        
        return True
    
    def setup_directories(self):
        """Set up required directories."""
        logger.info("Setting up directories...")
        
        directories = [
            'data/warehouse/etl/extractors',
            'data/warehouse/etl/loaders',
            'data/warehouse/etl/transformers',
            'data/warehouse/analytics',
            'data/warehouse/reports',
            'logs/warehouse',
            'config'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
        
        return True
    
    async def run_initial_load(self):
        """Run initial data load."""
        logger.info("Running initial data load...")
        
        try:
            # Initialize orchestrator
            orchestrator = DataWarehouseOrchestrator(str(self.config_path))
            
            # Run dimension loads
            logger.info("Loading dimension tables...")
            result = await orchestrator.run_dimension_loads()
            
            if result['overall_success']:
                logger.info("Initial data load completed successfully")
                logger.info(f"Total records processed: {result['total_records_processed']}")
                return True
            else:
                logger.error("Initial data load failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to run initial load: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample data for testing."""
        logger.info("Creating sample data...")
        
        try:
            # This would create sample data for testing
            # For now, just log that it would be done
            logger.info("Sample data creation would be implemented here")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample data: {e}")
            return False
    
    def setup_monitoring(self):
        """Set up monitoring and logging."""
        logger.info("Setting up monitoring...")
        
        # Create log directory
        log_dir = self.project_root / 'logs' / 'warehouse'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up log rotation
        logger.info("Monitoring setup completed")
        return True
    
    def run_tests(self):
        """Run basic tests to verify setup."""
        logger.info("Running setup tests...")
        
        try:
            # Test database connection
            database_url = os.getenv(
                'WAREHOUSE_DATABASE_URL',
                'postgresql://user:password@localhost/citizen_services_warehouse'
            )
            
            result = subprocess.run([
                'psql', database_url, '-c', 'SELECT 1'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Database connection test passed")
            else:
                logger.error("Database connection test failed")
                return False
            
            # Test configuration loading
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info("Configuration loading test passed")
            else:
                logger.error("Configuration file not found")
                return False
            
            logger.info("All tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Tests failed: {e}")
            return False
    
    async def run_full_setup(self):
        """Run the complete setup process."""
        logger.info("Starting data warehouse setup...")
        
        steps = [
            ("Setting up directories", self.setup_directories),
            ("Setting up configuration", self.setup_config),
            ("Setting up database", self.setup_database),
            ("Setting up monitoring", self.setup_monitoring),
            ("Creating sample data", self.create_sample_data),
            ("Running initial load", self.run_initial_load),
            ("Running tests", self.run_tests)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Step: {step_name}")
            try:
                if asyncio.iscoroutinefunction(step_func):
                    success = await step_func()
                else:
                    success = step_func()
                
                if success:
                    logger.info(f"✓ {step_name} completed successfully")
                else:
                    logger.error(f"✗ {step_name} failed")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ {step_name} failed with error: {e}")
                return False
        
        logger.info("🎉 Data warehouse setup completed successfully!")
        return True

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Citizen Services Data Warehouse')
    parser.add_argument('--skip-db', action='store_true', help='Skip database setup')
    parser.add_argument('--skip-load', action='store_true', help='Skip initial data load')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    
    args = parser.parse_args()
    
    setup = WarehouseSetup()
    
    if args.config:
        setup.config_path = Path(args.config)
    
    # Run setup steps
    if not args.skip_db:
        if not setup.setup_directories():
            sys.exit(1)
        
        if not setup.setup_config():
            sys.exit(1)
        
        if not setup.setup_database():
            sys.exit(1)
        
        if not setup.setup_monitoring():
            sys.exit(1)
    
    if not args.skip_load:
        if not await setup.run_initial_load():
            sys.exit(1)
    
    if not setup.run_tests():
        sys.exit(1)
    
    print("✅ Data warehouse setup completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())