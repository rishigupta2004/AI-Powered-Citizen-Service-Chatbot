"""
Base ETL classes for data warehouse operations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

logger = logging.getLogger(__name__)

class ETLException(Exception):
    """Custom exception for ETL operations."""
    pass

class BaseETL(ABC):
    """Base class for all ETL operations."""
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        self.source_config = source_config
        self.target_config = target_config
        self.source_engine = None
        self.target_engine = None
        self.source_session = None
        self.target_session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
        
    async def connect(self):
        """Establish database connections."""
        try:
            # Source connection
            self.source_engine = create_engine(
                self.source_config['url'],
                echo=self.source_config.get('echo', False),
                pool_pre_ping=True
            )
            self.source_session = sessionmaker(bind=self.source_engine)()
            
            # Target connection
            self.target_engine = create_engine(
                self.target_config['url'],
                echo=self.target_config.get('echo', False),
                pool_pre_ping=True
            )
            self.target_session = sessionmaker(bind=self.target_engine)()
            
            logger.info("Database connections established successfully")
            
        except Exception as e:
            logger.error(f"Failed to establish database connections: {e}")
            raise ETLException(f"Connection failed: {e}")
    
    async def disconnect(self):
        """Close database connections."""
        try:
            if self.source_session:
                self.source_session.close()
            if self.target_session:
                self.target_session.close()
            if self.source_engine:
                self.source_engine.dispose()
            if self.target_engine:
                self.target_engine.dispose()
            logger.info("Database connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    @abstractmethod
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract data from source system."""
        pass
    
    @abstractmethod
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform extracted data."""
        pass
    
    @abstractmethod
    async def load(self, data: pd.DataFrame, **kwargs) -> int:
        """Load transformed data into target system."""
        pass
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the complete ETL process."""
        start_time = datetime.now()
        result = {
            'start_time': start_time,
            'end_time': None,
            'duration_seconds': None,
            'records_processed': 0,
            'success': False,
            'error': None
        }
        
        try:
            logger.info(f"Starting ETL process: {self.__class__.__name__}")
            
            # Extract
            logger.info("Extracting data...")
            extracted_data = await self.extract(**kwargs)
            logger.info(f"Extracted {len(extracted_data)} records")
            
            # Transform
            logger.info("Transforming data...")
            transformed_data = await self.transform(extracted_data, **kwargs)
            logger.info(f"Transformed {len(transformed_data)} records")
            
            # Load
            logger.info("Loading data...")
            records_loaded = await self.load(transformed_data, **kwargs)
            logger.info(f"Loaded {records_loaded} records")
            
            result['records_processed'] = records_loaded
            result['success'] = True
            
        except Exception as e:
            logger.error(f"ETL process failed: {e}")
            result['error'] = str(e)
            raise ETLException(f"ETL process failed: {e}")
        
        finally:
            end_time = datetime.now()
            result['end_time'] = end_time
            result['duration_seconds'] = (end_time - start_time).total_seconds()
            logger.info(f"ETL process completed in {result['duration_seconds']:.2f} seconds")
        
        return result

class DimensionETL(BaseETL):
    """Base class for dimension table ETL operations."""
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any], 
                 dimension_name: str):
        super().__init__(source_config, target_config)
        self.dimension_name = dimension_name
    
    async def load(self, data: pd.DataFrame, **kwargs) -> int:
        """Load dimension data with SCD Type 1 or Type 2 logic."""
        scd_type = kwargs.get('scd_type', 1)
        
        if scd_type == 1:
            return await self._load_scd_type1(data)
        elif scd_type == 2:
            return await self._load_scd_type2(data)
        else:
            raise ETLException(f"Unsupported SCD type: {scd_type}")
    
    async def _load_scd_type1(self, data: pd.DataFrame) -> int:
        """Load data using SCD Type 1 (overwrite)."""
        try:
            # Use pandas to_sql with if_exists='replace' for SCD Type 1
            records_loaded = data.to_sql(
                f"dim_{self.dimension_name}",
                self.target_engine,
                if_exists='replace',
                index=False,
                method='multi'
            )
            logger.info(f"Loaded {records_loaded} records to dim_{self.dimension_name}")
            return records_loaded
        except Exception as e:
            logger.error(f"Failed to load dimension data: {e}")
            raise ETLException(f"Dimension load failed: {e}")
    
    async def _load_scd_type2(self, data: pd.DataFrame) -> int:
        """Load data using SCD Type 2 (historical tracking)."""
        # This would implement SCD Type 2 logic
        # For now, using Type 1 as placeholder
        return await self._load_scd_type1(data)

class FactETL(BaseETL):
    """Base class for fact table ETL operations."""
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any], 
                 fact_name: str):
        super().__init__(source_config, target_config)
        self.fact_name = fact_name
    
    async def load(self, data: pd.DataFrame, **kwargs) -> int:
        """Load fact data with incremental loading support."""
        load_type = kwargs.get('load_type', 'append')
        
        try:
            if load_type == 'append':
                records_loaded = data.to_sql(
                    f"fct_{self.fact_name}",
                    self.target_engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
            elif load_type == 'replace':
                records_loaded = data.to_sql(
                    f"fct_{self.fact_name}",
                    self.target_engine,
                    if_exists='replace',
                    index=False,
                    method='multi'
                )
            else:
                raise ETLException(f"Unsupported load type: {load_type}")
            
            logger.info(f"Loaded {records_loaded} records to fct_{self.fact_name}")
            return records_loaded
            
        except Exception as e:
            logger.error(f"Failed to load fact data: {e}")
            raise ETLException(f"Fact load failed: {e}")

class DataQualityChecker:
    """Data quality validation and checking."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_rules = self._load_quality_rules()
    
    def _load_quality_rules(self) -> Dict[str, Any]:
        """Load data quality rules from configuration."""
        return self.config.get('quality_rules', {})
    
    async def validate_data(self, data: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Validate data quality against defined rules."""
        quality_results = {
            'table_name': table_name,
            'total_records': len(data),
            'quality_score': 0.0,
            'checks_passed': 0,
            'checks_failed': 0,
            'issues': []
        }
        
        rules = self.quality_rules.get(table_name, {})
        
        for rule_name, rule_config in rules.items():
            try:
                result = await self._apply_quality_rule(data, rule_name, rule_config)
                if result['passed']:
                    quality_results['checks_passed'] += 1
                else:
                    quality_results['checks_failed'] += 1
                    quality_results['issues'].append(result)
            except Exception as e:
                logger.error(f"Quality rule {rule_name} failed: {e}")
                quality_results['issues'].append({
                    'rule': rule_name,
                    'error': str(e),
                    'passed': False
                })
                quality_results['checks_failed'] += 1
        
        # Calculate overall quality score
        total_checks = quality_results['checks_passed'] + quality_results['checks_failed']
        if total_checks > 0:
            quality_results['quality_score'] = quality_results['checks_passed'] / total_checks
        
        return quality_results
    
    async def _apply_quality_rule(self, data: pd.DataFrame, rule_name: str, 
                                 rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a specific quality rule to the data."""
        rule_type = rule_config.get('type')
        
        if rule_type == 'not_null':
            column = rule_config['column']
            null_count = data[column].isnull().sum()
            passed = null_count == 0
            return {
                'rule': rule_name,
                'passed': passed,
                'null_count': null_count,
                'total_records': len(data)
            }
        
        elif rule_type == 'unique':
            column = rule_config['column']
            duplicate_count = data[column].duplicated().sum()
            passed = duplicate_count == 0
            return {
                'rule': rule_name,
                'passed': passed,
                'duplicate_count': duplicate_count,
                'total_records': len(data)
            }
        
        elif rule_type == 'range':
            column = rule_config['column']
            min_val = rule_config.get('min')
            max_val = rule_config.get('max')
            out_of_range = 0
            
            if min_val is not None:
                out_of_range += (data[column] < min_val).sum()
            if max_val is not None:
                out_of_range += (data[column] > max_val).sum()
            
            passed = out_of_range == 0
            return {
                'rule': rule_name,
                'passed': passed,
                'out_of_range_count': out_of_range,
                'total_records': len(data)
            }
        
        else:
            raise ETLException(f"Unknown quality rule type: {rule_type}")

class ETLOrchestrator:
    """Orchestrates multiple ETL processes."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.etl_processes = []
        self.quality_checker = DataQualityChecker(config.get('quality', {}))
    
    def add_etl_process(self, etl_process: BaseETL):
        """Add an ETL process to the orchestrator."""
        self.etl_processes.append(etl_process)
    
    async def run_all(self, **kwargs) -> Dict[str, Any]:
        """Run all ETL processes in sequence."""
        results = {
            'start_time': datetime.now(),
            'processes': [],
            'overall_success': True,
            'total_records_processed': 0
        }
        
        for etl_process in self.etl_processes:
            try:
                logger.info(f"Running ETL process: {etl_process.__class__.__name__}")
                process_result = await etl_process.run(**kwargs)
                results['processes'].append(process_result)
                results['total_records_processed'] += process_result['records_processed']
                
                if not process_result['success']:
                    results['overall_success'] = False
                    
            except Exception as e:
                logger.error(f"ETL process {etl_process.__class__.__name__} failed: {e}")
                results['processes'].append({
                    'process_name': etl_process.__class__.__name__,
                    'success': False,
                    'error': str(e)
                })
                results['overall_success'] = False
        
        results['end_time'] = datetime.now()
        results['duration_seconds'] = (results['end_time'] - results['start_time']).total_seconds()
        
        return results