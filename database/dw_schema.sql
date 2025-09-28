-- Data Warehouse Schema for Citizen Services
-- Star schemas for analytics on services, procedures, documents, and user interactions

-- Schema namespaces
CREATE SCHEMA IF NOT EXISTS dw;

-- Dimension tables
CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key INTEGER PRIMARY KEY,        -- yyyymmdd
    date_value DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.dim_service (
    service_key SERIAL PRIMARY KEY,
    service_id INTEGER,                  -- source system id
    name VARCHAR(150) NOT NULL,
    category VARCHAR(80),
    created_at TIMESTAMP,
    dw_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dw.dim_procedure (
    procedure_key SERIAL PRIMARY KEY,
    procedure_id INTEGER,                -- source system id
    service_id INTEGER,
    title TEXT,
    dw_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dw.dim_document (
    document_key SERIAL PRIMARY KEY,
    doc_id INTEGER,                      -- source system id
    service_id INTEGER,
    name VARCHAR(150),
    mandatory BOOLEAN,
    language VARCHAR(10),
    doc_type VARCHAR(50),
    source VARCHAR(100),
    dw_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dw.dim_user (
    user_key SERIAL PRIMARY KEY,
    user_id INTEGER,                     -- source system id
    name VARCHAR(150),
    email VARCHAR(200),
    role VARCHAR(50),
    dw_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact tables
CREATE TABLE IF NOT EXISTS dw.fact_document_ingestion (
    fact_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER REFERENCES dw.dim_date(date_key),
    document_key INTEGER REFERENCES dw.dim_document(document_key),
    service_key INTEGER REFERENCES dw.dim_service(service_key),
    source VARCHAR(100),
    file_name TEXT,
    bytes_ingested BIGINT,
    num_chunks INTEGER,
    load_type VARCHAR(20),               -- full/incremental
    status VARCHAR(20),                  -- success/failed
    error_message TEXT,
    dw_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dw.fact_user_interaction (
    fact_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER REFERENCES dw.dim_date(date_key),
    user_key INTEGER REFERENCES dw.dim_user(user_key),
    service_key INTEGER REFERENCES dw.dim_service(service_key),
    procedure_key INTEGER REFERENCES dw.dim_procedure(procedure_key),
    action VARCHAR(50),                  -- view_service, view_procedure, search, etc.
    duration_ms BIGINT,
    success BOOLEAN,
    dw_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dw.fact_service_content (
    fact_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER REFERENCES dw.dim_date(date_key),
    service_key INTEGER REFERENCES dw.dim_service(service_key),
    procedure_count INTEGER,
    document_count INTEGER,
    faq_count INTEGER,
    language_coverage INTEGER,           -- number of langs present for service content
    dw_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_dim_service_service_id ON dw.dim_service(service_id);
CREATE INDEX IF NOT EXISTS idx_dim_procedure_procedure_id ON dw.dim_procedure(procedure_id);
CREATE INDEX IF NOT EXISTS idx_dim_document_doc_id ON dw.dim_document(doc_id);
CREATE INDEX IF NOT EXISTS idx_dim_user_user_id ON dw.dim_user(user_id);
CREATE INDEX IF NOT EXISTS idx_fact_doc_ing_date ON dw.fact_document_ingestion(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_user_interaction_date ON dw.fact_user_interaction(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_service_content_date ON dw.fact_service_content(date_key);

