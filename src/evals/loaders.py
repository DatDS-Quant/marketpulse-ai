import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Safe loading of a JSON file."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Safe loading of a JSONL file."""
    if not path.exists():
        return []
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    return records

def load_csv(path: Path) -> Optional[pd.DataFrame]:
    """Safe loading of a CSV file."""
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None
