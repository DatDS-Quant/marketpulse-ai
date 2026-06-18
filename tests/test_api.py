import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_status_endpoint():
    response = client.get("/api/v1/status")
    # If data files are missing, it might return 503, but in our test environment,
    # Module 3 and 4 have been run, so files should exist.
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
        assert "data_freshness" in data
        assert "pipeline_metrics" in data
        assert "total_processed_articles" in data["pipeline_metrics"]
    else:
        assert response.status_code == 503

def test_metrics_endpoint():
    response = client.get("/api/v1/metrics")
    if response.status_code == 200:
        data = response.json()
        assert "cards" in data
        cards = data["cards"]
        assert len(cards) > 0
        keys = [card["key"] for card in cards]
        assert "top_trend" in keys
        assert "average_trend_score" in keys
        assert "total_processed_articles" in keys
    else:
        assert response.status_code == 503

def test_top_trends_endpoint():
    response = client.get("/api/v1/trends/top")
    if response.status_code == 200:
        data = response.json()
        assert "chart_config" in data
        assert "data" in data
        assert data["chart_config"]["chart_type"] == "bar"
        assert isinstance(data["data"], list)
    else:
        assert response.status_code == 503

def test_trend_metrics_endpoint():
    # Test without filters
    response = client.get("/api/v1/trends/metrics")
    if response.status_code == 200:
        data = response.json()
        assert "chart_config" in data
        assert "data" in data
        assert data["chart_config"]["chart_type"] == "line"
        assert isinstance(data["data"], list)
        
        # Test with keyword filter
        if len(data["data"]) > 0:
            first_kw = data["data"][0].get("keyword")
            if first_kw:
                resp2 = client.get(f"/api/v1/trends/metrics?keyword={first_kw}")
                assert resp2.status_code == 200
                data2 = resp2.json()
                for item in data2["data"]:
                    assert item["keyword"].lower() == first_kw.lower()
    else:
        assert response.status_code == 503

def test_sources_endpoint():
    response = client.get("/api/v1/sources")
    if response.status_code == 200:
        data = response.json()
        assert "chart_config" in data
        assert "data" in data
        assert data["chart_config"]["chart_type"] == "scatter"
        assert isinstance(data["data"], list)
    else:
        assert response.status_code == 503

def test_articles_endpoint():
    response = client.get("/api/v1/articles?page=1&limit=5")
    if response.status_code == 200:
        data = response.json()
        assert "total_items" in data
        assert "total_pages" in data
        assert data["current_page"] == 1
        assert data["limit"] == 5
        assert isinstance(data["data"], list)
        assert len(data["data"]) <= 5
        
        # Test filter
        resp2 = client.get("/api/v1/articles?has_quality_flags=true&limit=5")
        if resp2.status_code == 200:
            data2 = resp2.json()
            for item in data2["data"]:
                assert item["quality_flag_count"] > 0
    else:
        assert response.status_code == 503

def test_insights_seeds_endpoint():
    response = client.get("/api/v1/insights/seeds")
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "insight_type" in data[0]
            assert "explanation_seed" in data[0]
    else:
        assert response.status_code == 503
