import os
import json
import logging
from typing import Optional, List
from datetime import datetime, timezone
import httpx
from pydantic import ValidationError

from src.rag.schemas import RAGQuestion, RetrievedEvidence, RAGAnswer
from src.rag.answer_generator import generate_rule_based_answer
from src.rag.safety import is_answer_safe

logger = logging.getLogger(__name__)

def generate_ai_cited_answer(question: RAGQuestion, evidence: List[RetrievedEvidence]) -> RAGAnswer:
    """Attempts to use AI to generate an answer, falling back to rule-based."""
    
    rule_based_fallback = generate_rule_based_answer(question, evidence)
    
    # Check config
    if os.getenv("ENABLE_RAG_AI", "false").lower() != "true":
        return rule_based_fallback
        
    api_key = os.getenv("AI_ROUTER_API_KEY")
    if not api_key:
        return rule_based_fallback
        
    base_url = os.getenv("AI_ROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("AI_ROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
    
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
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": float(os.getenv("AI_ROUTER_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("AI_ROUTER_MAX_TOKENS", "900"))
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        timeout = float(os.getenv("AI_ROUTER_TIMEOUT_SECONDS", "30"))
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
            
            if resp.status_code == 429:
                logger.warning("RAG AI: 429 Rate Limit. Falling back to rule-based.")
                return rule_based_fallback
                
            resp.raise_for_status()
            data = resp.json()
            
            content = data["choices"][0]["message"]["content"].strip()
            
            # Clean possible markdown fences
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
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
                
    except Exception as e:
        logger.warning(f"RAG AI failed: {e}. Falling back to rule-based.")
        return rule_based_fallback
