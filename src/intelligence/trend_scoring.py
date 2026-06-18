"""Trend scoring logic for Module 4."""

import datetime
import pandas as pd

def classify_signal_type(row: pd.Series) -> str:
    """Classifies the trend signal deterministically."""
    if row["article_count"] < 3:
        return "weak_signal"
    elif row["growth_rate"] >= 0.25 and row["article_count"] >= 3 and row["confidence_score"] >= 60:
        return "rising_keyword"
    elif row["article_count"] >= 10 and row["trend_score"] >= 60:
        return "high_volume_keyword"
    elif row["trend_score"] >= 60 and row["confidence_score"] < 60:
        return "low_confidence_trend"
    elif row["freshness_score"] < 70:
        return "stale_data_warning"
    else:
        return "stable_keyword"

def determine_severity(row: pd.Series) -> str:
    """Determines the severity deterministically."""
    if row["signal_type"] == "stale_data_warning" and row["freshness_score"] < 50:
        return "high"
    elif row["trend_score"] >= 80 and row["confidence_score"] >= 70:
        return "high"
    elif row["trend_score"] >= 60:
        return "medium"
    else:
        return "low"

def calculate_trend_metrics(keyword_df: pd.DataFrame, freshness_score: float) -> pd.DataFrame:
    """
    Calculates deterministically mathematically sound trend metrics.
    """
    if keyword_df.empty:
        return pd.DataFrame(columns=[
            "date", "keyword", "article_count", "previous_article_count", "article_count_change",
            "growth_rate", "keyword_share", "unique_source_count", "source_diversity_score",
            "data_quality_score", "freshness_score", "quality_adjusted_score", "trend_score",
            "confidence_score", "signal_type", "severity", "created_at"
        ])

    df = keyword_df.copy()
    
    # 1. Sort by keyword and date
    df = df.sort_values(by=["keyword", "date"])
    
    # 2. Previous Article Count & Growth
    df["previous_article_count"] = df.groupby("keyword")["article_count"].shift(1).fillna(0).astype(int)
    df["article_count_change"] = df["article_count"] - df["previous_article_count"]
    df["growth_rate"] = df["article_count_change"] / df["previous_article_count"].clip(lower=1)
    
    # 3. Keyword Share
    total_per_date = df.groupby("date")["article_count"].transform("sum")
    df["keyword_share"] = df["article_count"] / total_per_date.clip(lower=1)
    
    # 4. Volume and Growth Score
    df["volume_score"] = (df["article_count"] / 20.0).clip(upper=1.0) * 100.0
    df["growth_score"] = df["growth_rate"].clip(lower=0.0, upper=2.0) / 2.0 * 100.0
    
    # 5. Source Diversity
    ratio_score = (df["unique_source_count"] / df["article_count"].clip(lower=1)) * 100.0
    vol_score = (df["unique_source_count"] / 5.0).clip(upper=1.0) * 100.0
    df["source_diversity_score"] = (0.6 * ratio_score + 0.4 * vol_score).clip(lower=0.0, upper=100.0)
    
    # 6. Quality and Freshness
    # data_quality_score already in keyword_df from Module 3
    df["freshness_score"] = freshness_score
    
    df["quality_adjusted_score"] = (df["volume_score"] * (df["data_quality_score"] / 100.0)).clip(lower=0.0, upper=100.0)
    
    # 7. Trend and Confidence Scores
    df["trend_score"] = (
        0.35 * df["volume_score"] +
        0.30 * df["growth_score"] +
        0.15 * df["source_diversity_score"] +
        0.10 * df["data_quality_score"] +
        0.10 * df["freshness_score"]
    ).clip(lower=0.0, upper=100.0)
    
    df["confidence_score"] = (
        0.40 * df["data_quality_score"] +
        0.30 * df["source_diversity_score"] +
        0.20 * df["freshness_score"] +
        0.10 * df["volume_score"]
    ).clip(lower=0.0, upper=100.0)
    
    # Round scores to 2 decimals
    score_cols = [
        "growth_rate", "keyword_share", "source_diversity_score", 
        "quality_adjusted_score", "trend_score", "confidence_score", "freshness_score"
    ]
    df[score_cols] = df[score_cols].round(2)
    
    # 8. Signals and Severity
    df["signal_type"] = df.apply(classify_signal_type, axis=1)
    df["severity"] = df.apply(determine_severity, axis=1)
    
    # 9. Meta
    df["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Keep only necessary columns
    out_cols = [
        "date", "keyword", "article_count", "previous_article_count", "article_count_change",
        "growth_rate", "keyword_share", "unique_source_count", "source_diversity_score",
        "data_quality_score", "freshness_score", "quality_adjusted_score", "trend_score",
        "confidence_score", "signal_type", "severity", "created_at"
    ]
    return df[out_cols]
