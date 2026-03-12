-- RAG/Search optimization SQL for PostgreSQL + pgvector
-- Run manually on the target database.

CREATE EXTENSION IF NOT EXISTS vector;

-- Full-text indexes used by repository search_text fallbacks.
CREATE INDEX IF NOT EXISTS idx_documents_fts
ON documents
USING gin (to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '') || ' ' || coalesce(raw_content, '')));

CREATE INDEX IF NOT EXISTS idx_faqs_fts
ON faqs
USING gin (to_tsvector('english', coalesce(question, '') || ' ' || coalesce(answer, '')));

CREATE INDEX IF NOT EXISTS idx_chunks_fts
ON content_chunks
USING gin (to_tsvector('english', coalesce(chunk_text, '')));

-- Fast service filters.
CREATE INDEX IF NOT EXISTS idx_documents_service_id ON documents(service_id);
CREATE INDEX IF NOT EXISTS idx_faqs_service_id ON faqs(service_id);
CREATE INDEX IF NOT EXISTS idx_chunks_service_id ON content_chunks(service_id);

-- Vector indexes (cosine); adjust lists based on row count.
CREATE INDEX IF NOT EXISTS idx_documents_embedding_ivfflat
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_faq_question_embedding_ivfflat
ON faqs USING ivfflat (question_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding_ivfflat
ON content_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 200);

ANALYZE documents;
ANALYZE faqs;
ANALYZE content_chunks;
