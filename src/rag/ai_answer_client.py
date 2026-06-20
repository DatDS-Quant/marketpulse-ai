import os
import json
import logging
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import ValidationError

from src.rag.schemas import RAGQuestion, RetrievedEvidence, RAGAnswer
from src.rag.answer_generator import generate_rule_based_answer
from src.rag.safety import is_answer_safe
from src.insights.ai_router_client import AIRouterClient

logger = logging.getLogger(__name__)

# Reusable client instance
_router_client = AIRouterClient()

def generate_ai_cited_answer(question: RAGQuestion, evidence: List[RetrievedEvidence]) -> RAGAnswer:
    """Attempts to use AI to generate an answer, falling back to rule-based."""
    
    rule_based_fallback = generate_rule_based_answer(question, evidence)
    
    # Check config
    if os.getenv("ENABLE_RAG_AI", "false").lower() != "true":
        return rule_based_fallback
        
    # Build prompt
    evidence_text = ""
    for e in evidence:
        evidence_text += f"[{e.citation_id}] Title: {e.title} | Source: {e.source}\n"
        
    system_prompt = (
        "You are an AI market intelligence assistant. Your task is to answer the user's question using ONLY the provided evidence.\n"
        "Rules:\n"
        "1. Do not invent facts, citations, or URLs.\n"
        "2. Do not forecast revenue or claim market domination.\n"
        "3. Include citation IDs inline like [E1], [E2].\n"
        "4. If evidence is weak, say so clearly.\n"
        "5. Output MUST be valid JSON only. No markdown fences.\n\n"
        "Required JSON schema:\n"
        "{\n"
        "  \"answer\": \"your detailed answer string with citations inline\",\n"
        "  \"limitation\": \"one sentence stating the limitation of this answer\",\n"
        "  \"confidence_note\": \"High/Moderate/Low based on evidence\"\n"
        "}"
    )
    
    user_prompt = f"Question: {question.question}\nEvidence:\n{evidence_text}"
    
    try:
        content = _router_client.call_api(
            prompt=user_prompt, 
            system_prompt=system_prompt, 
            response_format_json=True
        )
        
        if not content:
            logger.warning("RAG AI: Client returned no content. Falling back to rule-based.")
            return rule_based_fallback
            
        parsed = json.loads(content)
        
        ai_answer = RAGAnswer(
            question_id=question.question_id,
            question=question.question,
            answer=parsed.get("answer", rule_based_fallback.answer),
            citation_ids=[e.citation_id for e in evidence],
            retrieved_evidence=evidence,
            generated_by="ai_router",
            confidence_note=parsed.get("confidence_note", "Moderate"),
            limitation=parsed.get("limitation", "AI generated content may contain inaccuracies."),
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        if is_answer_safe(ai_answer):
            return ai_answer
        else:
            logger.warning("RAG AI: Answer failed safety check. Falling back to rule-based.")
            return rule_based_fallback
            
    except json.JSONDecodeError as e:
        logger.warning(f"RAG AI JSON parse failed: {e}. Raw content: {content[:100]}")
        return rule_based_fallback
    except Exception as e:
        logger.warning(f"RAG AI failed unexpectedly: {e}. Falling back to rule-based.")
        return rule_based_fallback
