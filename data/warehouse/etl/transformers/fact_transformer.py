from .base_transformer import BaseTransformer
from typing import List, Dict, Optional
from datetime import date, datetime
import logging
import random

logger = logging.getLogger(__name__)

class FactTransformer(BaseTransformer):
    """Transform data for fact tables"""
    
    def __init__(self, dimension_lookups: Dict = None):
        super().__init__("fact_transformer")
        self.dimension_lookups = dimension_lookups or {}
        
    def transform_service_usage_facts(self, raw_usage: List[Dict]) -> List[Dict]:
        """Transform raw usage data into fact_service_usage format"""
        self.start_transformation()
        
        transformed_facts = []
        
        for usage_record in raw_usage:
            try:
                self.transformation_stats['records_processed'] += 1
                
                # Get dimension keys
                service_key = self._get_service_key(usage_record.get('service_id'))
                date_key = self._get_date_key(usage_record.get('usage_date'))
                location_key = self._get_location_key(usage_record.get('state_name', 'Unknown'))
                user_segment_key = self._get_user_segment_key(
                    usage_record.get('age_group', 'Unknown'),
                    usage_record.get('education_level', 'Unknown'),
                    usage_record.get('device_type', 'Mobile')
                )
                channel_key = self._get_channel_key(usage_record.get('channel_name', 'Web Portal'))
                content_type_key = self._get_content_type_key(usage_record.get('content_type', 'FAQ'))
                
                # Calculate derived metrics
                query_count = usage_record.get('query_count', 0)
                success_count = usage_record.get('success_count', 0)
                failure_count = query_count - success_count
                
                # Calculate rates and scores
                completion_rate = (success_count / query_count) if query_count > 0 else 0
                bounce_rate = (failure_count / query_count) if query_count > 0 else 0
                conversion_rate = completion_rate  # Simplification
                
                fact_record = {
                    'service_key': service_key,
                    'date_key': date_key,
                    'location_key': location_key,
                    'user_segment_key': user_segment_key,
                    'channel_key': channel_key,
                    'content_type_key': content_type_key,
                    
                    # Usage metrics
                    'query_count': query_count,
                    'success_count': success_count,
                    'failure_count': failure_count,
                    'avg_response_time_ms': usage_record.get('avg_response_time_ms', 0),
                    'total_documents_served': usage_record.get('documents_served', 0),
                    'unique_users_count': max(1, int(query_count * 0.7)),  # Estimate
                    
                    # Quality metrics
                    'satisfaction_score': usage_record.get('satisfaction_score', 3.5),
                    'bounce_rate': bounce_rate,
                    'completion_rate': completion_rate,
                    
                    # Business metrics
                    'conversion_rate': conversion_rate,
                    'cost_per_interaction': self._calculate_cost_per_interaction(usage_record)
                }
                
                transformed_facts.append(fact_record)
                self.transformation_stats['records_transformed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to transform usage record: {str(e)}")
                self.transformation_stats['records_failed'] += 1
                continue
                
        self.end_transformation()
        return transformed_facts
        
    def transform_data_quality_facts(self, source_data: List[Dict]) -> List[Dict]:
        """Transform source data quality metrics into fact_data_quality format"""
        self.start_transformation()
        
        transformed_facts = []
        
        for source_record in source_data:
            try:
                self.transformation_stats['records_processed'] += 1
                
                # Get dimension keys
                source_key = self._get_source_key(source_record.get('source_name', 'Unknown'))
                date_key = self._get_date_key(source_record.get('check_date', date.today()))
                service_key = self._get_service_key(source_record.get('service_id'))
                
                # Calculate quality metrics
                total_records = source_record.get('total_records', 0)
                valid_records = source_record.get('valid_records', 0)
                
                fact_record = {
                    'source_key': source_key,
                    'date_key': date_key,
                    'service_key': service_key,
                    
                    # Volume metrics
                    'total_records': total_records,
                    'new_records': source_record.get('new_records', 0),
                    'updated_records': source_record.get('updated_records', 0),
                    'deleted_records': source_record.get('deleted_records', 0),
                    
                    # Quality metrics
                    'valid_records': valid_records,
                    'invalid_records': total_records - valid_records,
                    'duplicate_records': source_record.get('duplicate_records', 0),
                    'completeness_score': (valid_records / total_records) if total_records > 0 else 0,
                    'accuracy_score': source_record.get('accuracy_score', 0.95),
                    'consistency_score': source_record.get('consistency_score', 0.90),
                    
                    # Freshness metrics
                    'freshness_hours': source_record.get('freshness_hours', 24),
                    'lag_hours': source_record.get('lag_hours', 2),
                    
                    # Processing metrics
                    'processing_time_seconds': source_record.get('processing_time', 0),
                    'error_count': source_record.get('error_count', 0)
                }
                
                transformed_facts.append(fact_record)
                self.transformation_stats['records_transformed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to transform data quality record: {str(e)}")
                self.transformation_stats['records_failed'] += 1
                continue
                
        self.end_transformation()
        return transformed_facts
        
    def transform_content_analytics_facts(self, content_data: List[Dict]) -> List[Dict]:
        """Transform content analytics into fact_content_analytics format"""
        self.start_transformation()
        
        transformed_facts = []
        
        for content_record in content_data:
            try:
                self.transformation_stats['records_processed'] += 1
                
                # Get dimension keys
                service_key = self._get_service_key(content_record.get('service_id'))
                date_key = self._get_date_key(content_record.get('analytics_date', date.today()))
                content_type_key = self._get_content_type_key(content_record.get('content_type', 'FAQ'))
                language_key = self._get_language_key(content_record.get('language_code', 'en'))
                
                # Calculate engagement metrics
                views_count = content_record.get('views_count', 0)
                downloads_count = content_record.get('downloads_count', 0)
                
                fact_record = {
                    'service_key': service_key,
                    'date_key': date_key,
                    'content_type_key': content_type_key,
                    'language_key': language_key,
                    
                    # Engagement metrics
                    'views_count': views_count,
                    'downloads_count': downloads_count,
                    'shares_count': content_record.get('shares_count', 0),
                    'search_hits': content_record.get('search_hits', 0),
                    'avg_read_time_seconds': content_record.get('avg_read_time', 0),
                    
                    # Content metrics
                    'content_length_words': content_record.get('content_length_words', 0),
                    'content_length_characters': content_record.get('content_length_chars', 0),
                    'readability_score': content_record.get('readability_score', 0.0),
                    'translation_quality_score': content_record.get('translation_quality', 0.0),
                    
                    # Performance metrics
                    'load_time_ms': content_record.get('load_time_ms', 0),
                    'search_rank_position': content_record.get('search_rank', None),
                    'click_through_rate': (downloads_count / views_count) if views_count > 0 else 0
                }
                
                transformed_facts.append(fact_record)
                self.transformation_stats['records_transformed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to transform content analytics record: {str(e)}")
                self.transformation_stats['records_failed'] += 1
                continue
                
        self.end_transformation()
        return transformed_facts
        
    def generate_sample_usage_facts(self, service_ids: List[int], 
                                  date_range: tuple) -> List[Dict]:
        """Generate sample usage data for testing"""
        start_date, end_date = date_range
        current_date = start_date
        
        sample_facts = []
        
        while current_date <= end_date:
            for service_id in service_ids:
                # Generate realistic usage patterns
                base_queries = random.randint(50, 500)
                success_rate = random.uniform(0.75, 0.95)
                
                usage_record = {
                    'service_id': service_id,
                    'usage_date': current_date,
                    'query_count': base_queries,
                    'success_count': int(base_queries * success_rate),
                    'avg_response_time_ms': random.randint(200, 1000),
                    'documents_served': random.randint(10, 100),
                    'satisfaction_score': round(random.uniform(3.0, 5.0), 2),
                    'state_name': random.choice(['Delhi', 'Maharashtra', 'Karnataka']),
                    'age_group': random.choice(['18-25', '26-35', '36-50']),
                    'channel_name': random.choice(['Web Portal', 'Mobile App']),
                    'content_type': random.choice(['FAQ', 'Procedure', 'Document'])
                }
                
                sample_facts.append(usage_record)
                
            # Move to next day
            current_date = date(current_date.year, current_date.month, current_date.day + 1)
            
        return sample_facts
        
    # Helper methods for dimension lookups
    def _get_service_key(self, service_id: int) -> int:
        """Get service key from service ID"""
        if 'services' in self.dimension_lookups:
            return self.dimension_lookups['services'].get(service_id, 1)
        return 1  # Default key
        
    def _get_date_key(self, date_value) -> int:
        """Get date key from date value"""
        if isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                date_obj = date.today()
        elif isinstance(date_value, datetime):
            date_obj = date_value.date()
        elif isinstance(date_value, date):
            date_obj = date_value
        else:
            date_obj = date.today()
            
        return int(date_obj.strftime('%Y%m%d'))
        
    def _get_location_key(self, state_name: str) -> int:
        """Get location key from state name"""
        if 'locations' in self.dimension_lookups:
            return self.dimension_lookups['locations'].get(state_name, 1)
        return 1  # Default key
        
    def _get_user_segment_key(self, age_group: str, education_level: str, device_type: str) -> int:
        """Get user segment key from demographics"""
        segment_id = f"{age_group}|{education_level}|{device_type}"
        if 'user_segments' in self.dimension_lookups:
            return self.dimension_lookups['user_segments'].get(segment_id, 1)
        return 1  # Default key
        
    def _get_channel_key(self, channel_name: str) -> int:
        """Get channel key from channel name"""
        if 'channels' in self.dimension_lookups:
            return self.dimension_lookups['channels'].get(channel_name, 1)
        return 1  # Default key
        
    def _get_content_type_key(self, content_type: str) -> int:
        """Get content type key from content type"""
        if 'content_types' in self.dimension_lookups:
            return self.dimension_lookups['content_types'].get(content_type, 1)
        return 1  # Default key
        
    def _get_source_key(self, source_name: str) -> int:
        """Get source key from source name"""
        if 'sources' in self.dimension_lookups:
            return self.dimension_lookups['sources'].get(source_name, 1)
        return 1  # Default key
        
    def _get_language_key(self, language_code: str) -> int:
        """Get language key from language code"""
        if 'languages' in self.dimension_lookups:
            return self.dimension_lookups['languages'].get(language_code, 1)
        return 1  # Default key
        
    def _calculate_cost_per_interaction(self, usage_record: Dict) -> float:
        """Calculate cost per interaction based on complexity"""
        # Simple cost model - can be made more sophisticated
        base_cost = 0.05  # ₹0.05 per interaction
        
        response_time = usage_record.get('avg_response_time_ms', 500)
        complexity_multiplier = 1.0
        
        if response_time > 1000:
            complexity_multiplier = 1.5
        elif response_time > 500:
            complexity_multiplier = 1.2
            
        return round(base_cost * complexity_multiplier, 4)