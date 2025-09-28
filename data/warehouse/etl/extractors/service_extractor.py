from .base_extractor import BaseExtractor
from typing import List, Dict
from datetime import datetime, date
import asyncpg
import logging

logger = logging.getLogger(__name__)

class ServiceDataExtractor(BaseExtractor):
    """Extract service data from operational database"""
    
    def __init__(self, connection_config: Dict):
        super().__init__("operational_db", connection_config)
        self.db_pool = None
        
    async def _get_connection(self):
        """Get database connection"""
        if not self.db_pool:
            self.db_pool = await asyncpg.create_pool(**self.connection_config)
        return self.db_pool
        
    async def extract(self, extraction_date: date, **kwargs) -> List[Dict]:
        """Extract all service data for the given date"""
        pool = await self._get_connection()
        
        query = """
        SELECT 
            s.service_id,
            s.name as service_name,
            s.description,
            s.category,
            s.created_at,
            COUNT(DISTINCT p.procedure_id) as procedure_count,
            COUNT(DISTINCT d.doc_id) as document_count,
            COUNT(DISTINCT f.faq_id) as faq_count,
            ARRAY_AGG(DISTINCT d.language) FILTER (WHERE d.language IS NOT NULL) as languages_supported
        FROM services s
        LEFT JOIN procedures p ON s.service_id = p.service_id
        LEFT JOIN documents d ON s.service_id = d.service_id  
        LEFT JOIN faqs f ON s.service_id = f.service_id
        WHERE DATE(s.created_at) <= $1
        GROUP BY s.service_id, s.name, s.description, s.category, s.created_at
        ORDER BY s.service_id
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, extraction_date)
            
        return [dict(row) for row in rows]
        
    async def get_incremental_data(self, last_extracted: datetime) -> List[Dict]:
        """Extract only services modified since last extraction"""
        pool = await self._get_connection()
        
        query = """
        SELECT 
            s.service_id,
            s.name as service_name,
            s.description,
            s.category,
            s.created_at,
            COUNT(DISTINCT p.procedure_id) as procedure_count,
            COUNT(DISTINCT d.doc_id) as document_count,
            COUNT(DISTINCT f.faq_id) as faq_count,
            ARRAY_AGG(DISTINCT d.language) FILTER (WHERE d.language IS NOT NULL) as languages_supported,
            GREATEST(s.created_at, 
                    COALESCE(MAX(p.created_at), s.created_at),
                    COALESCE(MAX(d.created_at), s.created_at),
                    COALESCE(MAX(f.created_at), s.created_at)) as last_modified
        FROM services s
        LEFT JOIN procedures p ON s.service_id = p.service_id
        LEFT JOIN documents d ON s.service_id = d.service_id
        LEFT JOIN faqs f ON s.service_id = f.service_id
        WHERE GREATEST(s.created_at,
                      COALESCE(MAX(p.created_at), s.created_at),
                      COALESCE(MAX(d.created_at), s.created_at), 
                      COALESCE(MAX(f.created_at), s.created_at)) > $1
        GROUP BY s.service_id, s.name, s.description, s.category, s.created_at
        ORDER BY last_modified DESC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, last_extracted)
            
        return [dict(row) for row in rows]
        
    async def extract_usage_analytics(self, date_range: Tuple[date, date]) -> List[Dict]:
        """Extract usage analytics from application logs"""
        # This would typically extract from log files or analytics tables
        # For now, we'll simulate some usage data
        
        start_date, end_date = date_range
        pool = await self._get_connection()
        
        # Simulate extracting from hypothetical analytics/logs table
        # In real implementation, this would come from actual usage logs
        query = """
        WITH service_usage AS (
            SELECT 
                s.service_id,
                CURRENT_DATE as usage_date,
                -- Simulate usage metrics based on service complexity
                CASE 
                    WHEN s.category LIKE '%passport%' THEN RANDOM() * 1000 + 500
                    WHEN s.category LIKE '%aadhaar%' THEN RANDOM() * 800 + 300
                    ELSE RANDOM() * 300 + 100
                END::INTEGER as daily_queries,
                -- Success rate varies by service type
                CASE 
                    WHEN s.category LIKE '%passport%' THEN 0.85 + RANDOM() * 0.10
                    WHEN s.category LIKE '%aadhaar%' THEN 0.90 + RANDOM() * 0.08
                    ELSE 0.80 + RANDOM() * 0.15
                END as success_rate,
                -- Response time varies by complexity
                CASE 
                    WHEN s.category LIKE '%passport%' THEN 800 + RANDOM() * 400
                    ELSE 400 + RANDOM() * 200
                END::INTEGER as avg_response_time_ms,
                -- Satisfaction scores
                3.5 + RANDOM() * 1.5 as satisfaction_score
            FROM services s
            WHERE s.created_at <= $2
        )
        SELECT 
            service_id,
            usage_date,
            daily_queries as query_count,
            (daily_queries * success_rate)::INTEGER as success_count,
            (daily_queries * (1 - success_rate))::INTEGER as failure_count,
            avg_response_time_ms,
            (daily_queries * 0.3)::INTEGER as documents_served,
            satisfaction_score,
            -- Default values for missing dimensions
            'Unknown' as state_name,
            'Unknown' as age_group,
            'Web Portal' as channel_name,
            'FAQ' as content_type,
            'en' as language_code
        FROM service_usage
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, start_date, end_date)
            
        return [dict(row) for row in rows]
        
    def _is_valid_record(self, record: Dict) -> bool:
        """Validate service record"""
        required_fields = ['service_id', 'service_name']
        return all(field in record and record[field] is not None for field in required_fields)
        
    async def close(self):
        """Close database connections"""
        if self.db_pool:
            await self.db_pool.close()