import json
import datetime
from pathlib import Path
from src.utils.config import LOGS_DIR

def log_ingestion_run(records_collected: int, source_used: str, output_path: str, error: str = None):
    """
    Appends a structured JSON log line for an ingestion run to logs/ingestion_runs.jsonl.
    """
    log_file = LOGS_DIR / "ingestion_runs.jsonl"
    
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "records_collected": records_collected,
        "source_used": source_used,
        "output_path": output_path,
        "error": error
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
