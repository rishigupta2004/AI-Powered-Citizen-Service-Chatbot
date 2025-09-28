-- =====================================================
-- Citizen Services Data Warehouse Schema
-- =====================================================

-- Create data warehouse database (run this separately)
-- CREATE DATABASE citizen_services_warehouse;

-- Connect to warehouse database
-- \c citizen_services_warehouse;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =====================================================
-- DIMENSION TABLES
-- =====================================================

-- Date Dimension
CREATE TABLE dim_date (
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
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Time Dimension
CREATE TABLE dim_time (
    time_key INTEGER PRIMARY KEY,
    full_time TIME NOT NULL UNIQUE,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    second INTEGER NOT NULL,
    hour_of_day INTEGER NOT NULL,
    period_of_day VARCHAR(20) NOT NULL,
    is_business_hours BOOLEAN NOT NULL DEFAULT FALSE,
    is_peak_hours BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service Dimension
CREATE TABLE dim_service (
    service_key SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL,
    service_name VARCHAR(150) NOT NULL,
    service_category VARCHAR(80) NOT NULL,
    department VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    priority_level INTEGER NOT NULL CHECK (priority_level BETWEEN 1 AND 5),
    service_type VARCHAR(50) NOT NULL,
    data_source VARCHAR(100) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(service_id)
);

-- User Dimension
CREATE TABLE dim_user (
    user_key SERIAL PRIMARY KEY,
    user_id INTEGER,
    user_type VARCHAR(50) NOT NULL,
    location_state VARCHAR(100),
    location_district VARCHAR(100),
    language_preference VARCHAR(10),
    device_type VARCHAR(50),
    browser_type VARCHAR(50),
    is_first_time_user BOOLEAN DEFAULT FALSE,
    registration_date DATE,
    last_activity_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Content Dimension
CREATE TABLE dim_content (
    content_key SERIAL PRIMARY KEY,
    content_id INTEGER NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    language VARCHAR(10) NOT NULL,
    content_source VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(content_id, content_type)
);

-- Query Type Dimension
CREATE TABLE dim_query_type (
    query_type_key SERIAL PRIMARY KEY,
    query_type VARCHAR(50) NOT NULL UNIQUE,
    query_category VARCHAR(50) NOT NULL,
    complexity_level VARCHAR(20) NOT NULL,
    expected_response_time_ms INTEGER,
    is_api_required BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Language Dimension
CREATE TABLE dim_language (
    language_key SERIAL PRIMARY KEY,
    language_code VARCHAR(10) NOT NULL UNIQUE,
    language_name VARCHAR(50) NOT NULL,
    script_type VARCHAR(20) NOT NULL,
    is_rtl BOOLEAN NOT NULL DEFAULT FALSE,
    is_supported BOOLEAN NOT NULL DEFAULT TRUE,
    coverage_percentage DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content Source Dimension
CREATE TABLE dim_content_source (
    content_source_key SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL,
    reliability_score DECIMAL(3,2) NOT NULL CHECK (reliability_score BETWEEN 0.00 AND 1.00),
    update_frequency VARCHAR(50) NOT NULL,
    last_sync TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    contact_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quality Metric Dimension
CREATE TABLE dim_quality_metric (
    quality_metric_key SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL UNIQUE,
    metric_category VARCHAR(50) NOT NULL,
    measurement_unit VARCHAR(20) NOT NULL,
    threshold_good DECIMAL(10,4),
    threshold_warning DECIMAL(10,4),
    threshold_critical DECIMAL(10,4),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FACT TABLES
-- =====================================================

-- Service Query Fact
CREATE TABLE fct_service_queries (
    query_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    user_key INTEGER,
    query_type_key INTEGER NOT NULL,
    language_key INTEGER NOT NULL,
    response_time_ms INTEGER,
    success_flag BOOLEAN NOT NULL,
    result_count INTEGER DEFAULT 0,
    user_satisfaction_score INTEGER CHECK (user_satisfaction_score BETWEEN 1 AND 5),
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    query_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Key Constraints
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (service_key) REFERENCES dim_service(service_key),
    FOREIGN KEY (user_key) REFERENCES dim_user(user_key),
    FOREIGN KEY (query_type_key) REFERENCES dim_query_type(query_type_key),
    FOREIGN KEY (language_key) REFERENCES dim_language(language_key)
);

-- Content Usage Fact
CREATE TABLE fct_content_usage (
    usage_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    content_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    user_key INTEGER,
    content_type_key INTEGER NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    duration_seconds INTEGER,
    scroll_depth_percent INTEGER CHECK (scroll_depth_percent BETWEEN 0 AND 100),
    referrer_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Key Constraints
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (content_key) REFERENCES dim_content(content_key),
    FOREIGN KEY (service_key) REFERENCES dim_service(service_key),
    FOREIGN KEY (user_key) REFERENCES dim_user(user_key)
);

-- Data Quality Fact
CREATE TABLE fct_data_quality (
    quality_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    content_source_key INTEGER NOT NULL,
    quality_metric_key INTEGER NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    threshold_value DECIMAL(10,4),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pass', 'warning', 'fail')),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Key Constraints
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (service_key) REFERENCES dim_service(service_key),
    FOREIGN KEY (content_source_key) REFERENCES dim_content_source(content_source_key),
    FOREIGN KEY (quality_metric_key) REFERENCES dim_quality_metric(quality_metric_key)
);

-- System Performance Fact
CREATE TABLE fct_system_performance (
    performance_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    threshold_value DECIMAL(10,4),
    status VARCHAR(20) NOT NULL CHECK (status IN ('normal', 'warning', 'critical')),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Key Constraints
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (service_key) REFERENCES dim_service(service_key)
);

-- =====================================================
-- DATA MARTS (AGGREGATED TABLES)
-- =====================================================

-- Service Analytics Data Mart
CREATE TABLE dm_service_analytics (
    service_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    total_queries BIGINT DEFAULT 0,
    successful_queries BIGINT DEFAULT 0,
    failed_queries BIGINT DEFAULT 0,
    avg_response_time_ms DECIMAL(10,2),
    unique_users BIGINT DEFAULT 0,
    satisfaction_score DECIMAL(3,2),
    content_views BIGINT DEFAULT 0,
    content_downloads BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (service_key, date_key),
    FOREIGN KEY (service_key) REFERENCES dim_service(service_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- User Analytics Data Mart
CREATE TABLE dm_user_analytics (
    user_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    session_count BIGINT DEFAULT 0,
    total_queries BIGINT DEFAULT 0,
    avg_session_duration_seconds INTEGER,
    most_used_service VARCHAR(150),
    language_preference VARCHAR(10),
    device_type VARCHAR(50),
    engagement_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (user_key, date_key),
    FOREIGN KEY (user_key) REFERENCES dim_user(user_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- Content Analytics Data Mart
CREATE TABLE dm_content_analytics (
    content_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    view_count BIGINT DEFAULT 0,
    download_count BIGINT DEFAULT 0,
    share_count BIGINT DEFAULT 0,
    avg_view_duration_seconds INTEGER,
    bounce_rate DECIMAL(5,2),
    search_rank_position INTEGER,
    user_rating DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (content_key, date_key),
    FOREIGN KEY (content_key) REFERENCES dim_content(content_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- System Performance Data Mart
CREATE TABLE dm_system_analytics (
    date_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    total_requests BIGINT DEFAULT 0,
    avg_response_time_ms DECIMAL(10,2),
    error_rate DECIMAL(5,2),
    throughput_rps DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_percent DECIMAL(5,2),
    disk_usage_percent DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (date_key, time_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Fact table indexes
CREATE INDEX idx_fct_service_queries_date_service ON fct_service_queries(date_key, service_key);
CREATE INDEX idx_fct_service_queries_user_date ON fct_service_queries(user_key, date_key);
CREATE INDEX idx_fct_service_queries_created_at ON fct_service_queries(created_at);
CREATE INDEX idx_fct_service_queries_success ON fct_service_queries(success_flag);

CREATE INDEX idx_fct_content_usage_date_content ON fct_content_usage(date_key, content_key);
CREATE INDEX idx_fct_content_usage_user_date ON fct_content_usage(user_key, date_key);
CREATE INDEX idx_fct_content_usage_action_type ON fct_content_usage(action_type);

CREATE INDEX idx_fct_data_quality_date_service ON fct_data_quality(date_key, service_key);
CREATE INDEX idx_fct_data_quality_status ON fct_data_quality(status);

CREATE INDEX idx_fct_system_performance_date_time ON fct_system_performance(date_key, time_key);
CREATE INDEX idx_fct_system_performance_metric_type ON fct_system_performance(metric_type);

-- Data mart indexes
CREATE INDEX idx_dm_service_analytics_date ON dm_service_analytics(date_key);
CREATE INDEX idx_dm_user_analytics_date ON dm_user_analytics(date_key);
CREATE INDEX idx_dm_content_analytics_date ON dm_content_analytics(date_key);
CREATE INDEX idx_dm_system_analytics_date ON dm_system_analytics(date_key);

-- =====================================================
-- PARTITIONING (for large fact tables)
-- =====================================================

-- Partition fct_service_queries by month
-- Note: This requires PostgreSQL 10+ and should be set up after initial data load
-- ALTER TABLE fct_service_queries RENAME TO fct_service_queries_old;
-- CREATE TABLE fct_service_queries (LIKE fct_service_queries_old) PARTITION BY RANGE (date_key);
-- 
-- -- Create monthly partitions (example for 2024)
-- CREATE TABLE fct_service_queries_202401 PARTITION OF fct_service_queries
--     FOR VALUES FROM (20240101) TO (20240201);
-- CREATE TABLE fct_service_queries_202402 PARTITION OF fct_service_queries
--     FOR VALUES FROM (20240201) TO (20240301);
-- -- ... continue for each month

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Daily service performance summary
CREATE VIEW v_daily_service_performance AS
SELECT 
    d.full_date,
    s.service_name,
    s.service_category,
    COUNT(*) as total_queries,
    COUNT(*) FILTER (WHERE sq.success_flag = true) as successful_queries,
    COUNT(*) FILTER (WHERE sq.success_flag = false) as failed_queries,
    ROUND(AVG(sq.response_time_ms), 2) as avg_response_time_ms,
    COUNT(DISTINCT sq.user_key) as unique_users,
    ROUND(AVG(sq.user_satisfaction_score), 2) as avg_satisfaction_score
FROM fct_service_queries sq
JOIN dim_date d ON sq.date_key = d.date_key
JOIN dim_service s ON sq.service_key = s.service_key
GROUP BY d.full_date, s.service_name, s.service_category
ORDER BY d.full_date DESC, total_queries DESC;

-- Content popularity ranking
CREATE VIEW v_content_popularity AS
SELECT 
    c.title,
    c.content_type,
    s.service_name,
    l.language_name,
    SUM(cu.duration_seconds) as total_view_time,
    COUNT(*) as total_views,
    ROUND(AVG(cu.duration_seconds), 2) as avg_view_duration,
    ROUND(AVG(cu.scroll_depth_percent), 2) as avg_scroll_depth
FROM fct_content_usage cu
JOIN dim_content c ON cu.content_key = c.content_key
JOIN dim_service s ON cu.service_key = s.service_key
JOIN dim_language l ON c.language = l.language_code
WHERE cu.action_type = 'view'
GROUP BY c.title, c.content_type, s.service_name, l.language_name
ORDER BY total_views DESC;

-- Data quality dashboard
CREATE VIEW v_data_quality_summary AS
SELECT 
    d.full_date,
    s.service_name,
    cs.source_name,
    qm.metric_name,
    qm.metric_category,
    AVG(fdq.metric_value) as avg_metric_value,
    qm.threshold_good,
    qm.threshold_warning,
    qm.threshold_critical,
    COUNT(*) FILTER (WHERE fdq.status = 'pass') as pass_count,
    COUNT(*) FILTER (WHERE fdq.status = 'warning') as warning_count,
    COUNT(*) FILTER (WHERE fdq.status = 'fail') as fail_count
FROM fct_data_quality fdq
JOIN dim_date d ON fdq.date_key = d.date_key
JOIN dim_service s ON fdq.service_key = s.service_key
JOIN dim_content_source cs ON fdq.content_source_key = cs.content_source_key
JOIN dim_quality_metric qm ON fdq.quality_metric_key = qm.quality_metric_key
GROUP BY d.full_date, s.service_name, cs.source_name, qm.metric_name, qm.metric_category, qm.threshold_good, qm.threshold_warning, qm.threshold_critical
ORDER BY d.full_date DESC, s.service_name, qm.metric_name;

-- =====================================================
-- FUNCTIONS FOR DATA WAREHOUSE MAINTENANCE
-- =====================================================

-- Function to generate date dimension data
CREATE OR REPLACE FUNCTION generate_date_dimension(start_date DATE, end_date DATE)
RETURNS VOID AS $$
DECLARE
    current_date DATE := start_date;
    date_key INTEGER;
    is_weekend BOOLEAN;
    is_holiday BOOLEAN;
    fiscal_year INTEGER;
    fiscal_quarter INTEGER;
BEGIN
    WHILE current_date <= end_date LOOP
        date_key := EXTRACT(YEAR FROM current_date) * 10000 + 
                   EXTRACT(MONTH FROM current_date) * 100 + 
                   EXTRACT(DAY FROM current_date);
        
        is_weekend := EXTRACT(DOW FROM current_date) IN (0, 6);
        is_holiday := FALSE; -- Add holiday logic here
        
        fiscal_year := EXTRACT(YEAR FROM current_date);
        fiscal_quarter := CEIL(EXTRACT(MONTH FROM current_date) / 3.0);
        
        INSERT INTO dim_date (
            date_key, full_date, year, quarter, month, month_name,
            week_of_year, day_of_year, day_of_week, day_name,
            is_weekend, is_holiday, fiscal_year, fiscal_quarter
        ) VALUES (
            date_key, current_date, EXTRACT(YEAR FROM current_date),
            EXTRACT(QUARTER FROM current_date), EXTRACT(MONTH FROM current_date),
            TO_CHAR(current_date, 'Month'), EXTRACT(WEEK FROM current_date),
            EXTRACT(DOY FROM current_date), EXTRACT(DOW FROM current_date),
            TO_CHAR(current_date, 'Day'), is_weekend, is_holiday,
            fiscal_year, fiscal_quarter
        ) ON CONFLICT (date_key) DO NOTHING;
        
        current_date := current_date + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to generate time dimension data
CREATE OR REPLACE FUNCTION generate_time_dimension()
RETURNS VOID AS $$
DECLARE
    hour_val INTEGER;
    minute_val INTEGER;
    second_val INTEGER;
    time_key INTEGER;
    full_time TIME;
    period_of_day VARCHAR(20);
    is_business_hours BOOLEAN;
    is_peak_hours BOOLEAN;
BEGIN
    FOR hour_val IN 0..23 LOOP
        FOR minute_val IN 0..59 LOOP
            FOR second_val IN 0..59 LOOP
                time_key := hour_val * 10000 + minute_val * 100 + second_val;
                full_time := MAKE_TIME(hour_val, minute_val, second_val);
                
                -- Determine period of day
                IF hour_val BETWEEN 6 AND 11 THEN
                    period_of_day := 'morning';
                ELSIF hour_val BETWEEN 12 AND 17 THEN
                    period_of_day := 'afternoon';
                ELSIF hour_val BETWEEN 18 AND 21 THEN
                    period_of_day := 'evening';
                ELSE
                    period_of_day := 'night';
                END IF;
                
                is_business_hours := hour_val BETWEEN 9 AND 17 AND EXTRACT(DOW FROM CURRENT_DATE) BETWEEN 1 AND 5;
                is_peak_hours := hour_val IN (9, 10, 11, 14, 15, 16);
                
                INSERT INTO dim_time (
                    time_key, full_time, hour, minute, second, hour_of_day,
                    period_of_day, is_business_hours, is_peak_hours
                ) VALUES (
                    time_key, full_time, hour_val, minute_val, second_val, hour_val,
                    period_of_day, is_business_hours, is_peak_hours
                ) ON CONFLICT (time_key) DO NOTHING;
            END LOOP;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA LOADING
-- =====================================================

-- Generate date dimension for 2024-2025
SELECT generate_date_dimension('2024-01-01'::DATE, '2025-12-31'::DATE);

-- Generate time dimension
SELECT generate_time_dimension();

-- Insert initial query types
INSERT INTO dim_query_type (query_type, query_category, complexity_level, expected_response_time_ms, is_api_required, description) VALUES
('search', 'general', 'simple', 500, false, 'General content search'),
('status_check', 'specific', 'moderate', 2000, true, 'Application status verification'),
('verification', 'specific', 'moderate', 1500, true, 'Document or identity verification'),
('information', 'general', 'simple', 300, false, 'General information request'),
('procedural', 'specific', 'complex', 3000, false, 'Step-by-step procedure guidance');

-- Insert supported languages
INSERT INTO dim_language (language_code, language_name, script_type, is_rtl, is_supported, coverage_percentage) VALUES
('en', 'English', 'latin', false, true, 100.00),
('hi', 'Hindi', 'devanagari', false, true, 95.00),
('bn', 'Bengali', 'bengali', false, true, 80.00),
('ta', 'Tamil', 'tamil', false, true, 75.00),
('te', 'Telugu', 'telugu', false, true, 70.00),
('mr', 'Marathi', 'devanagari', false, true, 65.00),
('gu', 'Gujarati', 'gujarati', false, true, 60.00),
('kn', 'Kannada', 'kannada', false, true, 55.00);

-- Insert content sources
INSERT INTO dim_content_source (source_name, source_type, reliability_score, update_frequency, is_active, contact_info) VALUES
('apisetu', 'api', 0.95, 'real_time', true, '{"website": "https://apisetu.gov.in", "contact": "support@apisetu.gov.in"}'),
('uidai', 'api', 0.98, 'real_time', true, '{"website": "https://uidai.gov.in", "contact": "help@uidai.gov.in"}'),
('passportindia', 'scraping', 0.90, 'daily', true, '{"website": "https://passportindia.gov.in", "contact": "support@passportindia.gov.in"}'),
('incometax', 'scraping', 0.88, 'daily', true, '{"website": "https://incometax.gov.in", "contact": "help@incometax.gov.in"}'),
('epfindia', 'scraping', 0.85, 'daily', true, '{"website": "https://epfindia.gov.in", "contact": "support@epfindia.gov.in"}'),
('parivahan', 'scraping', 0.87, 'daily', true, '{"website": "https://parivahan.gov.in", "contact": "help@parivahan.gov.in"}');

-- Insert quality metrics
INSERT INTO dim_quality_metric (metric_name, metric_category, measurement_unit, threshold_good, threshold_warning, threshold_critical, description) VALUES
('completeness', 'data_quality', 'percentage', 95.00, 85.00, 75.00, 'Percentage of required fields populated'),
('accuracy', 'data_quality', 'percentage', 98.00, 90.00, 80.00, 'Percentage of data matching source systems'),
('freshness', 'data_quality', 'hours', 24.00, 72.00, 168.00, 'Age of data in hours'),
('consistency', 'data_quality', 'percentage', 95.00, 85.00, 75.00, 'Percentage of data following business rules'),
('availability', 'system_quality', 'percentage', 99.90, 99.00, 95.00, 'System uptime percentage'),
('response_time', 'system_quality', 'milliseconds', 500.00, 2000.00, 5000.00, 'Average response time in milliseconds');

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Create warehouse user (adjust as needed)
-- CREATE USER warehouse_user WITH PASSWORD 'secure_password';
-- GRANT CONNECT ON DATABASE citizen_services_warehouse TO warehouse_user;
-- GRANT USAGE ON SCHEMA public TO warehouse_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO warehouse_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO warehouse_user;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON DATABASE citizen_services_warehouse IS 'Data warehouse for Citizen Services Database analytics and reporting';
COMMENT ON TABLE dim_date IS 'Date dimension table with calendar and fiscal year information';
COMMENT ON TABLE dim_time IS 'Time dimension table with hour-level granularity';
COMMENT ON TABLE dim_service IS 'Service dimension with government service information';
COMMENT ON TABLE dim_user IS 'User dimension with citizen and system user information';
COMMENT ON TABLE dim_content IS 'Content dimension with all content types and sources';
COMMENT ON TABLE fct_service_queries IS 'Fact table tracking all service queries and interactions';
COMMENT ON TABLE fct_content_usage IS 'Fact table tracking content consumption and engagement';
COMMENT ON TABLE fct_data_quality IS 'Fact table tracking data quality metrics';
COMMENT ON TABLE fct_system_performance IS 'Fact table tracking system performance metrics';