# MarketPulse AI Specification

## Purpose

MarketPulse AI is an automated market intelligence and AI insight dashboard designed to demonstrate professional AI engineering, data pipeline building, and modern web application integration.

## Architecture Layers

MarketPulse AI is structured into 8 distinct architectural layers:

### 1. Data Pipeline Layer
- **Ingestion**: Fetches market and news feeds via RSS collectors with keyword search query parameters. Includes a sample data fallback mechanism to ensure offline capability.
- **ETL & Data Quality**: Cleans, parses dates, truncates summary text, deduplicates using deterministic SHA-256 hashes, and validates schemas using Pydantic. Tracks data quality anomalies and outputs data quality reports containing quality flags (e.g., `missing_title`, `invalid_url`).

### 2. Analytics Layer
- **Analytics Data Mart**: Aggregates processed articles into analytics-ready tables or files.
- **Trend Detection & Metrics**: Computes mathematical trend signals, keyword frequency metrics, and relevance scores.
- **BI Compatibility**: Exports analytics-ready CSV files for optional Power BI visualization or offline reports.

### 3. API Layer (FastAPI Backend)
- Exposes structured REST endpoints to serve charts, tables, KPI metrics, and insight configurations.
- Does not contain UI logic; returns clean JSON objects that define both chart configuration and data.
- Implements secure API key authentication if needed and encapsulates all business logic.

### 4. Web Dashboard Layer (Next.js Frontend)
- Built with Next.js, Tailwind CSS, shadcn/ui, and Recharts (or Apache ECharts) for interactive visualizations.
- **Data-Driven UI**: Dynamically renders KPI cards, trend charts, tabular lists, and AI insight blocks based on configurations returned by the API layer.
- Never connects directly to external data sources or LLM APIs; routes all queries through the API layer.

### 5. AI Insight Layer
- **Structured Insight Generator**: Generates human-readable market summaries and action items.
- **Gemini API Integration**: Uses Google Gemini (or equivalent LLM) with structured output validation (Pydantic/instructor) when `GEMINI_API_KEY` is present.
- **Rule-Based Fallback**: Gracefully falls back to template-based and heuristic-based insights if no API key is configured.

### 6. Evidence & RAG Layer
- **Evidence Explorer**: Grounding and alignment mechanism. Every generated insight must cite specific metrics, timestamps, and source article IDs.
- Prevents hallucination by filtering LLM inputs using analytics-ready facts and enforcing strict citation formats.

### 7. Automation Layer
- Automates ingestion, processing, analytics aggregation, and insight generation using standard scripts or workflow orchestrators.

### 8. Review & Delivery Layer
- Supports human review actions (approving, editing, rejecting insights) and schedules report delivery (email, Slack, Webhooks, PDF export).

---

## Technical Constraints & Boundaries

- **Streamlit**: Maintained only as a minimal internal administration or skeleton interface. It is NOT the primary user dashboard.
- **Power BI**: Treated strictly as an optional export compatibility target (via CSV outputs). The main application does not rely on Power BI.
- **AI Keys & Secrets**: Must reside strictly in a local `.env` file and must never be committed to git.
- **No Direct LLM Calls**: The frontend dashboard must never call LLM endpoints directly. All AI processing occurs inside the backend.
- **Structured Outputs**: All LLM interactions must yield schema-validated JSON outputs, not raw freeform text.

## Quality Bar

- Simple, readable, and clean Python and TypeScript.
- Strong separation of concerns (pipeline doesn't know about UI, UI doesn't know about raw database).
- Unit and integration tests for every module (aim for >80% test coverage).
- Automated CI pipeline verification before merging.


