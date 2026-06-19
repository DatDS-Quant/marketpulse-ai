import json
import logging
import uuid
from datetime import datetime, timezone

from src.evidence.loaders import load_csv, load_json
from src.evidence.indexer import build_evidence_index
from src.evidence.citation_mapper import map_citations_to_insights
from src.evidence.report_citations import generate_cited_markdown_report
from src.evidence.schemas import RetrievalManifest, EvidenceRunSummary
from src.utils.config import (
    ANALYTICS_DATA_DIR, INSIGHTS_DATA_DIR, 
    EVIDENCE_DATA_DIR, LOGS_DIR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_evidence_pipeline():
    logger.info("Starting Module 8: Evidence Retrieval & Citation Pipeline...")
    
    run_id = f"evd_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    
    EVIDENCE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Load files
        articles_clean = load_csv(ANALYTICS_DATA_DIR / "articles_clean.csv")
        source_metrics = load_csv(ANALYTICS_DATA_DIR / "source_metrics.csv")
        insight_cards = load_json(INSIGHTS_DATA_DIR / "insight_cards.json")
        
        if articles_clean is None or insight_cards is None:
            msg = "Missing required inputs (articles_clean.csv or insight_cards.json). Please run python -m src.insights.run_insights first."
            logger.warning(msg)
            print(msg)
            return
            
        # 2. Build index
        logger.info("Building Evidence Index...")
        evidence_index = build_evidence_index(articles_clean, source_metrics)
        articles_indexed = len(evidence_index.records)
        
        # 3. Retrieve and Map Citations
        logger.info("Retrieving evidence and mapping citations...")
        citation_map, insight_links = map_citations_to_insights(evidence_index, insight_cards)
        
        # 4. Generate Manifest
        citations_created = len(citation_map.citations)
        missing_evidence_count = sum(1 for link in insight_links if not link.has_evidence)
        
        manifest = RetrievalManifest(
            run_id=run_id,
            timestamp=timestamp,
            articles_indexed=articles_indexed,
            insights_processed=len(insight_cards),
            citations_created=citations_created,
            insights_missing_evidence=missing_evidence_count
        )
        
        # 5. Save JSON outputs
        logger.info("Saving JSON outputs...")
        with open(EVIDENCE_DATA_DIR / "evidence_index.json", "w", encoding="utf-8") as f:
            json.dump(evidence_index.model_dump(), f, indent=2, ensure_ascii=False)
            
        with open(EVIDENCE_DATA_DIR / "citation_map.json", "w", encoding="utf-8") as f:
            json.dump(citation_map.model_dump(), f, indent=2, ensure_ascii=False)
            
        with open(EVIDENCE_DATA_DIR / "insight_evidence_links.json", "w", encoding="utf-8") as f:
            json.dump([link.model_dump() for link in insight_links], f, indent=2, ensure_ascii=False)
            
        with open(EVIDENCE_DATA_DIR / "retrieval_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(), f, indent=2, ensure_ascii=False)
            
        # 6. Generate Markdown Report
        logger.info("Generating Cited Markdown Report...")
        generate_cited_markdown_report(insight_cards, citation_map, insight_links, manifest)
        
        # 7. Log Run
        run_summary = EvidenceRunSummary(
            run_id=run_id,
            timestamp=timestamp,
            status="success",
            manifest=manifest
        )
        with open(LOGS_DIR / "evidence_runs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(run_summary.model_dump(), ensure_ascii=False) + "\n")
            
        # Print summary
        print(f"\n--- Evidence Retrieval Summary ---")
        print(f"Run ID:                    {run_id}")
        print(f"Articles Indexed:          {articles_indexed}")
        print(f"Insights Processed:        {len(insight_cards)}")
        print(f"Citations Created:         {citations_created}")
        print(f"Insights Missing Evidence: {missing_evidence_count}")
        print(f"Output Directory:          {EVIDENCE_DATA_DIR}")
        print(f"----------------------------------\n")
        
    except Exception as e:
        logger.error(f"Evidence pipeline failed: {str(e)}")
        run_summary = EvidenceRunSummary(
            run_id=run_id,
            timestamp=timestamp,
            status="error",
            error_message=str(e)
        )
        with open(LOGS_DIR / "evidence_runs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(run_summary.model_dump(), ensure_ascii=False) + "\n")
        raise

if __name__ == "__main__":
    run_evidence_pipeline()
