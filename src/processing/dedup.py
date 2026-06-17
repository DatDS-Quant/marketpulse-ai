"""Deduplication logic for ETL."""

from typing import List
from src.processing.models import ProcessedArticle

def deduplicate_records(articles: List[ProcessedArticle]) -> List[ProcessedArticle]:
    """Removes exact duplicates based on id and url. Keeps first occurrence."""
    seen_ids = set()
    seen_urls = set()
    unique_articles = []
    
    for article in articles:
        if article.id in seen_ids or article.url in seen_urls:
            continue
            
        seen_ids.add(article.id)
        seen_urls.add(article.url)
        unique_articles.append(article)
        
    return unique_articles
