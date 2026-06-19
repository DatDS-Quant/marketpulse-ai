from src.evals.schemas import EvaluationSummary, EvaluationRunSummary
from src.utils.config import EVALS_DIR, REPORTS_GENERATED_DIR, REPORTS_TEMPLATES_DIR, LOGS_DIR
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def save_json_outputs(summary: EvaluationSummary):
    """Saves the JSON outputs of the evaluation."""
    EVALS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save the full summary
    with open(EVALS_DIR / "evaluation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary.model_dump(), f, indent=2, ensure_ascii=False)
        
    # Save partial views
    with open(EVALS_DIR / "quality_gates.json", "w", encoding="utf-8") as f:
        json.dump([g.model_dump() for g in summary.quality_gates], f, indent=2, ensure_ascii=False)
        
    with open(EVALS_DIR / "pipeline_health.json", "w", encoding="utf-8") as f:
        json.dump(summary.pipeline_health.model_dump(), f, indent=2, ensure_ascii=False)
        
    with open(EVALS_DIR / "insight_quality_report.json", "w", encoding="utf-8") as f:
        json.dump(summary.insight_quality.model_dump(), f, indent=2, ensure_ascii=False)

def append_to_evaluation_logs(run_summary: EvaluationRunSummary):
    """Appends to the evaluation runs JSONL log."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "evaluation_runs.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(run_summary.model_dump(), ensure_ascii=False) + "\n")

def generate_markdown_report(summary: EvaluationSummary):
    """Generates the Markdown report using the template."""
    template_path = REPORTS_TEMPLATES_DIR / "evaluation_report_template.md"
    report_path = REPORTS_GENERATED_DIR / "evaluation_report_latest.md"
    
    if not template_path.exists():
        logger.warning("Markdown template not found. Skipping markdown report generation.")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replacements
    content = content.replace("{{ run_id }}", summary.run_id)
    content = content.replace("{{ timestamp }}", summary.timestamp)
    content = content.replace("{{ overall_status }}", summary.overall_status)
    
    gates_text = "\n".join([f"- **{g.gate_name}**: {g.status} - {g.reason}" for g in summary.quality_gates])
    content = content.replace("{{ quality_gates }}", gates_text)
    
    data_text = f"Articles: {summary.data_quality.articles_count}\nSources: {summary.data_quality.unique_sources}"
    content = content.replace("{{ data_quality }}", data_text)
    
    health_text = f"Files Exist: {summary.pipeline_health.required_files_exist}\nSuccess Rate: {summary.pipeline_health.pipeline_success_rate}"
    content = content.replace("{{ pipeline_health }}", health_text)
    
    insight_text = f"Insights: {summary.insight_quality.insight_count}\nBanned Phrases: {summary.insight_quality.banned_phrases_count}"
    content = content.replace("{{ insight_quality }}", insight_text)
    
    REPORTS_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
