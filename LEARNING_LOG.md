# Learning Log

Use this file to track what was learned while building MarketPulse AI.

## Module 0 - Project Operating System

Date: 2026-06-16

What was created:

- A clean Python project structure.
- Documentation for setup, scope, and development rules.
- A minimal Streamlit app.
- A smoke test for package imports.

What to understand before Module 1:

- Why a stable project structure matters.
- How `requirements.txt` and `pyproject.toml` support reproducible development.
- How `pytest` discovers and runs tests.
- How Streamlit runs an app from `app/main.py`.
- Why secrets belong in `.env`, not in git.


## Module 1 - Data Ingestion

Date: 2026-06-17

What I built:
- RSS collector for Google News
- Sample data fallback mechanism
- JSON normalization schema
- Structured logging to JSONL

What I learned:
- Working with the feedparser library.
- The importance of stable hashing (SHA-256) for generating deterministic IDs.
- How to structure fallback mechanisms that gracefully degrade.

Bugs and fixes:
- None encountered yet.

Interview explanation:
- Built the ingestion layer first because data is the foundation of the platform. Used RSS as an accessible source, decoupled collection from storage to keep things simple, and introduced fallback data to ensure the demo works reliably anywhere.

## Module 2 - ETL & Data Quality

Date: 2026-06-17

What I built:
- Pydantic models for data schema validation
- Data cleaning logic for handling missing values and text truncation
- Data quality reporting to track missing/invalid fields
- Deduplication logic to ensure idempotency

What I learned:
- How to separate pure logic (cleaning) from business rules (validation) and orchestration (ETL script).
- Leveraging Pydantic for strict typing and validation while applying flexible rules before instantiation.

Bugs and fixes:
- The `test_valid_raw_record` test originally failed because `content_length` became 30 when adding a valid summary to fix a quality flag. Fixed by explicitly defining expected content length in test assertions.

Trade-offs:
- Used Python standard library for basic date parsing and logging instead of importing heavy frameworks, which keeps the ETL pipeline extremely fast and beginner-friendly, but might lack advanced timezone edge-case handling.

Interview explanation:
- I implemented a lightweight ETL layer that bridges data ingestion and intelligence. The focus is on robust data quality: we don't just silently drop bad data, but we track metrics (missing titles, invalid URLs) via quality flags and reports. This creates an auditable data pipeline necessary for reliable AI outputs.

## Strategic Roadmap Update

Date: 2026-06-18

### Pivot Rationale
- **Why a Professional Web BI Dashboard?** Streamlit and Power BI are excellent for prototyping and standalone business analytics, but they do not scale well as customizable SaaS products. To deliver a unified, premium, and highly responsive user experience, we are transitioning to a dedicated web application stack (FastAPI backend and Next.js frontend). This ensures maximum control over custom UI components, responsive charts, and interactive AI grounding workflows.
- **Why is Power BI Export Optional?** Many enterprise users still require the ability to run custom ad-hoc analyses. Keeping Power BI compatibility via clean CSV exports guarantees interoperability without locking the main product interface into Microsoft's ecosystem.
- **Why Rule-Based Fallback for AI Insights?** Relying purely on LLM APIs creates single points of failure (network drops, API rate limits, pricing constraints, or key configuration errors). A rule-based fallback ensures that the dashboard remains fully functional and informative, generating deterministic analytical insights even when `GEMINI_API_KEY` is not provided.
- **Why Gemini/API Integration Only After Analytics Metrics Stability?** LLMs are highly dependent on the quality and structure of their input context. Integrating LLMs before analytics tables and trend calculation scores are fully mature would result in brittle prompts, excessive hallucinations, and frequent schema updates. Stabilizing the math first guarantees that the AI has clean, validated, and structured evidence to summarize.

## Module 3 - Analytics Data Mart

Date: 2026-06-18

What I built:
- Analytics data mart runner converting processed JSON logs to clean CSV files.
- Daily keyword metrics aggregation computing rates and data quality score.
- Source metrics aggregation for source quality analysis.
- Deterministic, rule-based insight seeds generation to ground future AI models.

What I learned:
- How to efficiently map error flags (list of strings) into Boolean feature columns in pandas.
- The value of separating data ingestion schemas (Pydantic) from analytical aggregations (pandas DataFrame).
- Standardizing and clamping derived quality scores (0 to 100) based on simple penalty math instead of complex black-box logic.

Bugs and fixes:
- The boolean flags returned by pandas (`numpy.bool_`) broke native python `assert X is True` checks in pytest. This was fixed by explicitly casting them to standard `bool()`.
- Floating point inaccuracies caused tests checking `1/3` to fail against `0.3333`. This was fixed by using a bounded tolerance check (`abs(val - target) < 0.001`).

Trade-offs:
- Decided to compute scores explicitly within Python/pandas instead of relying on a database engine like SQLite/DuckDB. This keeps dependencies low, eliminates schema migration issues for now, and fulfills the Power BI CSV requirements perfectly.

Interview explanation:
- For this module, I focused on building the foundational analytical layer. I converted the raw pipeline data into structured, multi-dimensional tables (articles, keywords, sources). Instead of jumping straight to LLMs, I built deterministic insight seeds and calculated transparent quality scores. This ensures any downstream dashboard or AI generator has mathematically sound facts to rely on, preventing hallucinations.

## Module 4 - Trend Detection & Insight Metrics

Date: 2026-06-18

What I built:
- A deterministic trend scoring engine calculating volume, growth, source diversity, quality, and freshness scores.
- A signal classification module to tag keywords (e.g., `rising_keyword`, `high_volume_keyword`, `stale_data_warning`).
- A top trends ranking mechanism providing structured explanation seeds for downstream LLM/Dashboard ingestion.
- Comprehensive `pytest` coverage validating mathematical bounds and avoiding division-by-zero edge cases.

What I learned:
- Leveraging pandas vectorized operations (`groupby`, `shift`, `transform`, `clip`) simplifies complex window calculations and ensures robust fallback behaviors.
- The importance of mathematically clamping scores (0 to 100) to keep indicators predictable and visually uniform on a dashboard.
- How to strictly separate insight rule-based fallbacks (generating summary explanation seeds) from stochastic LLM calls.

Bugs and fixes:
- The initial testing logic assumed the highest overall count would rank first, but an edge case keyword (`content automation`) with 0 previous articles experienced a 12.0x growth rate, legitimately pushing it to rank 1 via the growth_score constraint. Fixed by updating the test assertion to correctly reflect the mathematical truth.

Trade-offs:
- Decided to compute metrics sequentially on `daily_keyword_metrics.csv` instead of using a time-series forecasting model. This prevents black-box AI logic, keeps the pipeline highly deterministic, and allows exact auditing of why a keyword spiked.

Interview explanation:
- For this module, I built the Trend Detection core entirely using deterministic math. I deliberately avoided introducing LLMs or heavy ML forecasting models here. By calculating precise, bounded scores for growth, volume, and data freshness using Pandas, we guarantee that the upcoming Web Dashboard and AI Insights generator will be driven by validated, auditable, and interpretable market facts rather than black-box assumptions.
