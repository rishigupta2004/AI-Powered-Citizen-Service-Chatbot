<!-- Replace the live URL below with your actual production domain before publishing -->
# Seva Sindhu — AI-Powered Citizen Services Portal

![Seva Sindhu banner](artifacts/seva-sindhu-banner.png)

Seva Sindhu is a production-grade citizen services portal backed by a data warehouse and AI search stack. This repository contains:

- Backend: FastAPI, PostgreSQL, vector search (embeddings + RAG)
- Frontend: React (Vite) with an accessible UI, service explorer, step-by-step flows and an advanced context-aware chatbot
- Data pipelines and scripts for ingestion, PDF processing and quality checks

Production:  https://seva-sindu-portal-odh4v1o3v-rishiguptarg007-gmailcoms-projects.vercel.app 

![CI](https://img.shields.io/badge/CI--%20tests-passing-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue) ![Frontend](https://img.shields.io/badge/frontend-Vite%20%2B%20React-ff69b4)

---

## 🚀 Quick Start

### 1. Backend Setup
```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://username:password@localhost/gov_chatbot_db"
# Seva Sindhu — AI-Powered Citizen Services Portal

![Seva Sindhu Banner](artifacts/seva-sindhu-banner.png)

Professional, production-grade portal and data warehouse that helps citizens discover and complete government services. This repository contains the backend data warehouse (FastAPI + PostgreSQL + vector search/RAG) and the frontend Seva Sindhu portal (React + Tailwind) with an advanced AI assistant.

Live site:  https://seva-sindu-portal-odh4v1o3v-rishiguptarg007-gmailcoms-projects.vercel.app  (deployed)

Status: Production (deployed) • Latest release: main

Badges: [![CI](https://img.shields.io/badge/ci-pending-lightgrey)](https://github.com/rishigupta2004/AI-Powered-Citizen-Service-Chatbot/actions) [![License](https://img.shields.io/badge/license-MIT-brightgreen)](./LICENSE)

---

## Table of contents

- Overview
- Quick start
- Production deployment & verification
- Environment variables
- API examples
- Architecture & infra notes
- Development, testing & CI
- Security & secrets
- Contributing & PR checklist
- License & contact

---

## Quick start

Minimal steps to get both backend and frontend running locally (zsh):

Backend (development)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://username:password@localhost/gov_chatbot_db"
python init_db.py
uvicorn app:app --reload
```

Frontend (development)

```bash
cd frontend
npm ci
npm run dev
# open http://localhost:5173
```

Run backend tests

```bash
pytest -q
```

---

## Production deployment & verification

We ship the backend as a container and serve the frontend as a static site. Example verification after deployment:

1. Endpoint health

```bash
curl -fsS https://seva-sindhu.example.gov/health | jq
```

2. Search smoke test

```bash
curl -sS -X POST "https://seva-sindhu.example.gov/search" \
	-H "Content-Type: application/json" \
	-d '{"query":"apply passport", "top_k":5}' | jq
```

3. Frontend / Chatbot

- Open the production URL and confirm the chatbot welcome message appears and quick-actions are rendered.

4. Database & backups

- Confirm automated backups are running and WAL/archive retention is configured for Postgres.

5. Monitoring

- Check application logs, uptime monitors, and basic metrics (response times, error rates).

---

## Environment variables (recommended)

Use a secret manager, or a `.env` for local development. Replace values before deploying.

| Name | Example | Purpose |
|---|---|---|
| DATABASE_URL | postgresql://user:pass@db:5432/seva | Primary Postgres connection |
| EMBEDDING_MODEL | all-MiniLM-L6-v2 | Sentence transformer model for embeddings |
| LLM_PROVIDER | OPENAI | Optional LLM provider for RAG generation |
| OPENAI_API_KEY | sk-... | API key for LLM provider |
| REDIS_URL | redis://redis:6379/0 | Optional cache/session store |
| SECRET_KEY | changeme | App secret for signing tokens/csrf |

Security: Never commit secrets to Git.

---

## API examples

Health

```bash
curl -sS https://seva-sindhu.example.gov/health | jq
```

Search

```bash
curl -sS -X POST https://seva-sindhu.example.gov/search \
	-H "Content-Type: application/json" \
	-d '{"query":"how to apply for passport", "top_k":5}' | jq
```

Get services

```bash
curl -sS https://seva-sindhu.example.gov/services | jq
```

Process a document (admin)

```bash
curl -sS -X POST https://seva-sindhu.example.gov/process-document \
	-H "Content-Type: application/json" \
	-d '{"file_path":"/data/docs/passport/form.pdf","service_id":1}' | jq
```

---

## Architecture & infra notes

Simple ASCII overview:

```
	[Frontend] -- HTTPS --> [Load Balancer] --> [Backend (FastAPI)] --> Postgres
																		|                        
																		+--> Vector Store (Redis/Milvus/Pinecone)
																		+--> Object Storage (S3)
```

- Scale vectors using a managed vector DB for production workloads.
- Store large PDFs in object storage and only keep processed chunks in the DB.

---

## Development, testing & CI

- Backend: pytest, Black/isort, flake8
- Frontend: Vite, TypeScript, Tailwind, optional Vitest for unit tests
- CI recommendation: GitHub Actions to run tests, build frontend, and publish artifacts.

PR checklist (add to PR template):

1. Tests added/updated
2. Linting passes (pre-commit hooks)
3. Database migrations included (if needed)
4. Security review for credentials/secrets

---

## Security & secrets

- Use a secrets manager (AWS Secrets Manager, GCP Secret Manager) in prod.
- Rotate API keys regularly and enforce least-privilege for service accounts.
- Ensure CORS and rate-limiting are configured for public endpoints.

---

## Contributing & PR checklist

We love contributions. Please:

1. Fork and create a feature branch.
2. Run tests locally and include new tests for bugfixes/features.
3. Follow the code style rules (pre-commit hooks are recommended).
4. Provide a clear PR description with screenshots and testing notes.

Minimal PR template (copy to .github/PULL_REQUEST_TEMPLATE.md):

```
Summary of changes

Why

How was this tested

Checklist
- [ ] Tests added/updated
- [ ] Linting passed
- [ ] Documentation updated
```

---

## License

MIT — see `LICENSE`

---

## Maintainers & contact

Maintainer: Rishi Gupta — rishi@example.com

If you've deployed the site, please update the Production URL and add any deployment badges (Vercel/Netlify/DockerHub) and screenshots to `artifacts/` so we can display them here.

---

Would you like me to:

1. Add an example `docker-compose.yml` and a minimal `deploy/` folder (recommended)
2. Create a GitHub Actions workflow that runs tests and builds the frontend
3. Add a simple `.github/PULL_REQUEST_TEMPLATE.md` and `.github/ISSUE_TEMPLATE.md`

Tell me which item (1/2/3) you want next and I'll create it.