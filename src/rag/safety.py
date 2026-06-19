from typing import List
from src.rag.schemas import RAGAnswer

BANNED_PHRASES = [
    "will dominate",
    "guarantees",
    "definitely",
    "revenue will",
    "invest immediately",
    "guaranteed demand",
    "guaranteed growth",
    "must invest",
    "certain to",
    "explode in revenue"
]

def is_answer_safe(answer: RAGAnswer) -> bool:
    """Validates answer against safety rules."""
    
    text_lower = answer.answer.lower()
    
    # 1. Banned phrases
    for phrase in BANNED_PHRASES:
        if phrase in text_lower:
            return False
            
    # 2. Check citation existence in retrieved evidence
    evidence_ids = [e.citation_id for e in answer.retrieved_evidence]
    for cit_id in answer.citation_ids:
        if cit_id not in evidence_ids:
            return False # Invented citation ID
            
    # 3. Check for empty
    if not answer.answer.strip():
        return False
        
    # 4. Check limitation exists
    if not answer.limitation.strip():
        return False
        
    return True
