# MarketPulse AI Tasks & Roadmap

## Completed Modules

### Module 0 — Project Operating System ✅
- [x] Establish directory structures and standard folders.
- [x] Configure dependencies (`requirements.txt`, `pyproject.toml`).
- [x] Write environment template (`.env.example`) and setup `.gitignore`.
- [x] Build minimal Streamlit skeleton (`app/main.py`).
- [x] Implement smoke import tests (`tests/test_smoke.py`).

### Module 1 — Data Ingestion ✅
- [x] Choose Google News RSS feed parser as initial data source.
- [x] Implement robust keyword feed parser collector (`src/collectors/run_ingestion.py`).
- [x] Add offline/no-network sample fallback mechanism (`data/sample/sample_articles.json`).
- [x] Save raw records as JSON in `data/raw/` with stable SHA-256 hashes as IDs.
- [x] Write collection unit tests with mock network scenarios.

### Module 2 — ETL & Data Quality ✅
- [x] Define Pydantic models for raw and processed article data (`src/processing/models.py`).
- [x] Implement ETL pipeline for cleaning text, formatting dates, and deduplicating (`src/processing/etl.py`).
- [x] Build data quality reporting tool that logs quality flags (`missing_title`, `invalid_url`) instead of silent drops.
- [x] Orchestrate pipeline execution script (`src/processing/run_etl.py`).
- [x] Run test suite to verify ETL processing.

---

## Upcoming Roadmap (Modules 3 - 12)

### Module 3 — Analytics Data Mart ✅
- **Goal**: Module 3 — Analytics Data Mart converts processed article data into analytics-ready CSV/JSON tables for KPI metrics, source quality analysis, trend metrics, and future dashboard/API consumption. SQLite or DuckDB may be considered later only if querying requirements become more complex.
- **Input**: Cleaned, deduplicated, and validated JSON article records from `data/processed/`.
- **Output**: Analytics-ready CSV/JSON tables/files in `data/analytics/`. Power BI compatibility is satisfied by these CSV files directly without a separate exports directory.
- **Likely files/folders**:
  - `src/analytics/metrics.py` (data mart logic)
  - `src/analytics/run_analytics.py` (orchestrator CLI)
  - `tests/test_analytics.py` (unit/integration tests)
  - `data/analytics/` (analytics storage)
- **Definition of Done**:
  - Data from `data/processed/` is successfully converted into analytics-ready CSV and JSON tables.
  - CSV files for Power BI are automatically exported and verified in `data/analytics/`.
  - Tests verify that duplicate or schema-invalid items do not pollute the data mart.
- **What not to do**: Do not add FastAPI endpoints, trend scores, or LLM integrations yet. Do not build database servers or enforce SQLite/DuckDB requirements at this stage.
- [x] Create aggregation schemas for CSV/JSON tables.
- [x] Implement data mart CLI runner.
- [x] Implement optional CSV export logic for Power BI compatibility (via `data/analytics/`).
- [x] Write data mart integration tests.

### Module 4 — Trend Detection & Insight Metrics ✅
- **Goal**: Analyze the Analytics Data Mart to calculate keywords frequency, relevance, and trend signals (momentum, velocity, keyword co-occurrence) to yield mathematical and rule-based insights.
- **Input**: Data mart tables/files from `data/analytics/`.
- **Output**: Trend metrics records containing computed scores, top keywords, and signal indicators in `data/trends/` or data mart tables.
- **Likely files/folders**:
  - `src/intelligence/trend_scoring.py` (trend detection logic)
  - `src/intelligence/run_trends.py` (CLIs for trend detection)
  - `tests/test_trends.py` (unit tests verifying math/heuristics)
- **Definition of Done**:
  - Mathematical scores (e.g. TF-IDF, change rate, trend momentum) are computed deterministically.
  - Trend records are saved and schema-validated.
- **What not to do**: Do not run LLMs or call Gemini API. Do not write API endpoints or build frontend code.
- [x] Code trend calculation formulas and scoring logic.
- [x] Build script to extract top keywords and cluster co-occurring terms.
- [x] Create unit tests validating trend detection scores.

### Module 5 — FastAPI Analytics API ✅
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
- [x] Set up FastAPI project boilerplate and API routers.
- [x] Define dynamic response schemas that bundle data + chart visual configurations.
- [x] Write integration tests for API endpoints using FastAPI `TestClient`.

### Module 6 — Professional Web BI Dashboard ✅
- **Goal**: Implement a professional, multi-page BI storytelling console using Next.js, Tailwind, shadcn/ui, and Recharts.
- **Input**: FastAPI API responses from backend.
- **Output**: Modern, multi-page BI dashboard showing Executive Overview, Trends, Sources, Evidence, Insights, and System Health.
- **Likely files/folders**:
  - `web/` (Next.js frontend project directory)
  - `web/src/app/` (Next.js multi-page routing)
  - `web/src/components/dashboard/` (Reusable BI components)
- **Definition of Done**:
  - Frontend runs locally with `npm run dev` and renders a multi-page dashboard.
  - The UI is fully data-driven, retrieving chart configs and data solely from the FastAPI backend.
  - Zero placeholder UI elements.
  - Navigation cleanly highlights active pages.
- **What not to do**: Do not call the Gemini API or LLMs directly from frontend. Do not write local mock JSONs.
- [x] Initialize Next.js project with Tailwind CSS and Recharts.
- [x] Code dynamic UI components consuming API endpoints.
- [x] Refactor into a multi-page BI storytelling console (`/`, `/trends`, `/sources`, `/evidence`, `/insights`, `/system`).
- [x] Add sidebar navigation and metric explainers.

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
- [ ] Implement rule-based heuristic engine for fallback insight strings.
- [ ] Set up Gemini LLM integration with strict Pydantic parsing.
- [ ] Write tests confirming rule-based fallback behavior and mock Gemini calls.

### Module 8 — Evidence Explorer / RAG with Citations
- **Goal**: Build a Retrieval-Augmented Generation (RAG) system with a citations explorer to ensure every AI insight is grounded in source articles and raw statistics.
- **Input**: Data mart articles and AI generated insights.
- **Output**: Grounding maps and search indexes, plus frontend elements showing citations (links to source articles and exact statistics).
- **Likely files/folders**:
### Module 8 — Evidence Explorer / RAG with Citations ✅
- **Goal**: Allow users to trace insights back to raw sources deterministically.
- **Input**: Cleaned articles, insight cards.
- **Output**: Cited Markdown report, JSON evidence index, citations API.

- [x] Implement deterministic Evidence Layer.
- [x] Build lexical retrieval scoring.
- [x] Create `[E1]`-style citation mapping.
- [x] Create `src/api/routes/evidence.py`
- [x] Add tests validating citation linkages.

### Module 9 — Evaluation & Observability ✅
- **Goal**: Evaluate LLM outputs for correctness, grounding, and toxicity, and integrate structured logging/tracing for monitoring.
- **Input**: RAG prompts, generated insights, and gold-standard evaluation datasets.
- **Output**: Evaluation reports, latency dashboards, and structured tracing logs.
- **Likely files/folders**:
  - `src/evals/` (evaluation tests, loaders, quality gates)
  - `src/api/routes/evaluation.py`
  - `tests/test_evaluation.py`
- **Definition of Done**:
  - Automated evaluation runs can measure accuracy and grounding metrics.
  - System performance (latency, token usage) is monitored and logged.
- **What not to do**: Do not use slow blocking libraries that impact API latency.
- [x] Establish observability tracing setup using OpenTelemetry.
- [x] Create evaluation metrics for insight verification (grounding, relevance).
- [x] Build automated cron run for evaluator tests.

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
- [ ] Set up automated pipelines linking Ingestion -> ETL -> Datamart -> Trends.
- [ ] Integrate lightweight scheduler (cron / Prefect / n8n flows).

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
- [ ] Add an admin dashboard view in frontend for review queues.
- [ ] Implement Slack notification triggers and PDF generator compiling report data.

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
- [ ] Build multi-stage Dockerfiles for backend FastAPI and frontend Next.js.
- [ ] Establish GitHub Action workflow testing data collection, ETL, and backend.
- [ ] Add documentation screenshots and portfolio setup guide.


