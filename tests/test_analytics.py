"""Tests for analytics data mart module."""

import json
import pandas as pd
from pathlib import Path

from src.analytics.loaders import find_latest_processed_file, load_processed_records
from src.analytics.metrics import (
    generate_articles_clean,
    generate_daily_keyword_metrics,
    generate_source_metrics,
    generate_quality_metrics
)
from src.analytics.insight_seeds import generate_insight_seeds
from src.analytics.run_analytics import run_analytics

def test_find_latest_processed_file(monkeypatch, tmp_path):
    import src.utils.config
    import src.analytics.loaders
    
    proc_dir = tmp_path / "processed"
    proc_dir.mkdir()
    
    monkeypatch.setattr(src.utils.config, "PROCESSED_DATA_DIR", proc_dir)
    monkeypatch.setattr(src.analytics.loaders, "PROCESSED_DATA_DIR", proc_dir)
    
    # Empty dir
    assert find_latest_processed_file() is None
    
    # Add files
    file1 = proc_dir / "processed_20260101_000000.json"
    file2 = proc_dir / "processed_20260102_000000.json"
    file1.touch()
    file2.touch()
    
    latest = find_latest_processed_file()
    assert latest == file2

def test_articles_clean_generation():
    records = [
        {
            "id": "1",
            "title": "Title 1",
            "url": "http://example.com/1",
            "source": "Source A",
            "published_at": "2026-06-18T10:00:00Z",
            "ingested_at": "2026-06-18T11:00:00Z",
            "processed_at": "2026-06-18T12:00:00Z",
            "keyword": "AI",
            "content_length": 100,
            "quality_flags": ["invalid_url", "short_summary"],
            "collected_from": "rss"
        },
        {
            "id": "2",
            "title": "Title 2",
            "url": "http://example.com/2",
            "source": "Source B",
            "published_at": None,
            "ingested_at": "2026-06-19T11:00:00Z",
            "processed_at": "2026-06-19T12:00:00Z",
            "keyword": "ML",
            "content_length": 50,
            "quality_flags": [],
            "collected_from": "sample"
        }
    ]
    
    df = generate_articles_clean(records)
    
    # Expected columns
    expected_cols = [
        "id", "title", "url", "source", "keyword", "published_date", 
        "published_at", "ingested_at", "processed_at", "collected_from", 
        "content_length", "quality_flags", "quality_flag_count", 
        "has_invalid_url", "has_short_summary", "has_missing_source", "date_source"
    ]
    for col in expected_cols:
        assert col in df.columns
        
    assert len(df) == 2
    
    # Row 1 flags and dates
    row1 = df.iloc[0]
    assert row1["published_date"] == "2026-06-18"
    assert row1["date_source"] == "published_at"
    assert row1["quality_flags"] == "invalid_url|short_summary"
    assert row1["quality_flag_count"] == 2
    assert bool(row1["has_invalid_url"]) is True
    assert bool(row1["has_short_summary"]) is True
    assert bool(row1["has_missing_source"]) is False
    
    # Row 2 dates fallback
    row2 = df.iloc[1]
    assert row2["published_date"] == "2026-06-19"
    assert row2["date_source"] == "ingested_at"
    assert row2["quality_flags"] == ""
    assert row2["quality_flag_count"] == 0

def test_daily_keyword_metrics():
    records = [
        {"id": "1", "source": "A", "keyword": "AI", "published_date": "2026-06-18", "content_length": 100, "quality_flags": ["invalid_url"], "quality_flag_count": 1, "has_invalid_url": True, "has_short_summary": False, "has_missing_source": False},
        {"id": "2", "source": "B", "keyword": "AI", "published_date": "2026-06-18", "content_length": 200, "quality_flags": [], "quality_flag_count": 0, "has_invalid_url": False, "has_short_summary": False, "has_missing_source": False},
        {"id": "3", "source": "A", "keyword": "ML", "published_date": "2026-06-18", "content_length": 50, "quality_flags": ["short_summary"], "quality_flag_count": 1, "has_invalid_url": False, "has_short_summary": True, "has_missing_source": False},
    ]
    df = pd.DataFrame(records)
    
    metrics = generate_daily_keyword_metrics(df)
    assert len(metrics) == 2 # 2 keywords
    
    ai_row = metrics[metrics["keyword"] == "AI"].iloc[0]
    assert ai_row["article_count"] == 2
    assert ai_row["unique_source_count"] == 2
    assert ai_row["avg_content_length"] == 150.0
    assert ai_row["invalid_url_count"] == 1
    assert ai_row["invalid_url_rate"] == 0.5
    
    # 100 - 0.5 * 30 - 0 - 0 - (1/2)*10 = 100 - 15 - 5 = 80
    assert ai_row["data_quality_score"] == 80.0
    
def test_source_metrics():
    records = [
        {"id": "1", "source": "A", "keyword": "AI", "published_at": "2026-06-18T10:00", "processed_at": "2026-06-18T11:00", "content_length": 100, "quality_flags": ["invalid_url"], "quality_flag_count": 1, "has_invalid_url": True, "has_short_summary": False, "has_missing_source": False},
        {"id": "2", "source": "A", "keyword": "ML", "published_at": "2026-06-19T10:00", "processed_at": "2026-06-19T11:00", "content_length": 200, "quality_flags": ["invalid_url"], "quality_flag_count": 1, "has_invalid_url": True, "has_short_summary": False, "has_missing_source": False},
    ]
    df = pd.DataFrame(records)
    
    metrics = generate_source_metrics(df)
    assert len(metrics) == 1
    
    row = metrics.iloc[0]
    assert row["source"] == "A"
    assert row["article_count"] == 2
    assert row["unique_keyword_count"] == 2
    assert row["invalid_url_rate"] == 1.0
    assert row["latest_seen_at"] == "2026-06-19T10:00"
    
    # 100 - 1.0 * 35 - 0 - (2/2)*15 = 100 - 35 - 15 = 50
    assert row["source_quality_score"] == 50.0
    
def test_quality_metrics():
    # Empty dataframes should return 1 row with 100 score
    qm = generate_quality_metrics("run_1", "path", 0, pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    assert len(qm) == 1
    assert qm["overall_quality_score"].iloc[0] == 100.0
    assert qm["article_rows"].iloc[0] == 0
    
def test_insight_seeds():
    articles_df = pd.DataFrame([
        {"id": "1", "source": "A", "keyword": "AI", "has_short_summary": True},
        {"id": "2", "source": "A", "keyword": "AI", "has_short_summary": False},
        {"id": "3", "source": "B", "keyword": "AI", "has_short_summary": False},
    ])
    source_df = pd.DataFrame([
        {"source": "A", "source_quality_score": 40.0},
        {"source": "B", "source_quality_score": 90.0},
    ])
    
    seeds = generate_insight_seeds(articles_df, source_df, 60.0)
    
    assert len(seeds) > 0
    types = seeds["insight_type"].tolist()
    assert "high_volume_keyword" in types
    assert "broad_source_coverage" in types
    assert "source_quality_leader" in types
    assert "source_quality_warning" in types
    assert "data_quality_warning" in types
    assert "short_summary_warning" in types
    
    sqw = seeds[seeds["insight_type"] == "source_quality_warning"].iloc[0]
    assert sqw["entity"] == "A"
    assert sqw["severity"] == "high" # since 40 < 50
    
    ssw = seeds[seeds["insight_type"] == "short_summary_warning"].iloc[0]
    assert abs(ssw["metric_value"] - 1/3) < 0.001 # 33%

def test_empty_input_graceful():
    articles_df = generate_articles_clean([])
    assert articles_df.empty
    
    kw_metrics = generate_daily_keyword_metrics(articles_df)
    assert kw_metrics.empty
    assert "data_quality_score" in kw_metrics.columns
    
    src_metrics = generate_source_metrics(articles_df)
    assert src_metrics.empty
    
    qual_metrics = generate_quality_metrics("run_1", "path", 0, articles_df, kw_metrics, src_metrics)
    assert len(qual_metrics) == 1
    
    seeds = generate_insight_seeds(articles_df, src_metrics, 100.0)
    assert seeds.empty
    assert "insight_type" in seeds.columns

def test_run_analytics_e2e(monkeypatch, tmp_path):
    proc_dir = tmp_path / "processed"
    analytics_dir = tmp_path / "analytics"
    logs_dir = tmp_path / "logs"
    
    proc_dir.mkdir()
    analytics_dir.mkdir()
    logs_dir.mkdir()
    
    # Mock data
    mock_records = [{
        "id": "1", "title": "Valid", "url": "http://x.com", "source": "S", 
        "published_at": "2026-06-18T10:00:00Z", "keyword": "AI", 
        "content_length": 100, "quality_flags": [], "collected_from": "rss",
        "processed_at": "2026-06-18T11:00:00Z"
    }]
    file_path = proc_dir / "processed_2026.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(mock_records, f)
        
    import src.utils.config
    import src.analytics.run_analytics
    import src.analytics.loaders
    
    monkeypatch.setattr(src.utils.config, "PROCESSED_DATA_DIR", proc_dir)
    monkeypatch.setattr(src.analytics.loaders, "PROCESSED_DATA_DIR", proc_dir)
    monkeypatch.setattr(src.utils.config, "ANALYTICS_DATA_DIR", analytics_dir)
    monkeypatch.setattr(src.analytics.run_analytics, "ANALYTICS_DATA_DIR", analytics_dir)
    monkeypatch.setattr(src.utils.config, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(src.analytics.run_analytics, "LOGS_DIR", logs_dir)
    
    run_analytics()
    
    assert (analytics_dir / "articles_clean.csv").exists()
    assert (analytics_dir / "daily_keyword_metrics.csv").exists()
    assert (analytics_dir / "source_metrics.csv").exists()
    assert (analytics_dir / "quality_metrics.csv").exists()
    assert (analytics_dir / "insight_seed_metrics.csv").exists()
    assert (analytics_dir / "analytics_manifest.json").exists()
    assert (logs_dir / "analytics_runs.jsonl").exists()
