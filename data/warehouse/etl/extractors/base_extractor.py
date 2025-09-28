from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
import asyncio
import logging

logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    """Base class for all data extractors"""
    
    def __init__(self, source_name: str, connection_config: Dict):
        self.source_name = source_name
        self.connection_config = connection_config
        self.last_extracted = None
        
    @abstractmethod
    async def extract(self, extraction_date: date, **kwargs) -> List[Dict]:
        """Extract data for the given date"""
        pass
        
    @abstractmethod
    async def get_incremental_data(self, last_extracted: datetime) -> List[Dict]:
        """Extract only new/changed data since last extraction"""
        pass
        
    def validate_extracted_data(self, data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Validate extracted data and return valid/invalid records"""
        valid_records = []
        invalid_records = []
        
        for record in data:
            if self._is_valid_record(record):
                valid_records.append(record)
            else:
                invalid_records.append(record)
                
        if invalid_records:
            logger.warning(f"Found {len(invalid_records)} invalid records from {self.source_name}")
            
        return valid_records, invalid_records
        
    def _is_valid_record(self, record: Dict) -> bool:
        """Basic validation - override in subclasses for specific validation"""
        return record is not None and len(record) > 0
        
    async def extract_with_retry(self, extraction_date: date, max_retries: int = 3) -> List[Dict]:
        """Extract data with retry mechanism"""
        for attempt in range(max_retries):
            try:
                data = await self.extract(extraction_date)
                logger.info(f"Successfully extracted {len(data)} records from {self.source_name}")
                return data
            except Exception as e:
                logger.error(f"Extraction attempt {attempt + 1} failed for {self.source_name}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        return []