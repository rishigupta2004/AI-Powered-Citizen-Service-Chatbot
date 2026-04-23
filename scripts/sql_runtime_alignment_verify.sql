-- Verification SQL after running scripts/sql_runtime_alignment.sql

-- Verify content_chunks columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'content_chunks'
ORDER BY ordinal_position;

-- Expected content_chunks shape for app runtime
SELECT
    ARRAY_AGG(column_name ORDER BY column_name) AS present_columns
FROM information_schema.columns
WHERE table_name = 'content_chunks'
  AND column_name IN (
    'chunk_id', 'uuid', 'content_id', 'service_id',
    'chunk_text', 'chunk_index', 'chunk_type', 'metadata', 'created_at'
  );

-- Verify authmethod enum values
SELECT enumlabel
FROM pg_enum
JOIN pg_type ON pg_enum.enumtypid = pg_type.oid
WHERE pg_type.typname = 'authmethod'
ORDER BY enumsortorder;
