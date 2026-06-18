from fastapi import APIRouter, HTTPException
from typing import List
from src.api.schemas import KPIResponse, KPICard
from src.api.data_loader import data_loader

router = APIRouter()

@router.get("/metrics", response_model=KPIResponse)
async def get_metrics():
    """
    Returns high-level KPI cards for the BI dashboard.
    """
    try:
        trend_summary = data_loader.get_data("trend_summary")
        quality_metrics_df = data_loader.get_data("quality_metrics")

        if not trend_summary or quality_metrics_df is None or quality_metrics_df.empty:
            raise FileNotFoundError("Missing necessary data files.")

        summary_cards = trend_summary.get("summary_cards", {})
        
        # Determine status for freshness
        freshness_status = "positive" if summary_cards.get("freshness_status") == "fresh" else "negative"

        # Determine status for top trend
        top_trend_status = "positive" if summary_cards.get("top_trend") else "neutral"

        latest_qm = quality_metrics_df.iloc[-1]
        quality_score = float(latest_qm["overall_quality_score"])
        total_records = int(latest_qm["total_records"])

        quality_status = "positive" if quality_score >= 90 else ("neutral" if quality_score >= 70 else "negative")

        cards: List[KPICard] = [
            KPICard(
                key="top_trend",
                label="Top Trend Keyword",
                value=summary_cards.get("top_trend", "N/A"),
                unit="",
                status=top_trend_status
            ),
            KPICard(
                key="average_trend_score",
                label="Average Trend Score",
                value=round(summary_cards.get("average_trend_score", 0), 2),
                unit="pts",
                status="neutral"
            ),
            KPICard(
                key="average_confidence_score",
                label="Average Confidence Score",
                value=round(summary_cards.get("average_confidence_score", 0), 2),
                unit="pts",
                status="neutral"
            ),
            KPICard(
                key="freshness_status",
                label="Data Freshness",
                value=summary_cards.get("freshness_status", "unknown").capitalize(),
                unit="",
                status=freshness_status
            ),
            KPICard(
                key="strong_signal_count",
                label="Strong Signals",
                value=summary_cards.get("strong_signal_count", 0),
                unit="keywords",
                status="positive" if summary_cards.get("strong_signal_count", 0) > 0 else "neutral"
            ),
            KPICard(
                key="total_processed_articles",
                label="Total Articles Analyzed",
                value=total_records,
                unit="articles",
                status="neutral"
            ),
            KPICard(
                key="pipeline_quality_score",
                label="Data Quality Score",
                value=quality_score,
                unit="pts",
                status=quality_status
            )
        ]

        return KPIResponse(cards=cards)

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
