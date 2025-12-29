# Quick Start Guide

Get started with the RSS Feed Scraper in 5 minutes!

## Prerequisites
- Python 3.7 or higher
- Google account
- Internet connection

## Installation

### 1. Clone and Setup
```bash
git clone https://github.com/datsvarun/AAP_Mumbai_RSS_Feed.git
cd AAP_Mumbai_RSS_Feed
chmod +x setup.sh
./setup.sh
```

### 2. Configure Keywords and Output
Edit `config.py` and customize:
```python
KEYWORDS = [
    "AAP",
    "Aam Aadmi Party",
    "BJP",
    "Congress",
    # Add your keywords...
]

# Choose output format
OUTPUT_FORMAT = "sheets"  # or "docs"
```

### 3. Get Google Credentials
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Google Docs API and Google Sheets API
4. Create OAuth credentials (Desktop app)
5. Download as `credentials.json`

### 4. Run the Scraper

**Test without Google APIs:**
```bash
python test_scraper.py
```

**Run once (with Google Sheets - default):**
```bash
python main.py --mode once
```

**Run once (with Google Docs):**
```bash
python main.py --mode once --output docs
```

On first run, it will open a browser for authentication.

**Run on schedule (every hour):**
```bash
python main.py --mode schedule
```

## Common Commands

```bash
# Run once with Google Sheets (default)
python main.py --mode once

# Run once with Google Docs
python main.py --mode once --output docs

# Run every 2 hours with Google Sheets
python main.py --mode schedule --interval 2 --output sheets

# Append to specific spreadsheet
python main.py --mode once --sheet-id YOUR_SHEET_ID

# Append to specific document
python main.py --mode once --output docs --doc-id YOUR_DOC_ID

# Test without Google APIs
python test_scraper.py

# Test Google Sheets integration
python test_sheets.py

# Run unit tests
python test_unit.py

# View logs
tail -f scraper.log
```

## File Structure

```
AAP_Mumbai_RSS_Feed/
├── main.py              # Main script - run this
├── scraper.py           # RSS feed scraper
├── google_docs.py       # Google Docs integration
├── google_sheets.py     # Google Sheets integration
├── config.py            # Configuration (customize this)
├── requirements.txt     # Dependencies
├── README.md            # Full documentation
├── ARCHITECTURE.md      # System design
├── TROUBLESHOOTING.md   # Common issues
├── test_scraper.py      # Integration test
├── test_sheets.py       # Google Sheets test
├── test_unit.py         # Unit tests
└── setup.sh            # Setup script
```

## Configuration Quick Reference

**config.py:**
- `KEYWORDS` - List of keywords to search for
- `RSS_FEEDS` - Dictionary of RSS feed URLs by language
- `OUTPUT_FORMAT` - Choose "docs" or "sheets" (default: "sheets")
- `GOOGLE_DOC_ID` - Document ID to append to (optional)
- `GOOGLE_SHEET_ID` - Spreadsheet ID to append to (optional)
- `DOC_TITLE_PREFIX` - Prefix for new document titles
- `SHEET_TITLE_PREFIX` - Prefix for new spreadsheet titles
- `SCRAPE_INTERVAL_HOURS` - How often to scrape (default: 1)
- `MAX_ARTICLES_PER_RUN` - Max articles per run (default: 50)

## Output Formats

### Google Sheets (Recommended)
Articles are organized in columns:
- **Timestamp** - When the article was scraped
- **Title** - Article headline
- **Link** - URL to full article
- **Summary** - Article summary/excerpt
- **Source** - News source name
- **Language** - Article language (english/hindi/marathi)
- **Published Date** - Original publication date
- **Matched Keywords** - Keywords that triggered the match

### Google Docs
Articles are formatted as text with:
- Title
- Source name and language
- Published date
- Link to full article
- Summary (if available)
- Timestamp of when scraped

## Deployment Options

### Local Machine
```bash
python main.py --mode schedule
```

### Linux Server
```bash
# Run in background
nohup python main.py --mode schedule &

# Or use systemd (see README.md)
```

### GitHub Actions
Already configured! Just:
1. Add `GOOGLE_CREDENTIALS` secret (contents of credentials.json)
2. Add `GOOGLE_DOC_ID` secret (your document ID)
3. Push to GitHub

Workflow runs automatically every hour.

## Troubleshooting

**No articles found?**
- Check your keywords are spelled correctly
- RSS feeds may only have recent articles
- Try broadening your keyword list

**Authentication errors?**
- Delete `token.pickle` and re-authenticate
- Make sure you downloaded Desktop app credentials

**Network errors?**
- Check internet connection
- Some networks block RSS feeds
- Try different network or VPN

**More help?**
See TROUBLESHOOTING.md for detailed solutions.

## Next Steps

1. ✅ Install and test the scraper
2. 📝 Customize keywords in config.py
3. 📰 Add more RSS feed URLs
4. 🔄 Set up scheduled execution
5. 📊 Monitor scraper.log for issues

## Support

- Issues: https://github.com/datsvarun/AAP_Mumbai_RSS_Feed/issues
- Documentation: README.md
- Architecture: ARCHITECTURE.md
- Troubleshooting: TROUBLESHOOTING.md

## Tips

- Start with a small keyword list and expand
- Test with `--mode once` before scheduling
- Check logs regularly for errors
- Use a dedicated Google account for automation
- Keep credentials.json secure (never commit to git)

Happy scraping! 🚀
