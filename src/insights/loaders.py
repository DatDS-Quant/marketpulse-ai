import pandas as pd
from typing import List, Dict, Any
from src.utils.config import ANALYTICS_DATA_DIR, TRENDS_DATA_DIR
from .schemas import TrendSignalFact, SourceReliabilityFact, EvidenceArticle

class InsightDataLoader:
    @staticmethod
    def load_trend_facts() -> List[TrendSignalFact]:
        path = TRENDS_DATA_DIR / "top_trends.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path).fillna("")
        facts = []
        for _, row in df.iterrows():
            facts.append(TrendSignalFact(
                keyword=str(row.get("keyword", "")),
                trend_score=float(row.get("trend_score", 0.0)),
                confidence_score=float(row.get("confidence_score", 0.0)),
                article_count=int(row.get("article_count", 0)),
                severity=str(row.get("severity", "low"))
            ))
        return facts

    @staticmethod
    def load_source_facts() -> List[SourceReliabilityFact]:
        path = ANALYTICS_DATA_DIR / "source_metrics.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path).fillna("")
        facts = []
        for _, row in df.iterrows():
            facts.append(SourceReliabilityFact(
                source=str(row.get("source", "")),
                article_count=int(row.get("article_count", 0)),
                quality_score=float(row.get("source_quality_score", 0.0)),
                status=str(row.get("quality_status", ""))
            ))
        return facts

    @staticmethod
    def load_articles() -> List[EvidenceArticle]:
        path = ANALYTICS_DATA_DIR / "articles_clean.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path).fillna("")
        articles = []
        for _, row in df.iterrows():
            articles.append(EvidenceArticle(
                article_id=str(row.get("id", "")),
                title=str(row.get("title", "")),
                source=str(row.get("source", "")),
                keyword=str(row.get("keyword", "")),
                url=str(row.get("url", "")),
                published_at=str(row.get("published_at", ""))
            ))
        return articles
