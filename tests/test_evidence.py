import pytest
import pandas as pd
from fastapi.testclient import TestClient
from src.evidence.indexer import build_evidence_index
from src.evidence.retriever import compute_relevance_score, retrieve_evidence_for_keyword
from src.evidence.citation_mapper import map_citations_to_insights
from src.evidence.schemas import EvidenceRecord
from src.api.main import app

def test_evidence_index_builder():
    df_articles = pd.DataFrame({
        "article_id": ["art1", "art2"],
        "title": ["AI Agents are great", "No matching title"],
        "source": ["TechCrunch", "Unknown"],
        "url": ["http://test.com", "http://test2.com"],
        "keyword": ["AI agents", "none"],
        "summary": ["Detailed text about ai agents", "Empty"]
    })
    
    df_sources = pd.DataFrame({
        "source": ["TechCrunch"],
        "source_quality_score": [0.9]
    })
    
    index = build_evidence_index(df_articles, df_sources)
    assert len(index.records) == 2
    assert index.records[0].source_quality_score == 0.9
    assert index.records[1].source_quality_score == 0.5

def test_evidence_retriever():
    r1 = EvidenceRecord(
        article_id="1", title="AI agents boom", source="A", url="u", keyword="ai agents",
        summary="AI agents are taking over", source_quality_score=0.9
    )
    r2 = EvidenceRecord(
        article_id="2", title="Unrelated", source="B", url="u", keyword="none",
        summary="Nothing to see here", source_quality_score=0.1
    )
    r3 = EvidenceRecord(
        article_id="3", title="Also AI agents", source="A", url="u", keyword="ai agents",
        summary="Another post", source_quality_score=0.9, quality_flags="missing_url"
    )
    
    from src.evidence.schemas import EvidenceIndex
    idx = EvidenceIndex(records=[r1, r2, r3])
    
    # Retrieval
    results = retrieve_evidence_for_keyword(idx, "ai agents", top_k=2)
    assert len(results) == 2
    assert results[0][0].article_id == "1"
    
    # Score bounds and values
    score1, terms = compute_relevance_score(r1, "ai agents")
    assert score1 > 0
    assert "exact_keyword" in terms
    
    # Penalties
    score3, _ = compute_relevance_score(r3, "ai agents")
    assert score3 < score1

def test_citation_mapper():
    r1 = EvidenceRecord(
        article_id="1", title="AI boom", source="A", url="u", keyword="ai agents",
        summary="AI agents", source_quality_score=0.9
    )
    from src.evidence.schemas import EvidenceIndex
    idx = EvidenceIndex(records=[r1])
    
    cards = [
        {"id": "ins1", "keyword": "ai agents"},
        {"id": "ins2", "keyword": "not found keyword"}
    ]
    
    cmap, links = map_citations_to_insights(idx, cards)
    
    # Check citations
    assert len(cmap.citations) == 1
    cit = list(cmap.citations.values())[0]
    assert cit.citation_id == "[E1]"
    assert cit.article_id == "1"
    
    # Check links
    assert len(links) == 2
    assert links[0].has_evidence is True
    assert links[0].citation_ids == ["[E1]"]
    
    assert links[1].has_evidence is False
    assert links[1].missing_evidence_reason is not None

def test_api_evidence_endpoint(tmp_path, monkeypatch):
    client = TestClient(app)
    
    # When missing
    response = client.get("/api/v1/evidence/citations")
    assert response.status_code in [503, 200]
