-- Data Warehouse Schema (Kimball-style) for Citizen Services
-- Layers: ODS (existing), DW (this file)
-- Conventions:
--   - Surrogate keys as GENERATED ALWAYS AS IDENTITY
--   - Natural keys retained where useful
--   - Timestamps are timezone-aware

-- Create DW schema namespace
CREATE SCHEMA IF NOT EXISTS dw;

-- Shared type(s)
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
    WHERE t.typname = 'language_code' AND n.nspname = 'dw'
  ) THEN
    CREATE TYPE dw.language_code AS ENUM ('en','hi','bn','ta','te','mr','gu','kn','ml','pa');
  END IF;
END $$;

-- Dimension: Service
CREATE TABLE IF NOT EXISTS dw.dim_service (
  service_sk       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  service_id_nk    INTEGER,                  -- ODS natural key (services.service_id)
  name             VARCHAR(150) NOT NULL,
  category         VARCHAR(80),
  is_current       BOOLEAN DEFAULT TRUE,     -- SCD2 indicator
  valid_from_ts    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  valid_to_ts      TIMESTAMPTZ,
  UNIQUE (service_id_nk, is_current)
);

CREATE INDEX IF NOT EXISTS ix_dim_service_nk ON dw.dim_service(service_id_nk) WHERE is_current;

-- Dimension: Document (business docs required by services)
CREATE TABLE IF NOT EXISTS dw.dim_document (
  document_sk      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  doc_id_nk        INTEGER,                  -- ODS natural key (documents.doc_id)
  service_id_nk    INTEGER,
  name             VARCHAR(150),
  description      TEXT,
  mandatory        BOOLEAN,
  source           VARCHAR(100),
  file_name        TEXT,
  language         dw.language_code,
  doc_type         VARCHAR(50),
  is_current       BOOLEAN DEFAULT TRUE,
  valid_from_ts    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  valid_to_ts      TIMESTAMPTZ,
  UNIQUE (doc_id_nk, is_current)
);

CREATE INDEX IF NOT EXISTS ix_dim_document_nk ON dw.dim_document(doc_id_nk) WHERE is_current;

-- Dimension: Procedure (high-level steps per service)
CREATE TABLE IF NOT EXISTS dw.dim_procedure (
  procedure_sk     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  procedure_id_nk  INTEGER,                  -- ODS natural key (procedures.procedure_id)
  service_id_nk    INTEGER,
  title            TEXT,
  steps_hash       TEXT,                     -- hash of steps for change detection
  is_current       BOOLEAN DEFAULT TRUE,
  valid_from_ts    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  valid_to_ts      TIMESTAMPTZ,
  UNIQUE (procedure_id_nk, is_current)
);

CREATE INDEX IF NOT EXISTS ix_dim_procedure_nk ON dw.dim_procedure(procedure_id_nk) WHERE is_current;

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dw.dim_date (
  date_sk          INTEGER PRIMARY KEY,      -- yyyymmdd
  date_actual      DATE NOT NULL UNIQUE,
  year_num         INTEGER NOT NULL,
  quarter_num      INTEGER NOT NULL,
  month_num        INTEGER NOT NULL,
  day_num          INTEGER NOT NULL,
  day_of_week      INTEGER NOT NULL,
  is_weekend       BOOLEAN NOT NULL
);

-- Fact: Document Availability by Service
-- Grain: one row per document version per load date
CREATE TABLE IF NOT EXISTS dw.fact_document_availability (
  fact_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  service_sk       INTEGER NOT NULL REFERENCES dw.dim_service(service_sk),
  document_sk      INTEGER NOT NULL REFERENCES dw.dim_document(document_sk),
  load_date_sk     INTEGER NOT NULL REFERENCES dw.dim_date(date_sk),
  language         dw.language_code,
  mandatory        BOOLEAN,
  is_present       BOOLEAN NOT NULL,
  source           VARCHAR(100),
  doc_type         VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS ix_fact_doc_avail_keys 
  ON dw.fact_document_availability(service_sk, document_sk, load_date_sk);

-- Fact: Procedure Coverage by Service
-- Grain: one row per procedure version per load date
CREATE TABLE IF NOT EXISTS dw.fact_procedure_coverage (
  fact_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  service_sk       INTEGER NOT NULL REFERENCES dw.dim_service(service_sk),
  procedure_sk     INTEGER NOT NULL REFERENCES dw.dim_procedure(procedure_sk),
  load_date_sk     INTEGER NOT NULL REFERENCES dw.dim_date(date_sk),
  has_steps        BOOLEAN NOT NULL,
  step_count       INTEGER
);

CREATE INDEX IF NOT EXISTS ix_fact_proc_cov_keys 
  ON dw.fact_procedure_coverage(service_sk, procedure_sk, load_date_sk);

-- Staging helper: upsert functions (idempotent loads)
CREATE OR REPLACE FUNCTION dw.upsert_dim_service(
  p_service_id_nk INTEGER,
  p_name VARCHAR,
  p_category VARCHAR
) RETURNS INTEGER AS $$
DECLARE v_sk INTEGER; v_existing_sk INTEGER; BEGIN
  -- Close current if data changed
  SELECT service_sk INTO v_existing_sk
  FROM dw.dim_service 
  WHERE service_id_nk = p_service_id_nk AND is_current = TRUE;

  IF v_existing_sk IS NOT NULL THEN
    PERFORM 1 FROM dw.dim_service
    WHERE service_sk = v_existing_sk 
      AND name = p_name 
      AND COALESCE(category,'') = COALESCE(p_category,'');

    IF NOT FOUND THEN
      UPDATE dw.dim_service
        SET is_current = FALSE, valid_to_ts = NOW()
        WHERE service_sk = v_existing_sk;
      INSERT INTO dw.dim_service(service_id_nk, name, category)
        VALUES (p_service_id_nk, p_name, p_category)
        RETURNING service_sk INTO v_sk;
      RETURN v_sk;
    ELSE
      RETURN v_existing_sk;
    END IF;
  ELSE
    INSERT INTO dw.dim_service(service_id_nk, name, category)
      VALUES (p_service_id_nk, p_name, p_category)
      RETURNING service_sk INTO v_sk;
    RETURN v_sk;
  END IF;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dw.upsert_dim_document(
  p_doc_id_nk INTEGER,
  p_service_id_nk INTEGER,
  p_name VARCHAR,
  p_description TEXT,
  p_mandatory BOOLEAN,
  p_source VARCHAR,
  p_file_name TEXT,
  p_language dw.language_code,
  p_doc_type VARCHAR
) RETURNS INTEGER AS $$
DECLARE v_sk INTEGER; v_existing_sk INTEGER; BEGIN
  SELECT document_sk INTO v_existing_sk
  FROM dw.dim_document 
  WHERE doc_id_nk = p_doc_id_nk AND is_current = TRUE;

  IF v_existing_sk IS NOT NULL THEN
    PERFORM 1 FROM dw.dim_document
    WHERE document_sk = v_existing_sk 
      AND COALESCE(name,'') = COALESCE(p_name,'')
      AND COALESCE(description,'') = COALESCE(p_description,'')
      AND COALESCE(mandatory,false) = COALESCE(p_mandatory,false)
      AND COALESCE(source,'') = COALESCE(p_source,'')
      AND COALESCE(file_name,'') = COALESCE(p_file_name,'')
      AND COALESCE(language::text,'') = COALESCE(p_language::text,'')
      AND COALESCE(doc_type,'') = COALESCE(p_doc_type,'');

    IF NOT FOUND THEN
      UPDATE dw.dim_document
        SET is_current = FALSE, valid_to_ts = NOW()
        WHERE document_sk = v_existing_sk;
      INSERT INTO dw.dim_document(
        doc_id_nk, service_id_nk, name, description, mandatory,
        source, file_name, language, doc_type
      ) VALUES (
        p_doc_id_nk, p_service_id_nk, p_name, p_description, p_mandatory,
        p_source, p_file_name, p_language, p_doc_type
      ) RETURNING document_sk INTO v_sk;
      RETURN v_sk;
    ELSE
      RETURN v_existing_sk;
    END IF;
  ELSE
    INSERT INTO dw.dim_document(
      doc_id_nk, service_id_nk, name, description, mandatory,
      source, file_name, language, doc_type
    ) VALUES (
      p_doc_id_nk, p_service_id_nk, p_name, p_description, p_mandatory,
      p_source, p_file_name, p_language, p_doc_type
    ) RETURNING document_sk INTO v_sk;
    RETURN v_sk;
  END IF;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dw.upsert_dim_procedure(
  p_procedure_id_nk INTEGER,
  p_service_id_nk INTEGER,
  p_title TEXT,
  p_steps_hash TEXT
) RETURNS INTEGER AS $$
DECLARE v_sk INTEGER; v_existing_sk INTEGER; BEGIN
  SELECT procedure_sk INTO v_existing_sk
  FROM dw.dim_procedure 
  WHERE procedure_id_nk = p_procedure_id_nk AND is_current = TRUE;

  IF v_existing_sk IS NOT NULL THEN
    PERFORM 1 FROM dw.dim_procedure
    WHERE procedure_sk = v_existing_sk 
      AND COALESCE(title,'') = COALESCE(p_title,'')
      AND COALESCE(steps_hash,'') = COALESCE(p_steps_hash,'');

    IF NOT FOUND THEN
      UPDATE dw.dim_procedure
        SET is_current = FALSE, valid_to_ts = NOW()
        WHERE procedure_sk = v_existing_sk;
      INSERT INTO dw.dim_procedure(
        procedure_id_nk, service_id_nk, title, steps_hash
      ) VALUES (
        p_procedure_id_nk, p_service_id_nk, p_title, p_steps_hash
      ) RETURNING procedure_sk INTO v_sk;
      RETURN v_sk;
    ELSE
      RETURN v_existing_sk;
    END IF;
  ELSE
    INSERT INTO dw.dim_procedure(
      procedure_id_nk, service_id_nk, title, steps_hash
    ) VALUES (
      p_procedure_id_nk, p_service_id_nk, p_title, p_steps_hash
    ) RETURNING procedure_sk INTO v_sk;
    RETURN v_sk;
  END IF;
END; $$ LANGUAGE plpgsql;

-- Seed dim_date helper (optional small range)
INSERT INTO dw.dim_date(date_sk, date_actual, year_num, quarter_num, month_num, day_num, day_of_week, is_weekend)
SELECT 
  EXTRACT(YEAR FROM d)::INT * 10000 + EXTRACT(MONTH FROM d)::INT * 100 + EXTRACT(DAY FROM d)::INT AS date_sk,
  d::date,
  EXTRACT(YEAR FROM d)::INT,
  EXTRACT(QUARTER FROM d)::INT,
  EXTRACT(MONTH FROM d)::INT,
  EXTRACT(DAY FROM d)::INT,
  EXTRACT(DOW FROM d)::INT,
  CASE WHEN EXTRACT(DOW FROM d) IN (0,6) THEN TRUE ELSE FALSE END
FROM generate_series(date_trunc('year', NOW()) - INTERVAL '5 years', date_trunc('year', NOW()) + INTERVAL '5 years', INTERVAL '1 day') AS d
ON CONFLICT (date_actual) DO NOTHING;

