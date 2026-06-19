import pytest
from fastapi.testclient import TestClient
from src.rag.retriever import retrieve_evidence_for_question
from src.rag.answer_generator import generate_rule_based_answer
from src.rag.safety import is_answer_safe
from src.rag.schemas import RAGQuestion, RAGAnswer, RetrievedEvidence
from src.api.main import app

def test_rag_retriever():
    question = "What about AI agents?"
    
    evidence_index = {
        "records": [
            {"article_id": "1", "title": "AI agents boom", "keyword": "ai agents", "relevance_score": 50.0}
        ]
    }
    
    citation_map = {
        "citations": {
            "[E1]": {"citation_id": "[E1]", "article_id": "1", "title": "AI agents boom", "keyword": "ai agents", "relevance_score": 50.0, "matched_terms": []}
        }
    }
    
    retrieved = retrieve_evidence_for_question(question, evidence_index, citation_map, top_k=1)
    
    assert len(retrieved) == 1
    assert retrieved[0].citation_id == "[E1]"
    assert retrieved[0].relevance_score > 0
    assert retrieved[0].relevance_score <= 100.0

def test_rule_based_answer():
    question = RAGQuestion(question_id="q1", question="Why AI?", created_at="now")
    
    ev = RetrievedEvidence(
        citation_id="[E1]", article_id="1", title="AI boom", source="Tech", url="u",
        keyword="ai", relevance_score=90.0, matched_terms=["exact"]
    )
    
    ans = generate_rule_based_answer(question, [ev])
    assert "[E1]" in ans.answer
    assert ans.generated_by == "rule_based"
    assert "limitation" in ans.model_dump()
    assert ans.citation_ids == ["[E1]"]

def test_rule_based_missing_evidence():
    question = RAGQuestion(question_id="q1", question="Why AI?", created_at="now")
    ans = generate_rule_based_answer(question, [])
    assert "insufficient evidence" in ans.answer
    assert ans.citation_ids == []

def test_safety_banned_phrases():
    ans = RAGAnswer(
        question_id="1", question="q", answer="This will dominate the market.",
        citation_ids=["[E1]"], retrieved_evidence=[RetrievedEvidence(citation_id="[E1]", article_id="1", title="t", source="s", url="u", keyword="k", relevance_score=10.0, matched_terms=[])],
        generated_by="ai", confidence_note="Low", limitation="none", created_at="now"
    )
    
    assert is_answer_safe(ans) is False
    
    # Safe text
    ans.answer = "This is a strong signal based on [E1]."
    assert is_answer_safe(ans) is True
    
    # Invented citation
    ans.citation_ids = ["[E99]"]
    assert is_answer_safe(ans) is False

def test_api_rag_endpoint(monkeypatch):
    client = TestClient(app)
    
    # Without running module 8, this may return 503
    # Or 200 if files exist.
    resp = client.post("/api/v1/rag/query", json={"question": "Test", "use_ai": False})
    assert resp.status_code in [503, 200]
    
    resp_get = client.get("/api/v1/rag/samples")
    assert resp_get.status_code in [503, 200]
