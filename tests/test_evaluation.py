import pytest
import pandas as pd
from pathlib import Path
from src.evals.data_quality_checks import evaluate_data_quality
from src.evals.pipeline_health import evaluate_pipeline_health
from src.evals.insight_quality import evaluate_insight_quality
from src.evals.quality_gates import evaluate_quality_gates
from src.evals.schemas import CheckResult
from fastapi.testclient import TestClient
from src.api.main import app

def test_data_quality_evaluation():
    # Pass scenario
    df_articles = pd.DataFrame({
        "source": ["A", "B", "C"] * 10,
        "title": ["Title"] * 30,
        "url": ["http://test.com"] * 30
    })
    
    df_quality = pd.DataFrame({
        "missing_title": [0, 0],
        "missing_url": [0, 0],
        "missing_source": [0, 0],
        "invalid_keyword": [0, 0]
    })
    
    res = evaluate_data_quality(df_articles, df_quality)
    assert res.articles_count == 30
    assert res.unique_sources == 3
    assert res.missing_fields_ratio == 0.0
    
    # Fail scenario
    res_fail = evaluate_data_quality(pd.DataFrame(), None)
    assert res_fail.articles_count == 0
    assert any(c.status == "FAIL" for c in res_fail.checks)

def test_pipeline_health_evaluation(tmp_path):
    # Mock required files
    f1 = tmp_path / "f1.csv"
    f1.touch()
    
    logs = [{"step": "ingestion", "status": "success"}]
    res = evaluate_pipeline_health({}, {}, logs, [f1])
    
    assert res.required_files_exist is True
    assert res.pipeline_success_rate == 1.0

def test_insight_quality_evaluation():
    insight_brief = {
        "insights": [
            {"factual_explanation": "Good data", "limitation": "None", "recommended_next_step": "Do it"},
            {"factual_explanation": "will dominate the market", "limitation": "None", "recommended_next_step": "Buy"}
        ]
    }
    
    res = evaluate_insight_quality(insight_brief)
    assert res.insight_count == 2
    assert res.banned_phrases_count > 0  # 'will dominate' is banned
    
def test_quality_gates():
    from src.evals.schemas import DataQualityResult, PipelineHealthResult, InsightQualityResult
    
    dq = DataQualityResult(articles_count=30, missing_fields_ratio=0.0, invalid_keyword_ratio=0.0, unique_sources=3, checks=[])
    ph = PipelineHealthResult(required_files_exist=True, pipeline_success_rate=1.0, checks=[])
    iq = InsightQualityResult(insight_count=5, banned_phrases_count=0, completeness_score=1.0, checks=[])
    
    gates = evaluate_quality_gates(dq, ph, iq)
    assert all(g.status == "PASS" for g in gates)

def test_api_evaluation_endpoint(tmp_path, monkeypatch):
    client = TestClient(app)
    
    # Missing summary
    response = client.get("/api/v1/evaluation/summary")
    # if it doesn't exist yet, it should be 503
    assert response.status_code in [503, 200]
