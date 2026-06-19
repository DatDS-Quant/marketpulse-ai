import pytest
from unittest.mock import patch, MagicMock
from src.insights.schemas import TrendSignalFact, EvidenceArticle, InsightCard
from src.insights.rule_based import RuleBasedInsightGenerator
from src.insights.agents import BannedPhrasesReviewerAgent
from src.insights.ai_router_client import AIRouterClient
import httpx

@pytest.fixture
def mock_trend_facts():
    return [
        TrendSignalFact(keyword="AI", trend_score=85.0, confidence_score=75.0, article_count=5, severity="high"),
        TrendSignalFact(keyword="ML", trend_score=60.0, confidence_score=40.0, article_count=2, severity="medium")
    ]

@pytest.fixture
def mock_articles():
    return [
        EvidenceArticle(article_id="1", title="AI News", source="Source1", keyword="AI", url="http://test.com", published_at="2026-06-19"),
        EvidenceArticle(article_id="2", title="ML News", source="Source2", keyword="ML", url="http://test.com", published_at="2026-06-19")
    ]

def test_rule_based_generator(mock_trend_facts, mock_articles):
    generator = RuleBasedInsightGenerator()
    insights = generator.generate(mock_trend_facts, mock_articles)
    
    assert len(insights) == 2
    assert insights[0].keyword == "AI"
    assert insights[0].source_count == 1
    assert insights[0].generated_by == "rule_based"
    assert "AI" in insights[0].factual_explanation

def test_banned_phrases():
    # Test text containing banned phrase
    assert BannedPhrasesReviewerAgent.contains_banned_phrases("This will dominate the market.") == True
    assert BannedPhrasesReviewerAgent.contains_banned_phrases("We guarantees success.") == True
    assert BannedPhrasesReviewerAgent.contains_banned_phrases("explode in revenue") == True
    # Test clean text
    assert BannedPhrasesReviewerAgent.contains_banned_phrases("The market shows growth.") == False

    card_clean = InsightCard(
        insight_id="1", keyword="AI", signal_type="Signal", severity="high",
        trend_score=10.0, confidence_score=50.0, article_count=1, source_count=1,
        factual_explanation="Fact", business_implication="Implication",
        recommended_next_step="Step", limitation="Limit", created_at="2026-06-19"
    )
    
    card_banned = InsightCard(
        insight_id="2", keyword="AI", signal_type="Signal", severity="high",
        trend_score=10.0, confidence_score=50.0, article_count=1, source_count=1,
        factual_explanation="Fact", business_implication="It will dominate.",
        recommended_next_step="Step", limitation="Limit", created_at="2026-06-19"
    )
    
    assert BannedPhrasesReviewerAgent.review_insights([card_clean]) == True
    assert BannedPhrasesReviewerAgent.review_insights([card_clean, card_banned]) == False

@patch('src.insights.ai_router_client.httpx.Client')
def test_ai_router_client_success(mock_client_class, monkeypatch):
    monkeypatch.setenv("AI_ROUTER_BASE_URL", "http://test")
    monkeypatch.setenv("AI_ROUTER_API_KEY", "test-key")
    monkeypatch.setenv("AI_ROUTER_MODEL", "test-model")
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": '```json\n[{"keyword": "AI", "insight_id": "1", "signal_type": "Market", "severity": "high", "trend_score": 85.0, "confidence_score": 75.0, "article_count": 5, "source_count": 1, "factual_explanation": "Fact", "business_implication": "Imp", "recommended_next_step": "Step", "limitation": "Lim", "created_at": "2026-06-19"}]\n```'}}
        ]
    }
    mock_client.post.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client_class.return_value = mock_client
    
    client = AIRouterClient()
    result = client.generate_insights("test prompt")
    
    assert result is not None
    assert len(result) == 1
    assert result[0]["keyword"] == "AI"
    assert client.last_successful_model == "test-model"

@patch('src.insights.ai_router_client.httpx.Client')
def test_ai_router_client_429_fallback(mock_client_class, monkeypatch):
    monkeypatch.setenv("AI_ROUTER_BASE_URL", "http://test")
    monkeypatch.setenv("AI_ROUTER_API_KEY", "test-key")
    monkeypatch.setenv("AI_ROUTER_MODEL", "test-model")
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_client.post.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client_class.return_value = mock_client
    
    client = AIRouterClient()
    result = client.generate_insights("test prompt")
    
    assert result is None

@patch('src.insights.ai_router_client.httpx.Client')
def test_ai_router_client_json_error_fallback(mock_client_class, monkeypatch):
    monkeypatch.setenv("AI_ROUTER_BASE_URL", "http://test")
    monkeypatch.setenv("AI_ROUTER_API_KEY", "test-key")
    monkeypatch.setenv("AI_ROUTER_MODEL", "primary-model")
    monkeypatch.setenv("AI_ROUTER_MODELS", "fallback-model1,fallback-model2")
    
    mock_client = MagicMock()
    
    # First response: Invalid JSON
    resp1 = MagicMock()
    resp1.status_code = 200
    resp1.json.return_value = {"choices": [{"message": {"content": "invalid json"}}]}
    
    # Second response: Valid JSON
    resp2 = MagicMock()
    resp2.status_code = 200
    resp2.json.return_value = {
        "choices": [
            {"message": {"content": '[{"keyword": "AI"}]'}}
        ]
    }
    
    mock_client.post.side_effect = [resp1, resp2]
    mock_client.__enter__.return_value = mock_client
    mock_client_class.return_value = mock_client
    
    client = AIRouterClient()
    result = client.generate_insights("test prompt")
    
    assert result is not None
    assert len(result) == 1
    assert result[0]["keyword"] == "AI"
    assert client.last_successful_model == "fallback-model1"
    assert mock_client.post.call_count == 2
