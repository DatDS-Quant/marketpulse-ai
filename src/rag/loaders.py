import json
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
