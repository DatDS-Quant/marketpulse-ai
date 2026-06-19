import os
import json
import logging
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timezone
from typing import List

# Set up logging early
from src.utils.config import LOGS_DIR
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

from src.insights.loaders import InsightDataLoader
from src.insights.schemas import InsightBrief, InsightCard, InsightRunSummary
from src.insights.rule_based import RuleBasedInsightGenerator
from src.insights.ai_router_client import AIRouterClient
from src.insights.agents import BannedPhrasesReviewerAgent
from src.insights.report_writer import ReportWriterAgent

def build_ai_prompt(draft_insights: List[InsightCard], source_facts: List) -> str:
    prompt = """You are writing a market intelligence brief. Your task is to improve the wording of the provided insight drafts.
Rules:
- Use ONLY the provided facts.
- Do NOT invent numbers, statistics, or evidence.
- Do NOT invent URLs or citations.
- Do NOT forecast revenue or claim market domination.
- Do NOT recommend investment.
- Keep claims cautious and evidence-backed.
- Include practical limitations.
- Preserve exact values for: insight_id, keyword, signal_type, severity, trend_score, confidence_score, article_count, source_count, evidence_articles, created_at.
- Return ONLY a valid JSON array of objects matching the original schema. Do not return Markdown fences.

Here are the drafts and source facts to improve:
"""
    facts_data = {
        "source_quality_summary": [s.model_dump() for s in source_facts[:5]],
        "draft_insights": [i.model_dump() for i in draft_insights]
    }
    prompt += json.dumps(facts_data, indent=2)
    return prompt

def run_pipeline():
    logger.info("Starting Module 7: Insight Generator Pipeline...")
    
    # Load input data
    trend_facts = InsightDataLoader.load_trend_facts()
    articles = InsightDataLoader.load_articles()
    source_facts = InsightDataLoader.load_source_facts()
    
    if not trend_facts:
        logger.warning("No trend facts found. Please run Module 4 first.")
        return
        
    enable_ai = os.getenv("ENABLE_AI_INSIGHTS", "true").lower() == "true"
    ai_client = AIRouterClient()
    
    # Always generate rule-based drafts first
    logger.info("Generating rule-based insight drafts...")
    generator = RuleBasedInsightGenerator()
    rule_based_insights = generator.generate(trend_facts, articles)
    
    final_insights = rule_based_insights
    generated_by = "rule_based"
    mode_used = "rule_based"
    error_message = None

    if enable_ai and ai_client.is_configured:
        logger.info("AI Insights enabled. Primary Provider configured.")
        prompt = build_ai_prompt(rule_based_insights[:5], source_facts)
            
        try:
            ai_response = ai_client.generate_insights(prompt)
            if ai_response and isinstance(ai_response, list):
                # Ensure it's a valid list of cards
                parsed_insights = []
                for card in ai_response:
                    card['generated_by'] = "ai_router"
                    parsed_insights.append(InsightCard(**card))
                
                # Check for banned phrases
                if BannedPhrasesReviewerAgent.review_insights(parsed_insights):
                    final_insights = parsed_insights
                    generated_by = "ai_router"
                    mode_used = ai_client.last_successful_model or "ai_router"
                    logger.info(f"AI Router generated insights successfully using {mode_used}.")
                else:
                    logger.warning("AI Insights contained banned phrases. Falling back to rule-based.")
                    error_message = "Banned phrases detected"
            else:
                logger.warning("AI Response invalid format or empty. Falling back to rule-based.")
                error_message = "Invalid JSON format or Provider Error"
        except Exception as e:
            logger.warning(f"AI Router parsing/validation failed: {e}. Falling back to rule-based.")
            error_message = str(e)
    elif enable_ai:
        logger.warning("AI Insights enabled but missing configuration (Keys/Models). Using rule-based.")
        
    # Compile brief
    brief = InsightBrief(
        summary=f"Generated {len(final_insights)} insight cards using {mode_used}.",
        generated_by=generated_by,
        insights=final_insights
    )
    
    # Write outputs
    ReportWriterAgent.write_json(brief)
    ReportWriterAgent.write_markdown(brief)
    
    # Write log
    run_summary = InsightRunSummary(
        run_id=f"run_{int(datetime.now(timezone.utc).timestamp())}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        status="success",
        insights_generated=len(final_insights),
        mode_used=mode_used,
        error_message=error_message
    )
    
    log_file = LOGS_DIR / "insight_runs.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(run_summary.model_dump()) + "\n")
        
    logger.info(f"Pipeline completed successfully. Generated {len(final_insights)} insights via {mode_used}.")
    logger.info("Report saved to reports/generated/market_brief_latest.md")

if __name__ == "__main__":
    run_pipeline()
