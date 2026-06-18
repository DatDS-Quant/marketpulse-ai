"""Summarization and output formatting for Trend Detection Module."""

import json
import datetime
import pandas as pd
from pathlib import Path
from src.utils.config import LOGS_DIR

def generate_top_trends(trend_metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Generates the top ranked trends."""
    if trend_metrics_df.empty:
        return pd.DataFrame(columns=[
            "rank", "keyword", "latest_date", "signal_type", "article_count",
            "growth_rate", "keyword_share", "unique_source_count", "trend_score",
            "confidence_score", "freshness_score", "data_quality_score", "severity",
            "explanation_seed", "created_at"
        ])
        
    # Get latest available date per keyword
    latest_df = trend_metrics_df.sort_values("date").groupby("keyword").last().reset_index()
    
    # Sort for ranking
    latest_df = latest_df.sort_values(
        by=["trend_score", "confidence_score", "article_count"], 
        ascending=[False, False, False]
    ).head(10).reset_index(drop=True)
    
    latest_df["rank"] = latest_df.index + 1
    latest_df["latest_date"] = latest_df["date"]
    
    def make_explanation(row):
        return f"{row['keyword']} is a top ranked keyword in the latest analytics batch with {row['article_count']} articles, {row['unique_source_count']} unique sources, and a trend score of {row['trend_score']}."
        
    latest_df["explanation_seed"] = latest_df.apply(make_explanation, axis=1)
    latest_df["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    out_cols = [
        "rank", "keyword", "latest_date", "signal_type", "article_count",
        "growth_rate", "keyword_share", "unique_source_count", "trend_score",
        "confidence_score", "freshness_score", "data_quality_score", "severity",
        "explanation_seed", "created_at"
    ]
    return latest_df[out_cols]

def generate_trend_summary(run_id: str, trend_metrics_df: pd.DataFrame, top_trends_df: pd.DataFrame, freshness_score: float, analytics_run_at: datetime.datetime | None, in_paths: dict, out_paths: dict) -> dict:
    """Generates the overview dashboard metadata JSON."""
    
    status_label = "unknown"
    if freshness_score >= 100:
        status_label = "fresh"
    elif freshness_score >= 80:
        status_label = "aging"
    elif freshness_score >= 70:
        status_label = "aging" # Actually wait, 70 is not stale, but 60 is stale. Let's make <70 stale.
    else:
        status_label = "stale"
        
    latest_date = None
    if not trend_metrics_df.empty:
        latest_date = str(trend_metrics_df["date"].max())
        
    top_keyword = None
    top_trend_score = 0.0
    top_conf_score = 0.0
    if not top_trends_df.empty:
        top_keyword = str(top_trends_df.iloc[0]["keyword"])
        top_trend_score = float(top_trends_df.iloc[0]["trend_score"])
        top_conf_score = float(top_trends_df.iloc[0]["confidence_score"])
        
    avg_trend = float(trend_metrics_df["trend_score"].mean()) if not trend_metrics_df.empty else 0.0
    avg_conf = float(trend_metrics_df["confidence_score"].mean()) if not trend_metrics_df.empty else 0.0
    strong_signals = int((trend_metrics_df["trend_score"] >= 60).sum()) if not trend_metrics_df.empty else 0
    
    warnings = []
    if freshness_score < 60:
        warnings.append("Analytics data is stale.")
    if top_trend_score >= 60 and top_conf_score < 60:
        warnings.append("Top trend has low confidence.")
    if strong_signals == 0:
        warnings.append("No strong trend detected.")
    if analytics_run_at is None:
        warnings.append("No analytics timestamp found.")
        
    summary = {
        "run_id": run_id,
        "module": "trend_detection",
        "status": "success",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "latest_analytics_run_at": analytics_run_at.isoformat() if analytics_run_at else None,
        "freshness_score": freshness_score,
        "freshness_status": status_label,
        "trend_metric_rows": len(trend_metrics_df),
        "top_trend_rows": len(top_trends_df),
        "latest_date": latest_date,
        "top_keyword": top_keyword,
        "top_trend_score": top_trend_score,
        "top_confidence_score": top_conf_score,
        "warnings": warnings,
        "summary_cards": {
            "top_trend": top_keyword,
            "average_trend_score": round(avg_trend, 2),
            "average_confidence_score": round(avg_conf, 2),
            "freshness_status": status_label,
            "strong_signal_count": strong_signals
        },
        "input_paths": in_paths,
        "output_paths": out_paths
    }
    return summary

def generate_trend_manifest(run_id: str, trend_metrics_df: pd.DataFrame, top_trends_df: pd.DataFrame, latest_date: str | None, in_paths: dict, out_paths: dict) -> dict:
    """Generates the manifest JSON."""
    return {
        "run_id": run_id,
        "module": "trend_detection",
        "input_paths": in_paths,
        "outputs": out_paths,
        "trend_metric_rows": len(trend_metrics_df),
        "top_trend_rows": len(top_trends_df),
        "latest_date": latest_date,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "success",
        "notes": "Trend metrics generated successfully."
    }

def append_trend_run_log(log_data: dict):
    """Appends a log line to trend_runs.jsonl."""
    log_file = LOGS_DIR / "trend_runs.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data) + "\n")
