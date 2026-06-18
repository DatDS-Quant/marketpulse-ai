"""Tests for Trend Detection & Insight Metrics (Module 4)."""

import pytest
import pandas as pd
import datetime
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.intelligence.trend_scoring import calculate_trend_metrics, classify_signal_type, determine_severity
from src.intelligence.trend_loaders import get_latest_analytics_run_time
from src.intelligence.trend_summary import generate_top_trends, generate_trend_summary

@pytest.fixture
def mock_keyword_df():
    data = [
        {"date": "2026-06-16", "keyword": "AI agents business", "article_count": 10, "unique_source_count": 5, "data_quality_score": 90.0},
        {"date": "2026-06-17", "keyword": "AI agents business", "article_count": 15, "unique_source_count": 6, "data_quality_score": 92.0},
        {"date": "2026-06-17", "keyword": "EdTech AI", "article_count": 2, "unique_source_count": 1, "data_quality_score": 80.0},
        {"date": "2026-06-17", "keyword": "content automation", "article_count": 12, "unique_source_count": 4, "data_quality_score": 85.0},
    ]
    return pd.DataFrame(data)

def test_growth_rate_and_previous_count(mock_keyword_df):
    """Test growth rate calculation and avoidance of div zero."""
    metrics = calculate_trend_metrics(mock_keyword_df, freshness_score=100.0)
    
    # Check AI agents business on 2026-06-17
    row = metrics[(metrics["keyword"] == "AI agents business") & (metrics["date"] == "2026-06-17")].iloc[0]
    assert row["previous_article_count"] == 10
    assert row["article_count_change"] == 5
    assert row["growth_rate"] == 0.5  # 5 / 10
    
    # Check EdTech AI on 2026-06-17 (first appearance)
    row_edtech = metrics[(metrics["keyword"] == "EdTech AI")].iloc[0]
    assert row_edtech["previous_article_count"] == 0
    assert row_edtech["article_count_change"] == 2
    # growth rate = 2 / max(0, 1) = 2.0
    assert row_edtech["growth_rate"] == 2.0

def test_keyword_share(mock_keyword_df):
    metrics = calculate_trend_metrics(mock_keyword_df, freshness_score=100.0)
    # Total on 2026-06-17 = 15 + 2 + 12 = 29
    row = metrics[(metrics["keyword"] == "AI agents business") & (metrics["date"] == "2026-06-17")].iloc[0]
    assert round(row["keyword_share"], 2) == round(15 / 29, 2)

def test_source_diversity_bounded(mock_keyword_df):
    metrics = calculate_trend_metrics(mock_keyword_df, freshness_score=100.0)
    assert metrics["source_diversity_score"].min() >= 0.0
    assert metrics["source_diversity_score"].max() <= 100.0

def test_trend_and_confidence_scores_bounded(mock_keyword_df):
    metrics = calculate_trend_metrics(mock_keyword_df, freshness_score=100.0)
    assert metrics["trend_score"].min() >= 0.0
    assert metrics["trend_score"].max() <= 100.0
    assert metrics["confidence_score"].min() >= 0.0
    assert metrics["confidence_score"].max() <= 100.0

def test_signal_classification():
    # Weak signal: < 3 articles
    assert classify_signal_type({"article_count": 2, "growth_rate": 0.5, "confidence_score": 80, "trend_score": 70, "freshness_score": 100}) == "weak_signal"
    # Rising keyword: growth >= 0.25, count >= 3, conf >= 60
    assert classify_signal_type({"article_count": 5, "growth_rate": 0.3, "confidence_score": 65, "trend_score": 50, "freshness_score": 100}) == "rising_keyword"
    # High volume: count >= 10, trend >= 60
    assert classify_signal_type({"article_count": 12, "growth_rate": 0.1, "confidence_score": 65, "trend_score": 65, "freshness_score": 100}) == "high_volume_keyword"
    # Low confidence: trend >= 60, conf < 60
    assert classify_signal_type({"article_count": 8, "growth_rate": 0.1, "confidence_score": 50, "trend_score": 65, "freshness_score": 100}) == "low_confidence_trend"
    # Stale: freshness < 70
    assert classify_signal_type({"article_count": 8, "growth_rate": 0.1, "confidence_score": 80, "trend_score": 50, "freshness_score": 60}) == "stale_data_warning"
    # Stable
    assert classify_signal_type({"article_count": 8, "growth_rate": 0.1, "confidence_score": 80, "trend_score": 50, "freshness_score": 100}) == "stable_keyword"

def test_severity_classification():
    # High via stale data warning
    assert determine_severity({"signal_type": "stale_data_warning", "freshness_score": 40, "trend_score": 50, "confidence_score": 50}) == "high"
    # High via scores
    assert determine_severity({"signal_type": "stable_keyword", "freshness_score": 100, "trend_score": 85, "confidence_score": 75}) == "high"
    # Medium
    assert determine_severity({"signal_type": "stable_keyword", "freshness_score": 100, "trend_score": 65, "confidence_score": 50}) == "medium"
    # Low
    assert determine_severity({"signal_type": "stable_keyword", "freshness_score": 100, "trend_score": 50, "confidence_score": 50}) == "low"

def test_top_trends_ranking(mock_keyword_df):
    metrics = calculate_trend_metrics(mock_keyword_df, freshness_score=100.0)
    top_trends = generate_top_trends(metrics)
    
    # Should only return the latest dates per keyword (3 keywords total)
    assert len(top_trends) == 3
    # content automation should be ranked first due to max growth score (12.0 growth rate -> 100 growth score)
    assert top_trends.iloc[0]["keyword"] == "content automation"
    # Check explanation seed format
    seed = top_trends.iloc[0]["explanation_seed"]
    assert "content automation" in seed
    assert "top ranked keyword" in seed

def test_freshness_extraction():
    manifest = {"created_at": "2026-06-18T10:00:00+00:00"}
    quality_df = pd.DataFrame({"created_at": ["2026-06-17T10:00:00+00:00"]})
    
    ts1 = get_latest_analytics_run_time(manifest, pd.DataFrame())
    assert ts1 is not None and ts1.day == 18
    
    ts2 = get_latest_analytics_run_time({}, quality_df)
    assert ts2 is not None and ts2.day == 17
    
    ts3 = get_latest_analytics_run_time({}, pd.DataFrame())
    assert ts3 is None

def test_trend_summary_generation(mock_keyword_df):
    metrics = calculate_trend_metrics(mock_keyword_df, freshness_score=100.0)
    top_trends = generate_top_trends(metrics)
    summary = generate_trend_summary(
        "test_run", metrics, top_trends, 100.0, 
        datetime.datetime.now(datetime.timezone.utc), 
        {}, {}
    )
    
    assert summary["module"] == "trend_detection"
    assert summary["freshness_status"] == "fresh"
    assert summary["top_keyword"] == "content automation"
    assert "top_trend" in summary["summary_cards"]
    assert summary["trend_metric_rows"] == 4
    assert summary["top_trend_rows"] == 3

@patch("src.intelligence.run_trends.check_analytics_files_exist", return_value=False)
@patch("sys.exit")
def test_runner_graceful_exit(mock_exit, mock_check, capsys):
    from src.intelligence.run_trends import run_trends
    run_trends()
    captured = capsys.readouterr()
    assert "No analytics data found" in captured.out
    mock_exit.assert_called_once_with(0)
