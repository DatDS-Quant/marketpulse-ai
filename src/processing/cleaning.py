"""Data cleaning functions for ETL."""

from typing import Any

def clean_string(value: Any) -> str | None:
    """Strips whitespace and normalizes empty strings to None."""
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None

def calculate_content_length(raw_text: str | None, summary: str | None) -> int:
    """Calculates content length based on raw_text or summary."""
    if raw_text:
        return len(raw_text)
    if summary:
        return len(summary)
    return 0
