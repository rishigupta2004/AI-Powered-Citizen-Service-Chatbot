# 🏛️ Citizen Services Data Warehouse

## Overview

This data warehouse is designed to support analytics, reporting, and business intelligence for the Citizen Services Database project. It provides comprehensive insights into service usage, user behavior, content performance, and system health.

## 🏗️ Architecture

### Data Warehouse Layers

1. **Source Systems (OLTP)**
   - Operational PostgreSQL database
   - API data from government services
   - Scraped data from government websites
   - Document store (MongoDB)

2. **ETL Layer**
   - Extract: Data extraction from source systems
   - Transform: Data cleaning, validation, and transformation
   - Load: Data loading into warehouse tables

3. **Data Warehouse Core**
   - Dimensional model with fact and dimension tables
   - Star schema design for optimal query performance
   - Data marts for specific analytics domains

4. **Analytics Layer**
   - Streamlit dashboard for interactive analytics
   - Pre-built reports and visualizations
   - Real-time monitoring and alerting

## 📊 Data Model

### Dimension Tables

- **dim_date**: Calendar and fiscal year information
- **dim_time**: Hour-level time granularity
- **dim_service**: Government service information
- **dim_user**: User profiles and demographics
- **dim_content**: Content items (procedures, documents, FAQs)
- **dim_query_type**: Types of queries and their characteristics
- **dim_language**: Supported languages and coverage
- **dim_content_source**: Data sources and their reliability
- **dim_quality_metric**: Data quality measurement criteria

### Fact Tables

- **fct_service_queries**: All service queries and interactions
- **fct_content_usage**: Content consumption and engagement
- **fct_data_quality**: Data quality metrics and scores
- **fct_system_performance**: System performance metrics

### Data Marts

- **dm_service_analytics**: Aggregated service performance metrics
- **dm_user_analytics**: User behavior and engagement metrics
- **dm_content_analytics**: Content performance and usage metrics
- **dm_system_analytics**: System performance and health metrics

## 🚀 Quick Start

### Prerequisites

- PostgreSQL 15+ with pgvector extension
- Python 3.8+
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd citizen-services-db
   ```

2. **Set up environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/citizen_services"
   export WAREHOUSE_DATABASE_URL="postgresql://user:password@localhost/citizen_services_warehouse"
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run setup script**
   ```bash
   python scripts/setup_warehouse.py
   ```

### Manual Setup

1. **Create warehouse database**
   ```sql
   CREATE DATABASE citizen_services_warehouse;
   ```

2. **Run schema creation**
   ```bash
   psql $WAREHOUSE_DATABASE_URL -f database/warehouse_schema.sql
   ```

3. **Run initial data load**
   ```bash
   python -m data.warehouse.etl.orchestrator --operation dimensions
   ```

## 🔧 Usage

### ETL Operations

#### Dimension Loading
```bash
# Load all dimension tables
python -m data.warehouse.etl.orchestrator --operation dimensions

# Load with custom configuration
python -m data.warehouse.etl.orchestrator --operation dimensions --config config/custom_config.yaml
```

#### Incremental Loading
```bash
# Load data for specific date range
python -m data.warehouse.etl.orchestrator --operation incremental --start-date 2024-01-01 --end-date 2024-01-31
```

#### Full Refresh
```bash
# Refresh entire warehouse
python -m data.warehouse.etl.orchestrator --operation full_refresh
```

### Analytics Dashboard

#### Start Streamlit Dashboard
```bash
streamlit run data/warehouse/analytics/dashboard.py
```

The dashboard will be available at `http://localhost:8501`

#### Dashboard Features

- **Overview**: Key metrics and trends
- **Service Analytics**: Service performance and usage
- **User Analytics**: User behavior and engagement
- **Content Analytics**: Content performance and popularity
- **System Performance**: System health and performance metrics

### Data Quality Monitoring

The warehouse includes comprehensive data quality monitoring:

- **Completeness**: Percentage of required fields populated
- **Accuracy**: Data accuracy against source systems
- **Freshness**: Age of data in the warehouse
- **Consistency**: Data following business rules

## 📈 Key Metrics

### Service Metrics
- Total queries and success rates
- Average response times
- Service usage trends
- Error rates and patterns

### User Metrics
- User engagement and retention
- Query patterns and preferences
- Language usage distribution
- Device and browser analytics

### Content Metrics
- Content popularity and performance
- View duration and engagement
- Search ranking and discovery
- Content type effectiveness

### System Metrics
- Performance and availability
- Resource utilization
- Error rates and patterns
- Data processing efficiency

## 🔍 Sample Queries

### Daily Service Performance
```sql
SELECT 
    d.full_date,
    s.service_name,
    COUNT(*) as total_queries,
    COUNT(*) FILTER (WHERE sq.success_flag = true) as successful_queries,
    ROUND(AVG(sq.response_time_ms), 2) as avg_response_time_ms
FROM fct_service_queries sq
JOIN dim_date d ON sq.date_key = d.date_key
JOIN dim_service s ON sq.service_key = s.service_key
WHERE d.full_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY d.full_date, s.service_name
ORDER BY d.full_date DESC, total_queries DESC;
```

### Top Performing Content
```sql
SELECT 
    c.title,
    c.content_type,
    s.service_name,
    COUNT(*) as total_views,
    ROUND(AVG(cu.duration_seconds), 2) as avg_view_duration
FROM fct_content_usage cu
JOIN dim_content c ON cu.content_key = c.content_key
JOIN dim_service s ON cu.service_key = s.service_key
WHERE cu.action_type = 'view'
GROUP BY c.title, c.content_type, s.service_name
ORDER BY total_views DESC
LIMIT 10;
```

### Data Quality Summary
```sql
SELECT 
    d.full_date,
    s.service_name,
    qm.metric_name,
    AVG(fdq.metric_value) as avg_metric_value,
    COUNT(*) FILTER (WHERE fdq.status = 'pass') as pass_count,
    COUNT(*) FILTER (WHERE fdq.status = 'fail') as fail_count
FROM fct_data_quality fdq
JOIN dim_date d ON fdq.date_key = d.date_key
JOIN dim_service s ON fdq.service_key = s.service_key
JOIN dim_quality_metric qm ON fdq.quality_metric_key = qm.quality_metric_key
WHERE d.full_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY d.full_date, s.service_name, qm.metric_name
ORDER BY d.full_date DESC, s.service_name, qm.metric_name;
```

## 🛠️ Configuration

### Warehouse Configuration

The warehouse configuration is stored in `config/warehouse_config.yaml`:

```yaml
source:
  url: "postgresql://user:password@localhost/citizen_services"
  echo: false

target:
  url: "postgresql://user:password@localhost/citizen_services_warehouse"
  echo: false

quality:
  quality_rules:
    dim_service:
      not_null_service_name:
        type: "not_null"
        column: "service_name"

etl:
  batch_size: 1000
  max_retries: 3
  parallel_processes: 4
```

### Data Quality Rules

Quality rules are defined in the configuration file and can include:

- **not_null**: Check for null values
- **unique**: Check for duplicate values
- **range**: Check value ranges
- **format**: Check data format compliance

## 📊 Monitoring and Alerting

### Performance Monitoring
- ETL job execution times
- Query performance metrics
- Resource utilization
- Error rates and patterns

### Data Quality Monitoring
- Automated quality checks
- Quality score tracking
- Alert generation for quality issues
- Trend analysis

### System Health Monitoring
- Database performance
- ETL pipeline health
- Dashboard availability
- Data freshness

## 🔄 Maintenance

### Regular Tasks

1. **Daily ETL Runs**
   - Incremental data loading
   - Data quality checks
   - Performance monitoring

2. **Weekly Tasks**
   - Full dimension refreshes
   - Data quality reports
   - Performance optimization

3. **Monthly Tasks**
   - Data archiving
   - Capacity planning
   - Security reviews

### Data Retention

- **Fact Tables**: 2 years (configurable)
- **Dimension Tables**: Permanent
- **Logs**: 30 days
- **Backups**: 90 days

## 🚨 Troubleshooting

### Common Issues

1. **ETL Failures**
   - Check database connections
   - Verify data quality rules
   - Review error logs

2. **Performance Issues**
   - Check query execution plans
   - Review index usage
   - Monitor resource utilization

3. **Data Quality Issues**
   - Review quality rules
   - Check source data
   - Validate transformations

### Logs

- ETL logs: `logs/warehouse/etl.log`
- Application logs: `logs/warehouse/app.log`
- Error logs: `logs/warehouse/error.log`

## 📚 Documentation

- [Architecture Overview](data_warehouse_architecture.md)
- [ETL Process Guide](docs/etl_guide.md)
- [Analytics Dashboard Guide](docs/dashboard_guide.md)
- [Data Quality Guide](docs/data_quality_guide.md)
- [API Reference](docs/api_reference.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for better citizen services**