from pathlib import Path
from typing import Dict, Any, List
from src.evidence.schemas import CitationMap, InsightEvidenceLink, RetrievalManifest
from src.utils.config import REPORTS_TEMPLATES_DIR, REPORTS_GENERATED_DIR

def generate_cited_markdown_report(
    insight_cards: List[Dict[str, Any]],
    citation_map: CitationMap,
    insight_links: List[InsightEvidenceLink],
    manifest: RetrievalManifest
):
    template_path = REPORTS_TEMPLATES_DIR / "cited_market_brief_template.md"
    report_path = REPORTS_GENERATED_DIR / "market_brief_with_citations.md"
    
    if not template_path.exists():
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace metadata
    content = content.replace("{{ insight_count }}", str(manifest.insights_processed))
    content = content.replace("{{ citation_count }}", str(manifest.citations_created))
    content = content.replace("{{ articles_indexed }}", str(manifest.articles_indexed))
    content = content.replace("{{ generated_at }}", manifest.timestamp)
    content = content.replace("{{ missing_evidence_count }}", str(manifest.insights_missing_evidence))
    
    # Generate Top Signals & Interpretations
    top_signals = []
    interpretations = []
    
    link_lookup = {link.insight_id: link for link in insight_links}
    
    for card in insight_cards:
        insight_id = str(card.get('id', 'unknown'))
        keyword = str(card.get('keyword', 'unknown'))
        trend_score = card.get('trend_score', 0)
        conf_score = card.get('confidence_score', 0)
        
        explanation = card.get('factual_explanation', '')
        
        link = link_lookup.get(insight_id)
        
        citation_str = ""
        if link and link.has_evidence:
            citation_str = "".join(link.citation_ids)
            
        top_signals.append(f"- **{keyword}** (Trend: {trend_score}, Confidence: {conf_score}) {citation_str}")
        
        if explanation:
            interpretations.append(f"### {keyword}\n{explanation} {citation_str}\n")
            
    content = content.replace("{{ top_signals }}", "\n".join(top_signals) if top_signals else "No signals found.")
    content = content.replace("{{ interpretations }}", "\n".join(interpretations) if interpretations else "No interpretations available.")
    
    # Generate Citation Table
    citation_table_lines = []
    
    # Sort citations numerically by E number to make table clean
    sorted_citations = sorted(citation_map.citations.values(), key=lambda c: int(c.citation_id[2:-1]))
    
    for cit in sorted_citations:
        title = cit.title.replace('\n', ' ').strip()
        source = cit.source.strip()
        pub_date = cit.published_at[:10] if cit.published_at else "Unknown Date"
        url_link = f"([link]({cit.url}))" if cit.url else ""
        
        citation_table_lines.append(f"- **{cit.citation_id}** {title} — *{source}* — {pub_date} {url_link}")
        
    content = content.replace("{{ citation_table }}", "\n".join(citation_table_lines) if citation_table_lines else "No citations available.")
    
    REPORTS_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
