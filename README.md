# MarketPulse AI

MarketPulse AI is an AI-powered market intelligence automation platform. The project is designed as a portfolio-grade AI engineering system that demonstrates data ingestion, ETL, schema validation, trend detection, RAG with citations, structured LLM outputs, evaluation, observability, human-in-the-loop review, and Streamlit dashboarding.

## Problem

Market research often requires manually collecting scattered market signals, cleaning data, identifying trends, writing summaries, and checking sources. This process is slow, hard to reproduce, and difficult to evaluate.

## Solution

MarketPulse AI will automate a practical market intelligence workflow. The platform will collect data, process it into validated datasets, detect trends, generate cited insights, and present results in a simple dashboard.

Module 0 only sets up the project operating system. Real AI features will be added in later modules.

## Core Features

- Data ingestion from selected market sources.
- ETL and schema validation.
- Trend detection and signal ranking.
- Retrieval-augmented generation with citations.
- Structured LLM outputs.
- Evaluation and observability.
- Human-in-the-loop review.
- Streamlit dashboard for exploration and reporting.

## Architecture Placeholder

```text
Data Sources
    -> Collectors
    -> Processing and Validation
    -> Storage
    -> Intelligence Layer
    -> RAG and Agents
    -> Evaluation and Observability
    -> Streamlit Dashboard
```

This architecture is a placeholder for Module 0. Each layer will be implemented incrementally.

## Tech Stack

- Python
- Streamlit
- pytest
- Standard Python project structure

Future modules may add data validation, vector search, LLM providers, workflow orchestration, and observability tools only when needed.

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

Current status: Module 0 initialized.

No real AI features have been implemented yet. The current version provides the project skeleton, documentation, basic Streamlit entry point, and smoke test.

