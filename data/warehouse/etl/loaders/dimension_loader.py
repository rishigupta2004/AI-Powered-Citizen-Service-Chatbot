"""
Load dimension data into data warehouse.
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text
from ..base_etl import DimensionETL, ETLException
import logging

logger = logging.getLogger(__name__)

class ServiceDimensionLoader(DimensionETL):
    """Load service dimension data."""
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config, 'service')
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract service data from operational database."""
        query = """
        SELECT 
            service_id,
            name as service_name,
            category as service_category,
            description,
            created_at,
            'operational_db' as data_source,
            'scraped' as service_type,
            3 as priority_level,
            CASE 
                WHEN category = 'passport' THEN 'Ministry of External Affairs'
                WHEN category = 'aadhaar' THEN 'UIDAI'
                WHEN category = 'pan' THEN 'Income Tax Department'
                WHEN category = 'epfo' THEN 'Ministry of Labour'
                WHEN category = 'parivahan' THEN 'Ministry of Road Transport'
                ELSE 'General'
            END as department,
            TRUE as is_active,
            created_at as last_updated
        FROM services
        """
        
        try:
            result = self.source_session.execute(text(query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Extracted {len(data)} service records")
            return data
        except Exception as e:
            logger.error(f"Failed to extract service data: {e}")
            raise ETLException(f"Service extraction failed: {e}")
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform service data for dimension table."""
        if data.empty:
            return data
        
        # Ensure all required columns are present
        required_columns = [
            'service_id', 'service_name', 'service_category', 'department',
            'is_active', 'priority_level', 'service_type', 'data_source',
            'last_updated', 'created_at'
        ]
        
        for col in required_columns:
            if col not in data.columns:
                if col == 'created_at':
                    data[col] = datetime.now()
                elif col == 'last_updated':
                    data[col] = data.get('created_at', datetime.now())
                else:
                    data[col] = None
        
        return data[required_columns]

class UserDimensionLoader(DimensionETL):
    """Load user dimension data."""
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config, 'user')
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract user data from operational database."""
        query = """
        SELECT 
            user_id,
            name,
            email,
            role,
            created_at,
            CASE 
                WHEN role = 'citizen' THEN 'citizen'
                WHEN role = 'admin' THEN 'admin'
                ELSE 'api_client'
            END as user_type,
            NULL as location_state,
            NULL as location_district,
            'en' as language_preference,
            NULL as device_type,
            NULL as browser_type,
            FALSE as is_first_time_user,
            created_at::date as registration_date,
            created_at::date as last_activity_date
        FROM users
        """
        
        try:
            result = self.source_session.execute(text(query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Extracted {len(data)} user records")
            return data
        except Exception as e:
            logger.error(f"Failed to extract user data: {e}")
            raise ETLException(f"User extraction failed: {e}")
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform user data for dimension table."""
        if data.empty:
            return data
        
        # Ensure all required columns are present
        required_columns = [
            'user_id', 'user_type', 'location_state', 'location_district',
            'language_preference', 'device_type', 'browser_type',
            'is_first_time_user', 'registration_date', 'last_activity_date',
            'created_at'
        ]
        
        for col in required_columns:
            if col not in data.columns:
                if col == 'created_at':
                    data[col] = datetime.now()
                else:
                    data[col] = None
        
        return data[required_columns]

class ContentDimensionLoader(DimensionETL):
    """Load content dimension data."""
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config, 'content')
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract content data from multiple sources."""
        # Extract procedures
        procedures_query = """
        SELECT 
            procedure_id as content_id,
            'procedure' as content_type,
            title,
            'en' as language,
            'operational_db' as content_source,
            TRUE as is_active,
            created_at as last_updated,
            created_at
        FROM procedures
        """
        
        # Extract documents
        documents_query = """
        SELECT 
            doc_id as content_id,
            'document' as content_type,
            name as title,
            'en' as language,
            'operational_db' as content_source,
            TRUE as is_active,
            created_at as last_updated,
            created_at
        FROM documents
        """
        
        # Extract FAQs
        faqs_query = """
        SELECT 
            faq_id as content_id,
            'faq' as content_type,
            question as title,
            'en' as language,
            'operational_db' as content_source,
            TRUE as is_active,
            created_at as last_updated,
            created_at
        FROM faqs
        """
        
        try:
            # Execute all queries
            procedures_result = self.source_session.execute(text(procedures_query))
            documents_result = self.source_session.execute(text(documents_query))
            faqs_result = self.source_session.execute(text(faqs_query))
            
            # Combine results
            procedures_data = pd.DataFrame(procedures_result.fetchall(), columns=procedures_result.keys())
            documents_data = pd.DataFrame(documents_result.fetchall(), columns=documents_result.keys())
            faqs_data = pd.DataFrame(faqs_result.fetchall(), columns=faqs_result.keys())
            
            # Combine all content
            all_content = pd.concat([procedures_data, documents_data, faqs_data], ignore_index=True)
            logger.info(f"Extracted {len(all_content)} content records")
            
            return all_content
            
        except Exception as e:
            logger.error(f"Failed to extract content data: {e}")
            raise ETLException(f"Content extraction failed: {e}")
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform content data for dimension table."""
        if data.empty:
            return data
        
        # Ensure all required columns are present
        required_columns = [
            'content_id', 'content_type', 'title', 'language',
            'content_source', 'is_active', 'last_updated', 'created_at'
        ]
        
        for col in required_columns:
            if col not in data.columns:
                if col == 'created_at':
                    data[col] = datetime.now()
                elif col == 'last_updated':
                    data[col] = data.get('created_at', datetime.now())
                else:
                    data[col] = None
        
        return data[required_columns]

class QueryTypeDimensionLoader(DimensionETL):
    """Load query type dimension data."""
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config, 'query_type')
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract query type data (static data)."""
        query_types = [
            {
                'query_type': 'search',
                'query_category': 'general',
                'complexity_level': 'simple',
                'expected_response_time_ms': 500,
                'is_api_required': False,
                'description': 'General content search'
            },
            {
                'query_type': 'status_check',
                'query_category': 'specific',
                'complexity_level': 'moderate',
                'expected_response_time_ms': 2000,
                'is_api_required': True,
                'description': 'Application status verification'
            },
            {
                'query_type': 'verification',
                'query_category': 'specific',
                'complexity_level': 'moderate',
                'expected_response_time_ms': 1500,
                'is_api_required': True,
                'description': 'Document or identity verification'
            },
            {
                'query_type': 'information',
                'query_category': 'general',
                'complexity_level': 'simple',
                'expected_response_time_ms': 300,
                'is_api_required': False,
                'description': 'General information request'
            },
            {
                'query_type': 'procedural',
                'query_category': 'specific',
                'complexity_level': 'complex',
                'expected_response_time_ms': 3000,
                'is_api_required': False,
                'description': 'Step-by-step procedure guidance'
            }
        ]
        
        data = pd.DataFrame(query_types)
        logger.info(f"Extracted {len(data)} query type records")
        return data
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform query type data for dimension table."""
        if data.empty:
            return data
        
        # Add created_at timestamp
        data['created_at'] = datetime.now()
        
        return data

class LanguageDimensionLoader(DimensionETL):
    """Load language dimension data."""
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config, 'language')
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract language data (static data)."""
        languages = [
            {
                'language_code': 'en',
                'language_name': 'English',
                'script_type': 'latin',
                'is_rtl': False,
                'is_supported': True,
                'coverage_percentage': 100.00
            },
            {
                'language_code': 'hi',
                'language_name': 'Hindi',
                'script_type': 'devanagari',
                'is_rtl': False,
                'is_supported': True,
                'coverage_percentage': 95.00
            },
            {
                'language_code': 'bn',
                'language_name': 'Bengali',
                'script_type': 'bengali',
                'is_rtl': False,
                'is_supported': True,
                'coverage_percentage': 80.00
            },
            {
                'language_code': 'ta',
                'language_name': 'Tamil',
                'script_type': 'tamil',
                'is_rtl': False,
                'is_supported': True,
                'coverage_percentage': 75.00
            },
            {
                'language_code': 'te',
                'language_name': 'Telugu',
                'script_type': 'telugu',
                'is_rtl': False,
                'is_supported': True,
                'coverage_percentage': 70.00
            },
            {
                'language_code': 'mr',
                'language_name': 'Marathi',
                'script_type': 'devanagari',
                'is_rtl': False,
                'is_supported': True,
                'coverage_percentage': 65.00
            },
            {
                'language_code': 'gu',
                'language_name': 'Gujarati',
                'script_type': 'gujarati',
                'is_rtl': False,
                'is_supported': True,
                'coverage_percentage': 60.00
            },
            {
                'language_code': 'kn',
                'language_name': 'Kannada',
                'script_type': 'kannada',
                'is_rtl': False,
                'is_supported': True,
                'coverage_percentage': 55.00
            }
        ]
        
        data = pd.DataFrame(languages)
        logger.info(f"Extracted {len(data)} language records")
        return data
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform language data for dimension table."""
        if data.empty:
            return data
        
        # Add created_at timestamp
        data['created_at'] = datetime.now()
        
        return data