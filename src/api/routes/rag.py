from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import uuid
from datetime import datetime, timezone

from src.utils.config import EVIDENCE_DATA_DIR, RAG_DATA_DIR
from src.rag.schemas import RAGQuestion
from src.rag.retriever import retrieve_evidence_for_question
from src.rag.ai_answer_client import generate_ai_cited_answer
from src.rag.answer_generator import generate_rule_based_answer

router = APIRouter()

class RAGQueryRequest(BaseModel):
    question: str
    use_ai: bool = False

@router.post("/query")
async def query_rag(request: RAGQueryRequest):
    evidence_index_path = EVIDENCE_DATA_DIR / "evidence_index.json"
    citation_map_path = EVIDENCE_DATA_DIR / "citation_map.json"
    
    if not evidence_index_path.exists() or not citation_map_path.exists():
        raise HTTPException(
            status_code=503,
            detail="RAG evidence index has not been generated yet. Run python -m src.evidence.run_evidence first."
        )
        
    try:
        with open(evidence_index_path, "r", encoding="utf-8") as f:
            evidence_index = json.load(f)
        with open(citation_map_path, "r", encoding="utf-8") as f:
            citation_map = json.load(f)
            
        q_id = f"q_api_{uuid.uuid4().hex[:8]}"
        q = RAGQuestion(
            question_id=q_id,
            question=request.question,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        evidence = retrieve_evidence_for_question(q.question, evidence_index, citation_map, top_k=3)
        
        if request.use_ai:
            ans = generate_ai_cited_answer(q, evidence)
        else:
            ans = generate_rule_based_answer(q, evidence)
            
        return ans.model_dump()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/samples")
async def get_rag_samples():
    samples_path = RAG_DATA_DIR / "rag_answers.json"
    
    if not samples_path.exists():
        raise HTTPException(
            status_code=503,
            detail="RAG samples have not been generated yet. Run python -m src.rag.run_rag first."
        )
        
    try:
        with open(samples_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
