"""Insight seeds generation logic for analytics data mart."""

import pandas as pd
import datetime

def generate_insight_seeds(articles_df: pd.DataFrame, source_df: pd.DataFrame, overall_quality_score: float) -> pd.DataFrame:
    """Generates structured insight seeds based on analytics metrics."""
    seeds = []
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if articles_df.empty:
        return pd.DataFrame(columns=[
            "insight_type", "entity", "metric_name", "metric_value", 
            "comparison_value", "change_percentage", "severity", 
            "explanation_seed", "created_at"
        ])
    
    # 1. high_volume_keyword
    keyword_counts = articles_df["keyword"].value_counts()
    if not keyword_counts.empty:
        top_keyword = keyword_counts.index[0]
        top_count = int(keyword_counts.values[0])
        seeds.append({
            "insight_type": "high_volume_keyword",
            "entity": top_keyword,
            "metric_name": "article_count",
            "metric_value": top_count,
            "comparison_value": None,
            "change_percentage": None,
            "severity": "low",
            "explanation_seed": f"Keyword '{top_keyword}' has the highest article volume with {top_count} articles.",
            "created_at": created_at
        })
        
    # 2. broad_source_coverage
    if not articles_df.empty:
        keyword_sources = articles_df.groupby("keyword")["source"].nunique()
        if not keyword_sources.empty:
            broad_keyword = keyword_sources.idxmax()
            broad_count = int(keyword_sources.max())
            seeds.append({
                "insight_type": "broad_source_coverage",
                "entity": broad_keyword,
                "metric_name": "unique_source_count",
                "metric_value": broad_count,
                "comparison_value": None,
                "change_percentage": None,
                "severity": "low",
                "explanation_seed": f"Keyword '{broad_keyword}' has the broadest source coverage with {broad_count} unique sources.",
                "created_at": created_at
            })
            
    # 3. source_quality_leader
    if not source_df.empty:
        top_source_idx = source_df["source_quality_score"].idxmax()
        if pd.notna(top_source_idx):
            top_source = source_df.loc[top_source_idx]
            source_name = top_source["source"]
            score_val = float(top_source["source_quality_score"])
            seeds.append({
                "insight_type": "source_quality_leader",
                "entity": source_name,
                "metric_name": "source_quality_score",
                "metric_value": score_val,
                "comparison_value": None,
                "change_percentage": None,
                "severity": "low",
                "explanation_seed": f"Source '{source_name}' is the quality leader with a score of {score_val}.",
                "created_at": created_at
            })
            
    # 4. source_quality_warning
    if not source_df.empty:
        low_sources = source_df[source_df["source_quality_score"] < 70]
        for _, row in low_sources.iterrows():
            source_name = row["source"]
            score_val = float(row["source_quality_score"])
            sev = "high" if score_val < 50 else "medium"
            seeds.append({
                "insight_type": "source_quality_warning",
                "entity": source_name,
                "metric_name": "source_quality_score",
                "metric_value": score_val,
                "comparison_value": None,
                "change_percentage": None,
                "severity": sev,
                "explanation_seed": f"Source '{source_name}' has a low quality score of {score_val}.",
                "created_at": created_at
            })
            
    # 5. data_quality_warning
    sev = "high" if overall_quality_score < 70 else "medium" if overall_quality_score < 85 else "low"
    seeds.append({
        "insight_type": "data_quality_warning",
        "entity": "overall pipeline",
        "metric_name": "overall_quality_score",
        "metric_value": overall_quality_score,
        "comparison_value": None,
        "change_percentage": None,
        "severity": sev,
        "explanation_seed": f"Overall data quality score is {overall_quality_score}.",
        "created_at": created_at
    })
    
    # 6. short_summary_warning
    short_summary_count = articles_df["has_short_summary"].sum()
    article_rows = len(articles_df)
    short_summary_rate = short_summary_count / max(article_rows, 1)
    if short_summary_rate > 0.1:
        sev = "high" if short_summary_rate > 0.3 else "medium"
        seeds.append({
            "insight_type": "short_summary_warning",
            "entity": "summary_quality",
            "metric_name": "short_summary_rate",
            "metric_value": round(short_summary_rate, 4),
            "comparison_value": None,
            "change_percentage": None,
            "severity": sev,
            "explanation_seed": f"Short summary rate is elevated at {short_summary_rate:.2%}.",
            "created_at": created_at
        })
        
    cols = [
        "insight_type", "entity", "metric_name", "metric_value", 
        "comparison_value", "change_percentage", "severity", 
        "explanation_seed", "created_at"
    ]
    if seeds:
        return pd.DataFrame(seeds)[cols]
    else:
        return pd.DataFrame(columns=cols)
