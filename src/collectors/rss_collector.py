import hashlib
import datetime
import urllib.parse
from typing import List, Dict, Any

try:
    import feedparser
except ImportError:
    feedparser = None


def generate_stable_id(url: str, title: str, keyword: str) -> str:
    """
    Generates a stable SHA-256 ID based on URL, or title + keyword if URL is missing.
    """
    base_string = url if url else f"{title}-{keyword}"
    return hashlib.sha256(base_string.encode("utf-8")).hexdigest()

def normalize_article(entry: Any, keyword: str) -> Dict[str, Any]:
    """
    Normalizes a feedparser entry into the raw article schema.
    """
    url = getattr(entry, "link", "")
    title = getattr(entry, "title", "")
    
    # Try to get published date, fallback to now if missing
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        # Convert struct_time to datetime
        published_at = datetime.datetime(*entry.published_parsed[:6]).isoformat()
    elif hasattr(entry, "published"):
        published_at = entry.published
    else:
        published_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
    source = getattr(entry, "source", {}).get("title", "Google News RSS") if hasattr(entry, "source") else "Google News RSS"
    summary = getattr(entry, "summary", "")

    return {
        "id": generate_stable_id(url, title, keyword),
        "title": title,
        "url": url,
        "source": source,
        "published_at": published_at,
        "summary": summary,
        "keyword": keyword,
        "raw_text": None,
        "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "collected_from": "rss"
    }

def collect_from_rss(keyword: str) -> List[Dict[str, Any]]:
    """
    Collects news articles from Google News RSS for a specific keyword.
    """
    if feedparser is None:
        print("Warning: feedparser is not installed. RSS collection failed.")
        return []
        
    query = urllib.parse.quote_plus(keyword)
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        
        # Check if we actually got entries or if there's an error
        if feed.bozo and not feed.entries:
            print(f"Warning: Failed to parse RSS feed for '{keyword}': {feed.bozo_exception}")
            return []
            
        records = []
        for entry in feed.entries:
            record = normalize_article(entry, keyword)
            records.append(record)
            
        return records
    except Exception as e:
        print(f"Error collecting RSS for '{keyword}': {e}")
        return []

def run_rss_collection(keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Runs RSS collection for multiple keywords and aggregates the results.
    """
    all_records = []
    for keyword in keywords:
        print(f"Collecting RSS data for keyword: '{keyword}'")
        records = collect_from_rss(keyword)
        all_records.extend(records)
    
    return all_records
