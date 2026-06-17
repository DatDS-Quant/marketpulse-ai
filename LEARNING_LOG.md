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
