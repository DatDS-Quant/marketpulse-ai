"""Loaders for Trend Detection Module."""

import json
import datetime
from pathlib import Path
import pandas as pd

from src.utils.config import ANALYTICS_DATA_DIR

def check_analytics_files_exist() -> bool:
    """Verifies that all required analytics files exist."""
    required_files = [
        "daily_keyword_metrics.csv",
        "source_metrics.csv",
        "quality_metrics.csv",
        "insight_seed_metrics.csv",
        "analytics_manifest.json"
    ]
    for file_name in required_files:
        if not (ANALYTICS_DATA_DIR / file_name).exists():
            return False
    return True

def load_analytics_files() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """
    Loads all required files and returns them as:
    (daily_keyword_metrics, source_metrics, quality_metrics, insight_seed_metrics, analytics_manifest)
    """
    keyword_df = pd.read_csv(ANALYTICS_DATA_DIR / "daily_keyword_metrics.csv")
    source_df = pd.read_csv(ANALYTICS_DATA_DIR / "source_metrics.csv")
    quality_df = pd.read_csv(ANALYTICS_DATA_DIR / "quality_metrics.csv")
    insight_df = pd.read_csv(ANALYTICS_DATA_DIR / "insight_seed_metrics.csv")
    
    with open(ANALYTICS_DATA_DIR / "analytics_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    return keyword_df, source_df, quality_df, insight_df, manifest

def get_latest_analytics_run_time(manifest: dict, quality_df: pd.DataFrame) -> datetime.datetime | None:
    """
    Parses the timestamp from analytics_manifest.json, falling back to quality_metrics.csv.
    """
    ts_str = manifest.get("created_at")
    if ts_str:
        try:
            return datetime.datetime.fromisoformat(ts_str)
        except Exception:
            pass
            
    if not quality_df.empty and "created_at" in quality_df.columns:
        ts_str = quality_df["created_at"].iloc[0]
        if pd.notna(ts_str):
            try:
                return datetime.datetime.fromisoformat(str(ts_str))
            except Exception:
                pass
                
    return None
