from fastapi import APIRouter, HTTPException
from src.api.schemas import StatusResponse, PipelineMetrics
from src.api.data_loader import data_loader

router = APIRouter()

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Returns the current operational status of the API, along with data freshness metrics.
    """
    try:
        # Load summary files
        trend_summary = data_loader.get_data("trend_summary")
        quality_metrics_df = data_loader.get_data("quality_metrics")
        
        if not trend_summary or quality_metrics_df is None or quality_metrics_df.empty:
            raise FileNotFoundError("Missing necessary data files.")

        freshness_status = trend_summary.get("freshness_status", "unknown")
        latest_run_at = trend_summary.get("created_at")

        # Get latest quality metrics (assuming one row or taking the latest)
        latest_qm = quality_metrics_df.iloc[-1]
        
        pipeline_metrics = PipelineMetrics(
            total_processed_articles=int(latest_qm["total_records"]),
            quality_score=float(latest_qm["overall_quality_score"])
        )

        return StatusResponse(
            status="online",
            version="1.0.0",
            data_freshness=freshness_status,
            latest_run_at=latest_run_at,
            pipeline_metrics=pipeline_metrics
        )
    except FileNotFoundError as e:
        # This will be caught by the global exception handler in main.py, 
        # or we can raise a 503 Service Unavailable here.
        raise HTTPException(
            status_code=503, 
            detail=f"Service Unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
