# Architecture and Design

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    RSS Feed Scraper                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   RSS Feeds │──────▶│   Scraper   │──────▶│ Google Docs  │
│             │      │             │      │              │
│ • English   │      │ • Parse     │      │ • Create Doc │
│ • Hindi     │      │ • Filter    │      │ • Append     │
│ • Marathi   │      │ • Dedupe    │      │ • Format     │
└─────────────┘      └─────────────┘      └──────────────┘
                           │
                           ▼
                     ┌─────────────┐
                     │  Scheduler  │
                     │             │
                     │ • 1 hour    │
                     │ • Manual    │
                     └─────────────┘
```

## Components

### 1. Scraper (`scraper.py`)
- Fetches RSS feeds from configured URLs
- Parses XML/RSS format
- Filters articles based on keywords (case-insensitive)
- Tracks seen URLs to avoid duplicates
- Returns structured article data

### 2. Google Docs Writer (`google_docs.py`)
- Handles OAuth authentication
- Creates or appends to Google Docs
- Formats articles for readability
- Manages API credentials

### 3. Main Controller (`main.py`)
- CLI interface
- Scheduling logic (using `schedule` library)
- Coordinates scraper and docs writer
- Logging and error handling

### 4. Configuration (`config.py`)
- Keywords list
- RSS feed URLs by language
- Scraping interval
- Document ID (optional)

## Data Flow

1. **Initialization**
   - Load configuration (keywords, RSS feeds)
   - Authenticate with Google Docs API (first run only)

2. **Scraping**
   - For each RSS feed:
     - Fetch and parse XML
     - Extract articles (title, summary, link, date)
     - Check if article contains any keyword
     - Filter out previously seen URLs

3. **Processing**
   - Sort articles by date (newest first)
   - Limit to max articles per run
   - Format for display

4. **Output**
   - Create new Google Doc or append to existing
   - Format each article with metadata
   - Add timestamp header
   - Log document URL

5. **Scheduling** (if enabled)
   - Sleep until next interval
   - Repeat from step 2

## Key Features

### Keyword Matching
- Case-insensitive search
- Searches in title and summary
- Supports multiple languages (UTF-8)
- Returns list of matched keywords per article

### Deduplication
- Tracks URLs in memory during session
- Prevents duplicate articles in same run
- Each run starts fresh (no persistent state)

### Error Handling
- Graceful handling of network errors
- Logs warnings for failed feeds
- Continues with remaining feeds on error
- Rate limiting (1 second between feeds)

### Google Docs Integration
- OAuth 2.0 authentication
- Token persistence (no re-auth needed)
- Batch updates for efficiency
- Formatted output with metadata

## Configuration Options

### Mode Selection
- **Once**: Run immediately and exit
- **Schedule**: Run continuously at intervals

### Document Strategy
- **New doc each run**: Leave `GOOGLE_DOC_ID` empty
- **Append to existing**: Provide document ID

### Customization
- Add/remove keywords in `config.py`
- Add/remove RSS feeds by language
- Adjust scraping interval
- Change max articles per run

## Deployment Options

1. **Local Machine**
   - Run manually: `python main.py --mode once`
   - Run scheduled: `python main.py --mode schedule`

2. **Linux Server (systemd)**
   - Service file included in README
   - Runs as background service
   - Auto-restart on failure

3. **GitHub Actions**
   - Workflow file: `.github/workflows/scraper.yml`
   - Runs on schedule (cron)
   - Stores credentials as secrets
   - Logs uploaded as artifacts

4. **Docker Container**
   - Dockerfile example in README
   - Portable and isolated
   - Volume mount for credentials

## Security Considerations

- Credentials stored locally (`.gitignore`d)
- OAuth tokens encrypted by Google
- No credentials in code
- HTTPS for all API calls
- Rate limiting to respect servers

## Limitations

- In-memory URL tracking (resets on restart)
- No database persistence
- Sequential feed processing
- Depends on RSS feed availability
- Subject to API rate limits

## Future Enhancements

Possible improvements:
- Database for persistent deduplication
- Parallel feed processing
- Email notifications
- Sentiment analysis
- Web dashboard
- Multiple output formats (Email, Slack, etc.)
- Advanced filtering (date range, source priority)
- Analytics and trends
