from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

# -------------------------------------------------------------------------
# Dynamic Chart Configurations (For Data-Driven UI rendering)
# -------------------------------------------------------------------------

class ChartConfig(BaseModel):
    """
    Configuration for frontend chart rendering (e.g. using Recharts).
    Allows the frontend to dynamically draw charts without hardcoding logic.
    """
    chart_type: str = Field(..., description="Type of the chart: 'line', 'bar', 'pie', 'scatter'")
    title: str = Field(..., description="Chart title")
    x_axis_key: str = Field(..., description="Data key for the X axis")
    y_axis_keys: List[str] = Field(..., description="Data keys for the Y axis series")
    labels: Dict[str, str] = Field(default_factory=dict, description="Friendly labels for axes/tooltips")
    colors: Dict[str, str] = Field(default_factory=dict, description="Hex colors mapped to y_axis_keys")


class ChartResponse(BaseModel):
    """
    Standard response format containing both the dynamic chart config and the array of data.
    """
    chart_config: ChartConfig
    data: List[Dict[str, Any]]


# -------------------------------------------------------------------------
# KPI Cards & Summary
# -------------------------------------------------------------------------

class KPICard(BaseModel):
    """
    Schema for a single KPI summary card.
    """
    key: str = Field(..., description="Internal identifier for the KPI")
    label: str = Field(..., description="Human-readable label")
    value: Union[int, float, str] = Field(..., description="The main KPI value")
    unit: str = Field(default="", description="Unit of measurement (e.g., '%', 'articles')")
    status: str = Field(default="neutral", description="'positive', 'negative', or 'neutral'")


class KPIResponse(BaseModel):
    """
    Response format for the metrics dashboard.
    """
    cards: List[KPICard]


# -------------------------------------------------------------------------
# Status & Pagination
# -------------------------------------------------------------------------

class PipelineMetrics(BaseModel):
    total_processed_articles: int
    quality_score: float

class StatusResponse(BaseModel):
    """
    System status and data freshness.
    """
    status: str = "online"
    version: str = "1.0.0"
    data_freshness: str
    latest_run_at: Optional[str] = None
    pipeline_metrics: PipelineMetrics


class PaginatedResponse(BaseModel):
    """
    Standard paginated response format for lists (like articles).
    """
    total_items: int
    total_pages: int
    current_page: int
    limit: int
    data: List[Dict[str, Any]]
