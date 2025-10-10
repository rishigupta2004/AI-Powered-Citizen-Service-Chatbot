-- Phase 4 Warehouse Inspection (DBeaver/SQL Client)
-- This script displays structure and content for key warehouse tables.
-- Compatible with PostgreSQL.

-- Show server version
SELECT version();

-- List tables in public schema relevant to Phase 4
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('services','procedures','documents','faqs','content_chunks','raw_content')
ORDER BY table_name;

-- Columns per table
-- Change :tbl parameter manually in DBeaver or run blocks per table
-- SERVICES
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'services'
ORDER BY ordinal_position;

-- PROCEDURES
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'procedures'
ORDER BY ordinal_position;

-- DOCUMENTS
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'documents'
ORDER BY ordinal_position;

-- FAQS
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'faqs'
ORDER BY ordinal_position;

-- CONTENT_CHUNKS
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'content_chunks'
ORDER BY ordinal_position;

-- RAW_CONTENT
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'raw_content'
ORDER BY ordinal_position;

-- Indexes per table
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('services','procedures','documents','faqs','content_chunks','raw_content')
ORDER BY tablename, indexname;

-- Row counts
SELECT 'services' AS table, COUNT(*) FROM services UNION ALL
SELECT 'procedures' AS table, COUNT(*) FROM procedures UNION ALL
SELECT 'documents'  AS table, COUNT(*) FROM documents UNION ALL
SELECT 'faqs'       AS table, COUNT(*) FROM faqs UNION ALL
SELECT 'content_chunks' AS table, COUNT(*) FROM content_chunks UNION ALL
SELECT 'raw_content'    AS table, COUNT(*) FROM raw_content;

-- Sample rows (adjust LIMITs as needed)
-- SERVICES
SELECT * FROM services ORDER BY service_id DESC LIMIT 10;

-- PROCEDURES
SELECT * FROM procedures ORDER BY procedure_id DESC LIMIT 10;

-- DOCUMENTS
SELECT doc_id, service_id, procedure_id, name, language, is_processed, created_at
FROM documents
ORDER BY doc_id DESC LIMIT 10;

-- FAQS
SELECT faq_id, service_id, question, language, created_at
FROM faqs
ORDER BY faq_id DESC LIMIT 10;

-- CONTENT_CHUNKS
SELECT chunk_id, service_id, category, created_at, LEFT(content_text, 300) AS preview
FROM content_chunks
ORDER BY chunk_id DESC LIMIT 10;

-- RAW_CONTENT
SELECT content_id, source_type, source_name, language, created_at, LEFT(content, 300) AS preview
FROM raw_content
ORDER BY content_id DESC LIMIT 10;