"""Pydantic models for data validation."""

from typing import List, Optional
from pydantic import BaseModel, Field

class ProcessedArticle(BaseModel):
    """Schema for a processed article after ETL."""
    id: str = Field(..., description="Unique identifier for the article")
    title: str = Field(..., description="Article title, must not be empty")
    url: str = Field(..., description="Article URL")
    source: str = Field(..., description="Source of the article")
    published_at: Optional[str] = Field(None, description="ISO formatted publication date")
    summary: Optional[str] = Field(None, description="Short summary of the article")
    keyword: str = Field(..., description="Keyword used to collect the article")
    raw_text: Optional[str] = Field(None, description="Raw text or HTML content")
    ingested_at: Optional[str] = Field(None, description="ISO timestamp of ingestion")
    collected_from: str = Field(..., description="Source of collection, e.g., 'rss' or 'sample'")
    processed_at: str = Field(..., description="ISO timestamp of processing")
    content_length: int = Field(..., description="Length of the content")
    quality_flags: List[str] = Field(default_factory=list, description="List of quality issues")
