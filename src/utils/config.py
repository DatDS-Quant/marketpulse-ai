import os
from pathlib import Path

# Project Root Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
ANALYTICS_DATA_DIR = DATA_DIR / "analytics"
TRENDS_DATA_DIR = DATA_DIR / "trends"

INSIGHTS_DATA_DIR = DATA_DIR / "insights"
EVIDENCE_DATA_DIR = DATA_DIR / "evidence"
RAG_DATA_DIR = DATA_DIR / "rag"
EVALS_DIR = PROJECT_ROOT / "evals"
LOGS_DIR = PROJECT_ROOT / "logs"

# Reports Directory
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_GENERATED_DIR = REPORTS_DIR / "generated"
REPORTS_SAMPLES_DIR = REPORTS_DIR / "samples"
REPORTS_TEMPLATES_DIR = REPORTS_DIR / "templates"

# Ensure essential directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
ANALYTICS_DATA_DIR.mkdir(parents=True, exist_ok=True)
TRENDS_DATA_DIR.mkdir(parents=True, exist_ok=True)
INSIGHTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_DATA_DIR.mkdir(parents=True, exist_ok=True)
RAG_DATA_DIR.mkdir(parents=True, exist_ok=True)
EVALS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Default keywords for data ingestion
DEFAULT_KEYWORDS = [
    "AI marketing automation",
    "generative AI tools",
    "AI agents business",
    "content automation",
    "EdTech AI",
]
