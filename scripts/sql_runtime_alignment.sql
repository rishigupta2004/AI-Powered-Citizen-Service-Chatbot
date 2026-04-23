-- Runtime alignment SQL (manual execution)
-- Run against your target database (for example citizen_services_dev).
-- Do NOT wrap in an explicit transaction for maximum PostgreSQL compatibility.

-- 1) Align content_chunks column name with ORM
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'content_chunks' AND column_name = 'category'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'content_chunks' AND column_name = 'chunk_type'
    )
    THEN
        ALTER TABLE content_chunks RENAME COLUMN category TO chunk_type;
    END IF;
END $$;

ALTER TABLE content_chunks ADD COLUMN IF NOT EXISTS content_id INTEGER;
ALTER TABLE content_chunks ADD COLUMN IF NOT EXISTS chunk_index INTEGER;
ALTER TABLE content_chunks ADD COLUMN IF NOT EXISTS chunk_type VARCHAR(100);
ALTER TABLE content_chunks ADD COLUMN IF NOT EXISTS metadata JSONB;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints tc
        WHERE tc.table_name = 'content_chunks'
          AND tc.constraint_name = 'content_chunks_content_id_fkey'
    ) THEN
        ALTER TABLE content_chunks
            ADD CONSTRAINT content_chunks_content_id_fkey
            FOREIGN KEY (content_id) REFERENCES raw_content(content_id)
            ON DELETE CASCADE;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        -- raw_content table missing in this DB: skip FK creation.
        NULL;
END $$;

DROP INDEX IF EXISTS idx_chunks_category;
CREATE INDEX IF NOT EXISTS idx_chunks_type ON content_chunks(chunk_type);

-- 2) Align authmethod enum values with application enum
ALTER TYPE authmethod ADD VALUE IF NOT EXISTS 'clerk';
ALTER TYPE authmethod ADD VALUE IF NOT EXISTS 'clerk_google';
ALTER TYPE authmethod ADD VALUE IF NOT EXISTS 'clerk_phone';
