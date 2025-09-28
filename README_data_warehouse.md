# 🏗️ Citizen Services Data Warehouse

## Overview

This data warehouse provides a comprehensive analytical platform for the Citizen Services Database project. It transforms operational data from multiple government service sources into actionable insights for both citizens and administrators.

## 🏛️ Architecture

The data warehouse follows a **star schema** design with:
- **Fact Tables**: Store measurable events (service usage, data quality metrics, content analytics)
- **Dimension Tables**: Store descriptive attributes (services, dates, locations, user segments)
- **Data Marts**: Pre-aggregated views for specific analytical needs
- **ETL Pipeline**: Automated data extraction, transformation, and loading

## 📊 Key Features

### 1. **Service Performance Analytics**
- Track citizen interactions with government services
- Monitor success rates, response times, and satisfaction scores
- Analyze trends by service category, department, and ministry

### 2. **Citizen Engagement Insights**
- Understand user behavior patterns by demographics
- Analyze channel preferences (web, mobile, API)
- Track geographic usage patterns

### 3. **Content Analytics**
- Monitor multilingual content performance
- Track document downloads and engagement
- Identify content gaps across languages

### 4. **Data Quality Monitoring**
- Monitor ETL pipeline health
- Track data freshness and accuracy
- Alert on quality degradation

### 5. **Operational Dashboards**
- Real-time monitoring of system performance
- Daily, weekly, and monthly trend analysis
- Automated alerting for performance issues

## 🚀 Quick Start

### 1. Initialize the Data Warehouse

```bash
# Install dependencies
pip install asyncpg pandas plotly streamlit

# Initialize warehouse schema and load initial data
python scripts/initialize_warehouse.py --environment development

# Verify installation
python scripts/initialize_warehouse.py --environment development --skip-sample-data
```

### 2. Run ETL Processes

```bash
# Full ETL for date range
python scripts/run_warehouse_etl.py --mode full --start-date 2024-01-01 --end-date 2024-01-31

# Incremental ETL for today
python scripts/run_warehouse_etl.py --mode incremental

# Setup schema only
python scripts/run_warehouse_etl.py --mode setup-schema
```

### 3. Launch Monitoring Dashboard

```bash
# Start the Streamlit dashboard
python -m streamlit run data/warehouse/dashboard/monitoring_dashboard.py
```

Open http://localhost:8501 to access the dashboard.

## 📁 Project Structure

```
data/warehouse/
├── schemas/
│   └── dimensional_schema.sql      # Complete warehouse schema
├── etl/
│   ├── extractors/                 # Data extraction from sources
│   ├── transformers/               # Data transformation logic
│   └── loaders/                    # Data loading into warehouse
├── analytics/
│   └── data_marts.sql             # Pre-built analytical views
├── dashboard/
│   └── monitoring_dashboard.py    # Streamlit monitoring dashboard
├── config/
│   └── warehouse_config.py        # Configuration management
└── warehouse_orchestrator.py      # Main ETL orchestrator

scripts/
├── initialize_warehouse.py        # One-time setup script
└── run_warehouse_etl.py          # ETL execution script
```

## 🗄️ Database Schema

### Core Dimension Tables
- `dim_service` - Government services (with SCD Type 2)
- `dim_date` - Date/time attributes including fiscal calendar
- `dim_location` - Geographic hierarchy (state, district, city)
- `dim_user_segment` - User demographics and behavior
- `dim_channel` - Access channels (web, mobile, API)
- `dim_content_type` - Content classification
- `dim_language` - Multilingual support

### Core Fact Tables
- `fact_service_usage` - Service interaction metrics
- `fact_data_quality` - Data quality monitoring
- `fact_content_analytics` - Content performance metrics
- `fact_search_analytics` - Search behavior analysis

### Pre-built Data Marts
- `dm_service_performance_monthly` - Service performance summaries
- `dm_citizen_engagement_demographics` - User behavior analysis
- `dm_content_multilingual` - Multilingual content insights
- `dm_data_quality_sources` - Source reliability metrics
- `dm_daily_operations` - Operational KPIs

## 🔧 Configuration

### Environment Variables

```bash
# Operational Database (Source)
OPERATIONAL_DB_HOST=localhost
OPERATIONAL_DB_PORT=5432
OPERATIONAL_DB_NAME=citizen_services_dev
OPERATIONAL_DB_USER=postgres
OPERATIONAL_DB_PASSWORD=your_password

# Data Warehouse Database (Target)
WAREHOUSE_DB_HOST=localhost
WAREHOUSE_DB_PORT=5432
WAREHOUSE_DB_NAME=citizen_services_dwh
WAREHOUSE_DB_USER=postgres
WAREHOUSE_DB_PASSWORD=your_password

# ETL Configuration
ETL_BATCH_SIZE=1000
ETL_MAX_RETRIES=3
ETL_PARALLEL_WORKERS=4
ETL_RETENTION_DAYS=365
```

### Database Setup

1. **Create Warehouse Database**:
```sql
CREATE DATABASE citizen_services_dwh;
```

2. **Enable Extensions**:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## 📈 Analytics Examples

### 1. Service Performance Query
```sql
SELECT 
    service_name,
    total_queries,
    success_rate_percent,
    avg_satisfaction,
    satisfaction_rating
FROM dwh.dm_service_performance_monthly
WHERE year = 2024 AND month = 1
ORDER BY total_queries DESC;
```

### 2. Citizen Demographics Analysis
```sql
SELECT 
    age_group,
    education_level,
    device_type,
    SUM(total_queries) as queries,
    AVG(avg_satisfaction) as satisfaction
FROM dwh.dm_citizen_engagement_demographics
WHERE year = 2024
GROUP BY age_group, education_level, device_type
ORDER BY queries DESC;
```

### 3. Content Gap Analysis
```sql
SELECT 
    service_name,
    language_name,
    content_availability,
    creation_priority
FROM dwh.dm_content_gaps
WHERE content_availability = 'Missing'
AND creation_priority = 'High';
```

## 🔍 Monitoring & Alerting

### Key Metrics to Monitor

1. **ETL Health**
   - Success rate > 95%
   - Processing time < 30 minutes
   - Data freshness < 24 hours

2. **Service Performance**
   - Success rate > 80%
   - Satisfaction score > 3.5
   - Response time < 2 seconds

3. **Data Quality**
   - Completeness > 95%
   - Accuracy > 90%
   - Consistency > 85%

### Setting Up Alerts

The warehouse includes built-in views for performance monitoring:

```sql
-- Check for performance alerts
SELECT * FROM dwh.dm_performance_alerts
WHERE alert_severity = 'Critical';

-- Monitor data freshness
SELECT * FROM dwh.dm_data_freshness
WHERE freshness_status = 'Very Stale';
```

## 🔄 ETL Scheduling

### Recommended Schedule

- **Incremental ETL**: Every hour during business hours
- **Full ETL**: Daily at 2 AM
- **Data Quality Checks**: Every 6 hours
- **Materialized View Refresh**: Every 4 hours

### Using Cron

```bash
# Add to crontab
0 */1 9-18 * * /path/to/run_warehouse_etl.py --mode incremental
0 2 * * * /path/to/run_warehouse_etl.py --mode full --start-date $(date -d "yesterday" +\%Y-\%m-\%d) --end-date $(date +\%Y-\%m-\%d)
```

## 🔒 Security & Access Control

### Database Permissions

```sql
-- Create roles
CREATE ROLE analyst_role;
CREATE ROLE etl_role;

-- Grant permissions
GRANT USAGE ON SCHEMA dwh TO analyst_role;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh TO analyst_role;

GRANT ALL ON SCHEMA dwh TO etl_role;
GRANT ALL ON ALL TABLES IN SCHEMA dwh TO etl_role;
```

## 🚨 Troubleshooting

### Common Issues

1. **ETL Process Fails**
   - Check database connectivity
   - Verify source data availability
   - Review ETL logs in `dwh.etl_log`

2. **Poor Performance**
   - Check index usage
   - Review query execution plans
   - Consider materialized view refresh

3. **Data Quality Issues**
   - Review source data validation
   - Check transformation logic
   - Monitor `fact_data_quality` metrics

### Debugging Queries

```sql
-- Check recent ETL status
SELECT * FROM dwh.etl_log 
ORDER BY created_at DESC LIMIT 10;

-- Verify dimension data
SELECT COUNT(*) FROM dwh.dim_service WHERE is_current = true;
SELECT MIN(full_date), MAX(full_date) FROM dwh.dim_date;

-- Check fact table volumes
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables 
WHERE schemaname = 'dwh'
ORDER BY n_tup_ins DESC;
```

## 📚 Additional Resources

- **Architecture Document**: [data_warehouse_architecture.md](data_warehouse_architecture.md)
- **API Documentation**: See main project README
- **Performance Tuning**: PostgreSQL optimization guides
- **BI Tool Integration**: Connect Metabase, Grafana, or Power BI

## 🤝 Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate error handling and logging
3. Include unit tests for new transformations
4. Update documentation for schema changes
5. Test ETL processes thoroughly before deployment

---

**Next Steps**: After setting up the data warehouse, proceed to Week 6 development phases as outlined in the main architecture document.