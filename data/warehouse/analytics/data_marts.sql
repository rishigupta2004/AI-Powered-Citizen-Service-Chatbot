-- Data Warehouse Analytics Views and Data Marts
-- Citizen Services Database Project

-- ============================================================================
-- SERVICE PERFORMANCE DATA MART
-- ============================================================================

-- Monthly service performance aggregation
CREATE OR REPLACE VIEW dwh.dm_service_performance_monthly AS
SELECT 
    ds.service_name,
    ds.service_category,
    ds.department,
    ds.ministry,
    dd.year,
    dd.month,
    dd.month_name,
    SUM(fsu.query_count) as total_queries,
    SUM(fsu.success_count) as successful_queries,
    AVG(fsu.satisfaction_score) as avg_satisfaction,
    AVG(fsu.avg_response_time_ms) as avg_response_time,
    SUM(fsu.total_documents_served) as documents_served,
    AVG(fsu.completion_rate) as avg_completion_rate,
    COUNT(DISTINCT fsu.date_key) as active_days,
    CASE 
        WHEN SUM(fsu.query_count) = 0 THEN 0
        ELSE ROUND((SUM(fsu.success_count)::NUMERIC / SUM(fsu.query_count) * 100), 2)
    END as success_rate_percent,
    CASE 
        WHEN AVG(fsu.satisfaction_score) >= 4.0 THEN 'Excellent'
        WHEN AVG(fsu.satisfaction_score) >= 3.5 THEN 'Good'
        WHEN AVG(fsu.satisfaction_score) >= 3.0 THEN 'Average'
        ELSE 'Poor'
    END as satisfaction_rating
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_service ds ON fsu.service_key = ds.service_key
JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
WHERE ds.is_active = TRUE AND ds.is_current = TRUE
GROUP BY ds.service_name, ds.service_category, ds.department, ds.ministry, 
         dd.year, dd.month, dd.month_name
ORDER BY dd.year DESC, dd.month DESC, total_queries DESC;

-- Weekly service trends
CREATE OR REPLACE VIEW dwh.dm_service_trends_weekly AS
SELECT 
    ds.service_name,
    ds.service_category,
    dd.year,
    dd.week,
    SUM(fsu.query_count) as weekly_queries,
    AVG(fsu.satisfaction_score) as weekly_satisfaction,
    LAG(SUM(fsu.query_count)) OVER (
        PARTITION BY ds.service_key 
        ORDER BY dd.year, dd.week
    ) as prev_week_queries,
    CASE 
        WHEN LAG(SUM(fsu.query_count)) OVER (
            PARTITION BY ds.service_key 
            ORDER BY dd.year, dd.week
        ) IS NOT NULL THEN
        ROUND(
            (SUM(fsu.query_count) - LAG(SUM(fsu.query_count)) OVER (
                PARTITION BY ds.service_key 
                ORDER BY dd.year, dd.week
            ))::NUMERIC / LAG(SUM(fsu.query_count)) OVER (
                PARTITION BY ds.service_key 
                ORDER BY dd.year, dd.week
            ) * 100, 2
        )
        ELSE NULL
    END as query_growth_percent
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_service ds ON fsu.service_key = ds.service_key
JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
WHERE ds.is_active = TRUE AND ds.is_current = TRUE
GROUP BY ds.service_key, ds.service_name, ds.service_category, dd.year, dd.week
ORDER BY dd.year DESC, dd.week DESC, weekly_queries DESC;

-- ============================================================================
-- CITIZEN ENGAGEMENT DATA MART
-- ============================================================================

-- Demographic engagement analysis
CREATE OR REPLACE VIEW dwh.dm_citizen_engagement_demographics AS
SELECT 
    dus.age_group,
    dus.education_level,
    dus.income_bracket,
    dus.device_type,
    dl.state_name,
    dl.rural_urban,
    dd.year,
    dd.quarter,
    COUNT(DISTINCT fsu.usage_id) as unique_interactions,
    SUM(fsu.query_count) as total_queries,
    AVG(fsu.satisfaction_score) as avg_satisfaction,
    SUM(fsu.total_documents_served) as documents_accessed,
    AVG(fsu.avg_response_time_ms) as avg_response_time,
    CASE 
        WHEN dus.age_group IN ('18-25', '26-35') THEN 'Young Adults'
        WHEN dus.age_group IN ('36-50') THEN 'Middle Aged'
        ELSE 'Senior Citizens'
    END as age_category,
    CASE 
        WHEN dus.education_level IN ('Graduate', 'Post-Graduate') THEN 'Higher Education'
        ELSE 'School Education'
    END as education_category
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_user_segment dus ON fsu.user_segment_key = dus.segment_key
JOIN dwh.dim_location dl ON fsu.location_key = dl.location_key
JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
GROUP BY dus.age_group, dus.education_level, dus.income_bracket, dus.device_type,
         dl.state_name, dl.rural_urban, dd.year, dd.quarter
ORDER BY dd.year DESC, dd.quarter DESC, total_queries DESC;

-- Channel preference analysis
CREATE OR REPLACE VIEW dwh.dm_channel_analytics AS
SELECT 
    dc.channel_name,
    dc.channel_type,
    dc.platform,
    dus.age_group,
    dus.device_type,
    dd.year,
    dd.month,
    SUM(fsu.query_count) as channel_queries,
    SUM(fsu.success_count) as channel_successes,
    AVG(fsu.satisfaction_score) as channel_satisfaction,
    AVG(fsu.avg_response_time_ms) as channel_response_time,
    ROUND(
        (SUM(fsu.success_count)::NUMERIC / SUM(fsu.query_count) * 100), 2
    ) as channel_success_rate,
    -- Channel preference score
    CASE 
        WHEN dc.channel_name = 'Mobile App' AND dus.age_group IN ('18-25', '26-35') THEN 'High'
        WHEN dc.channel_name = 'Web Portal' AND dus.age_group IN ('36-50', '51-65') THEN 'High'
        WHEN dc.channel_name = 'Call Center' AND dus.age_group = '65+' THEN 'High'
        ELSE 'Medium'
    END as preference_score
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_channel dc ON fsu.channel_key = dc.channel_key
JOIN dwh.dim_user_segment dus ON fsu.user_segment_key = dus.segment_key
JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
WHERE dc.is_active = TRUE
GROUP BY dc.channel_name, dc.channel_type, dc.platform, dus.age_group, 
         dus.device_type, dd.year, dd.month
ORDER BY dd.year DESC, dd.month DESC, channel_queries DESC;

-- ============================================================================
-- CONTENT ANALYTICS DATA MART
-- ============================================================================

-- Multilingual content performance
CREATE OR REPLACE VIEW dwh.dm_content_multilingual AS
SELECT 
    ds.service_name,
    ds.service_category,
    dct.content_type,
    dct.content_format,
    dl.language_name,
    dl.language_code,
    dd.year,
    dd.quarter,
    COUNT(*) as content_pieces,
    SUM(fca.views_count) as total_views,
    SUM(fca.downloads_count) as total_downloads,
    AVG(fca.readability_score) as avg_readability,
    AVG(fca.translation_quality_score) as avg_translation_quality,
    AVG(fca.avg_read_time_seconds) as avg_engagement_time,
    CASE 
        WHEN SUM(fca.views_count) = 0 THEN 0
        ELSE ROUND((SUM(fca.downloads_count)::NUMERIC / SUM(fca.views_count) * 100), 2)
    END as conversion_rate_percent,
    -- Content quality rating
    CASE 
        WHEN AVG(fca.readability_score) >= 80 AND AVG(fca.translation_quality_score) >= 0.9 THEN 'Excellent'
        WHEN AVG(fca.readability_score) >= 60 AND AVG(fca.translation_quality_score) >= 0.8 THEN 'Good'
        WHEN AVG(fca.readability_score) >= 40 AND AVG(fca.translation_quality_score) >= 0.7 THEN 'Average'
        ELSE 'Needs Improvement'
    END as content_quality_rating
FROM dwh.fact_content_analytics fca
JOIN dwh.dim_service ds ON fca.service_key = ds.service_key
JOIN dwh.dim_content_type dct ON fca.content_type_key = dct.content_type_key
JOIN dwh.dim_language dl ON fca.language_key = dl.language_key
JOIN dwh.dim_date dd ON fca.date_key = dd.date_key
WHERE ds.is_active = TRUE AND ds.is_current = TRUE
GROUP BY ds.service_name, ds.service_category, dct.content_type, dct.content_format,
         dl.language_name, dl.language_code, dd.year, dd.quarter
ORDER BY dd.year DESC, dd.quarter DESC, total_views DESC;

-- Content gap analysis
CREATE OR REPLACE VIEW dwh.dm_content_gaps AS
WITH service_languages AS (
    SELECT DISTINCT 
        ds.service_key,
        ds.service_name,
        ds.service_category,
        dl.language_code,
        dl.language_name
    FROM dwh.dim_service ds
    CROSS JOIN dwh.dim_language dl
    WHERE ds.is_active = TRUE 
    AND ds.is_current = TRUE
    AND dl.is_supported = TRUE
),
existing_content AS (
    SELECT DISTINCT
        fca.service_key,
        fca.language_key,
        dl.language_code
    FROM dwh.fact_content_analytics fca
    JOIN dwh.dim_language dl ON fca.language_key = dl.language_key
    WHERE fca.views_count > 0
)
SELECT 
    sl.service_name,
    sl.service_category,
    sl.language_name,
    sl.language_code,
    CASE 
        WHEN ec.service_key IS NOT NULL THEN 'Available'
        ELSE 'Missing'
    END as content_availability,
    -- Priority for content creation
    CASE 
        WHEN sl.language_code IN ('hi', 'en') THEN 'High'
        WHEN sl.language_code IN ('bn', 'ta', 'te') THEN 'Medium'
        ELSE 'Low'
    END as creation_priority
FROM service_languages sl
LEFT JOIN existing_content ec ON sl.service_key = ec.service_key 
    AND sl.language_code = ec.language_code
ORDER BY sl.service_name, creation_priority DESC, sl.language_name;

-- ============================================================================
-- DATA QUALITY DATA MART
-- ============================================================================

-- Source reliability dashboard
CREATE OR REPLACE VIEW dwh.dm_data_quality_sources AS
SELECT 
    ds.source_name,
    ds.source_type,
    ds.department,
    dd.year,
    dd.month,
    COUNT(*) as quality_checks,
    AVG(fdq.completeness_score) as avg_completeness,
    AVG(fdq.accuracy_score) as avg_accuracy,
    AVG(fdq.consistency_score) as avg_consistency,
    AVG(fdq.freshness_hours) as avg_freshness_hours,
    SUM(fdq.total_records) as total_records_processed,
    SUM(fdq.error_count) as total_errors,
    -- Overall quality score
    ROUND(
        (AVG(fdq.completeness_score) + AVG(fdq.accuracy_score) + AVG(fdq.consistency_score)) / 3 * 100, 2
    ) as overall_quality_score,
    -- Quality rating
    CASE 
        WHEN (AVG(fdq.completeness_score) + AVG(fdq.accuracy_score) + AVG(fdq.consistency_score)) / 3 >= 0.95 THEN 'Excellent'
        WHEN (AVG(fdq.completeness_score) + AVG(fdq.accuracy_score) + AVG(fdq.consistency_score)) / 3 >= 0.90 THEN 'Good'
        WHEN (AVG(fdq.completeness_score) + AVG(fdq.accuracy_score) + AVG(fdq.consistency_score)) / 3 >= 0.80 THEN 'Average'
        ELSE 'Poor'
    END as quality_rating
FROM dwh.fact_data_quality fdq
JOIN dwh.dim_source ds ON fdq.source_key = ds.source_key
JOIN dwh.dim_date dd ON fdq.date_key = dd.date_key
WHERE ds.is_active = TRUE
GROUP BY ds.source_name, ds.source_type, ds.department, dd.year, dd.month
ORDER BY dd.year DESC, dd.month DESC, overall_quality_score DESC;

-- Data freshness monitoring
CREATE OR REPLACE VIEW dwh.dm_data_freshness AS
SELECT 
    ds.source_name,
    dserv.service_name,
    dserv.service_category,
    dd.full_date,
    fdq.freshness_hours,
    fdq.lag_hours,
    fdq.total_records,
    fdq.new_records,
    -- Freshness status
    CASE 
        WHEN fdq.freshness_hours <= 6 THEN 'Fresh'
        WHEN fdq.freshness_hours <= 24 THEN 'Acceptable'
        WHEN fdq.freshness_hours <= 72 THEN 'Stale'
        ELSE 'Very Stale'
    END as freshness_status,
    -- SLA compliance
    CASE 
        WHEN ds.source_type = 'API' AND fdq.freshness_hours <= 2 THEN 'SLA Met'
        WHEN ds.source_type = 'Website' AND fdq.freshness_hours <= 24 THEN 'SLA Met'
        WHEN ds.source_type = 'Manual' AND fdq.freshness_hours <= 168 THEN 'SLA Met'
        ELSE 'SLA Missed'
    END as sla_compliance
FROM dwh.fact_data_quality fdq
JOIN dwh.dim_source ds ON fdq.source_key = ds.source_key
JOIN dwh.dim_service dserv ON fdq.service_key = dserv.service_key
JOIN dwh.dim_date dd ON fdq.date_key = dd.date_key
WHERE ds.is_active = TRUE 
AND dserv.is_active = TRUE 
AND dserv.is_current = TRUE
ORDER BY dd.full_date DESC, fdq.freshness_hours DESC;

-- ============================================================================
-- OPERATIONAL KPI DASHBOARD
-- ============================================================================

-- Daily operational summary
CREATE OR REPLACE VIEW dwh.dm_daily_operations AS
SELECT 
    dd.full_date,
    dd.day_name,
    dd.is_weekend,
    dd.is_holiday,
    COUNT(DISTINCT fsu.service_key) as active_services,
    SUM(fsu.query_count) as total_daily_queries,
    SUM(fsu.success_count) as total_daily_successes,
    AVG(fsu.satisfaction_score) as daily_avg_satisfaction,
    AVG(fsu.avg_response_time_ms) as daily_avg_response_time,
    COUNT(DISTINCT fsu.user_segment_key) as unique_user_segments,
    COUNT(DISTINCT fsu.location_key) as active_locations,
    -- Daily performance indicators
    ROUND(
        (SUM(fsu.success_count)::NUMERIC / SUM(fsu.query_count) * 100), 2
    ) as daily_success_rate,
    CASE 
        WHEN AVG(fsu.satisfaction_score) >= 4.0 THEN 'Excellent Day'
        WHEN AVG(fsu.satisfaction_score) >= 3.5 THEN 'Good Day'
        WHEN AVG(fsu.satisfaction_score) >= 3.0 THEN 'Average Day'
        ELSE 'Poor Day'
    END as day_performance_rating
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
GROUP BY dd.full_date, dd.day_name, dd.is_weekend, dd.is_holiday
ORDER BY dd.full_date DESC;

-- Top performing services
CREATE OR REPLACE VIEW dwh.dm_top_services AS
SELECT 
    ds.service_name,
    ds.service_category,
    ds.department,
    SUM(fsu.query_count) as total_queries,
    SUM(fsu.success_count) as total_successes,
    AVG(fsu.satisfaction_score) as avg_satisfaction,
    AVG(fsu.avg_response_time_ms) as avg_response_time,
    ROUND(
        (SUM(fsu.success_count)::NUMERIC / SUM(fsu.query_count) * 100), 2
    ) as success_rate,
    -- Ranking
    ROW_NUMBER() OVER (ORDER BY SUM(fsu.query_count) DESC) as usage_rank,
    ROW_NUMBER() OVER (ORDER BY AVG(fsu.satisfaction_score) DESC) as satisfaction_rank,
    ROW_NUMBER() OVER (ORDER BY SUM(fsu.success_count)::NUMERIC / SUM(fsu.query_count) DESC) as success_rate_rank
FROM dwh.fact_service_usage fsu
JOIN dwh.dim_service ds ON fsu.service_key = ds.service_key
WHERE ds.is_active = TRUE AND ds.is_current = TRUE
GROUP BY ds.service_key, ds.service_name, ds.service_category, ds.department
HAVING SUM(fsu.query_count) > 0
ORDER BY total_queries DESC;

-- Performance alerts
CREATE OR REPLACE VIEW dwh.dm_performance_alerts AS
WITH recent_performance AS (
    SELECT 
        ds.service_name,
        ds.service_category,
        AVG(fsu.satisfaction_score) as recent_satisfaction,
        AVG(fsu.avg_response_time_ms) as recent_response_time,
        ROUND(
            (SUM(fsu.success_count)::NUMERIC / SUM(fsu.query_count) * 100), 2
        ) as recent_success_rate
    FROM dwh.fact_service_usage fsu
    JOIN dwh.dim_service ds ON fsu.service_key = ds.service_key
    JOIN dwh.dim_date dd ON fsu.date_key = dd.date_key
    WHERE ds.is_active = TRUE 
    AND ds.is_current = TRUE
    AND dd.full_date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY ds.service_key, ds.service_name, ds.service_category
)
SELECT 
    service_name,
    service_category,
    recent_satisfaction,
    recent_response_time,
    recent_success_rate,
    -- Alert conditions
    CASE 
        WHEN recent_satisfaction < 3.0 THEN 'Low Satisfaction Alert'
        WHEN recent_response_time > 2000 THEN 'High Response Time Alert'
        WHEN recent_success_rate < 80 THEN 'Low Success Rate Alert'
        ELSE 'No Alert'
    END as alert_type,
    CASE 
        WHEN recent_satisfaction < 2.5 OR recent_response_time > 5000 OR recent_success_rate < 60 THEN 'Critical'
        WHEN recent_satisfaction < 3.0 OR recent_response_time > 2000 OR recent_success_rate < 80 THEN 'Warning'
        ELSE 'Normal'
    END as alert_severity
FROM recent_performance
WHERE recent_satisfaction < 3.0 
   OR recent_response_time > 2000 
   OR recent_success_rate < 80
ORDER BY 
    CASE 
        WHEN recent_satisfaction < 2.5 OR recent_response_time > 5000 OR recent_success_rate < 60 THEN 1
        ELSE 2
    END,
    recent_satisfaction ASC;

-- Grant permissions for analytics views
-- GRANT SELECT ON ALL TABLES IN SCHEMA dwh TO analyst_role;
-- GRANT USAGE ON SCHEMA dwh TO analyst_role;

-- Create indexes for better performance on analytics views
CREATE INDEX IF NOT EXISTS idx_fact_service_usage_analytics 
ON dwh.fact_service_usage(service_key, date_key, user_segment_key);

CREATE INDEX IF NOT EXISTS idx_fact_content_analytics_multilingual 
ON dwh.fact_content_analytics(service_key, language_key, date_key);

CREATE INDEX IF NOT EXISTS idx_fact_data_quality_monitoring 
ON dwh.fact_data_quality(source_key, date_key, completeness_score);