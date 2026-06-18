"""Main Execution script for Trend Detection Module."""

import sys
import json
import datetime
from pathlib import Path

from src.utils.config import ANALYTICS_DATA_DIR, TRENDS_DATA_DIR
from src.intelligence.trend_loaders import check_analytics_files_exist, load_analytics_files, get_latest_analytics_run_time
from src.intelligence.trend_scoring import calculate_trend_metrics
from src.intelligence.trend_summary import generate_top_trends, generate_trend_summary, generate_trend_manifest, append_trend_run_log

def run_trends():
    print("Starting Trend Detection & Insight Metrics...")
    
    if not check_analytics_files_exist():
        print("No analytics data found. Run python -m src.analytics.run_analytics first.")
        sys.exit(0)
        
    print("Loading Analytics Data Mart files...")
    keyword_df, source_df, quality_df, insight_df, manifest = load_analytics_files()
    
    print("Calculating Data Freshness...")
    analytics_run_at = get_latest_analytics_run_time(manifest, quality_df)
    current_time = datetime.datetime.now(datetime.timezone.utc)
    
    freshness_score = 50.0
    if analytics_run_at:
        if analytics_run_at.tzinfo is None:
            analytics_run_at = analytics_run_at.replace(tzinfo=datetime.timezone.utc)
            
        diff_hours = (current_time - analytics_run_at).total_seconds() / 3600.0
        if diff_hours <= 24:
            freshness_score = 100.0
        elif diff_hours <= 48:
            freshness_score = 80.0
        elif diff_hours <= 72:
            freshness_score = 60.0
        else:
            freshness_score = 40.0
            
    print("Calculating Trend Metrics...")
    trend_metrics_df = calculate_trend_metrics(keyword_df, freshness_score)
    
    print("Ranking Top Trends...")
    top_trends_df = generate_top_trends(trend_metrics_df)
    
    run_id = f"run_trends_{current_time.strftime('%Y%m%d_%H%M%S')}"
    
    in_paths = {
        "daily_keyword_metrics": str(ANALYTICS_DATA_DIR / "daily_keyword_metrics.csv"),
        "source_metrics": str(ANALYTICS_DATA_DIR / "source_metrics.csv"),
        "quality_metrics": str(ANALYTICS_DATA_DIR / "quality_metrics.csv"),
        "insight_seed_metrics": str(ANALYTICS_DATA_DIR / "insight_seed_metrics.csv"),
        "analytics_manifest": str(ANALYTICS_DATA_DIR / "analytics_manifest.json")
    }
    
    out_paths = {
        "trend_metrics": str(TRENDS_DATA_DIR / "trend_metrics.csv"),
        "top_trends": str(TRENDS_DATA_DIR / "top_trends.csv"),
        "trend_summary": str(TRENDS_DATA_DIR / "trend_summary.json"),
        "trend_manifest": str(TRENDS_DATA_DIR / "trend_manifest.json")
    }
    
    print("Saving outputs...")
    trend_metrics_df.to_csv(out_paths["trend_metrics"], index=False)
    top_trends_df.to_csv(out_paths["top_trends"], index=False)
    
    summary = generate_trend_summary(run_id, trend_metrics_df, top_trends_df, freshness_score, analytics_run_at, in_paths, out_paths)
    with open(out_paths["trend_summary"], "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    latest_date = str(trend_metrics_df["date"].max()) if not trend_metrics_df.empty else None
    trend_manifest = generate_trend_manifest(run_id, trend_metrics_df, top_trends_df, latest_date, in_paths, out_paths)
    with open(out_paths["trend_manifest"], "w", encoding="utf-8") as f:
        json.dump(trend_manifest, f, indent=2, ensure_ascii=False)
        
    log_data = {
        "run_id": run_id,
        "step": "trend_detection",
        "status": "success",
        "input_dir": str(ANALYTICS_DATA_DIR),
        "output_dir": str(TRENDS_DATA_DIR),
        "trend_metric_rows": len(trend_metrics_df),
        "top_trend_rows": len(top_trends_df),
        "freshness_status": summary.get("freshness_status", "unknown"),
        "error_message": None,
        "created_at": current_time.isoformat()
    }
    append_trend_run_log(log_data)
    
    print("\n--- Trend Detection Summary ---")
    print(f"Run ID:                 {run_id}")
    print(f"Freshness Score:        {freshness_score} ({summary.get('freshness_status')})")
    print(f"Trend Metric Rows:      {len(trend_metrics_df)}")
    print(f"Top Trend Rows:         {len(top_trends_df)}")
    print(f"Top Keyword:            {summary.get('top_keyword')}")
    print(f"Warnings:               {len(summary.get('warnings', []))}")
    print(f"Output Directory:       {TRENDS_DATA_DIR}")
    print("-------------------------------\n")

if __name__ == "__main__":
    run_trends()
