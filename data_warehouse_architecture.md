# 🏗️ Citizen Services Data Warehouse Architecture

## 🎯 Executive Summary

This document outlines the comprehensive data warehouse architecture for the Citizen Services Database project. The data warehouse will serve as the central analytical platform that transforms operational data from multiple government service sources into actionable insights for both citizens and administrators.

## 🏛️ Data Warehouse Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Analytics Dashboard  │  Admin Reports  │  Public API  │  BI Tools│
└─────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────┐
│                      SEMANTIC LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│    Data Marts    │   OLAP Cubes   │  Aggregations │  KPI Models │
└─────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│         ETL Pipelines         │        Data Quality Engine      │
└─────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Fact Tables  │ Dimension Tables │ Staging Area │ Archive Store │
└─────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────┐
│                     SOURCE LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│ Operational DB │ Scraped Data │ API Responses │ Document Store  │
└─────────────────────────────────────────────────────────────────┘
```

## 🗂️ Dimensional Model Design

### Star Schema Architecture

The data warehouse follows a **star schema** pattern optimized for government service analytics:

```
              ┌─────────────────┐
              │  dim_service    │
              │─────────────────│
              │ service_key (PK)│
              │ service_id      │
              │ service_name    │
              │ category        │
              │ department      │
              │ ministry        │
              │ complexity_level│
              │ is_active       │
              └─────────────────┘
                       │
                       │
         ┌─────────────▼─────────────┐
         │     fact_service_usage    │
         │─────────────────────────  │
         │ usage_id (PK)             │
         │ service_key (FK)          │
         │ date_key (FK)             │
         │ location_key (FK)         │
         │ user_segment_key (FK)     │
         │ channel_key (FK)          │
         │ content_type_key (FK)     │
         │ query_count               │
         │ success_count             │
         │ failure_count             │
         │ avg_response_time_ms      │
         │ total_documents_served    │
         │ satisfaction_score        │
         └───────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
┌────────▼──────┐ ┌───▼────────┐ ┌──▼──────────────┐
│   dim_date    │ │dim_location│ │ dim_user_segment│
│───────────────│ │────────────│ │─────────────────│
│date_key (PK)  │ │location_key│ │segment_key (PK) │
│full_date      │ │state       │ │age_group        │
│year           │ │district    │ │education_level  │
│quarter        │ │city        │ │income_bracket   │
│month          │ │pin_code    │ │language_pref    │
│week           │ │rural_urban │ │device_type      │
│day_of_week    │ │region      │ │access_frequency │
│is_holiday     │ └────────────┘ └─────────────────┘
│fiscal_year    │
└───────────────┘
```

### Core Fact Tables

#### 1. fact_service_usage
**Purpose**: Track citizen interactions with government services
```sql
CREATE TABLE dwh.fact_service_usage (
    usage_id BIGSERIAL PRIMARY KEY,
    service_key INTEGER REFERENCES dwh.dim_service(service_key),
    date_key INTEGER REFERENCES dwh.dim_date(date_key),
    location_key INTEGER REFERENCES dwh.dim_location(location_key),
    user_segment_key INTEGER REFERENCES dwh.dim_user_segment(segment_key),
    channel_key INTEGER REFERENCES dwh.dim_channel(channel_key),
    content_type_key INTEGER REFERENCES dwh.dim_content_type(content_type_key),
    
    -- Metrics
    query_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_response_time_ms NUMERIC(8,2),
    total_documents_served INTEGER DEFAULT 0,
    satisfaction_score NUMERIC(3,2),
    bounce_rate NUMERIC(5,4),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. fact_data_quality
**Purpose**: Monitor data quality across all ingested sources
```sql
CREATE TABLE dwh.fact_data_quality (
    quality_id BIGSERIAL PRIMARY KEY,
    source_key INTEGER REFERENCES dwh.dim_source(source_key),
    date_key INTEGER REFERENCES dwh.dim_date(date_key),
    service_key INTEGER REFERENCES dwh.dim_service(service_key),
    
    -- Quality Metrics
    total_records INTEGER,
    valid_records INTEGER,
    invalid_records INTEGER,
    duplicate_records INTEGER,
    completeness_score NUMERIC(5,4),
    accuracy_score NUMERIC(5,4),
    freshness_hours INTEGER,
    consistency_score NUMERIC(5,4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. fact_content_analytics
**Purpose**: Analyze document and content performance
```sql
CREATE TABLE dwh.fact_content_analytics (
    content_id BIGSERIAL PRIMARY KEY,
    service_key INTEGER REFERENCES dwh.dim_service(service_key),
    date_key INTEGER REFERENCES dwh.dim_date(date_key),
    content_type_key INTEGER REFERENCES dwh.dim_content_type(content_type_key),
    language_key INTEGER REFERENCES dwh.dim_language(language_key),
    
    -- Content Metrics
    views_count INTEGER DEFAULT 0,
    downloads_count INTEGER DEFAULT 0,
    search_hits INTEGER DEFAULT 0,
    avg_read_time_seconds INTEGER,
    content_length_words INTEGER,
    readability_score NUMERIC(5,2),
    translation_quality_score NUMERIC(5,4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Core Dimension Tables

#### 1. dim_service
```sql
CREATE TABLE dwh.dim_service (
    service_key SERIAL PRIMARY KEY,
    service_id INTEGER UNIQUE,
    service_name VARCHAR(200) NOT NULL,
    service_category VARCHAR(100),
    parent_category VARCHAR(100),
    department VARCHAR(150),
    ministry VARCHAR(150),
    complexity_level VARCHAR(20), -- Simple, Medium, Complex
    avg_completion_time_days INTEGER,
    requires_documents BOOLEAN DEFAULT FALSE,
    has_fees BOOLEAN DEFAULT FALSE,
    digital_enabled BOOLEAN DEFAULT FALSE,
    languages_supported TEXT[], -- Array of language codes
    target_audience VARCHAR(100), -- Citizens, Businesses, Both
    service_type VARCHAR(50), -- Information, Transaction, Grievance
    priority_level VARCHAR(20), -- High, Medium, Low
    is_active BOOLEAN DEFAULT TRUE,
    created_date DATE,
    last_updated_date DATE
);
```

#### 2. dim_location
```sql
CREATE TABLE dwh.dim_location (
    location_key SERIAL PRIMARY KEY,
    state_code VARCHAR(10),
    state_name VARCHAR(100),
    district_code VARCHAR(10),
    district_name VARCHAR(100),
    city_name VARCHAR(100),
    pin_code VARCHAR(10),
    rural_urban VARCHAR(10), -- Rural, Urban, Semi-Urban
    region VARCHAR(50), -- North, South, East, West, Central, Northeast
    tier VARCHAR(10), -- Tier-1, Tier-2, Tier-3
    population_category VARCHAR(20), -- Metro, Large, Medium, Small
    literacy_rate NUMERIC(5,2),
    internet_penetration NUMERIC(5,2),
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 3. dim_user_segment
```sql
CREATE TABLE dwh.dim_user_segment (
    segment_key SERIAL PRIMARY KEY,
    age_group VARCHAR(20), -- 18-25, 26-35, 36-50, 51-65, 65+
    education_level VARCHAR(50), -- Primary, Secondary, Graduate, Post-Graduate
    income_bracket VARCHAR(30), -- Below 2L, 2-5L, 5-10L, 10-20L, Above 20L
    occupation_category VARCHAR(50), -- Student, Employee, Business, Retired
    language_preference VARCHAR(10), -- hi, en, bn, etc.
    device_type VARCHAR(20), -- Mobile, Desktop, Tablet
    access_frequency VARCHAR(20), -- Daily, Weekly, Monthly, Occasional
    tech_savviness VARCHAR(20), -- Low, Medium, High
    geographic_type VARCHAR(20), -- Urban, Rural, Semi-Urban
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 4. dim_channel
```sql
CREATE TABLE dwh.dim_channel (
    channel_key SERIAL PRIMARY KEY,
    channel_name VARCHAR(50), -- Web Portal, Mobile App, API, Chatbot, Call Center
    channel_type VARCHAR(30), -- Digital, Physical, Hybrid
    platform VARCHAR(30), -- Android, iOS, Web, Desktop
    version VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 5. dim_content_type
```sql
CREATE TABLE dwh.dim_content_type (
    content_type_key SERIAL PRIMARY KEY,
    content_type VARCHAR(50), -- FAQ, Procedure, Document, Form, Guide
    content_format VARCHAR(30), -- PDF, HTML, Word, Image, Video
    content_source VARCHAR(50), -- API, Scraping, Manual, Upload
    content_complexity VARCHAR(20), -- Simple, Medium, Complex
    requires_translation BOOLEAN DEFAULT FALSE,
    update_frequency VARCHAR(20), -- Daily, Weekly, Monthly, Quarterly
    is_active BOOLEAN DEFAULT TRUE
);
```

## 🔄 ETL Pipeline Architecture

### 1. Data Extraction Layer

```python
# data/warehouse/etl/extractors/
class ServiceDataExtractor:
    """Extract operational data from main database"""
    
    async def extract_services(self, last_extracted: datetime) -> List[Dict]:
        query = """
        SELECT s.*, COUNT(p.procedure_id) as procedure_count,
               COUNT(d.doc_id) as document_count,
               COUNT(f.faq_id) as faq_count
        FROM services s
        LEFT JOIN procedures p ON s.service_id = p.service_id  
        LEFT JOIN documents d ON s.service_id = d.service_id
        LEFT JOIN faqs f ON s.service_id = f.service_id
        WHERE s.updated_at > %s
        GROUP BY s.service_id
        """
        return await self.db.fetch_all(query, [last_extracted])

class UsageDataExtractor:
    """Extract usage analytics from logs and API calls"""
    
    async def extract_api_usage(self, date_range: Tuple[date, date]) -> List[Dict]:
        # Extract from API logs, search logs, user interaction logs
        pass

class ContentDataExtractor:
    """Extract content analytics from scraped data and documents"""
    
    async def extract_document_metrics(self, date_range: Tuple[date, date]) -> List[Dict]:
        # Analyze document engagement, download patterns, search relevance
        pass
```

### 2. Data Transformation Layer

```python
# data/warehouse/etl/transformers/
class DimensionTransformer:
    """Transform data for dimension tables"""
    
    def transform_service_dimension(self, raw_services: List[Dict]) -> List[Dict]:
        transformed = []
        for service in raw_services:
            transformed.append({
                'service_id': service['service_id'],
                'service_name': service['name'],
                'service_category': self.categorize_service(service['category']),
                'department': self.extract_department(service['description']),
                'ministry': self.map_to_ministry(service['category']),
                'complexity_level': self.assess_complexity(service),
                'avg_completion_time_days': self.estimate_completion_time(service),
                'requires_documents': service['document_count'] > 0,
                'has_fees': self.check_for_fees(service['description']),
                'digital_enabled': self.check_digital_capability(service),
                'languages_supported': self.detect_languages(service),
                'target_audience': self.identify_target_audience(service),
                'service_type': self.classify_service_type(service),
                'priority_level': self.assess_priority(service),
                'is_active': True,
                'created_date': service['created_at'].date(),
                'last_updated_date': date.today()
            })
        return transformed

class FactTransformer:
    """Transform data for fact tables"""
    
    def transform_usage_facts(self, raw_usage: List[Dict], 
                            dimension_lookups: Dict) -> List[Dict]:
        # Transform raw usage data into fact table format
        # Apply business rules and calculations
        pass
```

### 3. Data Loading Layer

```python
# data/warehouse/etl/loaders/
class DimensionLoader:
    """Load data into dimension tables with SCD Type 2 support"""
    
    async def load_service_dimension(self, transformed_data: List[Dict]):
        # Implement Slowly Changing Dimension Type 2
        for record in transformed_data:
            existing = await self.get_existing_record(record['service_id'])
            if existing:
                if self.has_changed(existing, record):
                    await self.expire_existing_record(existing['service_key'])
                    await self.insert_new_record(record)
            else:
                await self.insert_new_record(record)

class FactLoader:
    """Load data into fact tables with incremental processing"""
    
    async def load_usage_facts(self, transformed_data: List[Dict]):
        # Batch insert with conflict resolution
        await self.bulk_insert_with_upsert(transformed_data)
```

## 📊 Data Mart Specializations

### 1. Service Performance Data Mart
**Purpose**: Monitor government service delivery effectiveness

```sql
CREATE VIEW dm_service_performance AS
SELECT 
    ds.service_name,
    ds.service_category,
    ds.department,
    dd.year,
    dd.quarter,
    dd.month,
    SUM(fsu.query_count) as total_queries,
    SUM(fsu.success_count) as successful_queries,
    AVG(fsu.satisfaction_score) as avg_satisfaction,
    AVG(fsu.avg_response_time_ms) as avg_response_time,
    (SUM(fsu.success_count)::FLOAT / SUM(fsu.query_count) * 100) as success_rate
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_service ds ON fsu.service_key = ds.service_key
JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
WHERE ds.is_active = TRUE
GROUP BY ds.service_name, ds.service_category, ds.department, dd.year, dd.quarter, dd.month;
```

### 2. Citizen Engagement Data Mart
**Purpose**: Understand citizen behavior and preferences

```sql
CREATE VIEW dm_citizen_engagement AS
SELECT 
    dus.age_group,
    dus.education_level,
    dus.language_preference,
    dl.state_name,
    dl.rural_urban,
    dd.year,
    dd.month,
    COUNT(DISTINCT fsu.usage_id) as unique_interactions,
    AVG(fsu.satisfaction_score) as avg_satisfaction,
    SUM(fsu.total_documents_served) as documents_accessed,
    AVG(fca.avg_read_time_seconds) as avg_engagement_time
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_user_segment dus ON fsu.user_segment_key = dus.segment_key
JOIN dwh.dim_location dl ON fsu.location_key = dl.location_key
JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
LEFT JOIN dwh.fact_content_analytics fca ON fsu.service_key = fca.service_key 
    AND fsu.date_key = fca.date_key
GROUP BY dus.age_group, dus.education_level, dus.language_preference, 
         dl.state_name, dl.rural_urban, dd.year, dd.month;
```

### 3. Content Analytics Data Mart
**Purpose**: Optimize content strategy and multilingual support

```sql
CREATE VIEW dm_content_analytics AS
SELECT 
    ds.service_name,
    dct.content_type,
    dct.content_format,
    dl.language_name,
    dd.year,
    dd.quarter,
    SUM(fca.views_count) as total_views,
    SUM(fca.downloads_count) as total_downloads,
    AVG(fca.readability_score) as avg_readability,
    AVG(fca.translation_quality_score) as avg_translation_quality,
    (SUM(fca.downloads_count)::FLOAT / SUM(fca.views_count) * 100) as conversion_rate
FROM dwh.fact_content_analytics fca
JOIN dwh.dim_service ds ON fca.service_key = ds.service_key
JOIN dwh.dim_content_type dct ON fca.content_type_key = dct.content_type_key
JOIN dwh.dim_language dl ON fca.language_key = dl.language_key
JOIN dwh.dim_date dd ON fca.date_key = dd.date_key
GROUP BY ds.service_name, dct.content_type, dct.content_format, 
         dl.language_name, dd.year, dd.quarter;
```

## 🔧 Implementation Strategy

### Phase 1: Foundation (Week 6.1-6.2)
1. **Database Schema Creation**
   - Create separate schema `dwh` for data warehouse tables
   - Implement all dimension and fact tables
   - Set up indexes and constraints

2. **ETL Framework Setup**
   - Create base ETL classes and interfaces
   - Set up logging and monitoring for ETL processes
   - Implement error handling and retry mechanisms

### Phase 2: Data Pipeline (Week 6.3-6.4)  
1. **Dimension Loading**
   - Implement extractors for all dimension data
   - Create transformation logic with business rules
   - Set up SCD Type 2 for changing dimensions

2. **Fact Table Population**
   - Build usage analytics from existing logs
   - Implement incremental loading strategies
   - Create data quality validation

### Phase 3: Analytics Layer (Week 6.5-6.6)
1. **Data Marts Creation**
   - Build specialized views for different analysis needs
   - Create aggregated tables for performance
   - Implement OLAP cubes for multidimensional analysis

2. **Reporting Infrastructure**
   - Set up connection to BI tools (Metabase, Grafana)
   - Create standard reports and dashboards
   - Implement automated report generation

## 📈 Key Performance Indicators (KPIs)

### 1. Service Delivery KPIs
- **Service Completion Rate**: % of successful service interactions
- **Average Response Time**: Time to serve information/documents
- **Citizen Satisfaction Score**: User feedback ratings
- **Digital Adoption Rate**: % of services accessed digitally

### 2. Content Performance KPIs
- **Content Freshness**: % of content updated within SLA
- **Multilingual Coverage**: % of content available in regional languages
- **Content Accuracy**: % of information validated against official sources
- **Search Relevance**: % of searches returning useful results

### 3. Operational KPIs
- **Data Quality Score**: Overall data completeness and accuracy
- **ETL Success Rate**: % of successful data pipeline runs
- **System Availability**: Uptime of data warehouse services
- **Query Performance**: Average query response time

## 🚀 Benefits of the Data Warehouse

### For Citizens
- **Faster Service Discovery**: Optimized search based on usage patterns
- **Personalized Recommendations**: Services relevant to user profile
- **Multi-language Support**: Content in preferred regional languages
- **Mobile-First Experience**: Optimized for mobile device usage

### For Government Administrators
- **Performance Monitoring**: Real-time dashboards for service delivery
- **Citizen Insights**: Understanding of user needs and behavior
- **Resource Optimization**: Data-driven decisions for service improvements
- **Compliance Reporting**: Automated generation of regulatory reports

### For System Operators
- **Data Quality Monitoring**: Proactive identification of data issues
- **Usage Analytics**: Understanding of system load and performance
- **Content Optimization**: Insights for improving content strategy
- **Predictive Maintenance**: Forecasting of system resource needs

This data warehouse architecture will provide a solid foundation for advanced analytics, machine learning, and business intelligence on top of your citizen services platform, enabling data-driven improvements and better citizen experience.