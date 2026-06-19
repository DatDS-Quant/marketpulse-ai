from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json
from src.utils.config import EVALS_DIR

router = APIRouter()

@router.get("/summary")
async def get_evaluation_summary():
    """
    Returns the latest evaluation summary.
    """
    summary_path = EVALS_DIR / "evaluation_summary.json"
    
    if not summary_path.exists():
        raise HTTPException(
            status_code=503, 
            detail="Evaluation summary not found. Please run the evaluation pipeline first: python -m src.evals.run_evaluation"
        )
        
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
