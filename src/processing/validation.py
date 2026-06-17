"""Data validation and quality checks."""

from typing import Dict, Any, Tuple, List
from pydantic import ValidationError
import datetime
from src.processing.models import ProcessedArticle
from src.processing.cleaning import clean_string, calculate_content_length

def looks_like_valid_url(url: str | None) -> bool:
    """Checks if a URL has a basic valid format."""
    if not url:
        return False
    return url.startswith("http://") or url.startswith("https://")

def is_valid_date(date_str: str | None) -> bool:
    """Checks if a date string is parseable as ISO."""
    if not date_str:
        return False
    try:
        datetime.datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
        return True
    except (ValueError, TypeError):
        return False

def validate_and_format_record(record: Dict[str, Any]) -> Tuple[ProcessedArticle | None, List[str]]:
    """
    Validates a raw record, applies quality flags, and returns a ProcessedArticle.
    Returns (article, flags). If article is rejected, returns (None, flags).
    """
    flags = []
    
    # Clean strings
    title = clean_string(record.get("title"))
    url = clean_string(record.get("url"))
    source = clean_string(record.get("source"))
    summary = clean_string(record.get("summary"))
    published_at = clean_string(record.get("published_at"))
    keyword = clean_string(record.get("keyword"))
    raw_text = clean_string(record.get("raw_text"))
    ingested_at = clean_string(record.get("ingested_at"))
    collected_from = clean_string(record.get("collected_from"))
    record_id = clean_string(record.get("id"))
    
    # Check rejection rules
    if not record_id:
        return None, ["missing_id"]
    if not title:
        return None, ["missing_title"]
    if not url:
        return None, ["missing_url"]
    if collected_from not in ["rss", "sample"]:
        return None, ["invalid_collected_from"]
        
    # Check flag rules
    if not looks_like_valid_url(url):
        flags.append("invalid_url")
        
    if not source:
        flags.append("missing_source")
        source = "Unknown"  # Satisfy schema requirements
        
    if not summary or len(summary) < 10:
        flags.append("short_summary")
        
    if published_at:
        if not is_valid_date(published_at):
            flags.append("invalid_published_at")
            published_at = None
        else:
            try:
                dt = datetime.datetime.fromisoformat(str(published_at).replace('Z', '+00:00'))
                published_at = dt.isoformat()
            except ValueError:
                published_at = None
                
    content_length = calculate_content_length(raw_text, summary)
    processed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    try:
        article = ProcessedArticle(
            id=record_id,
            title=title,
            url=url,
            source=source,
            published_at=published_at,
            summary=summary,
            keyword=keyword or "unknown",
            raw_text=raw_text,
            ingested_at=ingested_at,
            collected_from=collected_from,
            processed_at=processed_at,
            content_length=content_length,
            quality_flags=flags
        )
        return article, flags
    except ValidationError:
        return None, ["schema_validation_error"]
