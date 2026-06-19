import pandas as pd
from typing import Optional
from src.evidence.schemas import EvidenceIndex, EvidenceRecord

def build_evidence_index(
    articles_df: Optional[pd.DataFrame], 
    source_metrics_df: Optional[pd.DataFrame]
) -> EvidenceIndex:
    """Builds a normalized evidence index from cleaned articles and source metrics."""
    if articles_df is None or articles_df.empty:
        return EvidenceIndex(records=[])

    # Convert source metrics to a lookup dictionary for fast access
    source_quality_lookup = {}
    if source_metrics_df is not None and not source_metrics_df.empty:
        if 'source' in source_metrics_df.columns and 'source_quality_score' in source_metrics_df.columns:
            for _, row in source_metrics_df.iterrows():
                source_quality_lookup[row['source']] = float(row['source_quality_score'])

    records = []
    
    for idx, row in articles_df.iterrows():
        # Handle article id
        article_id = str(row.get('article_id', row.get('id', f"art_{idx}")))
        title = str(row.get('title', 'Unknown Title'))
        source = str(row.get('source', 'Unknown Source'))
        url = str(row.get('url', ''))
        keyword = str(row.get('keyword', row.get('matched_keywords', '')))
        published_at = str(row.get('published_at', '')) if pd.notna(row.get('published_at')) else None
        summary = str(row.get('summary', row.get('raw_text', ''))) if pd.notna(row.get('summary', row.get('raw_text'))) else None
        quality_flags = str(row.get('quality_flags', '')) if pd.notna(row.get('quality_flags')) else None
        
        # Get quality score
        quality_score = source_quality_lookup.get(source, 0.5)

        records.append(EvidenceRecord(
            article_id=article_id,
            title=title,
            source=source,
            url=url,
            keyword=keyword,
            published_at=published_at,
            summary=summary,
            quality_flags=quality_flags,
            source_quality_score=quality_score
        ))

    return EvidenceIndex(records=records)
