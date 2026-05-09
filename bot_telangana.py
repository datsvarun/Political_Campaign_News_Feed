import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import quote_plus, urlparse, parse_qs

import feedparser
from notion_client import Client

# Telangana-focused keywords (English)
ENGLISH_KEYWORDS: List[str] = [
    "Telangana News",
    "Telangana Headlines",
    "Telangana Politics",
    "Hyderabad Politics",
    "Telangana Assembly",
    "GHMC",
    "BRS",
    "Congress Telangana",
    "BJP Telangana",
    "Revanth Reddy",
    "KTR",
    "KCR",
    "Huzurabad",
]

# Telangana-focused keywords (Telugu)
TELUGU_KEYWORDS: List[str] = [
    "తెలంగాణ",
    "తెలంగాణ వార్తలు",
    "తెలంగాణ రాజకీయాలు",
    "హైదరాబాద్",
    "జీహెచ్ఎంసీ",
    "తెలంగాణ అసెంబ్లీ",
    "బీఆర్ఎస్",
    "తెలంగాణ కాంగ్రెస్",
    "తెలంగాణ బీజేపీ",
    "రేవంత్ రెడ్డి",
    "కేటీఆర్",
    "కేసీఆర్",
]

KEYWORD_PRIORITY = {
    "telangana politics": 4,
    "telangana assembly": 4,
    "ghmc": 4,
    "telangana headlines": 3,
    "hyderabad politics": 3,
    "brs": 3,
    "congress telangana": 3,
    "bjp telangana": 3,
    "తెలంగాణ రాజకీయాలు": 4,
    "తెలంగాణ అసెంబ్లీ": 4,
    "జీహెచ్ఎంసీ": 4,
    "తెలంగాణ": 3,
    "హైదరాబాద్": 3,
    "బీఆర్ఎస్": 3,
}

MAX_ENGLISH_ARTICLES = 40
MAX_TELUGU_ARTICLES = 40

TELANGANA_DISTRICTS = {
    "adilabad", "bhadradri kothagudem", "hanamkonda", "hyderabad", "jagtial",
    "jangaon", "jayashankar bhupalpally", "jogulamba gadwal", "kamareddy",
    "karimnagar", "khammam", "komaram bheem", "mahabubabad", "mahabubnagar",
    "mancherial", "medak", "medchal malkajgiri", "mulugu", "nagarkurnool",
    "nalgonda", "narayanpet", "nirmal", "nizamabad", "peddapalli",
    "rajanna sircilla", "rangareddy", "sangareddy", "siddipet", "suryapet",
    "vikarabad", "wanaparthy", "warangal", "yadadri bhuvanagiri",
}

TELANGANA_ENTITIES = {
    "telangana", "hyderabad", "secunderabad", "ghmc", "hitech city",
    "telangana assembly", "telangana government", "secretariat", "charminar",
}

TELANGANA_PARTIES = {
    "brs", "bharat rastra samithi", "congress", "bjp", "aimim", "cpi", "cpm",
}

POLITICAL_TERMS = {
    "politics", "election", "poll", "assembly", "mla", "mp", "cabinet", "manifesto",
    "minister", "party", "campaign", "రాజకీయాలు", "ఎన్నిక", "అసెంబ్లీ", "మంత్రి",
}

POLITICIANS: Dict[str, List[str]] = {
    "Congress": ["Revanth Reddy", "Mallu Bhatti Vikramarka", "Uttam Kumar Reddy"],
    "BRS": ["K. Chandrashekar Rao", "KCR", "K. T. Rama Rao", "KTR", "Harish Rao"],
    "BJP": ["G. Kishan Reddy", "Bandi Sanjay Kumar", "Etela Rajender"],
    "AIMIM": ["Asaduddin Owaisi", "Akbaruddin Owaisi"],
}

HISTORY_PATH = Path("history_telangana.json")
MAX_HISTORY_ENTRIES = 3000


TELUGU_SCRIPT = re.compile(r"[\u0C00-\u0C7F]")


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def build_feed_url(keywords: List[str], hl: str, ceid: str) -> str:
    query = " OR ".join(f'"{kw}"' for kw in keywords)
    constrained_query = (
        f"({query}) AND (\"Telangana\" OR \"Hyderabad\" OR \"తెలంగాణ\" OR \"హైదరాబాద్\")"
    )
    encoded = quote_plus(constrained_query)
    return (
        "https://news.google.com/rss/search?"
        f"q={encoded}&hl={hl}&gl=IN&ceid={ceid}&tbs=qdr:d"
    )


def extract_target_url(url: str) -> str:
    parsed = urlparse(url)
    if "news.google.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if "url" in query and query["url"]:
            return query["url"][0]
    return url


def canonicalize_url(url: str) -> str:
    target_url = extract_target_url(url)
    parsed = urlparse(target_url)
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
    if TELUGU_SCRIPT.search(text):
        return "Telugu"
    return "English"


def detect_politician_and_party(title: str) -> tuple[str, str]:
    title_lower = title.lower()
    for party, names in POLITICIANS.items():
        for politician in names:
            if politician.lower() in title_lower:
                return politician, party
    return "Unknown", "Unknown"


def calculate_priority(text: str) -> int:
    text_lower = text.lower()
    priority = 0
    for keyword, prio in KEYWORD_PRIORITY.items():
        if keyword in text_lower:
            priority = max(priority, prio)
    return priority


def categorize_article(text: str) -> str:
    text_lower = text.lower()

    if any(person.lower() in text_lower for people in POLITICIANS.values() for person in people):
        return "People"
    if any(term in text_lower for term in POLITICAL_TERMS):
        return "State Politics"
    if "headline" in text_lower or "హెడ్లైన్స్" in text_lower:
        return "Telangana Headlines"
    return "Telangana News"


def build_tags(category: str) -> List[str]:
    return ["Telangana", category]


def is_telangana_relevant(article: Dict[str, str]) -> bool:
    text = f"{article['title']} {article['source']} {article['url']}".lower()

    has_geo = any(term in text for term in TELANGANA_ENTITIES)
    has_district = any(term in text for term in TELANGANA_DISTRICTS)
    has_party = any(term in text for term in TELANGANA_PARTIES)
    has_politics = any(term in text for term in POLITICAL_TERMS)
    has_telugu_keyword = any(keyword in text for keyword in (k.lower() for k in TELUGU_KEYWORDS))
    has_english_keyword = any(keyword.lower() in text for keyword in ENGLISH_KEYWORDS)

    # Keep strongly Telangana-specific items and avoid generic national noise
    return (has_geo or has_district or has_telugu_keyword or has_english_keyword) and (
        has_politics or has_party or "telangana" in text or "హైదరాబాద్" in article["title"]
    )


def fetch_articles(keywords: List[str], language: str, hl: str, ceid: str, max_articles: int) -> List[Dict[str, str]]:
    print(f"Fetching {language} articles...")
    feed_url = build_feed_url(keywords, hl=hl, ceid=ceid)

    accept_language = "en-IN, en;q=0.9" if language == "English" else "te-IN, te;q=0.9"
    headers = {
        "Accept-Language": accept_language,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    parsed = feedparser.parse(feed_url, request_headers=headers)
    articles = []

    for entry in parsed.entries[:max_articles]:
        link = entry.get("link")
        title = entry.get("title")
        if not link or not title:
            continue

        resolved_link = extract_target_url(str(link))
        politician, party = detect_politician_and_party(str(title))
        category = categorize_article(str(title))
        priority = calculate_priority(str(title))

        article = {
            "party": party,
            "politician": politician,
            "priority": priority,
            "category": category,
            "tags": build_tags(category),
            "title": str(title),
            "url": resolved_link,
            "canonical_url": canonicalize_url(str(link)),
            "source": extract_source(entry),
            "published": extract_date(entry),
            "language": detect_language(str(title)) if language == "Telugu" else "English",
        }

        if is_telangana_relevant(article):
            articles.append(article)

    print(f"Fetched {len(articles)} relevant {language} articles")
    return articles


def create_notion_client() -> Client:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN environment variable is required")
    return Client(auth=token)


def get_database_property_types(client: Client, database_id: str) -> Dict[str, str]:
    response = client.databases.retrieve(database_id=database_id)
    properties = response.get("properties", {})
    return {
        name: str(defn.get("type", ""))
        for name, defn in properties.items()
        if isinstance(defn, dict)
    }


def push_to_notion(
    client: Client,
    database_id: str,
    article: Dict[str, str],
    property_types: Dict[str, str],
) -> None:
    properties = {
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
    }

    # Optional Telangana prioritization metadata when schema supports it
    if property_types.get("Category") == "select":
        properties["Category"] = {"select": {"name": article["category"]}}
    elif property_types.get("Category") == "multi_select":
        properties["Category"] = {"multi_select": [{"name": article["category"]}]}

    if property_types.get("Tags") == "multi_select":
        properties["Tags"] = {"multi_select": [{"name": tag} for tag in article["tags"]]}

    client.pages.create(parent={"database_id": database_id}, properties=properties)


def print_sample(candidates: List[Dict[str, str]], sample_size: int = 10) -> None:
    print("\nSample Telangana-focused results:")
    print("-" * 80)
    for idx, article in enumerate(candidates[:sample_size], start=1):
        print(
            f"{idx:02d}. [{article['category']}] [{article['language']}] "
            f"{article['title'][:100]}"
        )
        print(f"    Source: {article['source']} | URL: {article['url']}")


def summarize_categories(candidates: List[Dict[str, str]]) -> None:
    counts: Dict[str, int] = {}
    for article in candidates:
        counts[article["category"]] = counts.get(article["category"], 0) + 1

    print("\nCategory distribution:")
    for category, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        print(f"  - {category}: {count}")


def main() -> None:
    dry_run = env_flag("DRY_RUN", default=False)

    # Load history
    history = load_history(HISTORY_PATH)
    seen_in_history: Set[str] = set(history)
    new_history: List[str] = list(history)

    # Fetch Telangana-focused articles from English + Telugu streams
    english_articles = fetch_articles(
        ENGLISH_KEYWORDS,
        language="English",
        hl="en-IN",
        ceid="IN:en",
        max_articles=MAX_ENGLISH_ARTICLES,
    )
    telugu_articles = fetch_articles(
        TELUGU_KEYWORDS,
        language="Telugu",
        hl="te-IN",
        ceid="IN:te",
        max_articles=MAX_TELUGU_ARTICLES,
    )

    # Merge and deduplicate (prefer Telugu if duplicate)
    all_articles = english_articles + telugu_articles
    seen_canonical: Dict[str, Dict[str, str]] = {}
    for article in all_articles:
        canonical = article["canonical_url"]
        if canonical not in seen_canonical:
            seen_canonical[canonical] = article
        elif article["language"] == "Telugu":
            seen_canonical[canonical] = article

    # Filter out articles already in history
    candidates = [
        article for article in seen_canonical.values()
        if article["canonical_url"] not in seen_in_history
    ]

    # Sort by priority then recency
    candidates.sort(key=lambda a: (a["priority"], a["published"]), reverse=True)

    print(f"\nProcessing {len(candidates)} new Telangana articles...")
    summarize_categories(candidates)
    print_sample(candidates)

    if dry_run:
        print("\nDRY_RUN is enabled; skipping Notion writes and history updates.")
        return

    notion_db_id = os.environ.get("NOTION_DB_ID")
    if not notion_db_id:
        raise RuntimeError("NOTION_DB_ID environment variable is required")

    client = create_notion_client()
    property_types = get_database_property_types(client, notion_db_id)

    pushed = 0
    failed = 0

    for article in candidates:
        canonical_url = article["canonical_url"]
        try:
            push_to_notion(client, notion_db_id, article, property_types)
            pushed += 1
            new_history.append(canonical_url)
            seen_in_history.add(canonical_url)
            print(f"✓ Added [{article['category']} | {article['language']}]: {article['title'][:80]}...")
        except Exception as exc:
            failed += 1
            print(f"✗ Failed [{article['language']}]: {article['title'][:80]}... Error: {exc}")

    save_history(new_history, HISTORY_PATH)

    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  English fetched: {len(english_articles)}")
    print(f"  Telugu fetched: {len(telugu_articles)}")
    print(f"  After dedup: {len(candidates)} new articles")
    print(f"  Successfully pushed: {pushed}")
    print(f"  Failed: {failed}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
