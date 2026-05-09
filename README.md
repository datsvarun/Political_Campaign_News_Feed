# Political Campaign News Feed (Google News RSS → Notion)

Automated news monitoring system designed to track media coverage relevant to the Mumbai Municipal Corporation Election (BMC Polls 2026).
The system aggregates news articles across multiple sources and languages, filters them using election-specific keywords, and publishes the results to a structured workspace for campaign monitoring.

A lightweight Python bot that:
1. Searches **Google News RSS** for campaign/civic-election coverage using configurable keywords (currently **English + Marathi**).
2. **Ranks** stories by keyword priority.
3. **Deduplicates** by canonical URL and keeps a local `history.json` so you don’t re-add the same story.
4. Pushes new articles into a **Notion database** for review by campaign/research teams.

> Repo focus (current defaults): monitoring Mumbai civic / BMC election coverage and major Maharashtra political actors.
>
> Telangana-focused variant: use `bot_telangana.py` for Telangana-specific news/headlines/people/politics monitoring.

<img width="1525" height="684" alt="image" src="https://github.com/user-attachments/assets/9296fe51-aea1-424e-8088-4a7387460319" />


---

## How it works (high level)

1. Build two Google News RSS search URLs:
   - English feed (`hl=en-IN&gl=IN&ceid=IN:en`)
   - Marathi feed (`hl=mr-IN&gl=IN&ceid=IN:mr`)
2. Fetch articles with `feedparser`
3. Normalize links to a **canonical URL** (drops query params/fragments)
4. Assign:
   - `language` (English/Marathi)
   - `priority` (based on keyword hits)
   - `party/politician` (simple name matching in the title)
5. Push each new article as a new page in a Notion database
6. Append pushed canonical URLs to `history.json`

---

## Repository layout

- `bot.py` — main script (Mumbai/BMC defaults)
- `bot_telangana.py` — Telangana-focused script (English + Telugu streams, Telangana relevance filters)
- `requirements.txt` — dependencies
- `history.json` — local dedupe store (already-seen canonical URLs)
- `history_telangana.json` — local dedupe store for Telangana scraper

---

## Requirements

- Python 3.10+ recommended
- A Notion integration token + a Notion database

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## Notion setup (API secret keys + database)

### 1) Create a Notion Integration + token

1. Go to Notion Integrations and create an internal integration
2. Copy the **Internal Integration Secret** (this becomes `NOTION_TOKEN`)

### 2) Create / prepare a Notion database

Create a database (table view) with the following properties (names matter because `bot.py` uses them):

| Property name | Type |
|---|---|
| `Headline` | Title |
| `Politician` | Select |
| `Party` | Select |
| `URL` | URL |
| `Source` | Rich text |
| `Date` | Date |
| `Language` | Select |

Notes:
- The script uses **Select** for `Politician`, `Party`, and `Language`. If Notion doesn’t already contain an option, Notion will typically create it when the API sends a new select value (depending on your workspace settings/database behavior).

### 3) Share the database with the integration

Open the database → **Share** → invite your integration (so it can write pages).

### 4) Get the Notion Database ID

You’ll need the database ID for `NOTION_DB_ID`.
Common approach:
- Open the database in the browser and copy the URL; the database ID is the long hex-like string in the URL.

---

## Configuration (keywords, languages, ranking)

All configuration is currently in **`bot.py`**.

### Keywords

Edit these lists:

```python
ENGLISH_KEYWORDS = [
    "BMC",
    "Polls",
    "Mumbai Election",
    "Brihanmumbai",
    "Civic Polls",
]

MARATHI_KEYWORDS = [
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
```

How search is constructed:
- The bot builds a *wide OR query* like: "kw1" OR "kw2" OR "kw3" and URL-encodes it.
- Google News RSS is queried with a **last-day** time filter via `tbs=qdr:d`.

### Keyword priority (ranking)

Articles are sorted by:
1) `priority` (higher first), then
2) `published` (more recent first)

Edit `KEYWORD_PRIORITY` to tune ranking:

```python
KEYWORD_PRIORITY = {
    "BMC": 3,
    "Mumbai Election": 3,
    "Polls": 2,
    "Brihanmumbai": 1,
    "महायुती": 3,
    # ...
}
```

### “Languages” / localization

The script currently uses two separate feeds with different localization parameters:

- English:
  - `hl=en-IN`
  - `gl=IN`
  - `ceid=IN:en`
- Marathi:
  - `hl=mr-IN`
  - `gl=IN`
  - `ceid=IN:mr`

If you want other languages/regions, update:
- `build_english_feed_url()` / `build_marathi_feed_url()`
- request headers in `fetch_english_articles()` / `fetch_marathi_articles()` ( `Accept-Language`)

### Politician/party detection

The bot tags articles by scanning the title for known names:

```python
POLITICIANS = {
  "Congress": ["Varsha Gaikwad", "Bhai Jagtap"],
  "Shiv Sena (UBT)": ["Uddhav Thackeray", "Anil Parab", "Sanjay Raut"],
  # ...
}
```

Update this map for your target geography/candidates.

---

## Secrets & environment variables (API keys)

This project uses environment variables (no `.env` file is included by default).

Required:

- `NOTION_TOKEN` — Notion integration secret
- `NOTION_DB_ID` — target Notion database ID

### macOS / Linux

```bash
export NOTION_TOKEN="secret_xxx"
export NOTION_DB_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
python bot.py
```

### Windows (PowerShell)

```powershell
setx NOTION_TOKEN "secret_xxx"
setx NOTION_DB_ID "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
python bot.py
```

---

## Running the bot

```bash
python bot.py
```

### Running Telangana scraper

Dry-run sample (recommended first):

```bash
DRY_RUN=1 python bot_telangana.py
```

Offline validation sample (no network required):

```bash
OFFLINE_SAMPLE=1 python bot_telangana.py
```

Production run to push to Notion:

```bash
export NOTION_TOKEN="secret_xxx"
export NOTION_DB_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
python bot_telangana.py
```

`bot_telangana.py` prioritizes Telangana categories (`Telangana News`, `Telangana Headlines`, `People`, `State Politics`) and applies Telangana-specific entity filters.

Expected behavior:
- Fetches up to `MAX_ENGLISH_ARTICLES` and `MAX_MARATHI_ARTICLES`
- Deduplicates within the batch (prefers Marathi if the canonical URL matches)
- Skips anything already listed in `history.json`
- Pushes remaining items into Notion
- Updates `history.json`

---

## Deduplication details (`history.json`)

- `history.json` stores a list of canonical URLs already pushed.
- Canonicalization currently keeps only: `scheme://netloc/path` and lowercases it (query params removed).

If you want more/less aggressive dedupe, adjust `canonicalize_url()` in `bot.py`.

---

## Troubleshooting

### `RuntimeError: NOTION_TOKEN environment variable is required`
Set `NOTION_TOKEN` in your shell/session (see above).

### `RuntimeError: NOTION_DB_ID environment variable is required`
Set `NOTION_DB_ID` in your shell/session (see above).

### Notion permission errors (401/403)
- Ensure the integration token is correct
- Ensure the database is **shared** with the integration

### Notion validation errors for properties
Your database schema must match the property names/types listed above (especially `Headline` as Title).

---

## Roadmap ideas (optional)
- Move keywords/priorities/politicians into a `config.json` or YAML file
- Add `.env.example` + optional `python-dotenv`
- Add GitHub Actions schedule to run automatically
- Add per-source weighting, sentiment, or topic classification

---

## Disclaimer

This tool aggregates publicly available links via Google News RSS and is intended for research/workflow automation. Always verify sources and comply with applicable laws/platform terms.
