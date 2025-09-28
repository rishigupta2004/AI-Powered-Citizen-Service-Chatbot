-- Citizen Services Data Warehouse Schema
-- Creates dimensional model for analytics and reporting

-- Create dedicated schema for data warehouse
CREATE SCHEMA IF NOT EXISTS dwh;

-- Enable pgvector extension for semantic search capabilities
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- Date dimension for time-based analysis
CREATE TABLE IF NOT EXISTS dwh.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    week INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE,
    holiday_name VARCHAR(100),
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service dimension with comprehensive service metadata
CREATE TABLE IF NOT EXISTS dwh.dim_service (
    service_key SERIAL PRIMARY KEY,
    service_id INTEGER UNIQUE NOT NULL,
    service_name VARCHAR(200) NOT NULL,
    service_category VARCHAR(100),
    parent_category VARCHAR(100),
    department VARCHAR(150),
    ministry VARCHAR(150),
    complexity_level VARCHAR(20) CHECK (complexity_level IN ('Simple', 'Medium', 'Complex')),
    avg_completion_time_days INTEGER,
    requires_documents BOOLEAN DEFAULT FALSE,
    has_fees BOOLEAN DEFAULT FALSE,
    digital_enabled BOOLEAN DEFAULT FALSE,
    languages_supported TEXT[], -- Array of language codes: ['hi', 'en', 'bn']
    target_audience VARCHAR(100), -- Citizens, Businesses, Both
    service_type VARCHAR(50) CHECK (service_type IN ('Information', 'Transaction', 'Grievance', 'Certificate')),
    priority_level VARCHAR(20) CHECK (priority_level IN ('High', 'Medium', 'Low')),
    
    -- Slowly Changing Dimension Type 2 fields
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expiry_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_date DATE DEFAULT CURRENT_DATE,
    last_updated_date DATE DEFAULT CURRENT_DATE
);

-- Location dimension for geographic analysis
CREATE TABLE IF NOT EXISTS dwh.dim_location (
    location_key SERIAL PRIMARY KEY,
    state_code VARCHAR(10),
    state_name VARCHAR(100),
    district_code VARCHAR(10), 
    district_name VARCHAR(100),
    city_name VARCHAR(100),
    pin_code VARCHAR(10),
    rural_urban VARCHAR(10) CHECK (rural_urban IN ('Rural', 'Urban', 'Semi-Urban')),
    region VARCHAR(50) CHECK (region IN ('North', 'South', 'East', 'West', 'Central', 'Northeast')),
    tier VARCHAR(10) CHECK (tier IN ('Tier-1', 'Tier-2', 'Tier-3')),
    population_category VARCHAR(20) CHECK (population_category IN ('Metro', 'Large', 'Medium', 'Small')),
    literacy_rate NUMERIC(5,2),
    internet_penetration NUMERIC(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User segment dimension for demographic analysis
CREATE TABLE IF NOT EXISTS dwh.dim_user_segment (
    segment_key SERIAL PRIMARY KEY,
    age_group VARCHAR(20) CHECK (age_group IN ('18-25', '26-35', '36-50', '51-65', '65+')),
    education_level VARCHAR(50) CHECK (education_level IN ('Primary', 'Secondary', 'Graduate', 'Post-Graduate', 'Professional')),
    income_bracket VARCHAR(30) CHECK (income_bracket IN ('Below 2L', '2-5L', '5-10L', '10-20L', 'Above 20L')),
    occupation_category VARCHAR(50) CHECK (occupation_category IN ('Student', 'Employee', 'Business', 'Retired', 'Unemployed')),
    language_preference VARCHAR(10), -- ISO language codes: hi, en, bn, ta, etc.
    device_type VARCHAR(20) CHECK (device_type IN ('Mobile', 'Desktop', 'Tablet')),
    access_frequency VARCHAR(20) CHECK (access_frequency IN ('Daily', 'Weekly', 'Monthly', 'Occasional')),
    tech_savviness VARCHAR(20) CHECK (tech_savviness IN ('Low', 'Medium', 'High')),
    geographic_type VARCHAR(20) CHECK (geographic_type IN ('Urban', 'Rural', 'Semi-Urban')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Channel dimension for access method analysis
CREATE TABLE IF NOT EXISTS dwh.dim_channel (
    channel_key SERIAL PRIMARY KEY,
    channel_name VARCHAR(50), -- Web Portal, Mobile App, API, Chatbot, Call Center
    channel_type VARCHAR(30) CHECK (channel_type IN ('Digital', 'Physical', 'Hybrid')),
    platform VARCHAR(30), -- Android, iOS, Web, Desktop
    version VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Content type dimension for content analysis
CREATE TABLE IF NOT EXISTS dwh.dim_content_type (
    content_type_key SERIAL PRIMARY KEY,
    content_type VARCHAR(50) CHECK (content_type IN ('FAQ', 'Procedure', 'Document', 'Form', 'Guide', 'Video', 'Infographic')),
    content_format VARCHAR(30) CHECK (content_format IN ('PDF', 'HTML', 'Word', 'Image', 'Video', 'Audio')),
    content_source VARCHAR(50) CHECK (content_source IN ('API', 'Scraping', 'Manual', 'Upload', 'Generated')),
    content_complexity VARCHAR(20) CHECK (content_complexity IN ('Simple', 'Medium', 'Complex')),
    requires_translation BOOLEAN DEFAULT FALSE,
    update_frequency VARCHAR(20) CHECK (update_frequency IN ('Daily', 'Weekly', 'Monthly', 'Quarterly', 'Annually')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Language dimension for multilingual analysis
CREATE TABLE IF NOT EXISTS dwh.dim_language (
    language_key SERIAL PRIMARY KEY,
    language_code VARCHAR(10) UNIQUE NOT NULL, -- ISO 639-1 codes
    language_name VARCHAR(50) NOT NULL,
    native_name VARCHAR(50),
    script_type VARCHAR(30), -- Latin, Devanagari, Bengali, etc.
    is_official BOOLEAN DEFAULT FALSE, -- Official Indian language
    speaker_population BIGINT, -- Number of speakers in India
    is_supported BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Source dimension for data lineage tracking
CREATE TABLE IF NOT EXISTS dwh.dim_source (
    source_key SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) CHECK (source_type IN ('API', 'Website', 'Database', 'File', 'Manual')),
    source_url VARCHAR(500),
    department VARCHAR(150),
    reliability_score NUMERIC(3,2) DEFAULT 1.0, -- 0.0 to 1.0
    update_frequency VARCHAR(20),
    last_successful_sync TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- Main fact table for service usage analytics
CREATE TABLE IF NOT EXISTS dwh.fact_service_usage (
    usage_id BIGSERIAL PRIMARY KEY,
    service_key INTEGER REFERENCES dwh.dim_service(service_key),
    date_key INTEGER REFERENCES dwh.dim_date(date_key),
    location_key INTEGER REFERENCES dwh.dim_location(location_key),
    user_segment_key INTEGER REFERENCES dwh.dim_user_segment(segment_key),
    channel_key INTEGER REFERENCES dwh.dim_channel(channel_key),
    content_type_key INTEGER REFERENCES dwh.dim_content_type(content_type_key),
    
    -- Usage Metrics
    query_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_response_time_ms NUMERIC(8,2),
    total_documents_served INTEGER DEFAULT 0,
    unique_users_count INTEGER DEFAULT 0,
    
    -- Quality Metrics
    satisfaction_score NUMERIC(3,2), -- 1.0 to 5.0
    bounce_rate NUMERIC(5,4), -- 0.0 to 1.0
    completion_rate NUMERIC(5,4), -- 0.0 to 1.0
    
    -- Business Metrics
    conversion_rate NUMERIC(5,4), -- Query to successful completion
    cost_per_interaction NUMERIC(10,4),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact table for data quality monitoring
CREATE TABLE IF NOT EXISTS dwh.fact_data_quality (
    quality_id BIGSERIAL PRIMARY KEY,
    source_key INTEGER REFERENCES dwh.dim_source(source_key),
    date_key INTEGER REFERENCES dwh.dim_date(date_key),
    service_key INTEGER REFERENCES dwh.dim_service(service_key),
    
    -- Volume Metrics
    total_records INTEGER DEFAULT 0,
    new_records INTEGER DEFAULT 0,
    updated_records INTEGER DEFAULT 0,
    deleted_records INTEGER DEFAULT 0,
    
    -- Quality Metrics
    valid_records INTEGER DEFAULT 0,
    invalid_records INTEGER DEFAULT 0,
    duplicate_records INTEGER DEFAULT 0,
    completeness_score NUMERIC(5,4) DEFAULT 0.0, -- 0.0 to 1.0
    accuracy_score NUMERIC(5,4) DEFAULT 0.0, -- 0.0 to 1.0
    consistency_score NUMERIC(5,4) DEFAULT 0.0, -- 0.0 to 1.0
    
    -- Freshness Metrics
    freshness_hours INTEGER DEFAULT 0,
    lag_hours INTEGER DEFAULT 0, -- Time from source update to warehouse
    
    -- Processing Metrics
    processing_time_seconds INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact table for content analytics
CREATE TABLE IF NOT EXISTS dwh.fact_content_analytics (
    content_id BIGSERIAL PRIMARY KEY,
    service_key INTEGER REFERENCES dwh.dim_service(service_key),
    date_key INTEGER REFERENCES dwh.dim_date(date_key),
    content_type_key INTEGER REFERENCES dwh.dim_content_type(content_type_key),
    language_key INTEGER REFERENCES dwh.dim_language(language_key),
    
    -- Engagement Metrics
    views_count INTEGER DEFAULT 0,
    downloads_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    search_hits INTEGER DEFAULT 0,
    avg_read_time_seconds INTEGER DEFAULT 0,
    
    -- Content Metrics
    content_length_words INTEGER DEFAULT 0,
    content_length_characters INTEGER DEFAULT 0,
    readability_score NUMERIC(5,2) DEFAULT 0.0, -- Flesch reading ease
    translation_quality_score NUMERIC(5,4) DEFAULT 0.0, -- ML-based quality score
    
    -- Performance Metrics
    load_time_ms INTEGER DEFAULT 0,
    search_rank_position INTEGER,
    click_through_rate NUMERIC(5,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact table for search analytics
CREATE TABLE IF NOT EXISTS dwh.fact_search_analytics (
    search_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER REFERENCES dwh.dim_date(date_key),
    location_key INTEGER REFERENCES dwh.dim_location(location_key),
    user_segment_key INTEGER REFERENCES dwh.dim_user_segment(segment_key),
    language_key INTEGER REFERENCES dwh.dim_language(language_key),
    
    -- Search Metrics
    search_query TEXT,
    search_query_hash VARCHAR(64), -- For privacy and deduplication
    search_type VARCHAR(20) CHECK (search_type IN ('Semantic', 'Keyword', 'Hybrid')),
    results_count INTEGER DEFAULT 0,
    results_clicked INTEGER DEFAULT 0,
    
    -- Performance Metrics
    search_time_ms INTEGER DEFAULT 0,
    first_result_relevance_score NUMERIC(5,4) DEFAULT 0.0,
    avg_result_relevance_score NUMERIC(5,4) DEFAULT 0.0,
    
    -- User Behavior
    session_duration_seconds INTEGER DEFAULT 0,
    pages_viewed INTEGER DEFAULT 0,
    query_refinements INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Fact table indexes
CREATE INDEX IF NOT EXISTS idx_fact_service_usage_date ON dwh.fact_service_usage(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_service_usage_service ON dwh.fact_service_usage(service_key);
CREATE INDEX IF NOT EXISTS idx_fact_service_usage_location ON dwh.fact_service_usage(location_key);
CREATE INDEX IF NOT EXISTS idx_fact_service_usage_composite ON dwh.fact_service_usage(date_key, service_key);

CREATE INDEX IF NOT EXISTS idx_fact_data_quality_date ON dwh.fact_data_quality(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_data_quality_source ON dwh.fact_data_quality(source_key);

CREATE INDEX IF NOT EXISTS idx_fact_content_analytics_date ON dwh.fact_content_analytics(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_content_analytics_service ON dwh.fact_content_analytics(service_key);
CREATE INDEX IF NOT EXISTS idx_fact_content_analytics_language ON dwh.fact_content_analytics(language_key);

-- Dimension table indexes
CREATE INDEX IF NOT EXISTS idx_dim_service_category ON dwh.dim_service(service_category);
CREATE INDEX IF NOT EXISTS idx_dim_service_active ON dwh.dim_service(is_active, is_current);
CREATE INDEX IF NOT EXISTS idx_dim_location_state ON dwh.dim_location(state_name);
CREATE INDEX IF NOT EXISTS idx_dim_location_rural_urban ON dwh.dim_location(rural_urban);

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Monthly service performance summary
CREATE MATERIALIZED VIEW IF NOT EXISTS dwh.mv_monthly_service_performance AS
SELECT 
    ds.service_name,
    ds.service_category,
    ds.department,
    dd.year,
    dd.month,
    SUM(fsu.query_count) as total_queries,
    SUM(fsu.success_count) as successful_queries,
    AVG(fsu.satisfaction_score) as avg_satisfaction,
    AVG(fsu.avg_response_time_ms) as avg_response_time,
    CASE 
        WHEN SUM(fsu.query_count) = 0 THEN 0
        ELSE ROUND((SUM(fsu.success_count)::NUMERIC / SUM(fsu.query_count) * 100), 2)
    END as success_rate,
    SUM(fsu.total_documents_served) as documents_served,
    COUNT(DISTINCT fsu.date_key) as active_days
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_service ds ON fsu.service_key = ds.service_key
JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
WHERE ds.is_active = TRUE AND ds.is_current = TRUE
GROUP BY ds.service_name, ds.service_category, ds.department, dd.year, dd.month;

-- Create unique index for materialized view refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_monthly_service_performance_unique 
ON dwh.mv_monthly_service_performance(service_name, service_category, department, year, month);

-- Language-wise content performance
CREATE MATERIALIZED VIEW IF NOT EXISTS dwh.mv_language_content_performance AS
SELECT 
    dl.language_name,
    dl.language_code,
    dct.content_type,
    dd.year,
    dd.quarter,
    COUNT(*) as content_pieces,
    SUM(fca.views_count) as total_views,
    SUM(fca.downloads_count) as total_downloads,
    AVG(fca.readability_score) as avg_readability,
    AVG(fca.translation_quality_score) as avg_translation_quality,
    CASE 
        WHEN SUM(fca.views_count) = 0 THEN 0
        ELSE ROUND((SUM(fca.downloads_count)::NUMERIC / SUM(fca.views_count) * 100), 2)
    END as conversion_rate
FROM dwh.fact_content_analytics fca
JOIN dwh.dim_language dl ON fca.language_key = dl.language_key
JOIN dwh.dim_content_type dct ON fca.content_type_key = dct.content_type_key
JOIN dwh.dim_date dd ON fca.date_key = dd.date_key
GROUP BY dl.language_name, dl.language_code, dct.content_type, dd.year, dd.quarter;

-- Create unique index for materialized view refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_language_content_performance_unique
ON dwh.mv_language_content_performance(language_name, language_code, content_type, year, quarter);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION dwh.refresh_all_materialized_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dwh.mv_monthly_service_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY dwh.mv_language_content_performance;
    
    -- Log the refresh
    INSERT INTO dwh.etl_log (process_name, status, message, created_at)
    VALUES ('refresh_materialized_views', 'SUCCESS', 'All materialized views refreshed', CURRENT_TIMESTAMP);
EXCEPTION
    WHEN OTHERS THEN
        INSERT INTO dwh.etl_log (process_name, status, message, error_details, created_at)
        VALUES ('refresh_materialized_views', 'FAILED', 'Error refreshing materialized views', SQLERRM, CURRENT_TIMESTAMP);
        RAISE;
END;
$$ LANGUAGE plpgsql;

-- ETL logging table
CREATE TABLE IF NOT EXISTS dwh.etl_log (
    log_id BIGSERIAL PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('STARTED', 'SUCCESS', 'FAILED', 'WARNING')) NOT NULL,
    message TEXT,
    error_details TEXT,
    records_processed INTEGER DEFAULT 0,
    processing_time_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions to appropriate users/roles
-- GRANT USAGE ON SCHEMA dwh TO analyst_role;
-- GRANT SELECT ON ALL TABLES IN SCHEMA dwh TO analyst_role;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA dwh TO analyst_role;

-- Comments for documentation
COMMENT ON SCHEMA dwh IS 'Data warehouse schema for citizen services analytics';
COMMENT ON TABLE dwh.dim_service IS 'Service dimension with SCD Type 2 for tracking changes over time';
COMMENT ON TABLE dwh.fact_service_usage IS 'Main fact table tracking citizen interactions with government services';
COMMENT ON TABLE dwh.fact_data_quality IS 'Data quality metrics for monitoring ETL pipeline health';
COMMENT ON MATERIALIZED VIEW dwh.mv_monthly_service_performance IS 'Pre-aggregated monthly service performance metrics for fast reporting';