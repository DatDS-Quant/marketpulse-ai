"""Metrics generation logic for the analytics data mart."""

import pandas as pd
import datetime

def extract_date_and_source(published_at, ingested_at, processed_at):
    """Extracts YYYY-MM-DD from the available timestamps and returns (date, source_used)."""
    for val, source in [(published_at, "published_at"), (ingested_at, "ingested_at"), (processed_at, "processed_at")]:
        if pd.notna(val) and val:
            try:
                dt = pd.to_datetime(val)
                if not pd.isna(dt):
                    return dt.strftime("%Y-%m-%d"), source
            except Exception:
                pass
    return "unknown", "unknown"

def generate_articles_clean(records: list[dict]) -> pd.DataFrame:
    """Generates the clean article-level analytics table."""
    if not records:
        return pd.DataFrame(columns=[
            "id", "title", "url", "source", "keyword", "published_date", 
            "published_at", "ingested_at", "processed_at", "collected_from", 
            "content_length", "quality_flags", "quality_flag_count", 
            "has_invalid_url", "has_short_summary", "has_missing_source", "date_source"
        ])

    df = pd.DataFrame(records)
    
    # Ensure columns exist even if some records don't have them
    for col in ["published_at", "ingested_at", "processed_at", "quality_flags"]:
        if col not in df.columns:
            if col == "quality_flags":
                df[col] = [[] for _ in range(len(df))]
            else:
                df[col] = None

    dates_sources = df.apply(
        lambda row: extract_date_and_source(row.get("published_at"), row.get("ingested_at"), row.get("processed_at")),
        axis=1
    )
    df["published_date"] = [ds[0] for ds in dates_sources]
    df["date_source"] = [ds[1] for ds in dates_sources]
    
    # Process flags
    def _join_flags(flags):
        if isinstance(flags, list):
            return "|".join(flags)
        return ""
        
    df["quality_flags_str"] = df["quality_flags"].apply(_join_flags)
    df["quality_flag_count"] = df["quality_flags"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    
    df["has_invalid_url"] = df["quality_flags"].apply(lambda x: "invalid_url" in x if isinstance(x, list) else False)
    df["has_short_summary"] = df["quality_flags"].apply(lambda x: "short_summary" in x if isinstance(x, list) else False)
    df["has_missing_source"] = df["quality_flags"].apply(lambda x: "missing_source" in x if isinstance(x, list) else False)
    
    # Rename for final output
    df["quality_flags"] = df["quality_flags_str"]
    
    cols = [
        "id", "title", "url", "source", "keyword", "published_date", 
        "published_at", "ingested_at", "processed_at", "collected_from", 
        "content_length", "quality_flags", "quality_flag_count", 
        "has_invalid_url", "has_short_summary", "has_missing_source", "date_source"
    ]
    return df[cols]

def _compute_data_quality_score(row):
    penalty = (
        row["invalid_url_rate"] * 30
        + row["short_summary_rate"] * 20
        + row["missing_source_rate"] * 15
        + min(row["quality_flag_count"] / max(row["article_count"], 1), 1.0) * 10
    )
    score = 100.0 - penalty
    return round(max(0.0, min(100.0, score)), 2)

def generate_daily_keyword_metrics(articles_df: pd.DataFrame) -> pd.DataFrame:
    """Generates daily keyword KPI metrics."""
    if articles_df.empty:
        return pd.DataFrame(columns=[
            "date", "keyword", "article_count", "unique_source_count", 
            "avg_content_length", "min_content_length", "max_content_length", 
            "invalid_url_count", "short_summary_count", "missing_source_count", 
            "quality_flag_count", "invalid_url_rate", "short_summary_rate", 
            "missing_source_rate", "data_quality_score"
        ])

    grouped = articles_df.groupby(["published_date", "keyword"])
    
    metrics = grouped.agg(
        article_count=("id", "count"),
        unique_source_count=("source", "nunique"),
        avg_content_length=("content_length", "mean"),
        min_content_length=("content_length", "min"),
        max_content_length=("content_length", "max"),
        invalid_url_count=("has_invalid_url", "sum"),
        short_summary_count=("has_short_summary", "sum"),
        missing_source_count=("has_missing_source", "sum"),
        quality_flag_count=("quality_flag_count", "sum")
    ).reset_index()
    
    metrics.rename(columns={"published_date": "date"}, inplace=True)
    
    metrics["invalid_url_rate"] = (metrics["invalid_url_count"] / metrics["article_count"]).astype(float)
    metrics["short_summary_rate"] = (metrics["short_summary_count"] / metrics["article_count"]).astype(float)
    metrics["missing_source_rate"] = (metrics["missing_source_count"] / metrics["article_count"]).astype(float)
    
    metrics["data_quality_score"] = metrics.apply(_compute_data_quality_score, axis=1)
    
    # Ensure average length is float and others are standard types
    metrics["avg_content_length"] = metrics["avg_content_length"].round(2)
    
    return metrics

def _compute_source_quality_score(row):
    penalty = (
        row["invalid_url_rate"] * 35
        + row["short_summary_rate"] * 25
        + min(row["quality_flag_count"] / max(row["article_count"], 1), 1.0) * 15
    )
    score = 100.0 - penalty
    return round(max(0.0, min(100.0, score)), 2)

def generate_source_metrics(articles_df: pd.DataFrame) -> pd.DataFrame:
    """Generates source-level KPI metrics."""
    if articles_df.empty:
        return pd.DataFrame(columns=[
            "source", "article_count", "unique_keyword_count", "avg_content_length", 
            "invalid_url_count", "short_summary_count", "missing_source_count", 
            "quality_flag_count", "invalid_url_rate", "short_summary_rate", 
            "source_quality_score", "latest_seen_at"
        ])

    # create seen_at column for aggregation
    def get_seen_at(row):
        pub = row.get("published_at")
        if pd.notna(pub) and pub: return pub
        return row.get("processed_at")
        
    df_copy = articles_df.copy()
    df_copy["seen_at"] = df_copy.apply(get_seen_at, axis=1)
    
    grouped = df_copy.groupby("source")
    
    metrics = grouped.agg(
        article_count=("id", "count"),
        unique_keyword_count=("keyword", "nunique"),
        avg_content_length=("content_length", "mean"),
        invalid_url_count=("has_invalid_url", "sum"),
        short_summary_count=("has_short_summary", "sum"),
        missing_source_count=("has_missing_source", "sum"),
        quality_flag_count=("quality_flag_count", "sum"),
        latest_seen_at=("seen_at", "max")
    ).reset_index()
    
    metrics["invalid_url_rate"] = (metrics["invalid_url_count"] / metrics["article_count"]).astype(float)
    metrics["short_summary_rate"] = (metrics["short_summary_count"] / metrics["article_count"]).astype(float)
    
    metrics["source_quality_score"] = metrics.apply(_compute_source_quality_score, axis=1)
    
    metrics["avg_content_length"] = metrics["avg_content_length"].round(2)
    
    cols = [
        "source", "article_count", "unique_keyword_count", "avg_content_length", 
        "invalid_url_count", "short_summary_count", "missing_source_count", 
        "quality_flag_count", "invalid_url_rate", "short_summary_rate", 
        "source_quality_score", "latest_seen_at"
    ]
    return metrics[cols]

def generate_quality_metrics(
    run_id: str, 
    input_path: str, 
    total_processed_records: int, 
    articles_df: pd.DataFrame, 
    keyword_df: pd.DataFrame, 
    source_df: pd.DataFrame
) -> pd.DataFrame:
    """Generates a single-row summary table for the analytics run."""
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    article_rows = len(articles_df)
    
    if article_rows > 0:
        invalid_url_count = articles_df["has_invalid_url"].sum()
        short_summary_count = articles_df["has_short_summary"].sum()
        missing_source_count = articles_df["has_missing_source"].sum()
        avg_len = round(articles_df["content_length"].mean(), 2)
        total_flags = articles_df["quality_flag_count"].sum()
        
        inv_rate = invalid_url_count / article_rows
        short_rate = short_summary_count / article_rows
        miss_rate = missing_source_count / article_rows
        
        penalty = (
            inv_rate * 30 +
            short_rate * 20 +
            miss_rate * 15 +
            min(total_flags / article_rows, 1.0) * 10
        )
        score = round(max(0.0, min(100.0, 100.0 - penalty)), 2)
    else:
        invalid_url_count = 0
        short_summary_count = 0
        missing_source_count = 0
        avg_len = 0.0
        score = 100.0
        
    data = [{
        "run_id": run_id,
        "date": date_str,
        "input_path": str(input_path),
        "total_records": total_processed_records,
        "article_rows": article_rows,
        "keyword_metric_rows": len(keyword_df),
        "source_metric_rows": len(source_df),
        "invalid_url_count": int(invalid_url_count),
        "short_summary_count": int(short_summary_count),
        "missing_source_count": int(missing_source_count),
        "average_content_length": avg_len,
        "overall_quality_score": score,
        "created_at": created_at
    }]
    
    return pd.DataFrame(data)
