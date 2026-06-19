import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Safe loading of a JSON file."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def load_csv(path: Path) -> Optional[pd.DataFrame]:
    """Safe loading of a CSV file."""
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None
