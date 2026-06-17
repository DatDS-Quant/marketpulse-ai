import json
import datetime
from typing import List, Dict, Any
from src.utils.config import SAMPLE_DATA_DIR

def load_sample_data() -> List[Dict[str, Any]]:
    """
    Loads fallback data from the sample JSON file.
    Updates the 'ingested_at' timestamp to the current time.
    Ensures 'collected_from' is strictly marked as 'sample'.
    """
    sample_file = SAMPLE_DATA_DIR / "sample_articles.json"
    
    if not sample_file.exists():
        print(f"Error: Sample file not found at {sample_file}")
        return []
        
    try:
        with open(sample_file, "r", encoding="utf-8") as f:
            records = json.load(f)
            
        # Update dynamic fields to make it look like a fresh run
        current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        for record in records:
            record["ingested_at"] = current_time
            record["collected_from"] = "sample"
            
        return records
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return []
