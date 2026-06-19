from src.evals.schemas import InsightQualityResult, CheckResult
from typing import Dict, Any, Optional

BANNED_PHRASES = [
    "will dominate", "guarantees", "definitely", "revenue will",
    "invest immediately", "guaranteed demand", "guaranteed growth",
    "must invest", "certain to", "explode in revenue"
]

def evaluate_insight_quality(insight_brief: Optional[Dict[str, Any]]) -> InsightQualityResult:
    checks = []
    
    insight_count = 0
    banned_phrases_count = 0
    completeness_score = 1.0
    
    if not insight_brief or "insights" not in insight_brief:
        checks.append(CheckResult(
            name="Insight Generation",
            status="FAIL",
            score=0,
            message="Insight brief is missing or empty."
        ))
        return InsightQualityResult(
            insight_count=0,
            banned_phrases_count=0,
            completeness_score=0.0,
            checks=checks
        )

    insights = insight_brief["insights"]
    insight_count = len(insights)
    
    checks.append(CheckResult(
        name="Insight Count",
        status="PASS" if insight_count >= 3 else ("WARN" if insight_count > 0 else "FAIL"),
        score=insight_count,
        message=f"Generated {insight_count} insights."
    ))

    # Check for completeness and banned phrases
    incomplete_count = 0
    
    for insight in insights:
        text_to_check = str(insight.get("factual_explanation", "")) + " " + \
                        str(insight.get("business_implication", "")) + " " + \
                        str(insight.get("recommended_next_step", "")) + " " + \
                        str(insight.get("limitation", ""))
        text_lower = text_to_check.lower()
        
        for phrase in BANNED_PHRASES:
            if phrase in text_lower:
                banned_phrases_count += 1
                
        if not insight.get("limitation") or not insight.get("recommended_next_step"):
            incomplete_count += 1

    completeness_score = ((insight_count - incomplete_count) / insight_count) if insight_count > 0 else 0.0

    checks.append(CheckResult(
        name="Banned Phrases",
        status="PASS" if banned_phrases_count == 0 else "FAIL",
        score=banned_phrases_count,
        message=f"Found {banned_phrases_count} banned phrase occurrences."
    ))

    checks.append(CheckResult(
        name="Completeness Score",
        status="PASS" if completeness_score == 1.0 else "WARN",
        score=completeness_score,
        message=f"Completeness score: {completeness_score*100:.1f}%"
    ))

    return InsightQualityResult(
        insight_count=insight_count,
        banned_phrases_count=banned_phrases_count,
        completeness_score=completeness_score,
        checks=checks
    )
