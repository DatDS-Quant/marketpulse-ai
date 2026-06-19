from src.evals.schemas import DataQualityResult, CheckResult
import pandas as pd
from typing import Optional

def evaluate_data_quality(
    articles_df: Optional[pd.DataFrame], 
    quality_metrics_df: Optional[pd.DataFrame]
) -> DataQualityResult:
    checks = []
    
    # Defaults
    articles_count = 0
    missing_fields_ratio = 1.0
    invalid_keyword_ratio = 1.0
    unique_sources = 0
    
    if articles_df is not None and not articles_df.empty:
        articles_count = len(articles_df)
        if "source" in articles_df.columns:
            unique_sources = articles_df["source"].nunique()
            
        checks.append(CheckResult(
            name="Articles Count",
            status="PASS" if articles_count >= 20 else ("WARN" if articles_count > 0 else "FAIL"),
            score=articles_count,
            message=f"Found {articles_count} articles."
        ))
        
        checks.append(CheckResult(
            name="Source Diversity",
            status="PASS" if unique_sources >= 3 else ("WARN" if unique_sources > 0 else "FAIL"),
            score=unique_sources,
            message=f"Found {unique_sources} unique sources."
        ))
    else:
        checks.append(CheckResult(
            name="Articles Content",
            status="FAIL",
            score=0,
            message="No articles found or dataframe empty."
        ))
        
    if quality_metrics_df is not None and not quality_metrics_df.empty:
        # Assuming the quality metrics df has columns like missing_title_ratio, invalid_url_ratio, etc.
        # Here we just take a simplistic approach
        cols = quality_metrics_df.columns
        if 'missing_title' in cols and 'missing_url' in cols and 'missing_source' in cols:
            total_missing = quality_metrics_df['missing_title'].sum() + quality_metrics_df['missing_url'].sum() + quality_metrics_df['missing_source'].sum()
            total_records = len(quality_metrics_df) if len(quality_metrics_df) > 0 else 1
            missing_fields_ratio = total_missing / (total_records * 3) # rough estimate
        else:
            missing_fields_ratio = 0.0 # fallback

        if 'invalid_keyword' in cols:
            invalid_keyword_ratio = quality_metrics_df['invalid_keyword'].sum() / len(quality_metrics_df)
        else:
            invalid_keyword_ratio = 0.0

        checks.append(CheckResult(
            name="Missing Fields Ratio",
            status="PASS" if missing_fields_ratio <= 0.05 else "FAIL",
            score=missing_fields_ratio,
            message=f"Missing fields ratio: {missing_fields_ratio:.2f}"
        ))
        
    else:
        # If no quality metrics, fallback to checking articles_df
        if articles_df is not None and not articles_df.empty:
            missing_titles = articles_df['title'].isna().sum() if 'title' in articles_df.columns else 0
            missing_urls = articles_df['url'].isna().sum() if 'url' in articles_df.columns else 0
            missing_fields_ratio = (missing_titles + missing_urls) / (len(articles_df) * 2)
            
            checks.append(CheckResult(
                name="Missing Fields Ratio",
                status="PASS" if missing_fields_ratio <= 0.05 else "FAIL",
                score=missing_fields_ratio,
                message=f"Missing fields ratio: {missing_fields_ratio:.2f}"
            ))
            invalid_keyword_ratio = 0.0
        else:
            checks.append(CheckResult(
                name="Missing Fields Ratio",
                status="FAIL",
                score=1.0,
                message="Cannot compute missing fields, data is absent."
            ))

    return DataQualityResult(
        articles_count=articles_count,
        missing_fields_ratio=missing_fields_ratio,
        invalid_keyword_ratio=invalid_keyword_ratio,
        unique_sources=unique_sources,
        checks=checks
    )
