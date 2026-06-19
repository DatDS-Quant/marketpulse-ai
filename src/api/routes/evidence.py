from fastapi import APIRouter, HTTPException
import json
from src.utils.config import EVIDENCE_DATA_DIR

router = APIRouter()

@router.get("/citations")
async def get_evidence_citations():
    """
    Returns the citation map mapping citation IDs to evidence records.
    """
    citation_map_path = EVIDENCE_DATA_DIR / "citation_map.json"
    
    if not citation_map_path.exists():
        raise HTTPException(
            status_code=503, 
            detail="Evidence citations have not been generated yet. Run python -m src.evidence.run_evidence first."
        )
        
    try:
        with open(citation_map_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
