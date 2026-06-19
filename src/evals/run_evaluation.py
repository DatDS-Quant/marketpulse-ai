import logging
import uuid
from datetime import datetime, timezone

from src.evals.loaders import load_json, load_jsonl, load_csv
from src.evals.data_quality_checks import evaluate_data_quality
from src.evals.pipeline_health import evaluate_pipeline_health
from src.evals.insight_quality import evaluate_insight_quality
from src.evals.quality_gates import evaluate_quality_gates, compute_overall_status
from src.evals.report_writer import save_json_outputs, generate_markdown_report, append_to_evaluation_logs
from src.evals.schemas import EvaluationSummary, EvaluationRunSummary
from src.utils.config import (
    ANALYTICS_DATA_DIR, TRENDS_DATA_DIR, INSIGHTS_DATA_DIR, LOGS_DIR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_evaluation():
    logger.info("Starting Evaluation Pipeline (Module 9)...")
    run_id = f"eval_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    
    try:
        # Load Logs
        ingestion_logs = load_jsonl(LOGS_DIR / "ingestion_runs.jsonl")
        processing_logs = load_jsonl(LOGS_DIR / "processing_runs.jsonl")
        analytics_logs = load_jsonl(LOGS_DIR / "analytics_runs.jsonl")
        trend_logs = load_jsonl(LOGS_DIR / "trend_runs.jsonl")
        insight_logs = load_jsonl(LOGS_DIR / "insight_runs.jsonl")
        
        all_logs = ingestion_logs + processing_logs + analytics_logs + trend_logs + insight_logs
        
        # Load Manifests
        analytics_manifest = load_json(ANALYTICS_DATA_DIR / "analytics_manifest.json")
        trend_manifest = load_json(TRENDS_DATA_DIR / "trend_manifest.json")
        
        # Load Data
        articles_clean = load_csv(ANALYTICS_DATA_DIR / "articles_clean.csv")
        quality_metrics = load_csv(ANALYTICS_DATA_DIR / "quality_metrics.csv")
        insight_brief = load_json(INSIGHTS_DATA_DIR / "insight_brief.json")
        
        required_files = [
            ANALYTICS_DATA_DIR / "articles_clean.csv",
            ANALYTICS_DATA_DIR / "source_metrics.csv",
            TRENDS_DATA_DIR / "top_trends.csv",
            INSIGHTS_DATA_DIR / "insight_brief.json"
        ]
        
        # Evaluations
        pipeline_health = evaluate_pipeline_health(
            analytics_manifest, trend_manifest, all_logs, required_files
        )
        
        data_quality = evaluate_data_quality(articles_clean, quality_metrics)
        insight_quality = evaluate_insight_quality(insight_brief)
        
        # Quality Gates
        gates = evaluate_quality_gates(data_quality, pipeline_health, insight_quality)
        overall_status = compute_overall_status(gates)
        
        summary = EvaluationSummary(
            run_id=run_id,
            timestamp=timestamp,
            overall_status=overall_status,
            quality_gates=gates,
            data_quality=data_quality,
            pipeline_health=pipeline_health,
            insight_quality=insight_quality
        )
        
        # Save Outputs
        save_json_outputs(summary)
        generate_markdown_report(summary)
        
        run_summary = EvaluationRunSummary(
            run_id=run_id,
            timestamp=timestamp,
            status="success",
            overall_status=overall_status
        )
        append_to_evaluation_logs(run_summary)
        
        logger.info(f"Evaluation finished with Overall Status: {overall_status}")
        
    except Exception as e:
        logger.error(f"Evaluation pipeline failed: {str(e)}")
        run_summary = EvaluationRunSummary(
            run_id=run_id,
            timestamp=timestamp,
            status="error",
            overall_status="FAIL",
            error_message=str(e)
        )
        append_to_evaluation_logs(run_summary)
        raise

if __name__ == "__main__":
    run_evaluation()
