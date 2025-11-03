# Models and RAG Information

This section details the LLM and embedding models, vector database configuration, and RAG pipeline specifics.

---

## 1. LLM, Embedding Models, Vector DB, and RAG Prompting

*   **LLM Name/Version:** The RAG pipeline is designed to work with an LLM, configurable via `LLM_PROVIDER` and `OPENAI_API_KEY` environment variables. The specific LLM is not hardcoded, allowing flexibility (OpenAI is a likely candidate).
*   **Embedding Model(s):**
    *   **Model Name:** `sentence-transformers` (default: `all-MiniLM-L6-v2`), configurable via `EMBEDDING_MODEL` environment variable.
    *   **Token Limit:** 256 word pieces.
    *   **Purpose:** Generates 384-dimensional vector embeddings for text content (documents, FAQs, user queries, content chunks).
*   **Vector DB Details:**
    *   **Database:** `pgvector` (PostgreSQL extension).
    *   **Schema/Dimensions:** Embeddings are stored in `VECTOR(384)` columns in `documents`, `faqs` (`question_embedding`, `answer_embedding`), and `content_chunks` tables.
    *   **Indexing:** `ivfflat` indexes are used for vector columns to optimize similarity search.
*   **RAG Prompt Templates/System Messages:** The `core/rag.py` `generate_response` method currently synthesizes a response by concatenating retrieved content parts and adding language information. Explicit prompt templates for external LLMs are not provided in the current implementation, as generative behavior is gated by `GENERATIVE_ENABLED`.

---

## 2. ASR/TTS Stack

*   There is no explicit ASR (Automatic Speech Recognition) or TTS (Text-to-Speech) stack currently implemented. Voice integration is mentioned as a future enhancement in the frontend roadmap.

---

## 3. Fine-tuning/LoRA and Tuning Approach

*   **Fine-tuning/LoRA Artifacts:** No explicit fine-tuning or LoRA artifacts are mentioned in the provided files.
*   **Prompting and Retrieval Tuning Approach:**
    *   **Retrieval Tuning:** Relies on semantic search using `pgvector` and `sentence-transformers` embeddings. The `SearchEngine` performs hybrid search across documents, FAQs, and content chunks.
    *   **Prompting:** The `core/rag.py` `generate_response` method synthesizes responses from retrieved contexts. Future LLM integration would involve constructing prompts with user queries and retrieved contexts.
