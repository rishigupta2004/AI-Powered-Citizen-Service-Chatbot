# 🏗️ Data Warehouse Architecture for Citizen Services Database

## Overview
This document outlines the comprehensive data warehouse architecture designed to complement the existing operational database and provide advanced analytics capabilities for the citizen services platform.

## Current State Assessment (Weeks 1-5 ✅)

### Completed Components:
- ✅ **Operational Database**: PostgreSQL with core models (Service, Procedure, Document, FAQ, User)
- ✅ **API Integration**: Complete API clients for all 10 government services
- ✅ **Web Scraping**: Framework for scraping government portals
- ✅ **Document Processing**: PDF parsing, OCR, and multilingual text processing
- ✅ **Basic ETL**: Data ingestion and validation pipelines

## Data Warehouse Architecture

### 1. Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  ETL Pipeline   │    │ Data Warehouse  │
│                 │    │                 │    │                 │
│ • APISetu APIs  │────▶│ • Airflow DAGs │────▶│ • Fact Tables   │
│ • Web Scraping  │    │ • Data Quality  │    │ • Dimensions    │
│ • PDF Documents │    │ • Transformations│    │ • Aggregations  │
│ • Gov Portals   │    │ • Validations   │    │ • ML Features   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Operational DB  │    │   Data Lake     │    │ Analytics Layer │
│                 │    │                 │    │                 │
│ • PostgreSQL    │    │ • Raw Data      │    │ • Grafana       │
│ • Document Store│    │ • Processed Data│    │ • BI Tools      │
│ • Redis Cache   │    │ • ML Features   │    │ • APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Data Warehouse Schema Design

#### 2.1 Fact Tables

**Service_Usage_Fact**
```sql
CREATE TABLE service_usage_fact (
    fact_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    user_key INTEGER,
    procedure_key INTEGER,
    document_key INTEGER,
    usage_count INTEGER DEFAULT 1,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    response_time_ms INTEGER,
    language_key INTEGER,
    region_key INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Content_Quality_Fact**
```sql
CREATE TABLE content_quality_fact (
    fact_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    content_type_key INTEGER NOT NULL,
    quality_score DECIMAL(5,2),
    completeness_score DECIMAL(5,2),
    accuracy_score DECIMAL(5,2),
    freshness_score DECIMAL(5,2),
    validation_errors INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API_Performance_Fact**
```sql
CREATE TABLE api_performance_fact (
    fact_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    endpoint_key INTEGER NOT NULL,
    request_count INTEGER,
    success_count INTEGER,
    error_count INTEGER,
    avg_response_time_ms DECIMAL(10,2),
    max_response_time_ms INTEGER,
    min_response_time_ms INTEGER,
    p95_response_time_ms INTEGER,
    p99_response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.2 Dimension Tables

**Date_Dim**
```sql
CREATE TABLE date_dim (
    date_key INTEGER PRIMARY KEY,
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
    is_holiday BOOLEAN DEFAULT FALSE,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER
);
```

**Service_Dim**
```sql
CREATE TABLE service_dim (
    service_key SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL,
    service_name VARCHAR(150) NOT NULL,
    category VARCHAR(80),
    description TEXT,
    government_department VARCHAR(100),
    service_type VARCHAR(50), -- 'api', 'scraping', 'hybrid'
    priority_level INTEGER, -- 1-5 scale
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**User_Dim**
```sql
CREATE TABLE user_dim (
    user_key SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_type VARCHAR(50), -- 'citizen', 'admin', 'analyst'
    region VARCHAR(100),
    language_preference VARCHAR(10),
    device_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP
);
```

**Content_Type_Dim**
```sql
CREATE TABLE content_type_dim (
    content_type_key SERIAL PRIMARY KEY,
    content_type VARCHAR(100) NOT NULL, -- 'procedure', 'document', 'faq', 'form'
    sub_type VARCHAR(100),
    format VARCHAR(50), -- 'text', 'pdf', 'html', 'json'
    language VARCHAR(10),
    source VARCHAR(100), -- 'api', 'scraping', 'manual'
    is_structured BOOLEAN DEFAULT FALSE
);
```

**Language_Dim**
```sql
CREATE TABLE language_dim (
    language_key SERIAL PRIMARY KEY,
    language_code VARCHAR(10) NOT NULL,
    language_name VARCHAR(50) NOT NULL,
    script VARCHAR(20), -- 'latin', 'devanagari', 'bengali'
    is_rtl BOOLEAN DEFAULT FALSE,
    is_official BOOLEAN DEFAULT FALSE
);
```

**Region_Dim**
```sql
CREATE TABLE region_dim (
    region_key SERIAL PRIMARY KEY,
    state_code VARCHAR(10),
    state_name VARCHAR(100),
    district_code VARCHAR(10),
    district_name VARCHAR(100),
    pincode VARCHAR(10),
    region_type VARCHAR(50), -- 'urban', 'rural', 'semi-urban'
    population_density VARCHAR(20) -- 'high', 'medium', 'low'
);
```

#### 2.3 Aggregated Tables

**Daily_Service_Summary**
```sql
CREATE TABLE daily_service_summary (
    summary_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    avg_response_time_ms DECIMAL(10,2),
    unique_users INTEGER DEFAULT 0,
    content_updates INTEGER DEFAULT 0,
    quality_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date_key, service_key)
);
```

**Weekly_Content_Analytics**
```sql
CREATE TABLE weekly_content_analytics (
    analytics_id SERIAL PRIMARY KEY,
    week_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    content_type_key INTEGER NOT NULL,
    total_content_items INTEGER DEFAULT 0,
    new_content_items INTEGER DEFAULT 0,
    updated_content_items INTEGER DEFAULT 0,
    avg_quality_score DECIMAL(5,2),
    multilingual_coverage DECIMAL(5,2),
    completeness_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. ETL Pipeline Design

#### 3.1 Airflow DAGs Structure

**Daily_ETL_DAG**
```python
# airflow/dags/daily_etl_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator

default_args = {
    'owner': 'citizen-services',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline for citizen services data warehouse',
    schedule_interval='0 2 * * *',  # Run at 2 AM daily
    catchup=False
)

# Extract data from operational database
extract_operational_data = PythonOperator(
    task_id='extract_operational_data',
    python_callable=extract_operational_data,
    dag=dag
)

# Transform and load into warehouse
transform_and_load = PythonOperator(
    task_id='transform_and_load',
    python_callable=transform_and_load_data,
    dag=dag
)

# Update aggregated tables
update_aggregations = PythonOperator(
    task_id='update_aggregations',
    python_callable=update_aggregated_tables,
    dag=dag
)

extract_operational_data >> transform_and_load >> update_aggregations
```

#### 3.2 ETL Functions

**Data Extraction**
```python
# data/warehouse/etl/extract.py
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta

def extract_operational_data():
    """Extract data from operational database for warehouse processing."""
    
    # Connect to operational database
    op_engine = create_engine(OPERATIONAL_DB_URL)
    
    # Extract service usage data
    usage_query = """
    SELECT 
        s.service_id,
        s.name as service_name,
        s.category,
        COUNT(p.procedure_id) as procedure_count,
        COUNT(d.doc_id) as document_count,
        COUNT(f.faq_id) as faq_count,
        CURRENT_DATE as date_key
    FROM services s
    LEFT JOIN procedures p ON s.service_id = p.service_id
    LEFT JOIN documents d ON s.service_id = d.service_id
    LEFT JOIN faqs f ON s.service_id = f.service_id
    WHERE s.created_at >= CURRENT_DATE - INTERVAL '1 day'
    GROUP BY s.service_id, s.name, s.category
    """
    
    usage_df = pd.read_sql(usage_query, op_engine)
    
    # Extract API performance data
    api_perf_query = """
    SELECT 
        service_id,
        endpoint,
        COUNT(*) as request_count,
        AVG(response_time) as avg_response_time,
        MAX(response_time) as max_response_time,
        MIN(response_time) as min_response_time,
        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
        CURRENT_DATE as date_key
    FROM api_logs
    WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
    GROUP BY service_id, endpoint
    """
    
    api_perf_df = pd.read_sql(api_perf_query, op_engine)
    
    return {
        'usage_data': usage_df,
        'api_performance': api_perf_df
    }
```

**Data Transformation**
```python
# data/warehouse/etl/transform.py
import pandas as pd
from datetime import datetime

def transform_usage_data(usage_df):
    """Transform usage data for warehouse loading."""
    
    # Add calculated fields
    usage_df['success_rate'] = usage_df['success_count'] / usage_df['total_requests']
    usage_df['error_rate'] = usage_df['error_count'] / usage_df['total_requests']
    
    # Categorize services by priority
    priority_mapping = {
        'passport': 1,
        'aadhaar': 1,
        'pan': 2,
        'epfo': 2,
        'driving_license': 3,
        'voter_id': 3,
        'ration_card': 4,
        'scholarship': 4,
        'grievance': 5
    }
    
    usage_df['priority_level'] = usage_df['service_name'].map(priority_mapping).fillna(5)
    
    return usage_df

def transform_api_performance(api_perf_df):
    """Transform API performance data for warehouse loading."""
    
    # Calculate percentiles
    api_perf_df['p95_response_time'] = api_perf_df['response_times'].apply(
        lambda x: np.percentile(x, 95) if len(x) > 0 else 0
    )
    api_perf_df['p99_response_time'] = api_perf_df['response_times'].apply(
        lambda x: np.percentile(x, 99) if len(x) > 0 else 0
    )
    
    return api_perf_df
```

### 4. Analytics and Reporting Layer

#### 4.1 Grafana Dashboards

**Service Performance Dashboard**
```json
{
  "dashboard": {
    "title": "Citizen Services Performance",
    "panels": [
      {
        "title": "Daily Service Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(service_usage_fact{usage_count})",
            "legendFormat": "Total Requests"
          }
        ]
      },
      {
        "title": "Service Success Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(service_usage_fact{success_count}[5m]) / rate(service_usage_fact{usage_count}[5m])",
            "legendFormat": "{{service_name}}"
          }
        ]
      }
    ]
  }
}
```

#### 4.2 Business Intelligence Queries

**Top Performing Services**
```sql
SELECT 
    s.service_name,
    s.category,
    AVG(dss.success_rate) as avg_success_rate,
    AVG(dss.avg_response_time_ms) as avg_response_time,
    SUM(dss.total_requests) as total_requests
FROM daily_service_summary dss
JOIN service_dim s ON dss.service_key = s.service_key
WHERE dss.date_key >= EXTRACT(EPOCH FROM CURRENT_DATE - INTERVAL '30 days')
GROUP BY s.service_key, s.service_name, s.category
ORDER BY avg_success_rate DESC, total_requests DESC
LIMIT 10;
```

**Content Quality Trends**
```sql
SELECT 
    s.service_name,
    ctd.content_type,
    AVG(cqf.quality_score) as avg_quality,
    AVG(cqf.completeness_score) as avg_completeness,
    COUNT(*) as content_items
FROM content_quality_fact cqf
JOIN service_dim s ON cqf.service_key = s.service_key
JOIN content_type_dim ctd ON cqf.content_type_key = ctd.content_type_key
WHERE cqf.date_key >= EXTRACT(EPOCH FROM CURRENT_DATE - INTERVAL '7 days')
GROUP BY s.service_name, ctd.content_type
ORDER BY avg_quality DESC;
```

### 5. Implementation Plan

#### Phase 1: Data Warehouse Setup (Week 6)
1. Create data warehouse database schema
2. Set up ETL pipeline infrastructure
3. Implement basic data extraction and transformation
4. Create initial fact and dimension tables

#### Phase 2: ETL Pipeline Development (Week 7)
1. Develop comprehensive ETL processes
2. Implement data quality checks
3. Set up automated data validation
4. Create data lineage tracking

#### Phase 3: Analytics Layer (Week 8)
1. Set up Grafana dashboards
2. Create business intelligence queries
3. Implement reporting APIs
4. Set up automated report generation

#### Phase 4: Advanced Analytics (Week 9)
1. Implement ML feature store
2. Create predictive analytics models
3. Set up anomaly detection
4. Implement real-time analytics

### 6. Data Quality and Governance

#### 6.1 Data Quality Rules
- **Completeness**: All required fields must be populated
- **Accuracy**: Data must match source systems
- **Consistency**: Data must be consistent across all tables
- **Timeliness**: Data must be updated within SLA
- **Validity**: Data must conform to defined schemas

#### 6.2 Data Lineage Tracking
```python
# data/warehouse/governance/lineage.py
class DataLineageTracker:
    def __init__(self):
        self.lineage_graph = {}
    
    def track_transformation(self, source_table, target_table, transformation_type):
        """Track data transformation lineage."""
        if source_table not in self.lineage_graph:
            self.lineage_graph[source_table] = []
        
        self.lineage_graph[source_table].append({
            'target': target_table,
            'transformation': transformation_type,
            'timestamp': datetime.now()
        })
    
    def get_lineage(self, table_name):
        """Get complete lineage for a table."""
        return self.lineage_graph.get(table_name, [])
```

### 7. Monitoring and Alerting

#### 7.1 Key Metrics to Monitor
- **Data Freshness**: Time since last successful ETL run
- **Data Quality**: Percentage of records passing validation
- **ETL Performance**: Processing time and throughput
- **System Health**: Database connections and resource usage

#### 7.2 Alerting Rules
```yaml
# monitoring/alerts.yml
alerts:
  - name: ETL_Failure
    condition: "etl_job_status == 'failed'"
    severity: "critical"
    notification: "email, slack"
  
  - name: Data_Quality_Degradation
    condition: "data_quality_score < 0.95"
    severity: "warning"
    notification: "email"
  
  - name: High_Response_Time
    condition: "avg_response_time > 2000"
    severity: "warning"
    notification: "slack"
```

This comprehensive data warehouse architecture will provide you with powerful analytics capabilities while maintaining the operational efficiency of your existing system. The design is scalable, maintainable, and follows industry best practices for data warehousing.

Would you like me to help you implement any specific part of this architecture?