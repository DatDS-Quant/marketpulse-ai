"""Main Analytics Data Mart execution script."""

import os
import json
import datetime
import pandas as pd
from pathlib import Path

from src.utils.config import ANALYTICS_DATA_DIR, LOGS_DIR
from src.analytics.loaders import find_latest_processed_file, load_processed_records
from src.analytics.metrics import (
    generate_articles_clean, 
    generate_daily_keyword_metrics, 
    generate_source_metrics, 
    generate_quality_metrics
)
from src.analytics.insight_seeds import generate_insight_seeds

def log_analytics_run(log_data: dict):
    """Appends a structured log line to analytics_runs.jsonl."""
    log_file = LOGS_DIR / "analytics_runs.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data) + "\n")

def run_analytics():
    """Runs the analytics data mart generation."""
    print("Starting Analytics Data Mart Processing...")
    
    input_file = find_latest_processed_file()
    if not input_file or not input_file.exists():
        print("No processed data found. Run python -m src.processing.run_etl first.")
        return
        
    print(f"Found processed JSON file: {input_file}")
    
    records = load_processed_records(input_file)
    total_processed_records = len(records)
    print(f"Loaded {total_processed_records} processed records.")
    
    # 1. Generate tables
    articles_clean = generate_articles_clean(records)
    daily_keyword_metrics = generate_daily_keyword_metrics(articles_clean)
    source_metrics = generate_source_metrics(articles_clean)
    
    # Generate overall quality metrics to get overall score
    quality_metrics = generate_quality_metrics(
        run_id="temp", 
        input_path=str(input_file), 
        total_processed_records=total_processed_records,
        articles_df=articles_clean,
        keyword_df=daily_keyword_metrics,
        source_df=source_metrics
    )
    
    overall_quality_score = float(quality_metrics["overall_quality_score"].iloc[0]) if not quality_metrics.empty else 100.0
    
    insight_seed_metrics = generate_insight_seeds(articles_clean, source_metrics, overall_quality_score)
    
    # 2. Save outputs to CSVs
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"run_analytics_{timestamp}"
    
    # Re-assign run_id in quality metrics
    if not quality_metrics.empty:
        quality_metrics["run_id"] = run_id
    
    out_paths = {
        "articles_clean": ANALYTICS_DATA_DIR / "articles_clean.csv",
        "daily_keyword_metrics": ANALYTICS_DATA_DIR / "daily_keyword_metrics.csv",
        "source_metrics": ANALYTICS_DATA_DIR / "source_metrics.csv",
        "quality_metrics": ANALYTICS_DATA_DIR / "quality_metrics.csv",
        "insight_seed_metrics": ANALYTICS_DATA_DIR / "insight_seed_metrics.csv",
    }
    
    articles_clean.to_csv(out_paths["articles_clean"], index=False)
    daily_keyword_metrics.to_csv(out_paths["daily_keyword_metrics"], index=False)
    source_metrics.to_csv(out_paths["source_metrics"], index=False)
    quality_metrics.to_csv(out_paths["quality_metrics"], index=False)
    insight_seed_metrics.to_csv(out_paths["insight_seed_metrics"], index=False)
    
    # 3. Create Manifest
    manifest_path = ANALYTICS_DATA_DIR / "analytics_manifest.json"
    manifest_data = {
        "run_id": run_id,
        "module": "analytics_data_mart",
        "input_path": str(input_file),
        "outputs": {k: str(v) for k, v in out_paths.items()},
        "total_processed_records": total_processed_records,
        "article_rows": len(articles_clean),
        "keyword_metric_rows": len(daily_keyword_metrics),
        "source_metric_rows": len(source_metrics),
        "quality_metric_rows": len(quality_metrics),
        "insight_seed_rows": len(insight_seed_metrics),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "success",
        "notes": "Analytics data mart tables generated successfully."
    }
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
    # 4. Create structured log line
    log_data = {
        "run_id": run_id,
        "step": "analytics_data_mart",
        "status": "success",
        "input_path": str(input_file),
        "output_dir": str(ANALYTICS_DATA_DIR),
        "total_processed_records": total_processed_records,
        "article_rows": len(articles_clean),
        "keyword_metric_rows": len(daily_keyword_metrics),
        "source_metric_rows": len(source_metrics),
        "insight_seed_rows": len(insight_seed_metrics),
        "error_message": None,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    log_analytics_run(log_data)
    
    # 5. Terminal summary
    print("\n--- Analytics Summary ---")
    print(f"Input Path:               {input_file}")
    print(f"Total Processed Records:  {total_processed_records}")
    print(f"Analytics Article Rows:   {len(articles_clean)}")
    print(f"Daily Keyword Rows:       {len(daily_keyword_metrics)}")
    print(f"Source Metric Rows:       {len(source_metrics)}")
    print(f"Quality Metric Rows:      {len(quality_metrics)}")
    print(f"Insight Seed Rows:        {len(insight_seed_metrics)}")
    print(f"Output Directory:         {ANALYTICS_DATA_DIR}")
    print(f"Manifest Path:            {manifest_path}")
    print("-------------------------\n")

if __name__ == "__main__":
    run_analytics()
