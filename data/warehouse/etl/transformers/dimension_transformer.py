from .base_transformer import BaseTransformer
from typing import List, Dict, Set
from datetime import date
import logging

logger = logging.getLogger(__name__)

class DimensionTransformer(BaseTransformer):
    """Transform data for dimension tables"""
    
    def __init__(self):
        super().__init__("dimension_transformer")
        
    def transform_service_dimension(self, raw_services: List[Dict]) -> List[Dict]:
        """Transform raw service data for dim_service table"""
        self.start_transformation()
        
        transformed_services = []
        
        for service in raw_services:
            try:
                self.transformation_stats['records_processed'] += 1
                
                # Extract and clean service data
                service_data = {
                    'service_id': service['service_id'],
                    'service_name': self.clean_text(service['service_name']),
                    'service_category': self.categorize_service(
                        service.get('category', ''),
                        service.get('description', '')
                    ),
                    'parent_category': self._get_parent_category(service.get('category', '')),
                    'department': self.extract_department(
                        service.get('description', ''),
                        service.get('category', '')
                    ),
                    'ministry': self._map_to_ministry(service.get('category', '')),
                    'complexity_level': self.assess_complexity(service),
                    'avg_completion_time_days': self._estimate_completion_time(service),
                    'requires_documents': (service.get('document_count', 0) > 0),
                    'has_fees': self._check_for_fees(service.get('description', '')),
                    'digital_enabled': self._check_digital_capability(service),
                    'languages_supported': self._process_languages(service.get('languages_supported', [])),
                    'target_audience': self._identify_target_audience(service),
                    'service_type': self._classify_service_type(service),
                    'priority_level': self._assess_priority(service),
                    'effective_date': self.parse_date(service.get('created_at', date.today())),
                    'expiry_date': date(9999, 12, 31),
                    'is_current': True,
                    'is_active': True,
                    'created_date': self.parse_date(service.get('created_at', date.today())),
                    'last_updated_date': date.today()
                }
                
                transformed_services.append(service_data)
                self.transformation_stats['records_transformed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to transform service {service.get('service_id')}: {str(e)}")
                self.transformation_stats['records_failed'] += 1
                continue
                
        self.end_transformation()
        return transformed_services
        
    def transform_location_dimension(self, raw_locations: List[Dict]) -> List[Dict]:
        """Transform raw location data for dim_location table"""
        self.start_transformation()
        
        # This would typically come from a comprehensive location dataset
        # For now, we'll create some sample location data
        default_locations = [
            {
                'state_code': 'DL',
                'state_name': 'Delhi',
                'district_name': 'New Delhi',
                'city_name': 'New Delhi',
                'pin_code': '110001',
                'rural_urban': 'Urban',
                'region': 'North',
                'tier': 'Tier-1',
                'population_category': 'Metro',
                'literacy_rate': 86.34,
                'internet_penetration': 75.2
            },
            {
                'state_code': 'MH',
                'state_name': 'Maharashtra',
                'district_name': 'Mumbai',
                'city_name': 'Mumbai',
                'pin_code': '400001',
                'rural_urban': 'Urban',
                'region': 'West',
                'tier': 'Tier-1',
                'population_category': 'Metro',
                'literacy_rate': 82.34,
                'internet_penetration': 71.8
            },
            {
                'state_code': 'KA',
                'state_name': 'Karnataka',
                'district_name': 'Bangalore',
                'city_name': 'Bangalore',
                'pin_code': '560001',
                'rural_urban': 'Urban',
                'region': 'South',
                'tier': 'Tier-1',
                'population_category': 'Metro',
                'literacy_rate': 75.36,
                'internet_penetration': 68.5
            }
        ]
        
        transformed_locations = []
        for location in default_locations:
            location['is_active'] = True
            transformed_locations.append(location)
            
        self.transformation_stats['records_processed'] = len(default_locations)
        self.transformation_stats['records_transformed'] = len(transformed_locations)
        self.end_transformation()
        
        return transformed_locations
        
    def transform_user_segment_dimension(self) -> List[Dict]:
        """Create user segment dimension data"""
        # Generate user segments based on common demographics
        age_groups = ['18-25', '26-35', '36-50', '51-65', '65+']
        education_levels = ['Primary', 'Secondary', 'Graduate', 'Post-Graduate']
        income_brackets = ['Below 2L', '2-5L', '5-10L', '10-20L', 'Above 20L']
        device_types = ['Mobile', 'Desktop', 'Tablet']
        
        segments = []
        for age in age_groups:
            for education in education_levels:
                for income in income_brackets[:3]:  # Limit combinations
                    for device in device_types[:2]:  # Mobile and Desktop only
                        segment = {
                            'age_group': age,
                            'education_level': education,
                            'income_bracket': income,
                            'occupation_category': self._map_occupation(age, education),
                            'language_preference': 'en',  # Default to English
                            'device_type': device,
                            'access_frequency': self._estimate_access_frequency(age, income),
                            'tech_savviness': self._assess_tech_savviness(age, education),
                            'geographic_type': 'Urban',  # Default
                            'is_active': True
                        }
                        segments.append(segment)
                        
        return segments
        
    def transform_channel_dimension(self) -> List[Dict]:
        """Create channel dimension data"""
        channels = [
            {
                'channel_name': 'Web Portal',
                'channel_type': 'Digital',
                'platform': 'Web',
                'version': '1.0',
                'is_primary': True,
                'is_active': True
            },
            {
                'channel_name': 'Mobile App',
                'channel_type': 'Digital',
                'platform': 'Android',
                'version': '1.0',
                'is_primary': False,
                'is_active': True
            },
            {
                'channel_name': 'Mobile App',
                'channel_type': 'Digital',
                'platform': 'iOS',
                'version': '1.0',
                'is_primary': False,
                'is_active': True
            },
            {
                'channel_name': 'API',
                'channel_type': 'Digital',
                'platform': 'REST',
                'version': '1.0',
                'is_primary': False,
                'is_active': True
            },
            {
                'channel_name': 'Call Center',
                'channel_type': 'Physical',
                'platform': 'Phone',
                'version': '1.0',
                'is_primary': False,
                'is_active': True
            }
        ]
        
        return channels
        
    def transform_content_type_dimension(self) -> List[Dict]:
        """Create content type dimension data"""
        content_types = [
            {
                'content_type': 'FAQ',
                'content_format': 'HTML',
                'content_source': 'Scraping',
                'content_complexity': 'Simple',
                'requires_translation': True,
                'update_frequency': 'Monthly',
                'is_active': True
            },
            {
                'content_type': 'Procedure',
                'content_format': 'HTML',
                'content_source': 'Scraping',
                'content_complexity': 'Medium',
                'requires_translation': True,
                'update_frequency': 'Weekly',
                'is_active': True
            },
            {
                'content_type': 'Document',
                'content_format': 'PDF',
                'content_source': 'API',
                'content_complexity': 'Complex',
                'requires_translation': False,
                'update_frequency': 'Quarterly',
                'is_active': True
            },
            {
                'content_type': 'Form',
                'content_format': 'PDF',
                'content_source': 'Manual',
                'content_complexity': 'Medium',
                'requires_translation': True,
                'update_frequency': 'Annually',
                'is_active': True
            }
        ]
        
        return content_types
        
    def transform_language_dimension(self) -> List[Dict]:
        """Create language dimension data"""
        languages = [
            {
                'language_code': 'en',
                'language_name': 'English',
                'native_name': 'English',
                'script_type': 'Latin',
                'is_official': True,
                'speaker_population': 125000000,
                'is_supported': True
            },
            {
                'language_code': 'hi',
                'language_name': 'Hindi',
                'native_name': 'हिन्दी',
                'script_type': 'Devanagari',
                'is_official': True,
                'speaker_population': 602000000,
                'is_supported': True
            },
            {
                'language_code': 'bn',
                'language_name': 'Bengali',
                'native_name': 'বাংলা',
                'script_type': 'Bengali',
                'is_official': True,
                'speaker_population': 104000000,
                'is_supported': True
            },
            {
                'language_code': 'ta',
                'language_name': 'Tamil',
                'native_name': 'தமிழ்',
                'script_type': 'Tamil',
                'is_official': True,
                'speaker_population': 75000000,
                'is_supported': True
            }
        ]
        
        return languages
        
    # Helper methods
    def _get_parent_category(self, category: str) -> str:
        """Get parent category for hierarchical categorization"""
        category_hierarchy = {
            'Identity & Documentation': 'Citizen Services',
            'Taxation': 'Financial Services',
            'Employment & Social Security': 'Social Services',
            'Food & Public Distribution': 'Social Services',
            'Transport & Mobility': 'Infrastructure Services',
            'Civil Registration': 'Citizen Services',
            'Election & Civic': 'Democratic Services',
            'Education & Learning': 'Social Services',
            'Grievance & Redressal': 'Administrative Services'
        }
        
        service_category = self.categorize_service(category)
        return category_hierarchy.get(service_category, 'Other Services')
        
    def _map_to_ministry(self, category: str) -> str:
        """Map service category to appropriate ministry"""
        ministry_mapping = {
            'passport': 'Ministry of External Affairs',
            'aadhaar': 'Ministry of Electronics & IT',
            'pan': 'Ministry of Finance',
            'epfo': 'Ministry of Labour & Employment',
            'ration': 'Ministry of Consumer Affairs',
            'license': 'Ministry of Road Transport',
            'voter': 'Election Commission',
            'scholarship': 'Ministry of Education'
        }
        
        category_lower = category.lower()
        for keyword, ministry in ministry_mapping.items():
            if keyword in category_lower:
                return ministry
                
        return 'Other Ministry'
        
    def _estimate_completion_time(self, service: Dict) -> int:
        """Estimate average completion time in days"""
        complexity = self.assess_complexity(service)
        if complexity == 'Complex':
            return 30
        elif complexity == 'Medium':
            return 15
        else:
            return 7
            
    def _check_for_fees(self, description: str) -> bool:
        """Check if service involves fees"""
        fee_keywords = ['fee', 'payment', 'cost', 'charge', 'amount', 'rupees']
        return any(keyword in description.lower() for keyword in fee_keywords)
        
    def _check_digital_capability(self, service: Dict) -> bool:
        """Check if service is digitally enabled"""
        # Services with procedures and documents are likely digitally enabled
        return (service.get('procedure_count', 0) > 0 or 
                service.get('document_count', 0) > 0)
        
    def _process_languages(self, languages: list) -> list:
        """Process and standardize language list"""
        if not languages:
            return ['en']  # Default to English
            
        # Clean and standardize language codes
        standardized = []
        for lang in languages:
            if lang and lang not in standardized:
                standardized.append(lang.lower()[:2])  # Use 2-letter codes
                
        return standardized if standardized else ['en']
        
    def _identify_target_audience(self, service: Dict) -> str:
        """Identify target audience for the service"""
        description = service.get('description', '').lower()
        
        if any(keyword in description for keyword in ['business', 'company', 'enterprise']):
            return 'Businesses'
        else:
            return 'Citizens'
            
    def _classify_service_type(self, service: Dict) -> str:
        """Classify service type based on function"""
        name = service.get('service_name', '').lower()
        category = service.get('category', '').lower()
        
        if any(keyword in f"{name} {category}" for keyword in ['certificate', 'license', 'card']):
            return 'Certificate'
        elif any(keyword in f"{name} {category}" for keyword in ['application', 'apply', 'registration']):
            return 'Transaction'
        elif any(keyword in f"{name} {category}" for keyword in ['complaint', 'grievance', 'feedback']):
            return 'Grievance'
        else:
            return 'Information'
            
    def _assess_priority(self, service: Dict) -> str:
        """Assess service priority level"""
        essential_services = ['passport', 'aadhaar', 'pan', 'ration', 'license']
        category = service.get('category', '').lower()
        
        if any(keyword in category for keyword in essential_services):
            return 'High'
        elif service.get('procedure_count', 0) > 3:
            return 'Medium'
        else:
            return 'Low'
            
    def _map_occupation(self, age_group: str, education_level: str) -> str:
        """Map occupation based on age and education"""
        if age_group == '18-25':
            return 'Student' if education_level in ['Primary', 'Secondary'] else 'Employee'
        elif age_group in ['26-35', '36-50']:
            return 'Employee' if education_level in ['Graduate', 'Post-Graduate'] else 'Business'
        elif age_group == '51-65':
            return 'Business' if education_level in ['Graduate', 'Post-Graduate'] else 'Employee'
        else:
            return 'Retired'
            
    def _estimate_access_frequency(self, age_group: str, income_bracket: str) -> str:
        """Estimate access frequency based on demographics"""
        if age_group in ['18-25', '26-35'] and income_bracket in ['5-10L', '10-20L', 'Above 20L']:
            return 'Weekly'
        elif age_group in ['36-50'] and income_bracket != 'Below 2L':
            return 'Monthly'
        else:
            return 'Occasional'
            
    def _assess_tech_savviness(self, age_group: str, education_level: str) -> str:
        """Assess tech savviness based on age and education"""
        if age_group in ['18-25', '26-35'] and education_level in ['Graduate', 'Post-Graduate']:
            return 'High'
        elif age_group in ['36-50'] and education_level in ['Graduate', 'Post-Graduate']:
            return 'Medium'
        elif age_group in ['18-35'] and education_level in ['Primary', 'Secondary']:
            return 'Medium'
        else:
            return 'Low'