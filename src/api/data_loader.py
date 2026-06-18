import os
import json
import logging
from typing import Optional, Dict, Any
import pandas as pd
from pathlib import Path

from src.utils.config import ANALYTICS_DATA_DIR, TRENDS_DATA_DIR

logger = logging.getLogger(__name__)

class APIDataLoader:
    """
    DataLoader with hot-reloading mechanism based on file modification time (mtime).
    Ensures that the API always serves the freshest data without requiring a server restart.
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Define the file mapping
        self.file_paths = {
            "articles_clean": ANALYTICS_DATA_DIR / "articles_clean.csv",
            "quality_metrics": ANALYTICS_DATA_DIR / "quality_metrics.csv",
            "source_metrics": ANALYTICS_DATA_DIR / "source_metrics.csv",
            "insight_seed_metrics": ANALYTICS_DATA_DIR / "insight_seed_metrics.csv",
            "top_trends": TRENDS_DATA_DIR / "top_trends.csv",
            "trend_metrics": TRENDS_DATA_DIR / "trend_metrics.csv",
            "trend_summary": TRENDS_DATA_DIR / "trend_summary.json"
        }

    def _load_file(self, file_key: str, path: Path) -> Optional[Any]:
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return None
        
        try:
            if path.suffix == '.csv':
                # Return pandas DataFrame for CSVs
                # Handle na values carefully so API can serialize it cleanly
                df = pd.read_csv(path)
                df = df.fillna("")
                return df
            elif path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return None

    def get_data(self, file_key: str) -> Optional[Any]:
        """
        Retrieves data for a given file_key. 
        Automatically checks file mtime and reloads if changed.
        """
        if file_key not in self.file_paths:
            raise ValueError(f"Unknown file key: {file_key}")
            
        path = self.file_paths[file_key]
        
        if not path.exists():
            # If the file doesn't exist, we must clear it from cache if it was there
            if file_key in self._cache:
                del self._cache[file_key]
            # We raise an error so the API can gracefully catch and return 503
            raise FileNotFoundError(f"Data file missing: {path}. Please run ETL and Analytics pipelines.")
            
        current_mtime = os.path.getmtime(path)
        
        # Check cache
        if file_key in self._cache:
            cached_mtime = self._cache[file_key]['mtime']
            if current_mtime <= cached_mtime:
                # Cache is fresh
                return self._cache[file_key]['data']
                
        # Cache miss or file changed -> reload
        logger.info(f"Loading/Reloading data for {file_key} from {path}")
        data = self._load_file(file_key, path)
        if data is not None:
            self._cache[file_key] = {
                'mtime': current_mtime,
                'data': data
            }
        return data

# Global instance to be used across API routes
data_loader = APIDataLoader()
