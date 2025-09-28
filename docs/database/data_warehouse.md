## Data Warehouse for Citizen Services

### Purpose
Provide analytics-ready dimensional models derived from the operational data (ODS): `services`, `procedures`, `documents`, `faqs`, and ingestion metadata. Optimized for reporting on coverage, freshness, and content availability across services.

### Layers
- ODS (existing): normalized OLTP tables in `public` schema
- DW (this doc): star-schema tables in `dw` schema

### Star Schemas
- dim_service(service_sk, service_id_nk, name, category, scd2 fields)
- dim_document(document_sk, doc_id_nk, service_id_nk, business + ingestion attrs, scd2)
- dim_procedure(procedure_sk, procedure_id_nk, service_id_nk, title, steps_hash, scd2)
- dim_date(date_sk, date_actual, year, quarter, month, day, dow, is_weekend)
- fact_document_availability(service_sk, document_sk, load_date_sk, language, mandatory, is_present, source, doc_type)
- fact_procedure_coverage(service_sk, procedure_sk, load_date_sk, has_steps, step_count)

### DDL
SQL file: `database/dw/schema_dw.sql`

### Build Script
Python: `scripts/build_dw.py`

Responsibilities:
- Creates/updates DW schema and types
- Upserts SCD2 dimensions via helper SQL functions
- Populates facts for the current date (idempotent by date_sk)

### Running Locally
Prereqs: environment variable `DATABASE_URL` pointing to your PostgreSQL with ODS tables loaded.

1) Apply DW DDL (automatic on script run):
```bash
python scripts/build_dw.py
```

2) Verify core tables:
```sql
SELECT COUNT(*) FROM dw.dim_service;
SELECT COUNT(*) FROM dw.dim_document;
SELECT COUNT(*) FROM dw.dim_procedure;
SELECT COUNT(*) FROM dw.fact_document_availability;
SELECT COUNT(*) FROM dw.fact_procedure_coverage;
```

### Scheduling
- Add to Airflow as a daily DAG before vector embedding refresh:
  - Task 1: run `scripts/build_dw.py`
  - Task 2: downstream analytics/embedding tasks

### Notes
- Languages coerced to a controlled enum; unmapped -> `en`
- Procedure `steps_hash` enables SCD2 change detection without storing full text
- Facts are append-only by load date; use `date_sk` to aggregate over time

