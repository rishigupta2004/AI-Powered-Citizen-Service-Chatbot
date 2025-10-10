-- Data Warehouse Validation Queries
-- ====================================
-- Run these queries in DBeaver or psql to validate your data warehouse
-- Usage: psql -d gov_chatbot_db -f scripts/validate_warehouse.sql

\echo '=============================================='
\echo 'DATA WAREHOUSE VALIDATION'
\echo '=============================================='

-- 1. Table Existence and Structure
\echo ''
\echo '1. TABLE STRUCTURE'
\echo '----------------------------------------------'

SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name IN ('services', 'procedures', 'documents', 'faqs', 'content_chunks', 'raw_content')
ORDER BY table_name, ordinal_position;

-- 2. Record Counts
\echo ''
\echo '2. RECORD COUNTS'
\echo '----------------------------------------------'

SELECT 'services' as table_name, COUNT(*) as count FROM services
UNION ALL
SELECT 'procedures', COUNT(*) FROM procedures
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'faqs', COUNT(*) FROM faqs
UNION ALL
SELECT 'content_chunks', COUNT(*) FROM content_chunks
UNION ALL
SELECT 'raw_content', COUNT(*) FROM raw_content
ORDER BY table_name;

-- 3. Services Overview
\echo ''
\echo '3. SERVICES OVERVIEW'
\echo '----------------------------------------------'

SELECT 
    service_id,
    name,
    category,
    ministry,
    is_active,
    array_length(languages_supported, 1) as num_languages,
    created_at
FROM services
ORDER BY service_id;

-- 4. Content Distribution
\echo ''
\echo '4. CONTENT DISTRIBUTION BY SERVICE'
\echo '----------------------------------------------'

SELECT 
    s.name as service_name,
    COUNT(DISTINCT p.procedure_id) as procedures,
    COUNT(DISTINCT d.doc_id) as documents,
    COUNT(DISTINCT f.faq_id) as faqs
FROM services s
LEFT JOIN procedures p ON s.service_id = p.service_id
LEFT JOIN documents d ON s.service_id = d.service_id
LEFT JOIN faqs f ON s.service_id = f.service_id
GROUP BY s.service_id, s.name
ORDER BY s.name;

-- 5. Raw Content by Source Type
\echo ''
\echo '5. RAW CONTENT BY SOURCE TYPE'
\echo '----------------------------------------------'

SELECT 
    source_type,
    COUNT(*) as count,
    SUM(CASE WHEN is_processed THEN 1 ELSE 0 END) as processed,
    SUM(CASE WHEN NOT is_processed THEN 1 ELSE 0 END) as unprocessed
FROM raw_content
GROUP BY source_type
ORDER BY count DESC;

-- 6. Content Chunks by Category
\echo ''
\echo '6. CONTENT CHUNKS BY CATEGORY'
\echo '----------------------------------------------'

SELECT 
    category,
    COUNT(*) as chunks,
    COUNT(embedding) as with_embeddings,
    COUNT(*) - COUNT(embedding) as without_embeddings
FROM content_chunks
GROUP BY category
ORDER BY chunks DESC;

-- 7. Document Processing Status
\echo ''
\echo '7. DOCUMENT PROCESSING STATUS'
\echo '----------------------------------------------'

SELECT 
    is_processed,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM documents
GROUP BY is_processed;

-- 8. Language Distribution
\echo ''
\echo '8. LANGUAGE DISTRIBUTION'
\echo '----------------------------------------------'

SELECT 
    language,
    COUNT(*) as count
FROM (
    SELECT language FROM procedures
    UNION ALL
    SELECT language FROM documents
    UNION ALL
    SELECT language FROM faqs
) combined
GROUP BY language
ORDER BY count DESC;

-- 9. Table Sizes
\echo ''
\echo '9. TABLE SIZES'
\echo '----------------------------------------------'

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) as bytes
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('services', 'procedures', 'documents', 'faqs', 'content_chunks', 'raw_content')
ORDER BY bytes DESC;

-- 10. Index Information
\echo ''
\echo '10. INDEXES'
\echo '----------------------------------------------'

SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('services', 'procedures', 'documents', 'faqs', 'content_chunks', 'raw_content')
ORDER BY tablename, indexname;

-- 11. Sample Data from Each Table
\echo ''
\echo '11. SAMPLE DATA'
\echo '----------------------------------------------'

\echo 'Sample Services:'
SELECT service_id, name, category FROM services LIMIT 3;

\echo ''
\echo 'Sample Documents:'
SELECT doc_id, name, document_type, is_processed FROM documents LIMIT 3;

\echo ''
\echo 'Sample Raw Content:'
SELECT content_id, source_type, source_name, processing_status FROM raw_content LIMIT 3;

\echo ''
\echo '=============================================='
\echo 'VALIDATION COMPLETE'
\echo '=============================================='

