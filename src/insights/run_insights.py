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

def run_pipeline():
    logger.info("Starting Module 7: Insight Generator Pipeline...")
    
    # Load input data
    trend_facts = InsightDataLoader.load_trend_facts()
    articles = InsightDataLoader.load_articles()
    
    if not trend_facts:
        logger.warning("No trend facts found. Please run Module 4 first.")
        return
        
    enable_ai = os.getenv("ENABLE_AI_INSIGHTS", "true").lower() == "true"
    ai_client = AIRouterClient()
    
    insights = []
    generated_by = "rule_based"
    mode_used = "rule_based"
    error_message = None

    if enable_ai and ai_client.is_configured:
        logger.info("AI Insights enabled and configured. Calling AI Router...")
        prompt = "Analyze the following market trends and return a JSON list of objects matching the InsightCard schema. Do NOT use speculative phrases like 'will dominate', 'guarantees', 'revenue will'. Stay factual.\n\nTrends:\n"
        for t in trend_facts[:3]:
            prompt += f"- {t.keyword} (Trend: {t.trend_score:.1f}, Confidence: {t.confidence_score:.1f})\n"
            
        try:
            ai_response = ai_client.generate_insights(prompt)
            if ai_response and isinstance(ai_response, list):
                # Parse to Pydantic
                parsed_insights = [InsightCard(**card) for card in ai_response]
                
                # Check for banned phrases
                if BannedPhrasesReviewerAgent.review_insights(parsed_insights):
                    insights = parsed_insights
                    generated_by = "ai_router"
                    mode_used = "ai_router"
                    logger.info("AI Router generated insights successfully.")
                else:
                    logger.warning("AI Insights contained banned phrases. Falling back to rule-based.")
                    error_message = "Banned phrases detected"
            else:
                logger.warning("AI Response invalid format. Falling back to rule-based.")
                error_message = "Invalid JSON format"
        except Exception as e:
            logger.warning(f"AI Router failed: {e}. Falling back to rule-based.")
            error_message = str(e)
            
    if not insights:
        logger.info("Running rule-based generator.")
        generator = RuleBasedInsightGenerator()
        insights = generator.generate(trend_facts, articles)

    # Compile brief
    brief = InsightBrief(
        summary=f"Generated {len(insights)} insight cards using {mode_used}.",
        generated_by=generated_by,
        insights=insights
    )
    
    # Write outputs
    ReportWriterAgent.write_json(brief)
    ReportWriterAgent.write_markdown(brief)
    
    # Write log
    run_summary = InsightRunSummary(
        run_id=f"run_{int(datetime.now(timezone.utc).timestamp())}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        status="success",
        insights_generated=len(insights),
        mode_used=mode_used,
        error_message=error_message
    )
    
    log_file = LOGS_DIR / "insight_runs.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(run_summary.model_dump()) + "\n")
        
    logger.info(f"Pipeline completed successfully. Generated {len(insights)} insights via {mode_used}.")

if __name__ == "__main__":
    run_pipeline()
