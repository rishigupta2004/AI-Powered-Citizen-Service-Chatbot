-- Migrate pgvector columns from 384 to 1024 dimensions.
-- Safe approach: clear existing embeddings, alter type, recreate vector indexes.

BEGIN;

DROP INDEX IF EXISTS idx_documents_embedding_ivfflat;
DROP INDEX IF EXISTS idx_faq_question_embedding_ivfflat;
DROP INDEX IF EXISTS idx_chunks_embedding_ivfflat;

UPDATE documents SET embedding = NULL WHERE embedding IS NOT NULL;
UPDATE faqs SET question_embedding = NULL WHERE question_embedding IS NOT NULL;
UPDATE faqs SET answer_embedding = NULL WHERE answer_embedding IS NOT NULL;
UPDATE content_chunks SET embedding = NULL WHERE embedding IS NOT NULL;

ALTER TABLE documents
    ALTER COLUMN embedding TYPE vector(1024);

ALTER TABLE faqs
    ALTER COLUMN question_embedding TYPE vector(1024),
    ALTER COLUMN answer_embedding TYPE vector(1024);

ALTER TABLE content_chunks
    ALTER COLUMN embedding TYPE vector(1024);

COMMIT;

CREATE INDEX IF NOT EXISTS idx_documents_embedding_ivfflat
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100)
WHERE embedding IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_faq_question_embedding_ivfflat
ON faqs USING ivfflat (question_embedding vector_cosine_ops)
WITH (lists = 100)
WHERE question_embedding IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_chunks_embedding_ivfflat
ON content_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 200)
WHERE embedding IS NOT NULL;

ANALYZE documents;
ANALYZE faqs;
ANALYZE content_chunks;
