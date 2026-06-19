# MarketPulse AI

MarketPulse AI is an automated market intelligence and AI insight dashboard that turns market/news data into validated datasets, trend metrics, visual dashboards, and AI-assisted business insights.

## Problem

Market research often requires manually collecting scattered market signals, cleaning data, identifying trends, writing summaries, and checking sources. This process is slow, hard to reproduce, and difficult to evaluate.

## Solution

MarketPulse AI automates a professional market intelligence workflow. The platform collects RSS and Google News data, processes and validates it, generates analytics-ready JSON/CSV tables in a data mart, computes trend metrics, and serves them via a FastAPI backend to a professional Next.js web dashboard. It optionally leverages LLMs (Gemini API) to generate detailed business insights grounded in collected metrics, with rule-based fallbacks.

## Core Features

- **Automated Data Ingestion**: Robust RSS and search-based keyword ingestion with sample fallback data.
- **ETL & Data Quality**: Strict schema validation, cleaning, and quality flag reporting.
- **Analytics Data Mart**: Converts processed article data into analytics-ready CSV/JSON tables for KPI metrics, source quality analysis, trend metrics, and future dashboard/API consumption. SQLite or DuckDB may be considered later only if querying requirements become more complex.
- **Trend Detection & Metrics**: Mathematical and rule-based signal ranking.
- **FastAPI Analytics API**: High-performance REST API serving chart configurations and analytics data.
- **Professional Web BI Dashboard**: A data-driven UI rendering KPI cards, interactive charts, and insight cards.
- **AI Insight Generator**: Optional LLM-assisted (Gemini API) business insights with structured validations and rule-based fallbacks.
- **Evidence Explorer**: Grounding and citing source metrics/news for all generated insights (RAG).
- **Automation & Orchestration**: Streamlined pipelines and scheduler workflows.

## Architecture

```text
  [Data Ingestion (RSS)] 
            │
            ▼
  [ETL & Data Quality (Pydantic)] 
            │
            ▼
  [Analytics Data Mart (JSON/CSV)] ──► Optional CSV Export (Power BI Compatibility)
            │
            ▼
  [Trend Detection & Metrics]
            │
            ▼
  [FastAPI Analytics API]
            │
            ▼
  [Professional Web BI Dashboard (Next.js + Tailwind + shadcn/ui + Recharts)]
      ▲                      │
      │ (Grounding Metrics)  │ (User Request)
      │                      ▼
  [AI Insight Generator (Gemini / Rule-based Fallback)]
```

## Tech Stack

- **Backend / Analytics API**: Python, FastAPI, Pydantic
- **Frontend / BI UI**: Next.js, Tailwind CSS, shadcn/ui, Recharts / Apache ECharts
- **Data & Processing**: Feedparser, Pydantic (SQLite / DuckDB optional later)
- **Internal Skeleton**: Streamlit (minimal internal admin/skeleton interface only)
- **BI Compatibility**: Exportable CSVs for Power BI (optional export)
- **Testing & Quality**: pytest
- **LLM/AI Engine**: Gemini API (optional) or Rule-based Engine (fallback)

## Setup Commands

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

On Windows PowerShell:

```bash
Copy-Item .env.example .env
```

Do not commit `.env`.

## Run Commands

Run the Streamlit app:

```bash
streamlit run app/main.py
```

Run tests:

```bash
pytest
```

Run a quick smoke test:

```bash
pytest tests/test_smoke.py
```

## Project Status

## Modules & Status

| Module | Status | Description |
|---|---|---|
| **0. OS** | ✅ Complete | Repository setup, configuration, conventions |
| **1. Ingest** | ✅ Complete | RSS news collection, initial parsing, raw JSON storage |
| **2. ETL** | ✅ Complete | Data cleaning, standardizing, chunking, processing into structured JSON |
| **3. Analytics** | ✅ Complete | Data Mart generation, metrics extraction, source tracking (CSV/JSON outputs) |
| **4. Trends** | ✅ Complete | Rule-based trend scoring, momentum tracking, deterministic insight generation |
| **5. API** | ✅ Complete | FastAPI REST endpoints serving analytics, trends, and insight metrics |
| **6. Web UI** | ✅ Complete | Professional Next.js BI Dashboard displaying metrics and system status |
| **7. AI Layer** | ✅ Complete | RAG pipeline, semantic search, AI-powered business insight synthesis |
| **8. Evidence Layer** | ✅ Done | Evidence Explorer with source grounding and keyword mapping |
| **8B. RAG Layer** | ✅ Done | Lightweight lexical RAG with Rule-based / AI Router answering |
| **9. Evals & QA** | ✅ Complete | Deterministic Evaluation, Quality Gates, and Observability layer |

## Quick Start

### 1. Run Data Pipeline

```bash
# Ingest raw data
python -m src.collectors.run_ingestion

# Process ETL
python -m src.processing.run_etl

# Build Analytics & Trends Data Mart
python -m src.analytics.run_analytics
```

### 2. Run Backend API

```bash
uvicorn src.api.main:app --reload
# API runs at http://127.0.0.1:8000
# Swagger Docs at http://127.0.0.1:8000/docs
```

### 3. Run Web Dashboard

```bash
cd web
npm run dev
# Dashboard runs at http://localhost:3000
```
**Available Dashboard Pages:**
- `/` - Executive Overview: High-level KPIs and business summary
- `/trends` - Trend Intelligence: Market momentum and signal strength
- `/sources` - Source Reliability: Data quality rankings
- `/evidence` - Evidence Explorer: Grounding articles and keyword mapping
- `/insights` - Insight Brief: Deterministic signals and practical next steps
- `/system` - System Health: Pipeline status and freshness

### Running Data Ingestion

```bash
python -m src.collectors.run_ingestion
```

This will output a JSON file to `data/raw/` and a structured log entry to `logs/ingestion_runs.jsonl`.

### Running Data Processing (ETL)

```bash
python -m src.processing.run_etl
```

This command will find the latest raw ingestion JSON file (or use sample data), clean it, validate it against a schema, and remove duplicates.
It produces:
- A processed JSON file containing valid articles in `data/processed/`
- A data quality report in `data/processed/`
- A structured log entry in `logs/processing_runs.jsonl`

### Running Analytics Data Mart

```bash
python -m src.analytics.run_analytics
```

This command will find the latest processed article JSON file from `data/processed/` and convert the records into an analytics data mart. It creates future-ready CSV and JSON outputs for the FastAPI backend, the Next.js web dashboard, and optional Power BI compatibility.
It produces:
- Analytics CSV tables in `data/analytics/` (e.g., `articles_clean.csv`, `daily_keyword_metrics.csv`, `source_metrics.csv`, `quality_metrics.csv`, `insight_seed_metrics.csv`)
- A manifest file `data/analytics/analytics_manifest.json`
- A structured log entry in `logs/analytics_runs.jsonl`

### Running Trend Detection & Metrics

```bash
python -m src.intelligence.run_trends
```

This command will read the latest analytics data mart files, calculate trend metrics, rank the top trends, compute data freshness, and generate structured insight seeds.
It produces:
- Trend metrics and top trends CSVs in `data/trends/`
- A trend summary and manifest JSON in `data/trends/`
- A structured log entry in `logs/trend_runs.jsonl`

### Running FastAPI Analytics API

```bash
uvicorn src.api.main:app --reload
```

This command will launch the high-performance REST API backend built with FastAPI. It serves the trend metrics, chart configurations, article tables, and insight seeds.
Key Endpoints:
- `GET /api/v1/status`: API health and data freshness metrics.
- `GET /api/v1/metrics`: High-level KPI summary cards.
- `GET /api/v1/trends/top`: Top trends ranking with Bar Chart config.
- `GET /api/v1/trends/metrics`: Detailed time-series trend scores with Line Chart config.
- `GET /api/v1/sources`: Source quality metrics with Scatter Chart config.
- `GET /api/v1/articles`: Paginated table of clean articles with filters.
- `GET /api/v1/insights/seeds`: Raw insight seeds for dashboard and LLMs.
Visit `http://127.0.0.1:8000/docs` to see the full Swagger UI documentation.


