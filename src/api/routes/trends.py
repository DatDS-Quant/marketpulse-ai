from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from src.api.schemas import ChartResponse, ChartConfig
from src.api.data_loader import data_loader
import pandas as pd

router = APIRouter()

@router.get("/top", response_model=ChartResponse)
async def get_top_trends():
    """
    Returns the top trends along with a Bar Chart configuration.
    """
    try:
        top_trends_df = data_loader.get_data("top_trends")
        if top_trends_df is None or top_trends_df.empty:
            raise FileNotFoundError("Missing top_trends.csv data.")

        # Prepare chart config
        chart_config = ChartConfig(
            chart_type="bar",
            title="Top Trends (Current Score)",
            x_axis_key="keyword",
            y_axis_keys=["trend_score"],
            labels={
                "keyword": "Keyword",
                "trend_score": "Trend Score",
                "confidence_score": "Confidence Score",
                "article_count": "Articles"
            },
            colors={
                "trend_score": "#3b82f6"  # Tailwind blue-500
            }
        )

        # We take top 10 trends for the chart
        data = top_trends_df.head(10).to_dict(orient="records")

        return ChartResponse(chart_config=chart_config, data=data)

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=ChartResponse)
async def get_trend_metrics(
    keyword: Optional[str] = Query(None, description="Filter by a specific keyword"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Returns detailed trend metrics over time, along with a Line Chart configuration.
    """
    try:
        trend_metrics_df = data_loader.get_data("trend_metrics")
        if trend_metrics_df is None or trend_metrics_df.empty:
            raise FileNotFoundError("Missing trend_metrics.csv data.")

        df = trend_metrics_df.copy()

        # Apply filters
        if keyword:
            df = df[df['keyword'].str.lower() == keyword.lower()]
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]

        # Sort chronologically
        df = df.sort_values(by=['keyword', 'date'])

        # Prepare chart config
        chart_config = ChartConfig(
            chart_type="line",
            title=f"Trend Metrics Over Time{f' - {keyword}' if keyword else ''}",
            x_axis_key="date",
            y_axis_keys=["trend_score", "confidence_score"],
            labels={
                "date": "Date",
                "trend_score": "Trend Score",
                "confidence_score": "Confidence Score",
                "article_count": "Articles"
            },
            colors={
                "trend_score": "#3b82f6",     # Blue
                "confidence_score": "#10b981" # Green
            }
        )

        data = df.to_dict(orient="records")

        return ChartResponse(chart_config=chart_config, data=data)

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
