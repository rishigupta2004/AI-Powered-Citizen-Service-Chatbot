# 🏗️ Citizen Services Data Warehouse Architecture

## Overview
This document outlines the data warehouse architecture for the Citizen Services Database project, designed to support analytics, reporting, and business intelligence on government service data.

## 🎯 Data Warehouse Objectives

### Primary Goals
1. **Analytics & Reporting**: Enable comprehensive analytics on service usage, citizen queries, and system performance
2. **Business Intelligence**: Support decision-making with historical data trends and patterns
3. **Data Quality Monitoring**: Track data quality metrics and identify issues
4. **Performance Analytics**: Monitor system performance and user behavior
5. **Compliance Reporting**: Generate reports for regulatory and audit requirements

### Key Metrics to Track
- Service usage patterns and trends
- Query success rates and response times
- Data freshness and quality scores
- User engagement and satisfaction
- System performance and availability
- Content coverage and completeness

## 🏛️ Data Warehouse Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA WAREHOUSE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  Analytics Layer (OLAP)                                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Reports   │ │ Dashboards  │ │   Alerts    │ │   Metrics   ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Data Marts (Subject-Oriented)                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Service   │ │   User      │ │  Content    │ │  System     ││
│  │   Analytics │ │  Analytics  │ │  Analytics  │ │  Analytics  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Data Warehouse Core (Dimensional Model)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Facts     │ │ Dimensions  │ │   Aggregates│ │   Metadata  ││
│  │   Tables    │ │   Tables    │ │   Tables    │ │   Tables    ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  ETL Layer (Extract, Transform, Load)                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Extract   │ │ Transform   │ │    Load     │ │   Quality   ││
│  │   Jobs      │ │   Jobs      │ │   Jobs      │ │   Checks    ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Source Systems (OLTP)                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ Operational │ │   API       │ │  Scraped    │ │  Document   ││
│  │   Database  │ │   Data      │ │   Data      │ │   Store     ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Dimensional Data Model

### Fact Tables

#### 1. Service Query Fact (fct_service_queries)
```sql
-- Tracks every query made to the system
CREATE TABLE fct_service_queries (
    query_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,                    -- FK to dim_date
    time_key INTEGER NOT NULL,                    -- FK to dim_time
    service_key INTEGER NOT NULL,                 -- FK to dim_service
    user_key INTEGER,                             -- FK to dim_user (nullable for anonymous)
    query_type_key INTEGER NOT NULL,              -- FK to dim_query_type
    language_key INTEGER NOT NULL,                -- FK to dim_language
    response_time_ms INTEGER,                     -- Response time in milliseconds
    success_flag BOOLEAN NOT NULL,                -- Query success/failure
    result_count INTEGER,                         -- Number of results returned
    user_satisfaction_score INTEGER,              -- 1-5 rating (if available)
    session_id VARCHAR(255),                      -- User session identifier
    ip_address INET,                              -- User IP (anonymized)
    user_agent TEXT,                              -- Browser/client info
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 2. Content Usage Fact (fct_content_usage)
```sql
-- Tracks content consumption and engagement
CREATE TABLE fct_content_usage (
    usage_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,                    -- FK to dim_date
    time_key INTEGER NOT NULL,                    -- FK to dim_time
    content_key INTEGER NOT NULL,                 -- FK to dim_content
    service_key INTEGER NOT NULL,                 -- FK to dim_service
    user_key INTEGER,                             -- FK to dim_user
    content_type_key INTEGER NOT NULL,            -- FK to dim_content_type
    action_type VARCHAR(50) NOT NULL,             -- 'view', 'download', 'share', 'bookmark'
    duration_seconds INTEGER,                     -- Time spent on content
    scroll_depth_percent INTEGER,                 -- How much of content was viewed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 3. Data Quality Fact (fct_data_quality)
```sql
-- Tracks data quality metrics
CREATE TABLE fct_data_quality (
    quality_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,                    -- FK to dim_date
    service_key INTEGER NOT NULL,                 -- FK to dim_service
    content_source_key INTEGER NOT NULL,          -- FK to dim_content_source
    quality_metric_key INTEGER NOT NULL,          -- FK to dim_quality_metric
    metric_value DECIMAL(10,4) NOT NULL,          -- Quality score (0-100)
    threshold_value DECIMAL(10,4),                -- Expected threshold
    status VARCHAR(20) NOT NULL,                  -- 'pass', 'warning', 'fail'
    details JSONB,                                -- Additional quality details
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 4. System Performance Fact (fct_system_performance)
```sql
-- Tracks system performance metrics
CREATE TABLE fct_system_performance (
    performance_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,                    -- FK to dim_date
    time_key INTEGER NOT NULL,                    -- FK to dim_time
    service_key INTEGER NOT NULL,                 -- FK to dim_service
    metric_type VARCHAR(50) NOT NULL,             -- 'response_time', 'throughput', 'error_rate'
    metric_value DECIMAL(10,4) NOT NULL,          -- Metric value
    unit VARCHAR(20) NOT NULL,                    -- 'ms', 'requests_per_second', 'percentage'
    threshold_value DECIMAL(10,4),                -- Performance threshold
    status VARCHAR(20) NOT NULL,                  -- 'normal', 'warning', 'critical'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Dimension Tables

#### 1. Date Dimension (dim_date)
```sql
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,                 -- YYYYMMDD format
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL
);
```

#### 2. Time Dimension (dim_time)
```sql
CREATE TABLE dim_time (
    time_key INTEGER PRIMARY KEY,                 -- HHMMSS format
    full_time TIME NOT NULL,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    second INTEGER NOT NULL,
    hour_of_day INTEGER NOT NULL,                 -- 0-23
    period_of_day VARCHAR(20) NOT NULL,           -- 'morning', 'afternoon', 'evening', 'night'
    is_business_hours BOOLEAN NOT NULL,
    is_peak_hours BOOLEAN NOT NULL
);
```

#### 3. Service Dimension (dim_service)
```sql
CREATE TABLE dim_service (
    service_key INTEGER PRIMARY KEY,
    service_id INTEGER NOT NULL,                  -- FK to operational services table
    service_name VARCHAR(150) NOT NULL,
    service_category VARCHAR(80) NOT NULL,
    department VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL,
    priority_level INTEGER NOT NULL,              -- 1-5 priority
    service_type VARCHAR(50) NOT NULL,            -- 'api', 'scraped', 'document'
    data_source VARCHAR(100) NOT NULL,            -- 'apisetu', 'uidai', 'scraped', etc.
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE
);
```

#### 4. User Dimension (dim_user)
```sql
CREATE TABLE dim_user (
    user_key INTEGER PRIMARY KEY,
    user_id INTEGER,                              -- FK to operational users table (nullable for anonymous)
    user_type VARCHAR(50) NOT NULL,               -- 'citizen', 'admin', 'api_client', 'anonymous'
    location_state VARCHAR(100),
    location_district VARCHAR(100),
    language_preference VARCHAR(10),
    device_type VARCHAR(50),                      -- 'mobile', 'desktop', 'tablet'
    browser_type VARCHAR(50),
    is_first_time_user BOOLEAN,
    registration_date DATE,
    last_activity_date DATE,
    created_at TIMESTAMP WITH TIME ZONE
);
```

#### 5. Content Dimension (dim_content)
```sql
CREATE TABLE dim_content (
    content_key INTEGER PRIMARY KEY,
    content_id INTEGER NOT NULL,                  -- FK to operational content tables
    content_type VARCHAR(50) NOT NULL,            -- 'procedure', 'document', 'faq', 'article'
    title VARCHAR(500) NOT NULL,
    language VARCHAR(10) NOT NULL,
    content_source VARCHAR(100) NOT NULL,         -- 'api', 'scraped', 'manual'
    is_active BOOLEAN NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE
);
```

#### 6. Query Type Dimension (dim_query_type)
```sql
CREATE TABLE dim_query_type (
    query_type_key INTEGER PRIMARY KEY,
    query_type VARCHAR(50) NOT NULL,              -- 'search', 'status_check', 'verification', 'information'
    query_category VARCHAR(50) NOT NULL,          -- 'general', 'specific', 'procedural'
    complexity_level VARCHAR(20) NOT NULL,        -- 'simple', 'moderate', 'complex'
    expected_response_time_ms INTEGER,            -- Expected response time
    is_api_required BOOLEAN NOT NULL,
    description TEXT
);
```

#### 7. Language Dimension (dim_language)
```sql
CREATE TABLE dim_language (
    language_key INTEGER PRIMARY KEY,
    language_code VARCHAR(10) NOT NULL,           -- 'en', 'hi', 'bn', etc.
    language_name VARCHAR(50) NOT NULL,
    script_type VARCHAR(20) NOT NULL,             -- 'latin', 'devanagari', 'bengali'
    is_rtl BOOLEAN NOT NULL,                      -- Right-to-left language
    is_supported BOOLEAN NOT NULL,
    coverage_percentage DECIMAL(5,2)              -- Content coverage percentage
);
```

#### 8. Content Source Dimension (dim_content_source)
```sql
CREATE TABLE dim_content_source (
    content_source_key INTEGER PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,            -- 'apisetu', 'uidai', 'passportindia', etc.
    source_type VARCHAR(50) NOT NULL,             -- 'api', 'scraping', 'manual', 'document'
    reliability_score DECIMAL(3,2) NOT NULL,      -- 0.00-1.00
    update_frequency VARCHAR(50) NOT NULL,        -- 'real_time', 'daily', 'weekly', 'monthly'
    last_sync TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL,
    contact_info JSONB,                           -- Source contact information
    created_at TIMESTAMP WITH TIME ZONE
);
```

#### 9. Quality Metric Dimension (dim_quality_metric)
```sql
CREATE TABLE dim_quality_metric (
    quality_metric_key INTEGER PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,            -- 'completeness', 'accuracy', 'freshness', 'consistency'
    metric_category VARCHAR(50) NOT NULL,         -- 'data_quality', 'content_quality', 'system_quality'
    measurement_unit VARCHAR(20) NOT NULL,        -- 'percentage', 'count', 'score'
    threshold_good DECIMAL(10,4),                 -- Good threshold
    threshold_warning DECIMAL(10,4),              -- Warning threshold
    threshold_critical DECIMAL(10,4),             -- Critical threshold
    description TEXT,
    is_active BOOLEAN NOT NULL
);
```

## 🔄 ETL Pipeline Architecture

### Extract Layer
```python
# data/warehouse/etl/extract/
├── extractors/
│   ├── operational_extractor.py      # Extract from operational DB
│   ├── api_extractor.py              # Extract from API responses
│   ├── scraping_extractor.py         # Extract from scraped data
│   └── document_extractor.py         # Extract from document store
├── connectors/
│   ├── postgres_connector.py         # PostgreSQL connection
│   ├── mongodb_connector.py          # MongoDB connection
│   └── redis_connector.py            # Redis connection
└── schedulers/
    ├── airflow_scheduler.py          # Airflow DAG definitions
    └── cron_scheduler.py             # Cron job definitions
```

### Transform Layer
```python
# data/warehouse/etl/transform/
├── transformers/
│   ├── data_quality_transformer.py   # Data quality checks
│   ├── business_rules_transformer.py # Business logic application
│   ├── aggregation_transformer.py    # Data aggregation
│   └── enrichment_transformer.py     # Data enrichment
├── validators/
│   ├── schema_validator.py           # Schema validation
│   ├── business_validator.py         # Business rule validation
│   └── quality_validator.py          # Quality validation
└── mappers/
    ├── dimension_mapper.py           # Dimension mapping
    └── fact_mapper.py                # Fact mapping
```

### Load Layer
```python
# data/warehouse/etl/load/
├── loaders/
│   ├── dimension_loader.py           # Dimension table loading
│   ├── fact_loader.py                # Fact table loading
│   ├── aggregate_loader.py           # Aggregate table loading
│   └── incremental_loader.py         # Incremental loading
├── strategies/
│   ├── scd_type1.py                  # Slowly Changing Dimension Type 1
│   ├── scd_type2.py                  # Slowly Changing Dimension Type 2
│   └── snapshot_strategy.py          # Snapshot strategy
└── optimizers/
    ├── index_optimizer.py            # Index optimization
    └── partition_optimizer.py        # Partition optimization
```

## 📈 Data Marts

### 1. Service Analytics Data Mart
```sql
-- Aggregated service performance metrics
CREATE TABLE dm_service_analytics (
    service_key INTEGER,
    date_key INTEGER,
    total_queries BIGINT,
    successful_queries BIGINT,
    failed_queries BIGINT,
    avg_response_time_ms DECIMAL(10,2),
    unique_users BIGINT,
    satisfaction_score DECIMAL(3,2),
    content_views BIGINT,
    content_downloads BIGINT
);
```

### 2. User Analytics Data Mart
```sql
-- User behavior and engagement metrics
CREATE TABLE dm_user_analytics (
    user_key INTEGER,
    date_key INTEGER,
    session_count BIGINT,
    total_queries BIGINT,
    avg_session_duration_seconds INTEGER,
    most_used_service VARCHAR(150),
    language_preference VARCHAR(10),
    device_type VARCHAR(50),
    engagement_score DECIMAL(3,2)
);
```

### 3. Content Analytics Data Mart
```sql
-- Content performance and usage metrics
CREATE TABLE dm_content_analytics (
    content_key INTEGER,
    date_key INTEGER,
    view_count BIGINT,
    download_count BIGINT,
    share_count BIGINT,
    avg_view_duration_seconds INTEGER,
    bounce_rate DECIMAL(5,2),
    search_rank_position INTEGER,
    user_rating DECIMAL(3,2)
);
```

### 4. System Performance Data Mart
```sql
-- System performance and health metrics
CREATE TABLE dm_system_analytics (
    date_key INTEGER,
    time_key INTEGER,
    total_requests BIGINT,
    avg_response_time_ms DECIMAL(10,2),
    error_rate DECIMAL(5,2),
    throughput_rps DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_percent DECIMAL(5,2),
    disk_usage_percent DECIMAL(5,2)
);
```

## 🔧 Implementation Plan

### Phase 1: Foundation (Week 6)
1. **Database Setup**
   - Create data warehouse database
   - Set up dimension and fact tables
   - Configure indexes and partitions
   - Set up data retention policies

2. **ETL Framework**
   - Implement base ETL classes
   - Create extractors for all source systems
   - Set up data quality validation
   - Implement error handling and logging

### Phase 2: Core ETL (Week 7)
1. **Dimension Loading**
   - Implement SCD Type 1 and Type 2 strategies
   - Create dimension loading jobs
   - Set up dimension maintenance procedures

2. **Fact Loading**
   - Implement fact table loading
   - Create incremental loading strategies
   - Set up data aggregation jobs

### Phase 3: Analytics Layer (Week 8)
1. **Data Marts**
   - Create aggregated data marts
   - Implement materialized views
   - Set up automated refresh schedules

2. **Reporting Infrastructure**
   - Set up reporting database connections
   - Create base reporting templates
   - Implement data access controls

### Phase 4: Monitoring & Optimization (Week 9)
1. **Performance Monitoring**
   - Set up ETL performance monitoring
   - Create data quality dashboards
   - Implement alerting systems

2. **Optimization**
   - Optimize query performance
   - Implement data archiving
   - Set up maintenance procedures

## 📊 Key Performance Indicators (KPIs)

### Data Quality KPIs
- **Completeness**: % of required fields populated
- **Accuracy**: % of data matching source systems
- **Freshness**: Age of data in warehouse
- **Consistency**: % of data following business rules

### Performance KPIs
- **ETL Processing Time**: Time to process daily data loads
- **Query Response Time**: Average query execution time
- **Data Availability**: % uptime of warehouse
- **Error Rate**: % of failed ETL jobs

### Business KPIs
- **Service Usage Trends**: Growth in service queries
- **User Engagement**: User activity and retention
- **Content Performance**: Most/least used content
- **System Health**: Overall system performance

## 🛠️ Technology Stack

### Database
- **Primary**: PostgreSQL 15+ with pgvector
- **Analytics**: ClickHouse (for high-performance analytics)
- **Cache**: Redis for ETL caching

### ETL Tools
- **Orchestration**: Apache Airflow
- **Processing**: Python with Pandas/Polars
- **Scheduling**: Cron + Airflow

### Analytics
- **BI Tools**: Grafana + custom dashboards
- **Reporting**: Jupyter notebooks + Streamlit
- **Visualization**: Plotly + D3.js

### Monitoring
- **ETL Monitoring**: Airflow + custom metrics
- **Database Monitoring**: pg_stat_statements
- **System Monitoring**: Prometheus + Grafana

This data warehouse architecture will provide comprehensive analytics capabilities for your citizen services project, enabling data-driven decision making and continuous improvement of the system.