"""
Extract data from operational database for data warehouse.
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy import text
from ..base_etl import BaseETL, ETLException
import logging

logger = logging.getLogger(__name__)

class OperationalExtractor(BaseETL):
    """Extract data from operational database."""
    
    async def extract(self, table_name: str, **kwargs) -> pd.DataFrame:
        """Extract data from operational database table."""
        try:
            # Build query with optional filters
            query = f"SELECT * FROM {table_name}"
            params = {}
            
            # Add date filter if provided
            if 'start_date' in kwargs:
                query += " WHERE created_at >= :start_date"
                params['start_date'] = kwargs['start_date']
            
            if 'end_date' in kwargs:
                if 'start_date' in kwargs:
                    query += " AND created_at <= :end_date"
                else:
                    query += " WHERE created_at <= :end_date"
                params['end_date'] = kwargs['end_date']
            
            # Add limit if provided
            if 'limit' in kwargs:
                query += f" LIMIT {kwargs['limit']}"
            
            logger.info(f"Executing query: {query}")
            result = self.source_session.execute(text(query), params)
            
            # Convert to DataFrame
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Extracted {len(data)} records from {table_name}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to extract data from {table_name}: {e}")
            raise ETLException(f"Extraction failed: {e}")
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform operational data for warehouse."""
        # Basic transformation - can be overridden by specific extractors
        return data
    
    async def load(self, data: pd.DataFrame, **kwargs) -> int:
        """Load data to warehouse (not used in extractor)."""
        return 0

class ServiceExtractor(OperationalExtractor):
    """Extract service data from operational database."""
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract service data."""
        return await super().extract('services', **kwargs)
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform service data for dimension table."""
        if data.empty:
            return data
        
        # Add warehouse-specific fields
        data['service_type'] = data['category'].apply(self._map_service_type)
        data['data_source'] = 'operational_db'
        data['priority_level'] = 3  # Default priority
        data['department'] = data['category'].apply(self._map_department)
        
        # Rename columns to match warehouse schema
        data = data.rename(columns={
            'service_id': 'service_id',
            'name': 'service_name',
            'category': 'service_category'
        })
        
        return data
    
    def _map_service_type(self, category: str) -> str:
        """Map service category to service type."""
        mapping = {
            'passport': 'api',
            'aadhaar': 'api',
            'pan': 'api',
            'epfo': 'api',
            'parivahan': 'api'
        }
        return mapping.get(category.lower(), 'scraped')
    
    def _map_department(self, category: str) -> str:
        """Map service category to department."""
        mapping = {
            'passport': 'Ministry of External Affairs',
            'aadhaar': 'UIDAI',
            'pan': 'Income Tax Department',
            'epfo': 'Ministry of Labour',
            'parivahan': 'Ministry of Road Transport'
        }
        return mapping.get(category.lower(), 'General')

class ProcedureExtractor(OperationalExtractor):
    """Extract procedure data from operational database."""
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract procedure data."""
        query = """
        SELECT p.*, s.name as service_name, s.category as service_category
        FROM procedures p
        JOIN services s ON p.service_id = s.service_id
        """
        
        try:
            result = self.source_session.execute(text(query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Extracted {len(data)} procedure records")
            return data
        except Exception as e:
            logger.error(f"Failed to extract procedure data: {e}")
            raise ETLException(f"Procedure extraction failed: {e}")
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform procedure data for content dimension."""
        if data.empty:
            return data
        
        # Create content records from procedures
        content_data = []
        for _, row in data.iterrows():
            content_data.append({
                'content_id': row['procedure_id'],
                'content_type': 'procedure',
                'title': row['title'],
                'language': 'en',  # Default language
                'content_source': 'operational_db',
                'is_active': True,
                'last_updated': row['created_at']
            })
        
        return pd.DataFrame(content_data)

class DocumentExtractor(OperationalExtractor):
    """Extract document data from operational database."""
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract document data."""
        query = """
        SELECT d.*, s.name as service_name, s.category as service_category
        FROM documents d
        JOIN services s ON d.service_id = s.service_id
        """
        
        try:
            result = self.source_session.execute(text(query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Extracted {len(data)} document records")
            return data
        except Exception as e:
            logger.error(f"Failed to extract document data: {e}")
            raise ETLException(f"Document extraction failed: {e}")
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform document data for content dimension."""
        if data.empty:
            return data
        
        # Create content records from documents
        content_data = []
        for _, row in data.iterrows():
            content_data.append({
                'content_id': row['doc_id'],
                'content_type': 'document',
                'title': row['name'],
                'language': 'en',  # Default language
                'content_source': 'operational_db',
                'is_active': True,
                'last_updated': row['created_at']
            })
        
        return pd.DataFrame(content_data)

class FAQExtractor(OperationalExtractor):
    """Extract FAQ data from operational database."""
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract FAQ data."""
        query = """
        SELECT f.*, s.name as service_name, s.category as service_category
        FROM faqs f
        JOIN services s ON f.service_id = s.service_id
        """
        
        try:
            result = self.source_session.execute(text(query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Extracted {len(data)} FAQ records")
            return data
        except Exception as e:
            logger.error(f"Failed to extract FAQ data: {e}")
            raise ETLException(f"FAQ extraction failed: {e}")
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform FAQ data for content dimension."""
        if data.empty:
            return data
        
        # Create content records from FAQs
        content_data = []
        for _, row in data.iterrows():
            content_data.append({
                'content_id': row['faq_id'],
                'content_type': 'faq',
                'title': row['question'],
                'language': 'en',  # Default language
                'content_source': 'operational_db',
                'is_active': True,
                'last_updated': row['created_at']
            })
        
        return pd.DataFrame(content_data)

class UserExtractor(OperationalExtractor):
    """Extract user data from operational database."""
    
    async def extract(self, **kwargs) -> pd.DataFrame:
        """Extract user data."""
        return await super().extract('users', **kwargs)
    
    async def transform(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform user data for user dimension."""
        if data.empty:
            return data
        
        # Add warehouse-specific fields
        data['user_type'] = data['role'].apply(self._map_user_type)
        data['is_first_time_user'] = False  # Default value
        data['registration_date'] = data['created_at'].dt.date
        data['last_activity_date'] = data['created_at'].dt.date  # Default to registration date
        
        # Rename columns to match warehouse schema
        data = data.rename(columns={
            'user_id': 'user_id',
            'name': 'name',  # Keep for reference
            'email': 'email',  # Keep for reference
            'role': 'role'  # Keep for reference
        })
        
        return data
    
    def _map_user_type(self, role: str) -> str:
        """Map user role to user type."""
        mapping = {
            'citizen': 'citizen',
            'admin': 'admin',
            'api_client': 'api_client'
        }
        return mapping.get(role.lower(), 'citizen')