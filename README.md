# Prism

Public health intelligence dashboard. Indexes CDC and WHO epidemiological data through a RAG pipeline and exposes it through a natural-language query interface via the Claude API.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)]()
[![Next.js](https://img.shields.io/badge/Next.js-14+-black?logo=next.js)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)]()
[![GCP](https://img.shields.io/badge/Cloud-GCP-4285F4?logo=google-cloud&logoColor=white)]()

---

## Overview

CDC and WHO publish authoritative epidemiological data across dozens of endpoints in formats designed for specialists. Prism ingests that data, indexes it semantically, and makes it queryable in plain language — returning structured, AI-synthesised answers with supporting chart data and source attribution.

```
"What is the current flu activity level in Spain compared to last year?"
"Show me measles case trends in Europe for the past six months."
"Which regions are under active WHO health alerts right now?"
```

Queries are embedded, matched against a pgvector store, and passed to the Claude API with retrieved context. The response includes a synthesised explanation, chart-ready JSON, and full data provenance.

---

## Features

| Feature | Description |
|---|---|
| Natural language queries | Plain-language questions; intent resolved through semantic retrieval |
| RAG pipeline | pgvector semantic search over indexed CDC/WHO data |
| AI synthesis | Claude API produces structured responses from retrieved context |
| Chart data output | Every response includes structured JSON for Recharts |
| Live data ingestion | Automated ingestion from CDC and WHO public APIs on a rolling schedule |
| Source attribution | Every answer includes provenance: dataset, endpoint, fetch timestamp |
| Freemium tiers | Free tier via Haiku 4.5; premium tier uses Sonnet for complex reasoning |
| Response caching | Query-hash-keyed cache (4h TTL) with Anthropic prompt caching |

---

## Architecture

```
User Query
    |
    v
Next.js  ------>  FastAPI Backend  ------>  Cache Layer
Frontend          (Cloud Run)              (query hash, 4h TTL)
                        |
                        | cache miss
                        v
                  model_router.py
                  Haiku / Sonnet
                        |
           _____________|_____________
          |                           |
    pgvector                   CDC / WHO APIs
    Semantic Search            (BigQuery raw store)
          |
          | top-k chunks
          v
    Claude API (Anthropic)
    system_prompt + retrieved_context + query
    -> structured JSON: { text, chart_data }
          |
          v
    Recharts UI + Source Panel
```

### RAG Pipeline

1. **Ingestion** — CDC/WHO API responses are chunked, embedded, and stored in pgvector. Raw JSON is archived in BigQuery.
2. **Retrieval** — Incoming queries are embedded and matched via cosine similarity. Top-k chunks are returned.
3. **Generation** — Retrieved chunks and the query are passed to the Claude API. The system prompt enforces structured JSON output containing a synthesised explanation and chart-ready data arrays.
4. **Response** — The frontend renders the explanation and passes `chart_data` directly to Recharts.

Approximate token cost per free-tier query: ~1,550 input + ~400 output tokens via Haiku 4.5.

---

## Tech Stack

**Frontend** — Next.js 14 (TypeScript, App Router), Tailwind CSS, Recharts

**Backend** — Python 3.11, FastAPI, pgvector on PostgreSQL, SQLAlchemy + Alembic

**AI and Data** — Anthropic Claude API (Haiku 4.5 / Sonnet 4.6), BigQuery

**Infrastructure** — GCP Cloud Run, Docker, Terraform, GitHub Actions, GCP Artifact Registry

**Data Sources** — [CDC Public Health Data API](https://data.cdc.gov), [WHO Global Health Observatory API](https://www.who.int/data/gho)

---

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker
- GCP account with Cloud Run, BigQuery, and Artifact Registry enabled
- PostgreSQL 15+ with pgvector extension
- Anthropic API key

### Local Development

```bash
# Clone
git clone https://github.com/<your-username>/prism.git
cd prism

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set DATABASE_URL, ANTHROPIC_API_KEY, GCP credentials

alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd ../frontend
npm install
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL

npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Docker

```bash
docker compose up --build
```

### Infrastructure

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

---

## Project Structure

```
prism/
├── frontend/
│   ├── app/                  # App Router pages and layouts
│   ├── components/           # Reusable UI components
│   └── lib/                  # API client, types, utilities
│
├── backend/
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   ├── core/             # Config, security, dependencies
│   │   ├── models/           # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── rag/          # Retrieval pipeline
│   │   │   ├── ingestion/    # CDC/WHO data fetchers
│   │   │   └── model_router.py
│   │   └── main.py
│   └── alembic/
│
├── infrastructure/
│   └── terraform/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

## Configuration

### Backend `.env`

```env
DATABASE_URL=postgresql://user:password@localhost:5432/prism

ANTHROPIC_API_KEY=sk-ant-...

GCP_PROJECT_ID=your-project-id
BIGQUERY_DATASET=prism_raw

CACHE_TTL_SECONDS=14400

FREE_TIER_MODEL=claude-haiku-4-5
PREMIUM_TIER_MODEL=claude-sonnet-4-6
```

### Frontend `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Model Routing

`model_router.py` selects the Claude model based on query complexity and user tier. Haiku 4.5 handles standard RAG queries; Sonnet 4.6 is reserved for complex multi-step reasoning, cross-disease comparisons, and longitudinal trend analysis. Switching models requires a single environment variable change.

```python
def get_model(user_tier: str, query_complexity: str) -> str:
    if user_tier == "premium" and query_complexity == "complex":
        return settings.PREMIUM_TIER_MODEL
    return settings.FREE_TIER_MODEL
```

---

## Roadmap

### Phase 1 — Academic Submission (current)
- [x] Project architecture and repository setup
- [ ] Authentication (JWT, freemium tiers)
- [ ] Core dashboard — query interface and Recharts visualisations
- [ ] RAG pipeline — pgvector and Claude API
- [ ] CDC/WHO data ingestion workers
- [ ] GCP Cloud Run deployment via GitHub Actions

### Phase 2 — Post-Submission
- [ ] Redis caching layer
- [ ] DeepL API — multilingual queries and responses
- [ ] Stripe billing — premium tier activation
- [ ] PubMed integration — scientific citation layer
- [ ] Expanded data sources

### Phase 3 — Productisation
- [ ] PWA mobile experience
- [ ] Customisable dashboard templates
- [ ] Drag-and-drop layout builder
- [ ] Organisation-level accounts and team sharing
- [ ] Webhook and API access for enterprise integrations

---

## Contributing

1. Open an issue describing the change and its motivation.
2. Fork the repository and create a branch: `git checkout -b feat/your-feature`.
3. Write tests for new backend logic.
4. Ensure `pre-commit` hooks pass.
5. Submit a PR referencing the issue.

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## License

Apache License 2.0. See [LICENSE](LICENSE).

Apache 2.0 provides explicit patent protection and clear ownership retention. Commercial use is permitted; attribution is required.

---

Data sourced from [CDC Open Data](https://data.cdc.gov) and [WHO Global Health Observatory](https://www.who.int/data/gho).
AI synthesis via [Anthropic Claude API](https://www.anthropic.com).
Semantic search via [pgvector](https://github.com/pgvector/pgvector).
