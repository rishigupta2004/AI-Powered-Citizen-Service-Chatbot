from .base_loader import BaseLoader
from typing import List, Dict, Optional
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

class DimensionLoader(BaseLoader):
    """Load data into dimension tables with SCD Type 2 support"""
    
    def __init__(self, connection_config: Dict):
        super().__init__(connection_config)
        
    async def load_service_dimension(self, transformed_data: List[Dict]) -> bool:
        """Load service dimension with Slowly Changing Dimension Type 2"""
        self.start_load()
        
        try:
            # Get existing active records
            service_ids = [record['service_id'] for record in transformed_data]
            existing_records = await self.fetch_existing_records(
                'dim_service', 'service_id', service_ids
            )
            
            new_records = []
            updated_records = []
            
            for record in transformed_data:
                service_id = record['service_id']
                existing = existing_records.get(service_id)
                
                if existing:
                    # Check if record has changed (excluding dates and SCD fields)
                    if self._has_service_changed(existing, record):
                        # Expire existing record
                        await self._expire_existing_record('dim_service', existing['service_key'])
                        # Add new version
                        new_records.append(record)
                        updated_records.append(service_id)
                else:
                    # New service
                    new_records.append(record)
                    
            # Insert new records
            if new_records:
                inserted = await self.bulk_insert('dim_service', new_records, 'IGNORE')
                logger.info(f"Inserted {inserted} service dimension records")
                
            await self.log_etl_process(
                'load_service_dimension', 
                'SUCCESS',
                f"Processed {len(transformed_data)} services, {len(new_records)} new/updated"
            )
            
            self.end_load('load_service_dimension')
            return True
            
        except Exception as e:
            logger.error(f"Failed to load service dimension: {str(e)}")
            await self.log_etl_process(
                'load_service_dimension',
                'FAILED', 
                error_details=str(e)
            )
            return False
            
    async def load_date_dimension(self, start_date: date, end_date: date) -> bool:
        """Load date dimension for specified date range"""
        self.start_load()
        
        try:
            date_records = self._generate_date_records(start_date, end_date)
            
            # Check which dates already exist
            existing_dates = await self._get_existing_dates(start_date, end_date)
            
            # Filter out existing dates
            new_dates = [record for record in date_records 
                        if record['date_key'] not in existing_dates]
            
            if new_dates:
                inserted = await self.bulk_insert('dim_date', new_dates, 'IGNORE')
                logger.info(f"Inserted {inserted} date dimension records")
                
            await self.log_etl_process(
                'load_date_dimension',
                'SUCCESS',
                f"Processed date range {start_date} to {end_date}, {len(new_dates)} new dates"
            )
            
            self.end_load('load_date_dimension')
            return True
            
        except Exception as e:
            logger.error(f"Failed to load date dimension: {str(e)}")
            await self.log_etl_process(
                'load_date_dimension',
                'FAILED',
                error_details=str(e)
            )
            return False
            
    async def load_simple_dimension(self, table_name: str, data: List[Dict]) -> bool:
        """Load simple dimension table (no SCD)"""
        self.start_load()
        
        try:
            if data:
                inserted = await self.bulk_insert(table_name, data, 'UPDATE')
                logger.info(f"Loaded {inserted} records into {table_name}")
                
            await self.log_etl_process(
                f'load_{table_name}',
                'SUCCESS',
                f"Loaded {len(data)} records"
            )
            
            self.end_load(f'load_{table_name}')
            return True
            
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {str(e)}")
            await self.log_etl_process(
                f'load_{table_name}',
                'FAILED',
                error_details=str(e)
            )
            return False
            
    async def _expire_existing_record(self, table_name: str, record_key: int):
        """Expire existing record for SCD Type 2"""
        query = f"""
        UPDATE {self.schema}.{table_name}
        SET expiry_date = CURRENT_DATE - INTERVAL '1 day',
            is_current = FALSE
        WHERE {table_name.replace('dim_', '')}_key = $1
        AND is_current = TRUE
        """
        
        await self.execute_query(query, record_key)
        
    def _has_service_changed(self, existing: Dict, new: Dict) -> bool:
        """Check if service record has changed for SCD Type 2"""
        # Fields to compare (excluding SCD and system fields)
        compare_fields = [
            'service_name', 'service_category', 'parent_category',
            'department', 'ministry', 'complexity_level',
            'requires_documents', 'has_fees', 'digital_enabled',
            'target_audience', 'service_type', 'priority_level'
        ]
        
        for field in compare_fields:
            if str(existing.get(field, '')).strip() != str(new.get(field, '')).strip():
                return True
                
        # Check arrays separately
        existing_languages = set(existing.get('languages_supported') or [])
        new_languages = set(new.get('languages_supported') or [])
        if existing_languages != new_languages:
            return True
            
        return False
        
    def _generate_date_records(self, start_date: date, end_date: date) -> List[Dict]:
        """Generate date dimension records for date range"""
        import calendar
        
        date_records = []
        current_date = start_date
        
        while current_date <= end_date:
            # Calculate various date attributes
            year = current_date.year
            month = current_date.month
            day = current_date.day
            
            # Calculate fiscal year (April to March)
            if month >= 4:
                fiscal_year = year
            else:
                fiscal_year = year - 1
                
            # Calculate fiscal quarter
            if month in [4, 5, 6]:
                fiscal_quarter = 1
            elif month in [7, 8, 9]:
                fiscal_quarter = 2
            elif month in [10, 11, 12]:
                fiscal_quarter = 3
            else:
                fiscal_quarter = 4
                
            # Calculate week of year
            week_of_year = current_date.isocalendar()[1]
            
            # Check if it's a weekend
            is_weekend = current_date.weekday() >= 5
            
            # Check if it's a holiday (basic implementation)
            is_holiday = self._is_indian_holiday(current_date)
            holiday_name = self._get_holiday_name(current_date) if is_holiday else None
            
            date_record = {
                'date_key': int(current_date.strftime('%Y%m%d')),
                'full_date': current_date,
                'year': year,
                'quarter': (month - 1) // 3 + 1,
                'month': month,
                'week': week_of_year,
                'day_of_year': current_date.timetuple().tm_yday,
                'day_of_month': day,
                'day_of_week': current_date.weekday() + 1,  # Monday = 1
                'day_name': calendar.day_name[current_date.weekday()],
                'month_name': calendar.month_name[month],
                'is_weekend': is_weekend,
                'is_holiday': is_holiday,
                'holiday_name': holiday_name,
                'fiscal_year': fiscal_year,
                'fiscal_quarter': fiscal_quarter
            }
            
            date_records.append(date_record)
            
            # Move to next day
            current_date = date(current_date.year, current_date.month, current_date.day)
            if current_date.month == 12 and current_date.day == 31:
                current_date = date(current_date.year + 1, 1, 1)
            elif current_date.day == calendar.monthrange(current_date.year, current_date.month)[1]:
                if current_date.month == 12:
                    current_date = date(current_date.year + 1, 1, 1)
                else:
                    current_date = date(current_date.year, current_date.month + 1, 1)
            else:
                current_date = date(current_date.year, current_date.month, current_date.day + 1)
                
        return date_records
        
    async def _get_existing_dates(self, start_date: date, end_date: date) -> set:
        """Get existing date keys in the dimension"""
        pool = await self._get_connection()
        
        start_key = int(start_date.strftime('%Y%m%d'))
        end_key = int(end_date.strftime('%Y%m%d'))
        
        query = """
        SELECT date_key FROM dwh.dim_date 
        WHERE date_key BETWEEN $1 AND $2
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, start_key, end_key)
            
        return {row['date_key'] for row in rows}
        
    def _is_indian_holiday(self, check_date: date) -> bool:
        """Check if date is an Indian national holiday (basic implementation)"""
        # Basic implementation - add more holidays as needed
        month = check_date.month
        day = check_date.day
        
        # Fixed date holidays
        fixed_holidays = [
            (1, 26),   # Republic Day
            (8, 15),   # Independence Day
            (10, 2),   # Gandhi Jayanti
        ]
        
        return (month, day) in fixed_holidays
        
    def _get_holiday_name(self, check_date: date) -> Optional[str]:
        """Get holiday name for the date"""
        month = check_date.month
        day = check_date.day
        
        holiday_names = {
            (1, 26): "Republic Day",
            (8, 15): "Independence Day", 
            (10, 2): "Gandhi Jayanti"
        }
        
        return holiday_names.get((month, day))