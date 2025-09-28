-- Data Warehouse Schema for Citizen Services Database
-- This schema complements the operational database with analytics-focused tables

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ==============================================
-- DIMENSION TABLES
-- ==============================================

-- Date Dimension Table
CREATE TABLE date_dim (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
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
    fiscal_quarter INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service Dimension Table
CREATE TABLE service_dim (
    service_key SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL,
    service_name VARCHAR(150) NOT NULL,
    category VARCHAR(80),
    description TEXT,
    government_department VARCHAR(100),
    service_type VARCHAR(50) NOT NULL, -- 'api', 'scraping', 'hybrid'
    priority_level INTEGER NOT NULL, -- 1-5 scale (1=highest priority)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(service_id)
);

-- User Dimension Table
CREATE TABLE user_dim (
    user_key SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_type VARCHAR(50) NOT NULL, -- 'citizen', 'admin', 'analyst', 'system'
    region VARCHAR(100),
    language_preference VARCHAR(10),
    device_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    UNIQUE(user_id)
);

-- Content Type Dimension Table
CREATE TABLE content_type_dim (
    content_type_key SERIAL PRIMARY KEY,
    content_type VARCHAR(100) NOT NULL, -- 'procedure', 'document', 'faq', 'form', 'api_response'
    sub_type VARCHAR(100),
    format VARCHAR(50) NOT NULL, -- 'text', 'pdf', 'html', 'json', 'xml'
    language VARCHAR(10),
    source VARCHAR(100) NOT NULL, -- 'api', 'scraping', 'manual', 'generated'
    is_structured BOOLEAN DEFAULT FALSE,
    requires_validation BOOLEAN DEFAULT TRUE
);

-- Language Dimension Table
CREATE TABLE language_dim (
    language_key SERIAL PRIMARY KEY,
    language_code VARCHAR(10) NOT NULL UNIQUE,
    language_name VARCHAR(50) NOT NULL,
    script VARCHAR(20) NOT NULL, -- 'latin', 'devanagari', 'bengali', 'tamil', etc.
    is_rtl BOOLEAN DEFAULT FALSE,
    is_official BOOLEAN DEFAULT FALSE,
    is_supported BOOLEAN DEFAULT TRUE
);

-- Region Dimension Table
CREATE TABLE region_dim (
    region_key SERIAL PRIMARY KEY,
    state_code VARCHAR(10),
    state_name VARCHAR(100),
    district_code VARCHAR(10),
    district_name VARCHAR(100),
    pincode VARCHAR(10),
    region_type VARCHAR(50), -- 'urban', 'rural', 'semi-urban'
    population_density VARCHAR(20), -- 'high', 'medium', 'low'
    literacy_rate DECIMAL(5,2),
    internet_penetration DECIMAL(5,2)
);

-- API Endpoint Dimension Table
CREATE TABLE endpoint_dim (
    endpoint_key SERIAL PRIMARY KEY,
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    endpoint_name VARCHAR(200) NOT NULL,
    endpoint_url TEXT NOT NULL,
    method VARCHAR(10) NOT NULL, -- 'GET', 'POST', 'PUT', 'DELETE'
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_minute INTEGER,
    timeout_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- FACT TABLES
-- ==============================================

-- Service Usage Fact Table
CREATE TABLE service_usage_fact (
    fact_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES date_dim(date_key),
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    user_key INTEGER REFERENCES user_dim(user_key),
    procedure_key INTEGER, -- References procedure_id from operational DB
    document_key INTEGER, -- References doc_id from operational DB
    language_key INTEGER REFERENCES language_dim(language_key),
    region_key INTEGER REFERENCES region_dim(region_key),
    usage_count INTEGER DEFAULT 1,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    response_time_ms INTEGER,
    session_duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Content Quality Fact Table
CREATE TABLE content_quality_fact (
    fact_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES date_dim(date_key),
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    content_type_key INTEGER NOT NULL REFERENCES content_type_dim(content_type_key),
    language_key INTEGER REFERENCES language_dim(language_key),
    quality_score DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    completeness_score DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    accuracy_score DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    freshness_score DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    validation_errors INTEGER DEFAULT 0,
    content_length INTEGER,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API Performance Fact Table
CREATE TABLE api_performance_fact (
    fact_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES date_dim(date_key),
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    endpoint_key INTEGER NOT NULL REFERENCES endpoint_dim(endpoint_key),
    request_count INTEGER NOT NULL,
    success_count INTEGER NOT NULL,
    error_count INTEGER NOT NULL,
    avg_response_time_ms DECIMAL(10,2) NOT NULL,
    max_response_time_ms INTEGER NOT NULL,
    min_response_time_ms INTEGER NOT NULL,
    p95_response_time_ms INTEGER,
    p99_response_time_ms INTEGER,
    timeout_count INTEGER DEFAULT 0,
    rate_limit_hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document Processing Fact Table
CREATE TABLE document_processing_fact (
    fact_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES date_dim(date_key),
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    content_type_key INTEGER NOT NULL REFERENCES content_type_dim(content_type_key),
    language_key INTEGER REFERENCES language_dim(language_key),
    documents_processed INTEGER NOT NULL,
    successful_extractions INTEGER NOT NULL,
    failed_extractions INTEGER NOT NULL,
    avg_processing_time_ms DECIMAL(10,2),
    ocr_accuracy_score DECIMAL(5,2),
    classification_accuracy DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Engagement Fact Table
CREATE TABLE user_engagement_fact (
    fact_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES date_dim(date_key),
    user_key INTEGER NOT NULL REFERENCES user_dim(user_key),
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    region_key INTEGER REFERENCES region_dim(region_key),
    session_count INTEGER DEFAULT 1,
    page_views INTEGER DEFAULT 0,
    search_queries INTEGER DEFAULT 0,
    successful_completions INTEGER DEFAULT 0,
    session_duration_seconds INTEGER,
    bounce_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- AGGREGATED TABLES
-- ==============================================

-- Daily Service Summary
CREATE TABLE daily_service_summary (
    summary_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES date_dim(date_key),
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN total_requests > 0 
        THEN (successful_requests::DECIMAL / total_requests) * 100 
        ELSE 0 END
    ) STORED,
    avg_response_time_ms DECIMAL(10,2),
    max_response_time_ms INTEGER,
    unique_users INTEGER DEFAULT 0,
    content_updates INTEGER DEFAULT 0,
    avg_quality_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date_key, service_key)
);

-- Weekly Content Analytics
CREATE TABLE weekly_content_analytics (
    analytics_id SERIAL PRIMARY KEY,
    week_key INTEGER NOT NULL, -- YYYYWW format
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    content_type_key INTEGER NOT NULL REFERENCES content_type_dim(content_type_key),
    language_key INTEGER REFERENCES language_dim(language_key),
    total_content_items INTEGER DEFAULT 0,
    new_content_items INTEGER DEFAULT 0,
    updated_content_items INTEGER DEFAULT 0,
    deleted_content_items INTEGER DEFAULT 0,
    avg_quality_score DECIMAL(5,2),
    multilingual_coverage DECIMAL(5,2),
    completeness_percentage DECIMAL(5,2),
    avg_processing_time_ms DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_key, service_key, content_type_key, language_key)
);

-- Monthly Service Performance
CREATE TABLE monthly_service_performance (
    performance_id SERIAL PRIMARY KEY,
    month_key INTEGER NOT NULL, -- YYYYMM format
    service_key INTEGER NOT NULL REFERENCES service_dim(service_key),
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    avg_response_time_ms DECIMAL(10,2),
    p95_response_time_ms INTEGER,
    p99_response_time_ms INTEGER,
    error_rate DECIMAL(5,2),
    availability_percentage DECIMAL(5,2),
    user_satisfaction_score DECIMAL(3,2), -- 1.00 to 5.00
    content_freshness_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(month_key, service_key)
);

-- ==============================================
-- INDEXES FOR PERFORMANCE
-- ==============================================

-- Date dimension indexes
CREATE INDEX idx_date_dim_full_date ON date_dim(full_date);
CREATE INDEX idx_date_dim_year_month ON date_dim(year, month);
CREATE INDEX idx_date_dim_quarter ON date_dim(quarter);

-- Service dimension indexes
CREATE INDEX idx_service_dim_category ON service_dim(category);
CREATE INDEX idx_service_dim_priority ON service_dim(priority_level);
CREATE INDEX idx_service_dim_active ON service_dim(is_active);

-- Fact table indexes
CREATE INDEX idx_service_usage_date_service ON service_usage_fact(date_key, service_key);
CREATE INDEX idx_service_usage_user ON service_usage_fact(user_key);
CREATE INDEX idx_service_usage_region ON service_usage_fact(region_key);

CREATE INDEX idx_content_quality_date_service ON content_quality_fact(date_key, service_key);
CREATE INDEX idx_content_quality_type ON content_quality_fact(content_type_key);

CREATE INDEX idx_api_performance_date_service ON api_performance_fact(date_key, service_key);
CREATE INDEX idx_api_performance_endpoint ON api_performance_fact(endpoint_key);

CREATE INDEX idx_document_processing_date_service ON document_processing_fact(date_key, service_key);
CREATE INDEX idx_document_processing_type ON document_processing_fact(content_type_key);

CREATE INDEX idx_user_engagement_date_user ON user_engagement_fact(date_key, user_key);
CREATE INDEX idx_user_engagement_service ON user_engagement_fact(service_key);

-- Aggregated table indexes
CREATE INDEX idx_daily_summary_date ON daily_service_summary(date_key);
CREATE INDEX idx_daily_summary_service ON daily_service_summary(service_key);

CREATE INDEX idx_weekly_analytics_week ON weekly_content_analytics(week_key);
CREATE INDEX idx_weekly_analytics_service ON weekly_content_analytics(service_key);

CREATE INDEX idx_monthly_performance_month ON monthly_service_performance(month_key);
CREATE INDEX idx_monthly_performance_service ON monthly_service_performance(service_key);

-- ==============================================
-- VIEWS FOR COMMON QUERIES
-- ==============================================

-- Service Performance Summary View
CREATE VIEW v_service_performance_summary AS
SELECT 
    s.service_name,
    s.category,
    s.priority_level,
    dss.date_key,
    dd.full_date,
    dss.total_requests,
    dss.successful_requests,
    dss.success_rate,
    dss.avg_response_time_ms,
    dss.unique_users,
    dss.avg_quality_score
FROM daily_service_summary dss
JOIN service_dim s ON dss.service_key = s.service_key
JOIN date_dim dd ON dss.date_key = dd.date_key
WHERE s.is_active = TRUE;

-- Content Quality Overview View
CREATE VIEW v_content_quality_overview AS
SELECT 
    s.service_name,
    ctd.content_type,
    ctd.sub_type,
    ld.language_name,
    cqf.quality_score,
    cqf.completeness_score,
    cqf.accuracy_score,
    cqf.freshness_score,
    cqf.validation_errors,
    dd.full_date
FROM content_quality_fact cqf
JOIN service_dim s ON cqf.service_key = s.service_key
JOIN content_type_dim ctd ON cqf.content_type_key = ctd.content_type_key
JOIN language_dim ld ON cqf.language_key = ld.language_key
JOIN date_dim dd ON cqf.date_key = dd.date_key;

-- API Performance Trends View
CREATE VIEW v_api_performance_trends AS
SELECT 
    s.service_name,
    ed.endpoint_name,
    dd.full_date,
    apf.request_count,
    apf.success_count,
    apf.error_count,
    apf.avg_response_time_ms,
    apf.p95_response_time_ms,
    apf.p99_response_time_ms,
    CASE WHEN apf.request_count > 0 
         THEN (apf.error_count::DECIMAL / apf.request_count) * 100 
         ELSE 0 END as error_rate
FROM api_performance_fact apf
JOIN service_dim s ON apf.service_key = s.service_key
JOIN endpoint_dim ed ON apf.endpoint_key = ed.endpoint_key
JOIN date_dim dd ON apf.date_key = dd.date_key;

-- ==============================================
-- FUNCTIONS FOR DATA WAREHOUSE OPERATIONS
-- ==============================================

-- Function to populate date dimension
CREATE OR REPLACE FUNCTION populate_date_dimension(start_date DATE, end_date DATE)
RETURNS VOID AS $$
DECLARE
    current_date DATE := start_date;
    date_key INTEGER;
BEGIN
    WHILE current_date <= end_date LOOP
        date_key := EXTRACT(EPOCH FROM current_date)::INTEGER;
        
        INSERT INTO date_dim (
            date_key, full_date, year, quarter, month, month_name,
            week_of_year, day_of_year, day_of_week, day_name,
            is_weekend, is_holiday
        ) VALUES (
            date_key,
            current_date,
            EXTRACT(YEAR FROM current_date),
            EXTRACT(QUARTER FROM current_date),
            EXTRACT(MONTH FROM current_date),
            TO_CHAR(current_date, 'Month'),
            EXTRACT(WEEK FROM current_date),
            EXTRACT(DOY FROM current_date),
            EXTRACT(DOW FROM current_date),
            TO_CHAR(current_date, 'Day'),
            EXTRACT(DOW FROM current_date) IN (0, 6),
            FALSE -- Holiday logic can be added later
        ) ON CONFLICT (date_key) DO NOTHING;
        
        current_date := current_date + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate service success rate
CREATE OR REPLACE FUNCTION calculate_service_success_rate(
    p_service_key INTEGER,
    p_start_date DATE,
    p_end_date DATE
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    success_rate DECIMAL(5,2);
BEGIN
    SELECT 
        CASE WHEN SUM(total_requests) > 0 
        THEN (SUM(successful_requests)::DECIMAL / SUM(total_requests)) * 100 
        ELSE 0 END
    INTO success_rate
    FROM daily_service_summary dss
    JOIN date_dim dd ON dss.date_key = dd.date_key
    WHERE dss.service_key = p_service_key
    AND dd.full_date BETWEEN p_start_date AND p_end_date;
    
    RETURN COALESCE(success_rate, 0);
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- INITIAL DATA POPULATION
-- ==============================================

-- Populate date dimension for the next 2 years
SELECT populate_date_dimension(CURRENT_DATE, CURRENT_DATE + INTERVAL '2 years');

-- Insert initial language data
INSERT INTO language_dim (language_code, language_name, script, is_official, is_supported) VALUES
('en', 'English', 'latin', TRUE, TRUE),
('hi', 'Hindi', 'devanagari', TRUE, TRUE),
('bn', 'Bengali', 'bengali', TRUE, TRUE),
('ta', 'Tamil', 'tamil', TRUE, TRUE),
('te', 'Telugu', 'telugu', TRUE, TRUE),
('mr', 'Marathi', 'devanagari', TRUE, TRUE),
('gu', 'Gujarati', 'gujarati', TRUE, TRUE),
('kn', 'Kannada', 'kannada', TRUE, TRUE),
('ml', 'Malayalam', 'malayalam', TRUE, TRUE),
('pa', 'Punjabi', 'gurmukhi', TRUE, TRUE);

-- Insert initial content types
INSERT INTO content_type_dim (content_type, sub_type, format, source, is_structured, requires_validation) VALUES
('procedure', 'step_by_step', 'text', 'scraping', TRUE, TRUE),
('procedure', 'checklist', 'text', 'scraping', TRUE, TRUE),
('document', 'requirement', 'text', 'scraping', TRUE, TRUE),
('document', 'template', 'pdf', 'scraping', FALSE, TRUE),
('faq', 'general', 'text', 'scraping', TRUE, TRUE),
('faq', 'troubleshooting', 'text', 'scraping', TRUE, TRUE),
('form', 'application', 'pdf', 'api', FALSE, TRUE),
('form', 'correction', 'pdf', 'api', FALSE, TRUE),
('api_response', 'status', 'json', 'api', TRUE, FALSE),
('api_response', 'data', 'json', 'api', TRUE, FALSE);

-- Insert initial regions (major states)
INSERT INTO region_dim (state_code, state_name, region_type, population_density) VALUES
('MH', 'Maharashtra', 'urban', 'high'),
('UP', 'Uttar Pradesh', 'rural', 'high'),
('WB', 'West Bengal', 'urban', 'high'),
('TN', 'Tamil Nadu', 'urban', 'high'),
('KA', 'Karnataka', 'urban', 'medium'),
('GJ', 'Gujarat', 'urban', 'medium'),
('RJ', 'Rajasthan', 'rural', 'low'),
('MP', 'Madhya Pradesh', 'rural', 'low'),
('DL', 'Delhi', 'urban', 'high'),
('BR', 'Bihar', 'rural', 'high');

-- ==============================================
-- COMMENTS AND DOCUMENTATION
-- ==============================================

COMMENT ON TABLE date_dim IS 'Date dimension table for time-based analytics';
COMMENT ON TABLE service_dim IS 'Service dimension table containing government service information';
COMMENT ON TABLE user_dim IS 'User dimension table for user analytics';
COMMENT ON TABLE content_type_dim IS 'Content type dimension for content analytics';
COMMENT ON TABLE language_dim IS 'Language dimension for multilingual analytics';
COMMENT ON TABLE region_dim IS 'Geographic region dimension for location-based analytics';

COMMENT ON TABLE service_usage_fact IS 'Fact table tracking service usage metrics';
COMMENT ON TABLE content_quality_fact IS 'Fact table tracking content quality metrics';
COMMENT ON TABLE api_performance_fact IS 'Fact table tracking API performance metrics';
COMMENT ON TABLE document_processing_fact IS 'Fact table tracking document processing metrics';
COMMENT ON TABLE user_engagement_fact IS 'Fact table tracking user engagement metrics';

COMMENT ON TABLE daily_service_summary IS 'Daily aggregated service performance metrics';
COMMENT ON TABLE weekly_content_analytics IS 'Weekly aggregated content analytics';
COMMENT ON TABLE monthly_service_performance IS 'Monthly aggregated service performance metrics';