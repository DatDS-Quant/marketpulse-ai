"""Tests for ETL data processing module."""

import json
from src.processing.validation import validate_and_format_record
from src.processing.dedup import deduplicate_records
from src.processing.run_etl import run_etl

def test_valid_raw_record():
    """Test that a valid raw record becomes a processed record."""
    record = {
        "id": "1",
        "title": "Valid Title",
        "url": "https://example.com",
        "source": "Test Source",
        "summary": "This is a long enough summary.",
        "keyword": "AI",
        "collected_from": "sample"
    }
    article, flags = validate_and_format_record(record)
    assert article is not None
    assert article.id == "1"
    assert article.title == "Valid Title"
    assert isinstance(article.quality_flags, list)
    assert len(flags) == 0
    assert article.processed_at is not None
    assert article.content_length == 30

def test_missing_title_rejected():
    """Test that a record with missing title is rejected."""
    record = {
        "id": "2",
        "title": "",
        "url": "https://example.com",
        "source": "Test Source",
        "keyword": "AI",
        "collected_from": "sample"
    }
    article, flags = validate_and_format_record(record)
    assert article is None
    assert "missing_title" in flags

def test_missing_url_rejected():
    """Test that a record with missing URL is rejected."""
    record = {
        "id": "3",
        "title": "Title",
        "url": "",
        "source": "Test Source",
        "keyword": "AI",
        "collected_from": "sample"
    }
    article, flags = validate_and_format_record(record)
    assert article is None
    assert "missing_url" in flags

def test_invalid_url_flagged():
    """Test that an invalid-looking URL is flagged but kept."""
    record = {
        "id": "4",
        "title": "Title",
        "url": "not-a-url",
        "source": "Test Source",
        "keyword": "AI",
        "collected_from": "sample"
    }
    article, flags = validate_and_format_record(record)
    assert article is not None
    assert "invalid_url" in flags

def test_deduplicate_records():
    """Test that duplicate URLs and IDs are removed."""
    record1 = {
        "id": "1", "title": "Title 1", "url": "https://example.com/1",
        "source": "Source", "keyword": "AI", "collected_from": "sample"
    }
    record2 = {
        "id": "1", "title": "Title 2", "url": "https://example.com/2",
        "source": "Source", "keyword": "AI", "collected_from": "sample"
    }
    record3 = {
        "id": "3", "title": "Title 3", "url": "https://example.com/1",
        "source": "Source", "keyword": "AI", "collected_from": "sample"
    }
    
    a1, _ = validate_and_format_record(record1)
    a2, _ = validate_and_format_record(record2)
    a3, _ = validate_and_format_record(record3)
    
    unique_articles = deduplicate_records([a1, a2, a3])
    assert len(unique_articles) == 1
    assert unique_articles[0].id == "1"

def test_content_length_calculated():
    """Test that content_length is correctly calculated."""
    record = {
        "id": "5",
        "title": "Title",
        "url": "https://example.com",
        "source": "Test Source",
        "keyword": "AI",
        "raw_text": "This is raw text",
        "collected_from": "sample"
    }
    article, _ = validate_and_format_record(record)
    assert article.content_length == 16

def test_etl_run_with_test_data(monkeypatch, tmp_path):
    """Test the full ETL flow using temporary data without internet."""
    raw_dir = tmp_path / "data" / "raw"
    processed_dir = tmp_path / "data" / "processed"
    logs_dir = tmp_path / "logs"
    
    raw_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)
    logs_dir.mkdir(parents=True)
    
    mock_raw_data = [
        {
            "id": "1", "title": "Valid", "url": "https://example.com/1",
            "source": "Source", "keyword": "AI", "collected_from": "sample"
        },
        {
            "id": "2", "title": "", "url": "https://example.com/2",
            "source": "Source", "keyword": "AI", "collected_from": "sample"
        }
    ]
    
    raw_file = raw_dir / "ingestion_20240101_000000.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(mock_raw_data, f)
        
    import src.utils.config
    import src.processing.run_etl
    monkeypatch.setattr(src.utils.config, "RAW_DATA_DIR", raw_dir)
    monkeypatch.setattr(src.processing.run_etl, "RAW_DATA_DIR", raw_dir)
    monkeypatch.setattr(src.utils.config, "PROCESSED_DATA_DIR", processed_dir)
    monkeypatch.setattr(src.processing.run_etl, "PROCESSED_DATA_DIR", processed_dir)
    monkeypatch.setattr(src.utils.config, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(src.processing.run_etl, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(src.utils.config, "SAMPLE_DATA_DIR", raw_dir)
    monkeypatch.setattr(src.processing.run_etl, "SAMPLE_DATA_DIR", raw_dir)
    
    run_etl()
    
    processed_files = list(processed_dir.glob("processed_*.json"))
    report_files = list(processed_dir.glob("data_quality_report_*.json"))
    log_file = logs_dir / "processing_runs.jsonl"
    
    assert len(processed_files) == 1
    assert len(report_files) == 1
    assert log_file.exists()
    
    with open(processed_files[0], "r", encoding="utf-8") as f:
        processed_data = json.load(f)
        assert len(processed_data) == 1
        assert processed_data[0]["id"] == "1"
        
    with open(report_files[0], "r", encoding="utf-8") as f:
        report = json.load(f)
        assert report["total_raw_records"] == 2
        assert report["valid_records"] == 1
        assert report["invalid_records"] == 1
