from typing import List, Dict, Any, Tuple
from src.evidence.schemas import (
    EvidenceIndex, EvidenceRecord, CitationRecord, 
    CitationMap, InsightEvidenceLink
)
from src.evidence.retriever import retrieve_evidence_for_keyword

def map_citations_to_insights(
    index: EvidenceIndex,
    insight_cards: List[Dict[str, Any]]
) -> Tuple[CitationMap, List[InsightEvidenceLink]]:
    
    citation_records: Dict[str, CitationRecord] = {}
    insight_links: List[InsightEvidenceLink] = []
    
    citation_counter = 1
    # article_id -> citation_id mapping to reuse citations for the same article
    article_to_citation: Dict[str, str] = {}
    
    for card in insight_cards:
        insight_id = str(card.get('id', 'unknown'))
        keyword = str(card.get('keyword', ''))
        
        if not keyword:
            insight_links.append(InsightEvidenceLink(
                insight_id=insight_id,
                keyword=keyword,
                citation_ids=[],
                evidence_count=0,
                has_evidence=False,
                missing_evidence_reason="Insight has no keyword to query."
            ))
            continue
            
        # Retrieve top evidence
        retrieved = retrieve_evidence_for_keyword(index, keyword, top_k=3)
        
        if not retrieved:
            insight_links.append(InsightEvidenceLink(
                insight_id=insight_id,
                keyword=keyword,
                citation_ids=[],
                evidence_count=0,
                has_evidence=False,
                missing_evidence_reason="No matching evidence found in index."
            ))
            continue
            
        citation_ids = []
        for record, score, matched_terms in retrieved:
            # Check if this article was already cited
            if record.article_id in article_to_citation:
                cit_id = article_to_citation[record.article_id]
                # We can update used_for_insight_id to be a list if we want, 
                # but currently schema supports a string. Let's just keep the original or append.
                # For simplicity, we just reuse the citation ID.
            else:
                cit_id = f"[E{citation_counter}]"
                citation_counter += 1
                article_to_citation[record.article_id] = cit_id
                
                citation_records[cit_id] = CitationRecord(
                    citation_id=cit_id,
                    article_id=record.article_id,
                    title=record.title,
                    source=record.source,
                    url=record.url,
                    keyword=record.keyword,
                    published_at=record.published_at,
                    quality_flags=record.quality_flags,
                    relevance_score=score,
                    matched_terms=matched_terms,
                    used_for_insight_id=insight_id
                )
            
            citation_ids.append(cit_id)
            
        insight_links.append(InsightEvidenceLink(
            insight_id=insight_id,
            keyword=keyword,
            citation_ids=citation_ids,
            evidence_count=len(citation_ids),
            has_evidence=True
        ))
        
    return CitationMap(citations=citation_records), insight_links
