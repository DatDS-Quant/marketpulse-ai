import json
import logging
import uuid
from datetime import datetime, timezone

from src.rag.loaders import load_json
from src.rag.schemas import RAGQuestion, RAGRunManifest, RAGRunSummary
from src.rag.retriever import retrieve_evidence_for_question
from src.rag.ai_answer_client import generate_ai_cited_answer
from src.rag.report_writer import write_rag_markdown_report
from src.utils.config import EVIDENCE_DATA_DIR, RAG_DATA_DIR, LOGS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_rag_pipeline():
    logger.info("Starting Module 8B: RAG Extension Pipeline...")
    
    run_id = f"rag_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    
    RAG_DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load data
    evidence_index = load_json(EVIDENCE_DATA_DIR / "evidence_index.json")
    citation_map = load_json(EVIDENCE_DATA_DIR / "citation_map.json")
    insight_links = load_json(EVIDENCE_DATA_DIR / "insight_evidence_links.json")
    
    if not evidence_index or not citation_map:
        msg = "Missing required inputs (evidence_index.json or citation_map.json). Please run python -m src.evidence.run_evidence first."
        logger.warning(msg)
        print(msg)
        return
        
    # 2. Define Sample Queries
    sample_queries = [
        "Why is AI agents business considered a strong signal?",
        "What evidence supports the strongest market signal?",
        "What are the limitations of the current content automation trend?"
    ]
    
    questions = []
    for q_idx, text in enumerate(sample_queries):
        questions.append(RAGQuestion(
            question_id=f"q_{run_id}_{q_idx}",
            question=text,
            created_at=timestamp
        ))
        
    # 3. Retrieve and Answer
    answers = []
    ai_count = 0
    rule_based_count = 0
    total_citations = 0
    
    for q in questions:
        evidence = retrieve_evidence_for_question(q.question, evidence_index, citation_map, top_k=3)
        ans = generate_ai_cited_answer(q, evidence)
        answers.append(ans)
        
        if ans.generated_by == "ai_router":
            ai_count += 1
        else:
            rule_based_count += 1
            
        total_citations += len(ans.citation_ids)
        
    # 4. Generate Manifest
    manifest = RAGRunManifest(
        run_id=run_id,
        timestamp=timestamp,
        questions_processed=len(questions),
        answers_generated=len(answers),
        ai_answers=ai_count,
        rule_based_answers=rule_based_count,
        total_citations_used=total_citations
    )
    
    # 5. Save JSONs
    with open(RAG_DATA_DIR / "rag_queries.json", "w", encoding="utf-8") as f:
        json.dump([q.model_dump() for q in questions], f, indent=2, ensure_ascii=False)
        
    with open(RAG_DATA_DIR / "rag_answers.json", "w", encoding="utf-8") as f:
        json.dump([a.model_dump() for a in answers], f, indent=2, ensure_ascii=False)
        
    with open(RAG_DATA_DIR / "rag_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(), f, indent=2, ensure_ascii=False)
        
    # 6. Generate Report
    write_rag_markdown_report(answers, manifest)
    
    # 7. Log Run
    summary = RAGRunSummary(
        run_id=run_id,
        timestamp=timestamp,
        status="success",
        manifest=manifest
    )
    with open(LOGS_DIR / "rag_runs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(summary.model_dump(), ensure_ascii=False) + "\n")
        
    # Print summary
    print(f"\n--- RAG Pipeline Summary ---")
    print(f"Run ID:              {run_id}")
    print(f"Questions Processed: {len(questions)}")
    print(f"Answers Generated:   {len(answers)} (AI: {ai_count}, Rule-based: {rule_based_count})")
    print(f"Citations Used:      {total_citations}")
    print(f"Output Directory:    {RAG_DATA_DIR}")
    print(f"----------------------------\n")

if __name__ == "__main__":
    run_rag_pipeline()
