import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import quote_plus, urlparse, parse_qs, urlencode

import feedparser
from notion_client import Client

# English Keywords
ENGLISH_KEYWORDS: List[str] = [
    "BMC",
    "Polls",
    "Mumbai Election",
    "Brihanmumbai",
    "Civic Polls"
]

# Marathi Keywords - Politicians/Parties + Civic/Election
MARATHI_KEYWORDS: List[str] = [
    "महायुती",
    "महाविकास आघाडी",
    "एकनाथ शिंदे",
    "देवेंद्र फडणवीस",
    "उद्धव ठाकरे",
    "शरद पवार",
    "मुंबई",
    "बृहन्मुंबई",
    "महानगरपालिका",
    "निवडणूक",
    "बीएमसी",
    "वॉर्ड",
]

KEYWORD_PRIORITY = {
    "BMC": 3,
    "Mumbai Election": 3,
    "Polls": 2,
    "Brihanmumbai": 1,
    "महायुती": 3,
    "महाविकास आघाडी": 3,
    "एकनाथ शिंदे": 3,
    "देवेंद्र फडणवीस": 3,
    "उद्धव ठाकरे": 3,
    "शरद पवार": 3,
    "बीएमसी": 3,
    "निवडणूक": 3,
    "महानगरपालिका": 2,
    "मुंबई": 2,
    "बृहन्मुंबई": 2,
    "वॉर्ड": 2,
}

MAX_ENGLISH_ARTICLES = 25
MAX_MARATHI_ARTICLES = 25

POLITICIANS: Dict[str, List[str]] = {
    "Congress": ["Varsha Gaikwad", "Bhai Jagtap"],
    "Shiv Sena (UBT)": ["Uddhav Thackeray", "Anil Parab", "Sanjay Raut"],
    "MNS": ["Raj Thackeray", "Nitin Sardesai", "Amit Thackeray", "Bala Nandgaonkar"],
    "Shiv Sena (Shinde)": ["Eknath Shinde", "Shrikant Shinde", "Krishna Hegde", "Milind Deora"],
    "NCP": ["Ajit Pawar", "Sharad Pawar", "Supriya Sule", "Chhagan Bhujbal"],
}

HISTORY_PATH = Path("history.json")
MAX_HISTORY_ENTRIES = 2000


def build_english_feed_url(keywords: List[str]) -> str:
    """Build Wide OR query for English search."""
    query = " OR ".join(f'"{kw}"' for kw in keywords)
    encoded = quote_plus(query)
    return (
        "https://news.google.com/rss/search?"
        f"q={encoded}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:d"
    )


def build_marathi_feed_url(keywords: List[str]) -> str:
    """Build Wide OR query for Marathi search with forced localization."""
    query = " OR ".join(f'"{kw}"' for kw in keywords)
    encoded = quote_plus(query)
    return (
        "https://news.google.com/rss/search?"
        f"q={encoded}&hl=mr-IN&gl=IN&ceid=IN:mr&tbs=qdr:d"
    )


def canonicalize_url(url: str) -> str:
    """Remove all query parameters and fragments to get canonical URL."""
    parsed = urlparse(url)
    # Keep only scheme, netloc, and path
    canonical = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return canonical.strip().lower()


def load_history(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [str(item) for item in data]
    except Exception:
        pass
    return []


def save_history(history: List[str], path: Path) -> None:
    trimmed = history[-MAX_HISTORY_ENTRIES:]
    with path.open("w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


def extract_date(entry) -> str:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        dt = datetime.fromtimestamp(time.mktime(parsed), tz=timezone.utc)
    else:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()


def extract_source(entry) -> str:
    source = entry.get("source")
    if isinstance(source, dict):
        title = source.get("title")
        if title:
            return str(title)
    if entry.get("source_title"):
        return str(entry.get("source_title"))
    if entry.get("author"):
        return str(entry.get("author"))
    return "Unknown"


def detect_language(text: str) -> str:
    """Detect if text is in Marathi or English based on Devanagari script."""
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    if devanagari_pattern.search(text):
        return "Marathi"
    return "English"


def detect_politician_and_party(title: str) -> tuple[str, str]:
    """Detect which politician and party from title."""
    title_lower = title.lower()
    for party, names in POLITICIANS.items():
        for politician in names:
            if politician.lower() in title_lower:
                return politician, party
    return "Unknown", "Unknown"


def fetch_english_articles() -> List[Dict[str, str]]:
    """Fetch top English articles using Wide OR query."""
    print("Fetching English articles...")
    feed_url = build_english_feed_url(ENGLISH_KEYWORDS)
    
    # Set headers for English localization
    headers = {
        'Accept-Language': 'en-IN, en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    parsed = feedparser.parse(feed_url, request_headers=headers)
    articles = []
    
    for entry in parsed.entries[:MAX_ENGLISH_ARTICLES]:
        link = entry.get("link")
        title = entry.get("title")
        if not link or not title:
            continue
        
        politician, party = detect_politician_and_party(str(title))
        
        # Determine priority based on keywords in title
        priority = 0
        for keyword, prio in KEYWORD_PRIORITY.items():
            if keyword.lower() in str(title).lower():
                priority = max(priority, prio)
        
        articles.append({
            "party": party,
            "politician": politician,
            "priority": priority,
            "title": str(title),
            "url": str(link),
            "canonical_url": canonicalize_url(str(link)),
            "source": extract_source(entry),
            "published": extract_date(entry),
            "language": "English",
        })
    
    print(f"Fetched {len(articles)} English articles")
    return articles


def fetch_marathi_articles() -> List[Dict[str, str]]:
    """Fetch top Marathi articles using Wide OR query with forced localization."""
    print("Fetching Marathi articles...")
    feed_url = build_marathi_feed_url(MARATHI_KEYWORDS)
    
    # Set headers for Marathi localization
    headers = {
        'Accept-Language': 'mr-IN, mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    parsed = feedparser.parse(feed_url, request_headers=headers)
    articles = []
    
    for entry in parsed.entries[:MAX_MARATHI_ARTICLES]:
        link = entry.get("link")
        title = entry.get("title")
        if not link or not title:
            continue
        
        politician, party = detect_politician_and_party(str(title))
        
        # Determine priority based on keywords in title
        priority = 0
        for keyword, prio in KEYWORD_PRIORITY.items():
            if keyword in str(title):
                priority = max(priority, prio)
        
        articles.append({
            "party": party,
            "politician": politician,
            "priority": priority,
            "title": str(title),
            "url": str(link),
            "canonical_url": canonicalize_url(str(link)),
            "source": extract_source(entry),
            "published": extract_date(entry),
            "language": "Marathi",
        })
    
    print(f"Fetched {len(articles)} Marathi articles")
    return articles


def create_notion_client() -> Client:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN environment variable is required")
    return Client(auth=token)


def push_to_notion(client: Client, database_id: str, article: Dict[str, str]) -> None:
    client.pages.create(
        parent={"database_id": database_id},
        properties={
            "Headline": {
                "title": [
                    {"text": {"content": article["title"][:1999]}}
                ]
            },
            "Politician": {"select": {"name": article["politician"]}},
            "Party": {"select": {"name": article["party"]}},
            "URL": {"url": article["url"]},
            "Source": {
                "rich_text": [
                    {"text": {"content": article["source"][:1999]}}
                ]
            },
            "Date": {"date": {"start": article["published"]}},
            "Language": {"select": {"name": article["language"]}},
        },
    )


def main() -> None:
    notion_db_id = os.environ.get("NOTION_DB_ID")
    if not notion_db_id:
        raise RuntimeError("NOTION_DB_ID environment variable is required")

    # Load history
    history = load_history(HISTORY_PATH)
    seen_in_history: Set[str] = set(history)
    new_history: List[str] = list(history)

    client = create_notion_client()

    # Fetch articles from both streams
    english_articles = fetch_english_articles()
    marathi_articles = fetch_marathi_articles()

    # Merge and deduplicate
    all_articles = english_articles + marathi_articles
    
    # Deduplicate within batch (prefer Marathi if duplicate)
    seen_canonical: Dict[str, Dict[str, str]] = {}
    for article in all_articles:
        canonical = article["canonical_url"]
        if canonical not in seen_canonical:
            seen_canonical[canonical] = article
        elif article["language"] == "Marathi":
            # Prefer Marathi version if duplicate
            seen_canonical[canonical] = article
    
    # Filter out articles already in history
    candidates = [
        article for article in seen_canonical.values()
        if article["canonical_url"] not in seen_in_history
    ]

    # Sort by priority then recency
    candidates.sort(key=lambda a: (a["priority"], a["published"]), reverse=True)

    print(f"\nProcessing {len(candidates)} new articles...")
    
    pushed = 0
    failed = 0
    
    for article in candidates:
        canonical_url = article["canonical_url"]
        try:
            push_to_notion(client, notion_db_id, article)
            pushed += 1
            new_history.append(canonical_url)
            seen_in_history.add(canonical_url)
            print(f"✓ Added [{article['language']}]: {article['title'][:80]}...")
        except Exception as exc:
            failed += 1
            print(f"✗ Failed [{article['language']}]: {article['title'][:80]}... Error: {exc}")

    save_history(new_history, HISTORY_PATH)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  English fetched: {len(english_articles)}")
    print(f"  Marathi fetched: {len(marathi_articles)}")
    print(f"  After dedup: {len(candidates)} new articles")
    print(f"  Successfully pushed: {pushed}")
    print(f"  Failed: {failed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
