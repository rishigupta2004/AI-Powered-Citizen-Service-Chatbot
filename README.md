# Citizen Services Database

## Data Warehouse (DW)

1. Apply DW schema (creates `dw` schema and star tables):

```sql
-- In psql or your SQL client
\i database/dw_schema.sql
```

2. Populate dimensions and facts:

```bash
# Uses the same operational DB via DATABASE_URL
export DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/citizen_services_dev
python scripts/etl_to_dw.py
```

3. Verify data:

```sql
SELECT * FROM dw.dim_service LIMIT 10;
SELECT * FROM dw.fact_service_content ORDER BY dw_loaded_at DESC LIMIT 10;
```

Notes:
- DW derives from operational tables `services`, `procedures`, `documents`, `faqs`, `users`.
- Extend with additional facts (e.g., ingestion metrics, search analytics) as pipelines mature.
- Re-run the ETL daily or via Airflow once orchestrated.