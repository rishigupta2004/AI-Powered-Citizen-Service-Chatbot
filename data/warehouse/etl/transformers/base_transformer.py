from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
import hashlib

logger = logging.getLogger(__name__)

class BaseTransformer(ABC):
    """Base class for all data transformers"""
    
    def __init__(self, transformer_name: str):
        self.transformer_name = transformer_name
        self.transformation_stats = {
            'records_processed': 0,
            'records_transformed': 0,
            'records_failed': 0,
            'start_time': None,
            'end_time': None
        }
        
    @abstractmethod
    def transform(self, raw_data: List[Dict]) -> List[Dict]:
        """Transform raw data into warehouse format"""
        pass
        
    def start_transformation(self):
        """Mark start of transformation process"""
        self.transformation_stats['start_time'] = datetime.now()
        self.transformation_stats['records_processed'] = 0
        self.transformation_stats['records_transformed'] = 0
        self.transformation_stats['records_failed'] = 0
        
    def end_transformation(self):
        """Mark end of transformation process"""
        self.transformation_stats['end_time'] = datetime.now()
        duration = (self.transformation_stats['end_time'] - 
                   self.transformation_stats['start_time']).total_seconds()
        
        logger.info(f"Transformation '{self.transformer_name}' completed in {duration:.2f}s")
        logger.info(f"Processed: {self.transformation_stats['records_processed']}, "
                   f"Transformed: {self.transformation_stats['records_transformed']}, "
                   f"Failed: {self.transformation_stats['records_failed']}")
                   
    def clean_text(self, text: str) -> str:
        """Clean and normalize text data"""
        if not text:
            return ""
            
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove special characters but keep important punctuation
        # This is a basic cleaning - you might want more sophisticated cleaning
        text = text.strip()
        
        return text
        
    def categorize_service(self, category: str, description: str = "") -> str:
        """Categorize service based on category and description"""
        if not category:
            return "Other"
            
        category_lower = category.lower()
        desc_lower = description.lower() if description else ""
        
        # Government service categorization
        if any(keyword in category_lower for keyword in ['passport', 'visa']):
            return "Identity & Documentation"
        elif any(keyword in category_lower for keyword in ['aadhaar', 'identity']):
            return "Identity & Documentation"
        elif any(keyword in category_lower for keyword in ['pan', 'tax']):
            return "Taxation"
        elif any(keyword in category_lower for keyword in ['epfo', 'provident', 'pension']):
            return "Employment & Social Security"
        elif any(keyword in category_lower for keyword in ['ration', 'food', 'pds']):
            return "Food & Public Distribution"
        elif any(keyword in category_lower for keyword in ['license', 'driving', 'vehicle']):
            return "Transport & Mobility"
        elif any(keyword in category_lower for keyword in ['birth', 'death', 'certificate']):
            return "Civil Registration"
        elif any(keyword in category_lower for keyword in ['voter', 'election']):
            return "Election & Civic"
        elif any(keyword in category_lower for keyword in ['scholarship', 'education']):
            return "Education & Learning"
        elif any(keyword in category_lower for keyword in ['grievance', 'complaint']):
            return "Grievance & Redressal"
        else:
            return "Other"
            
    def extract_department(self, description: str, category: str = "") -> str:
        """Extract department from service description or category"""
        text = f"{description} {category}".lower()
        
        # Department mapping based on keywords
        dept_mapping = {
            "Ministry of External Affairs": ['passport', 'visa', 'external affairs', 'mea'],
            "Ministry of Electronics & IT": ['aadhaar', 'uidai', 'digital india', 'meity'],
            "Central Board of Direct Taxes": ['pan', 'income tax', 'cbdt'],
            "Ministry of Labour & Employment": ['epfo', 'provident fund', 'labour'],
            "Ministry of Consumer Affairs": ['ration', 'food distribution', 'pds'],
            "Ministry of Road Transport": ['driving license', 'vehicle', 'transport', 'parivahan'],
            "Election Commission": ['voter', 'election', 'epic'],
            "Ministry of Education": ['scholarship', 'education', 'learning'],
            "Department of Administrative Reforms": ['grievance', 'cpgrams', 'darpg']
        }
        
        for dept, keywords in dept_mapping.items():
            if any(keyword in text for keyword in keywords):
                return dept
                
        return "Other Department"
        
    def assess_complexity(self, service_data: Dict) -> str:
        """Assess service complexity based on various factors"""
        complexity_score = 0
        
        # Factor 1: Number of procedures
        procedure_count = service_data.get('procedure_count', 0)
        if procedure_count > 5:
            complexity_score += 2
        elif procedure_count > 2:
            complexity_score += 1
            
        # Factor 2: Number of documents required
        document_count = service_data.get('document_count', 0)
        if document_count > 3:
            complexity_score += 2
        elif document_count > 1:
            complexity_score += 1
            
        # Factor 3: Service category complexity
        category = service_data.get('category', '').lower()
        if any(keyword in category for keyword in ['passport', 'visa', 'complex']):
            complexity_score += 2
        elif any(keyword in category for keyword in ['aadhaar', 'pan']):
            complexity_score += 1
            
        # Determine complexity level
        if complexity_score >= 4:
            return "Complex"
        elif complexity_score >= 2:
            return "Medium"
        else:
            return "Simple"
            
    def generate_hash(self, *args) -> str:
        """Generate hash for business keys"""
        combined = "|".join(str(arg) for arg in args)
        return hashlib.md5(combined.encode()).hexdigest()[:16]
        
    def safe_get(self, data: Dict, key: str, default: Any = None) -> Any:
        """Safely get value from dictionary"""
        return data.get(key, default)
        
    def parse_date(self, date_str: Any) -> Optional[date]:
        """Parse date from various formats"""
        if not date_str:
            return None
            
        if isinstance(date_str, date):
            return date_str
        elif isinstance(date_str, datetime):
            return date_str.date()
        elif isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    logger.warning(f"Could not parse date: {date_str}")
                    return None
        else:
            return None