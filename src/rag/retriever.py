from typing import List, Dict, Any
from src.rag.schemas import RetrievedEvidence

def retrieve_evidence_for_question(
    question: str, 
    evidence_index: Dict[str, Any], 
    citation_map: Dict[str, Any],
    top_k: int = 3
) -> List[RetrievedEvidence]:
    """
    Lightweight lexical retrieval: scores citations against question terms.
    """
    citations = citation_map.get("citations", {})
    if not citations:
        return []
        
    question_terms = set([t.lower() for t in question.replace('?', '').split() if len(t) > 2])
    
    scored_evidence = []
    
    for cit_id, cit in citations.items():
        score = 0.0
        matched = []
        
        # Base module 8 score heavily favored
        score += cit.get("relevance_score", 0) * 0.5  # Max 50
        
        # Match with keyword
        keyword = cit.get("keyword", "").lower()
        if any(term in keyword for term in question_terms):
            score += 20.0
            matched.append("keyword_match")
            
        # Match with title
        title = cit.get("title", "").lower()
        if any(term in title for term in question_terms):
            score += 20.0
            matched.append("title_match")
            
        # Optional exact phrase match boost
        if keyword in question.lower():
            score += 10.0
            matched.append("exact_keyword_in_q")
            
        score = min(100.0, score)
        
        if matched or score > 0:
            scored_evidence.append((score, cit_id, cit, matched))
            
    scored_evidence.sort(key=lambda x: x[0], reverse=True)
    
    results = []
    for score, cit_id, cit, matched in scored_evidence[:top_k]:
        results.append(RetrievedEvidence(
            citation_id=cit_id,
            article_id=cit.get("article_id", ""),
            title=cit.get("title", ""),
            source=cit.get("source", ""),
            url=cit.get("url", ""),
            keyword=cit.get("keyword", ""),
            published_at=cit.get("published_at"),
            relevance_score=score,
            matched_terms=matched
        ))
        
    return results
