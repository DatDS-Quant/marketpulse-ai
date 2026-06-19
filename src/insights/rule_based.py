import uuid
from datetime import datetime, timezone
from typing import List, Dict
from .schemas import InsightCard, TrendSignalFact, EvidenceArticle

class RuleBasedInsightGenerator:
    def generate(self, trends: List[TrendSignalFact], articles: List[EvidenceArticle]) -> List[InsightCard]:
        insights = []
        
        # Group articles by keyword
        articles_by_keyword = {}
        for a in articles:
            if a.keyword not in articles_by_keyword:
                articles_by_keyword[a.keyword] = []
            articles_by_keyword[a.keyword].append(a)

        for trend in trends:
            # Sort articles by length or title just to pick top 3
            evidences = articles_by_keyword.get(trend.keyword, [])[:3]
            
            factual_explanation = f"'{trend.keyword}' is a leading market signal with a trend score of {trend.trend_score:.1f} and confidence score of {trend.confidence_score:.1f}, supported by {trend.article_count} recent articles."
            
            limitation = "Confidence score is relatively low, indicating potential noise or single-source dependency." if trend.confidence_score < 60 else "No significant limitations detected. Signal appears robust."
            
            business_implication = f"The steady growth in '{trend.keyword}' suggests sustained market interest. Companies should evaluate their positioning relative to this area."
            
            next_step = "Monitor the keyword in the next run and review supporting articles in Evidence Explorer."
            
            insight = InsightCard(
                insight_id=str(uuid.uuid4()),
                keyword=trend.keyword,
                signal_type="Market Signal",
                severity=trend.severity,
                trend_score=trend.trend_score,
                confidence_score=trend.confidence_score,
                article_count=trend.article_count,
                source_count=len(set([e.source for e in evidences])),
                factual_explanation=factual_explanation,
                business_implication=business_implication,
                recommended_next_step=next_step,
                limitation=limitation,
                evidence_articles=evidences,
                generated_by="rule_based",
                created_at=datetime.now(timezone.utc).isoformat()
            )
            insights.append(insight)
            
        return insights
