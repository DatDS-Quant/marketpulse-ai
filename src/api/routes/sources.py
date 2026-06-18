from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from src.api.schemas import ChartResponse, ChartConfig
from src.api.data_loader import data_loader
import pandas as pd

router = APIRouter()

@router.get("/", response_model=ChartResponse)
async def get_sources(
    limit: int = Query(20, description="Limit the number of sources returned (default 20)")
):
    """
    Returns source metrics along with a Scatter or Bar Chart configuration.
    """
    try:
        source_metrics_df = data_loader.get_data("source_metrics")
        if source_metrics_df is None or source_metrics_df.empty:
            raise FileNotFoundError("Missing source_metrics.csv data.")

        df = source_metrics_df.copy()
        
        # Sort by article count descending
        df = df.sort_values(by="article_count", ascending=False).head(limit)

        # Prepare chart config
        chart_config = ChartConfig(
            chart_type="scatter",
            title="Source Quality vs Article Volume",
            x_axis_key="article_count",
            y_axis_keys=["source_quality_score"],
            labels={
                "source": "Source Name",
                "article_count": "Article Volume",
                "source_quality_score": "Quality Score (0-100)"
            },
            colors={
                "source_quality_score": "#f59e0b"  # Tailwind amber-500
            }
        )

        data = df.to_dict(orient="records")

        return ChartResponse(chart_config=chart_config, data=data)

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
