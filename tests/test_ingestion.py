import pytest
from src.collectors.rss_collector import generate_stable_id, normalize_article
from src.collectors.sample_loader import load_sample_data
from src.collectors.run_ingestion import save_raw_data

class MockFeedEntry:
    def __init__(self, title, link, summary, published, source_title):
        self.title = title
        self.link = link
        self.summary = summary
        self.published = published
        self.source = {'title': source_title}

def test_generate_stable_id():
    """Test that ID generation is stable and uses SHA-256."""
    url = "https://example.com/test-article"
    title = "Test Article"
    keyword = "AI tools"
    
    id1 = generate_stable_id(url, title, keyword)
    id2 = generate_stable_id(url, title, keyword)
    
    assert id1 == id2
    assert len(id1) == 64  # SHA-256 hex digest length
    
    # Test fallback to title + keyword if URL is empty
    id3 = generate_stable_id("", title, keyword)
    assert id3 != id1
    assert len(id3) == 64

def test_normalize_article():
    """Test that a feedparser entry is correctly normalized into our schema."""
    entry = MockFeedEntry(
        title="Test News",
        link="https://example.com/news",
        summary="A summary of the news.",
        published="Wed, 17 Jun 2026 12:00:00 GMT",
        source_title="Test Source"
    )
    
    record = normalize_article(entry, "AI Test")
    
    assert record["title"] == "Test News"
    assert record["url"] == "https://example.com/news"
    assert record["summary"] == "A summary of the news."
    assert record["source"] == "Test Source"
    assert record["keyword"] == "AI Test"
    assert record["collected_from"] == "rss"
    assert "id" in record
    assert "published_at" in record
    assert "ingested_at" in record
    assert record["raw_text"] is None

def test_sample_fallback():
    """Test that the sample loader returns records and marks them correctly."""
    records = load_sample_data()
    
    assert len(records) > 0
    for record in records:
        assert record["collected_from"] == "sample"
        assert "id" in record
        assert "title" in record
        assert "url" in record
        assert "ingested_at" in record

def test_save_raw_data(tmp_path, monkeypatch):
    """Test that saving raw data works and produces a JSON file."""
    # Monkeypatch RAW_DATA_DIR to point to tmp_path for testing
    import src.utils.config
    monkeypatch.setattr(src.utils.config, "RAW_DATA_DIR", tmp_path)
    # Monkeypatch in run_ingestion to use the updated config
    import src.collectors.run_ingestion
    monkeypatch.setattr(src.collectors.run_ingestion, "RAW_DATA_DIR", tmp_path)
    
    mock_records = [{"id": "1", "title": "Mock"}]
    output_path = save_raw_data(mock_records)
    
    import os
    import json
    assert os.path.exists(output_path)
    
    with open(output_path, "r", encoding="utf-8") as f:
        loaded_records = json.load(f)
        
    assert len(loaded_records) == 1
    assert loaded_records[0]["title"] == "Mock"
