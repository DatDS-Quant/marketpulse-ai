from typing import List
from datetime import datetime, timezone
from src.rag.schemas import RAGQuestion, RetrievedEvidence, RAGAnswer

def generate_rule_based_answer(question: RAGQuestion, evidence: List[RetrievedEvidence]) -> RAGAnswer:
    if not evidence:
        return RAGAnswer(
            question_id=question.question_id,
            question=question.question,
            answer="There is insufficient evidence in the current dataset to answer this question.",
            citation_ids=[],
            retrieved_evidence=[],
            generated_by="rule_based",
            confidence_note="Low - no evidence found.",
            limitation="Answer is limited by the lack of indexed articles matching the question terms.",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
    citation_ids = [e.citation_id for e in evidence]
    cit_str = "".join(citation_ids)
    
    # Simple rule-based generation
    keywords = list(set([e.keyword for e in evidence]))
    sources = list(set([e.source for e in evidence]))
    
    answer_text = (
        f"Based on the retrieved articles, this topic revolves around '{', '.join(keywords)}'. "
        f"The signals are supported by sources such as {', '.join(sources[:3])} {cit_str}. "
        f"This indicates visible news activity in the collected sources."
    )
    
    return RAGAnswer(
        question_id=question.question_id,
        question=question.question,
        answer=answer_text,
        citation_ids=citation_ids,
        retrieved_evidence=evidence,
        generated_by="rule_based",
        confidence_note="Moderate - based strictly on keyword matching.",
        limitation="It should not be interpreted as direct market demand or revenue forecast.",
        created_at=datetime.now(timezone.utc).isoformat()
    )
