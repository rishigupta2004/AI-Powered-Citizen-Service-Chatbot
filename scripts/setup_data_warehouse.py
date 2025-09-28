#!/usr/bin/env python3
"""
Data Warehouse Setup Script
Sets up the data warehouse schema and initial data for the citizen services database.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.warehouse.etl.pipeline import ETLPipeline
from data.warehouse.analytics.reports import AnalyticsReporter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_warehouse_schema(warehouse_db_url: str):
    """Set up the data warehouse schema."""
    try:
        logger.info("Setting up data warehouse schema...")
        
        engine = create_engine(warehouse_db_url)
        
        # Read and execute schema file
        schema_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'warehouse_schema.sql')
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        with engine.connect() as conn:
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Statement failed (may already exist): {e}")
        
        logger.info("Data warehouse schema setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up warehouse schema: {e}")
        return False

def populate_initial_data(warehouse_db_url: str):
    """Populate initial data in the warehouse."""
    try:
        logger.info("Populating initial data...")
        
        engine = create_engine(warehouse_db_url)
        
        with engine.connect() as conn:
            # Populate date dimension for the next 2 years
            conn.execute(text("""
                SELECT populate_date_dimension(CURRENT_DATE, CURRENT_DATE + INTERVAL '2 years')
            """))
            
            # Insert initial services from operational database
            conn.execute(text("""
                INSERT INTO service_dim (service_id, service_name, category, description, 
                                       government_department, service_type, priority_level, is_active, created_at)
                SELECT 
                    service_id,
                    name as service_name,
                    category,
                    description,
                    CASE 
                        WHEN LOWER(name) LIKE '%passport%' THEN 'MEA'
                        WHEN LOWER(name) LIKE '%aadhaar%' THEN 'UIDAI'
                        WHEN LOWER(name) LIKE '%pan%' THEN 'CBDT'
                        WHEN LOWER(name) LIKE '%epf%' THEN 'Ministry of Labour'
                        WHEN LOWER(name) LIKE '%driving%' OR LOWER(name) LIKE '%parivahan%' THEN 'MoRTH'
                        WHEN LOWER(name) LIKE '%voter%' THEN 'ECI'
                        WHEN LOWER(name) LIKE '%ration%' THEN 'FCS'
                        WHEN LOWER(name) LIKE '%scholarship%' THEN 'Ministry of Education'
                        WHEN LOWER(name) LIKE '%grievance%' THEN 'DARPG'
                        ELSE 'Unknown'
                    END as government_department,
                    'hybrid' as service_type,
                    CASE 
                        WHEN LOWER(name) LIKE '%passport%' OR LOWER(name) LIKE '%aadhaar%' THEN 1
                        WHEN LOWER(name) LIKE '%pan%' OR LOWER(name) LIKE '%epf%' THEN 2
                        WHEN LOWER(name) LIKE '%driving%' OR LOWER(name) LIKE '%voter%' THEN 3
                        ELSE 4
                    END as priority_level,
                    TRUE as is_active,
                    created_at
                FROM services
                ON CONFLICT (service_id) DO NOTHING
            """))
            
            conn.commit()
        
        logger.info("Initial data population completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error populating initial data: {e}")
        return False

def run_initial_etl(operational_db_url: str, warehouse_db_url: str):
    """Run initial ETL pipeline to populate warehouse with historical data."""
    try:
        logger.info("Running initial ETL pipeline...")
        
        pipeline = ETLPipeline(operational_db_url, warehouse_db_url)
        
        # Run ETL for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = pipeline.run_full_pipeline(start_date, end_date)
        
        if results['status'] == 'success':
            logger.info("Initial ETL pipeline completed successfully")
            logger.info(f"Extraction counts: {results['extraction_counts']}")
            logger.info(f"Transformation counts: {results['transformation_counts']}")
            return True
        else:
            logger.error(f"ETL pipeline failed: {results.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        logger.error(f"Error running initial ETL: {e}")
        return False

def test_analytics(warehouse_db_url: str):
    """Test analytics functionality."""
    try:
        logger.info("Testing analytics functionality...")
        
        reporter = AnalyticsReporter(warehouse_db_url)
        
        # Test basic analytics queries
        top_services = reporter.get_top_performing_services(7, 5)
        logger.info(f"Top 5 services (last 7 days): {len(top_services)} records")
        
        quality_dashboard = reporter.get_data_quality_dashboard()
        logger.info(f"Data quality dashboard: {quality_dashboard['overall_metrics']}")
        
        executive_summary = reporter.generate_executive_summary(7)
        logger.info(f"Executive summary generated for {executive_summary['period_days']} days")
        
        logger.info("Analytics functionality test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error testing analytics: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("Starting data warehouse setup...")
    
    # Get database URLs from environment
    operational_db_url = os.getenv("OPERATIONAL_DATABASE_URL")
    warehouse_db_url = os.getenv("WAREHOUSE_DATABASE_URL")
    
    if not operational_db_url:
        logger.error("OPERATIONAL_DATABASE_URL environment variable not set")
        sys.exit(1)
    
    if not warehouse_db_url:
        logger.error("WAREHOUSE_DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Step 1: Setup warehouse schema
    if not setup_warehouse_schema(warehouse_db_url):
        logger.error("Failed to setup warehouse schema")
        sys.exit(1)
    
    # Step 2: Populate initial data
    if not populate_initial_data(warehouse_db_url):
        logger.error("Failed to populate initial data")
        sys.exit(1)
    
    # Step 3: Run initial ETL
    if not run_initial_etl(operational_db_url, warehouse_db_url):
        logger.error("Failed to run initial ETL")
        sys.exit(1)
    
    # Step 4: Test analytics
    if not test_analytics(warehouse_db_url):
        logger.error("Failed to test analytics")
        sys.exit(1)
    
    logger.info("Data warehouse setup completed successfully!")
    logger.info("Next steps:")
    logger.info("1. Configure Grafana dashboard using the provided JSON configuration")
    logger.info("2. Set up monitoring and alerting for the ETL pipeline")
    logger.info("3. Schedule regular ETL runs using Apache Airflow or cron")
    logger.info("4. Access analytics API at /analytics endpoints")

if __name__ == "__main__":
    main()