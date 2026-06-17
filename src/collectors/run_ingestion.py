import json
import datetime
from src.utils.config import DEFAULT_KEYWORDS, RAW_DATA_DIR
from src.utils.logger import log_ingestion_run
from src.collectors.rss_collector import run_rss_collection
from src.collectors.sample_loader import load_sample_data

def save_raw_data(records: list) -> str:
    """
    Saves collected records to a timestamped JSON file in data/raw/.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"ingestion_{timestamp}.json"
    output_path = RAW_DATA_DIR / output_filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        
    return str(output_path)

def main():
    print("Starting Data Ingestion...")
    source_used = "rss"
    records = []
    error_msg = None
    
    # Try RSS collection
    try:
        records = run_rss_collection(DEFAULT_KEYWORDS)
    except Exception as e:
        error_msg = str(e)
        print(f"RSS collection failed: {e}")
        
    # Fallback to sample data if RSS failed or returned no records
    if not records:
        print("Falling back to sample data...")
        source_used = "sample"
        records = load_sample_data()
        
    if not records:
        print("Error: No data could be collected from either RSS or sample fallback.")
        log_ingestion_run(0, "none", "", "No data available")
        return
        
    # Save the results
    output_path = save_raw_data(records)
    
    # Write structured log
    log_ingestion_run(
        records_collected=len(records),
        source_used=source_used,
        output_path=output_path,
        error=error_msg
    )
    
    # Print summary
    print("\n--- Ingestion Summary ---")
    print(f"Records Collected: {len(records)}")
    print(f"Source Used:       {source_used}")
    print(f"Output Path:       {output_path}")
    print("-------------------------\n")

if __name__ == "__main__":
    main()
