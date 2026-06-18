# MarketPulse AI Implementation Roadmap

This document maps out the modules, inputs, outputs, file conventions, and definitions of done for each phase of the MarketPulse AI development cycle.

---

## Status Overview

- **Module 0**: Project Operating System — **Done** ✅
- **Module 1**: Data Ingestion — **Done** ✅
- **Module 2**: ETL & Data Quality — **Done** ✅
- **Module 3**: Analytics Data Mart — **Done** ✅
- **Module 4**: Trend Detection & Insight Metrics — **Done** ✅
- **Module 5**: FastAPI Analytics API — **Next Up** ──►
- **Module 6**: Professional Web BI Dashboard — **Planned**
- **Module 7**: AI Insight Generator with Gemini/Fallback — **Planned**
- **Module 8**: Evidence Explorer / RAG with Citations — **Planned**
- **Module 9**: Evaluation & Observability — **Planned**
- **Module 10**: Automation with Prefect/n8n — **Planned**
- **Module 11**: Human Review & Report Delivery — **Planned**
- **Module 12**: CI/CD & Portfolio Packaging — **Planned**

---

## Completed Modules

### Module 0 — Project Operating System ✅
- **Goal**: Set up workspace, dependencies, standard folder layout, code validation scripts, and initial Streamlit entrypoint.
- **Input**: Requirements documentation.
- **Output**: Core project structure, `.gitignore`, `.env.example`, `requirements.txt`, basic tests.

### Module 1 — Data Ingestion ✅
- **Goal**: Create RSS ingestion pipeline targeting keyword-specific Google News search URLs, with stable ID hashing and sample offline backup.
- **Input**: RSS feeds and user keyword parameters.
- **Output**: Raw article entries stored as JSONs in `data/raw/` with deterministic IDs.

### Module 2 — ETL & Data Quality ✅
- **Goal**: Build cleaning and verification flow checking incoming schemas using Pydantic, tag missing/bad keys without losing records, and deduplicate articles.
- **Input**: Ingested raw files from `data/raw/`.
- **Output**: Cleaned JSON article files and data validation quality reports in `data/processed/`.

---

## Planned Modules

### Module 3 — Analytics Data Mart
- **Goal**: Module 3 — Analytics Data Mart converts processed article data into analytics-ready CSV/JSON tables for KPI metrics, source quality analysis, trend metrics, and future dashboard/API consumption. SQLite or DuckDB may be considered later only if querying requirements become more complex.
- **Input**: Cleaned, deduplicated, and validated JSON article records from `data/processed/`.
- **Output**: Analytics-ready CSV/JSON tables/files in `data/analytics/` and `data/exports/` (for Power BI compatibility). SQLite/DuckDB schemas are optional and may be considered later.
- **Likely files/folders**:
  - `src/analytics/datamart.py` (data mart logic)
  - `src/analytics/run_datamart.py` (orchestrator CLI)
  - `tests/test_datamart.py` (unit/integration tests)
  - `data/analytics/` (analytics storage)
  - `data/exports/` (Power BI CSV outputs)
- **Definition of Done**:
  - Data from `data/processed/` is successfully converted into analytics-ready CSV and JSON tables.
  - CSV files for Power BI are automatically exported to `data/exports/` and verified.
  - Tests verify that duplicate or schema-invalid items do not pollute the data mart.
- **What not to do**: Do not add FastAPI endpoints, trend scores, or LLM integrations yet. Do not build database servers or enforce SQLite/DuckDB requirements at this stage.

### Module 4 — Trend Detection & Insight Metrics
- **Goal**: Analyze the Analytics Data Mart to calculate keywords frequency, relevance, and trend signals (momentum, velocity, keyword co-occurrence) to yield mathematical and rule-based insights.
- **Input**: Data mart tables/files from `data/analytics/`.
- **Output**: Trend metrics records containing computed scores, top keywords, and signal indicators in `data/trends/` or data mart tables.
- **Likely files/folders**:
  - `src/analytics/trends.py` (trend detection logic)
  - `src/analytics/run_trends.py` (CLIs for trend detection)
  - `tests/test_trends.py` (unit tests verifying math/heuristics)
- **Definition of Done**:
  - Mathematical scores (e.g. TF-IDF, change rate, trend momentum) are computed deterministically.
  - Trend records are saved and schema-validated.
- **What not to do**: Do not run LLMs or call Gemini API. Do not write API endpoints or build frontend code.

### Module 5 — FastAPI Analytics API
- **Goal**: Build a high-performance REST API backend using FastAPI to serve trend metrics, chart configurations, article tables, and insight summaries.
- **Input**: Trend metrics and article data from `data/trends/` and `data/analytics/`.
- **Output**: JSON REST API responses matching structure requirements for the BI Dashboard (providing both data and chart/card configurations).
- **Likely files/folders**:
  - `src/api/main.py` (FastAPI app)
  - `src/api/routes/` (endpoints for trends, metrics, config)
  - `src/api/schemas.py` (request/response models)
  - `tests/test_api.py` (API endpoints tests using `TestClient`)
- **Definition of Done**:
  - FastAPI server starts successfully and exposes endpoints like `/api/v1/metrics`, `/api/v1/charts`, `/api/v1/trends`.
  - API returns correct JSON schemas containing chart-friendly structures.
- **What not to do**: Do not write Next.js or Tailwind code. Do not implement direct LLM calls in API routes.

### Module 6 — Professional Web BI Dashboard
- **Goal**: Implement a professional web-based BI UI using Next.js, Tailwind, shadcn/ui, and Recharts to render the dashboard dynamically.
- **Input**: FastAPI API responses from backend.
- **Output**: Modern, interactive single-page BI dashboard showing charts, KPI cards, tables, and insight panels.
- **Likely files/folders**:
  - `web/` (Next.js frontend project directory)
  - `web/src/app/` (Next.js routing, components, and hooks)
  - `web/src/components/ui/` (shadcn components)
  - `web/src/components/charts/` (Recharts wrappers)
- **Definition of Done**:
  - Frontend runs locally with `npm run dev` and renders a dashboard with responsive layout.
  - The UI is fully data-driven, retrieving chart configs and data solely from the FastAPI backend.
  - Zero placeholder UI elements.
- **What not to do**: Do not call the Gemini API or LLMs directly from frontend. Do not write local mock JSONs on the frontend if the API is missing.

### Module 7 — AI Insight Generator with Gemini/Fallback
- **Goal**: Generate AI business insights from trend metrics and news content, falling back gracefully to rule-based heuristics if `GEMINI_API_KEY` is not present.
- **Input**: Analytics trend data and news summaries.
- **Output**: Structured, schema-validated JSON insights (e.g., summary, impact score, recommendations, cited sources).
- **Likely files/folders**:
  - `src/insights/generator.py` (LLM prompt/rule-based logic)
  - `src/insights/schemas.py` (Pydantic schemas for structured insight)
  - `src/insights/run_insights.py` (CLI or orchestrator)
  - `tests/test_insights.py` (tests for rules and mock LLM calls)
- **Definition of Done**:
  - Generates insights using Gemini when API key is provided, validated via Pydantic.
  - Generates sensible rule-based insights when API key is absent.
- **What not to do**: Do not write free-form, unvalidated LLM calls. Do not bypass the FastAPI backend (integrate this logic in backend API endpoints).

### Module 8 — Evidence Explorer / RAG with Citations
- **Goal**: Build a Retrieval-Augmented Generation (RAG) system with a citations explorer to ensure every AI insight is grounded in source articles and raw statistics.
- **Input**: Data mart articles and AI generated insights.
- **Output**: Grounding maps and search indexes, plus frontend elements showing citations (links to source articles and exact statistics).
- **Likely files/folders**:
  - `src/rag/indexer.py` (indexing, optional embeddings)
  - `src/rag/search.py` (citation verification search)
  - `tests/test_rag.py` (verifying citation accuracy)
- **Definition of Done**:
  - Insights are enriched with verifiable evidence references.
  - The UI allows clicking a citation to highlight the source news metadata.
- **What not to do**: Do not call LLMs without attaching the exact evidence context. Do not link to non-existent article hashes.

### Module 9 — Evaluation & Observability
- **Goal**: Evaluate LLM outputs for correctness, grounding, and toxicity, and integrate structured logging/tracing for monitoring.
- **Input**: RAG prompts, generated insights, and gold-standard evaluation datasets.
- **Output**: Evaluation reports, latency dashboards, and structured tracing logs.
- **Likely files/folders**:
  - `src/eval/evaluator.py` (evaluation tests)
  - `src/observability/tracing.py` (OpenTelemetry/LangSmith/Langfuse hooks)
  - `tests/test_eval.py`
- **Definition of Done**:
  - Automated evaluation runs can measure accuracy and grounding metrics.
  - System performance (latency, token usage) is monitored and logged.
- **What not to do**: Do not use slow blocking libraries that impact API latency.

### Module 10 — Automation with Prefect/n8n
- **Goal**: Schedule and automate the data collection, ETL, analytics, and insight pipelines.
- **Input**: Configuration files and run triggers.
- **Output**: Chronologically scheduled runs and automated alerts on pipeline failures.
- **Likely files/folders**:
  - `src/automation/flows.py` (Prefect flows or n8n workflow JSONs)
  - `src/automation/scheduler.py` (lightweight cron/schedule runner)
- **Definition of Done**:
  - Scheduled run automatically executes ingestion -> ETL -> datamart -> insights.
  - Failure notifications are triggered when data quality bars fall.
- **What not to do**: Do not hardcode execution schedules in Python files directly; keep it configurable.

### Module 11 — Human Review & Report Delivery
- **Goal**: Implement a mechanism for humans to review, modify, or approve AI insights before they are sent to downstream channels (email, Slack, Webhooks, PDF export).
- **Input**: Draft insights from Module 7/8.
- **Output**: Approved insights ready for distribution, and generated reports (e.g., PDF or formatted HTML).
- **Likely files/folders**:
  - `src/delivery/notifier.py` (Slack/Email integration)
  - `src/delivery/pdf_generator.py` (Report compilation)
  - `web/src/app/admin/` (Next.js admin review route)
- **Definition of Done**:
  - Interface allows updating insight text, adding human notes, and marking as "Approved".
  - Approved reports are delivered successfully to external targets.
- **What not to do**: Do not deliver unapproved insights automatically if human-in-the-loop is enabled in configs.

### Module 12 — CI/CD & Portfolio Packaging
- **Goal**: Package the entire system for production readiness, including Dockerization, CI/CD testing, and portfolio-ready presentation (README updates, screenshots, online demo setups).
- **Input**: Fully functional backend, frontend, and pipelines.
- **Output**: `Dockerfile`, Docker Compose setups, GitHub Action workflows, and a polished deployment.
- **Likely files/folders**:
  - `Dockerfile` (backend and frontend containerization)
  - `docker-compose.yml`
  - `.github/workflows/` (CI/CD setup)
- **Definition of Done**:
  - The application builds and starts successfully with a single `docker-compose up` command.
  - Continuous integration workflows successfully run tests on all modules.
- **What not to do**: Do not expose sensitive credentials in Docker files or GitHub action configs.
