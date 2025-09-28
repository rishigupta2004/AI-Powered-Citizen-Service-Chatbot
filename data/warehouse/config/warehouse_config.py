import os
from typing import Dict
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    
    def to_dict(self) -> Dict:
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }

class WarehouseConfig:
    """Configuration management for data warehouse"""
    
    def __init__(self, environment: str = 'development'):
        self.environment = environment
        self._load_config()
        
    def _load_config(self):
        """Load configuration based on environment"""
        
        # Operational database configuration (source)
        self.operational_db = DatabaseConfig(
            host=os.getenv('OPERATIONAL_DB_HOST', 'localhost'),
            port=int(os.getenv('OPERATIONAL_DB_PORT', '5432')),
            database=os.getenv('OPERATIONAL_DB_NAME', 'citizen_services_dev'),
            user=os.getenv('OPERATIONAL_DB_USER', 'postgres'),
            password=os.getenv('OPERATIONAL_DB_PASSWORD', '')
        )
        
        # Data warehouse database configuration (target)
        self.warehouse_db = DatabaseConfig(
            host=os.getenv('WAREHOUSE_DB_HOST', 'localhost'),
            port=int(os.getenv('WAREHOUSE_DB_PORT', '5432')),
            database=os.getenv('WAREHOUSE_DB_NAME', 'citizen_services_dwh'),
            user=os.getenv('WAREHOUSE_DB_USER', 'postgres'),
            password=os.getenv('WAREHOUSE_DB_PASSWORD', '')
        )
        
        # ETL Configuration
        self.etl_config = {
            'batch_size': int(os.getenv('ETL_BATCH_SIZE', '1000')),
            'max_retries': int(os.getenv('ETL_MAX_RETRIES', '3')),
            'parallel_workers': int(os.getenv('ETL_PARALLEL_WORKERS', '4')),
            'retention_days': int(os.getenv('ETL_RETENTION_DAYS', '365')),
            'incremental_hours': int(os.getenv('ETL_INCREMENTAL_HOURS', '24'))
        }
        
        # Logging Configuration
        self.logging_config = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'file': os.getenv('LOG_FILE', 'data_warehouse.log')
        }
        
        # Monitoring Configuration
        self.monitoring_config = {
            'enable_metrics': os.getenv('ENABLE_METRICS', 'true').lower() == 'true',
            'metrics_port': int(os.getenv('METRICS_PORT', '8000')),
            'alert_email': os.getenv('ALERT_EMAIL', ''),
            'slack_webhook': os.getenv('SLACK_WEBHOOK', '')
        }
        
    def get_operational_db_config(self) -> Dict:
        """Get operational database configuration"""
        return self.operational_db.to_dict()
        
    def get_warehouse_db_config(self) -> Dict:
        """Get warehouse database configuration"""
        return self.warehouse_db.to_dict()
        
    def get_etl_config(self) -> Dict:
        """Get ETL configuration"""
        return self.etl_config
        
    def get_logging_config(self) -> Dict:
        """Get logging configuration"""
        return self.logging_config
        
    def get_monitoring_config(self) -> Dict:
        """Get monitoring configuration"""
        return self.monitoring_config
        
    def validate_config(self) -> bool:
        """Validate configuration"""
        required_configs = [
            self.operational_db.host,
            self.operational_db.database,
            self.warehouse_db.host,
            self.warehouse_db.database
        ]
        
        missing_configs = [config for config in required_configs if not config]
        
        if missing_configs:
            raise ValueError(f"Missing required configuration: {missing_configs}")
            
        return True