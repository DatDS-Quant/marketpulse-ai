"""Loaders for finding and loading processed records."""

import glob
import json
from pathlib import Path
from src.utils.config import PROCESSED_DATA_DIR

def find_latest_processed_file() -> Path | None:
    """Finds the most recent processed JSON file in the processed data directory."""
    files = glob.glob(str(PROCESSED_DATA_DIR / "processed_*.json"))
    if not files:
        return None
    files.sort()
    return Path(files[-1])

def load_processed_records(file_path: Path) -> list[dict]:
    """Loads processed records from a JSON file."""
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
