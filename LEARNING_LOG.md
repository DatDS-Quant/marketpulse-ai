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
