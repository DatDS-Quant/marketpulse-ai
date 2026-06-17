"""Main ETL execution script."""

import os
import glob
import json
import datetime
from pathlib import Path

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR, SAMPLE_DATA_DIR
from src.processing.validation import validate_and_format_record
from src.processing.dedup import deduplicate_records

def get_latest_raw_file() -> Path | None:
    """Finds the most recent raw ingestion JSON file."""
    files = glob.glob(str(RAW_DATA_DIR / "ingestion_*.json"))
    if not files:
        return None
    files.sort()
    return Path(files[-1])

def log_processing_run(log_data: dict):
    """Appends a structured log line to processing_runs.jsonl."""
    log_file = LOGS_DIR / "processing_runs.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data) + "\n")

def run_etl():
    """Runs the ETL processing step."""
    print("Starting ETL Processing...")
    
    input_file = get_latest_raw_file()
    source_used = "raw"
    if not input_file or not input_file.exists():
        input_file = SAMPLE_DATA_DIR / "sample_articles.json"
        source_used = "sample"
        print(f"No raw ingestion file found. Using sample fallback: {input_file}")
    else:
        print(f"Found raw ingestion file: {input_file}")
        
    if not input_file.exists():
        print("Error: No input data found (even sample data is missing).")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        raw_records = json.load(f)
        
    print(f"Loaded {len(raw_records)} raw records.")
    
    valid_articles = []
    invalid_count = 0
    
    missing_title_count = 0
    missing_url_count = 0
    invalid_url_count = 0
    missing_source_count = 0
    short_summary_count = 0
    invalid_date_count = 0
    invalid_collected_from_count = 0
    
    for record in raw_records:
        article, flags = validate_and_format_record(record)
        
        if not article:
            invalid_count += 1
            if "missing_title" in flags: missing_title_count += 1
            if "missing_url" in flags: missing_url_count += 1
            if "invalid_collected_from" in flags: invalid_collected_from_count += 1
        else:
            valid_articles.append(article)
            if "invalid_url" in flags: invalid_url_count += 1
            if "missing_source" in flags: missing_source_count += 1
            if "short_summary" in flags: short_summary_count += 1
            if "invalid_published_at" in flags: invalid_date_count += 1
            
    unique_articles = deduplicate_records(valid_articles)
    duplicates_removed = len(valid_articles) - len(unique_articles)
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_filename = f"processed_{timestamp}.json"
    output_path = PROCESSED_DATA_DIR / output_filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([a.model_dump() for a in unique_articles], f, indent=2, ensure_ascii=False)
        
    run_id = f"run_{timestamp}"
    report_filename = f"data_quality_report_{timestamp}.json"
    report_path = PROCESSED_DATA_DIR / report_filename
    
    report_data = {
        "run_id": run_id,
        "input_path": str(input_file),
        "output_path": str(output_path),
        "report_path": str(report_path),
        "total_raw_records": len(raw_records),
        "valid_records": len(unique_articles),
        "invalid_records": invalid_count,
        "duplicate_records_removed": duplicates_removed,
        "missing_title_count": missing_title_count,
        "missing_url_count": missing_url_count,
        "invalid_url_count": invalid_url_count,
        "missing_source_count": missing_source_count,
        "empty_or_short_summary_count": short_summary_count,
        "invalid_date_count": invalid_date_count,
        "invalid_collected_from_count": invalid_collected_from_count,
        "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "notes": "ETL run completed successfully."
    }
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
        
    log_data = {
        "run_id": run_id,
        "step": "etl_processing",
        "status": "success",
        "input_path": str(input_file),
        "output_path": str(output_path),
        "report_path": str(report_path),
        "total_raw_records": len(raw_records),
        "valid_records": len(unique_articles),
        "invalid_records": invalid_count,
        "duplicate_records_removed": duplicates_removed,
        "error_message": None,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    log_processing_run(log_data)
    
    print("\n--- ETL Summary ---")
    print(f"Raw Records Loaded:  {len(raw_records)}")
    print(f"Valid Records:       {len(unique_articles)}")
    print(f"Invalid Records:     {invalid_count}")
    print(f"Duplicates Removed:  {duplicates_removed}")
    print(f"Source Input Path:   {input_file}")
    print(f"Processed Output:    {output_path}")
    print(f"Quality Report:      {report_path}")
    print("-------------------\n")

if __name__ == "__main__":
    run_etl()
