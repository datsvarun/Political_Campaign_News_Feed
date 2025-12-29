# AAP Mumbai RSS Feed Scraper

A Python-based RSS feed scraper that monitors news articles in English, Hindi, and Marathi based on configurable keywords. Perfect for political campaigns to track media coverage and competitor mentions.

## Features

- 📰 Scrapes multiple RSS feeds in English, Hindi, and Marathi
- 🔍 Keyword-based filtering for relevant articles
- 📝 Automatically pushes articles to Google Docs
- ⏰ Scheduled execution (runs every 1 hour by default)
- 🚀 Easy to configure and customize
- 📊 Logs all activities for monitoring

## Requirements

- Python 3.7 or higher
- Google Cloud Project with Docs API enabled
- Google OAuth credentials

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/datsvarun/AAP_Mumbai_RSS_Feed.git
   cd AAP_Mumbai_RSS_Feed
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Docs API**
   
   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project (or select an existing one)
   
   c. Enable the Google Docs API:
      - Go to "APIs & Services" > "Library"
      - Search for "Google Docs API"
      - Click "Enable"
   
   d. Create OAuth credentials:
      - Go to "APIs & Services" > "Credentials"
      - Click "Create Credentials" > "OAuth client ID"
      - Choose "Desktop app" as application type
      - Download the credentials and save as `credentials.json` in the project root

4. **Configure the scraper**
   
   Edit `config.py` to customize:
   - Keywords to search for
   - RSS feed URLs for different languages
   - Scraping interval
   - Google Doc ID (optional)

## Configuration

### Keywords

Edit the `KEYWORDS` list in `config.py`:

```python
KEYWORDS = [
    "AAP",
    "Aam Aadmi Party",
    "आम आदमी पार्टी",
    # Add more keywords...
]
```

### RSS Feeds

Add or modify RSS feed URLs in `config.py`:

```python
RSS_FEEDS = {
    "english": [
        "https://timesofindia.indiatimes.com/rssfeeds/4118245.cms",
        # Add more English feeds...
    ],
    "hindi": [
        "https://www.bhaskar.com/rss-feed/1061/",
        # Add more Hindi feeds...
    ],
    "marathi": [
        "https://maharashtratimes.com/rssfeedstopstories.cms",
        # Add more Marathi feeds...
    ]
}
```

### Google Doc ID

To append to an existing Google Doc, set `GOOGLE_DOC_ID` in `config.py`:

```python
GOOGLE_DOC_ID = "your-document-id-here"
```

Leave it empty to create a new document for each run.

## Usage

### Run Once

To run the scraper once and exit:

```bash
python main.py --mode once
```

### Run on Schedule

To run the scraper continuously on a schedule:

```bash
python main.py --mode schedule --interval 1
```

This will scrape feeds every 1 hour.

### Append to Existing Document

To append to a specific Google Doc:

```bash
python main.py --mode once --doc-id YOUR_DOCUMENT_ID
```

### Command Line Options

- `--mode`: Run mode (`once` or `schedule`)
- `--doc-id`: Google Doc ID to append articles to
- `--interval`: Scraping interval in hours (default: 1)

## First Run

On the first run, the script will:
1. Open a browser window for Google OAuth authentication
2. Ask you to sign in with your Google account
3. Request permission to access Google Docs
4. Save the authentication token for future runs

## Output

The scraper will:
- Create or append to a Google Doc with all matching articles
- Log all activities to console and `scraper.log`
- Display the Google Doc URL after each run

### Example Output Format

```
================================================================================
Articles scraped on: 2025-12-29 14:10:00
================================================================================

1. AAP announces new policy for Mumbai
   Source: Times of India (english)
   Published: 2025-12-29T10:30:00Z
   Link: https://...
   Summary: The Aam Aadmi Party announced...

2. भाजपा ने AAP पर लगाए आरोप
   Source: Dainik Bhaskar (hindi)
   Published: 2025-12-29T09:15:00Z
   Link: https://...
   Summary: भारतीय जनता पार्टी ने...
```

## Running as a Service

### Linux (systemd)

Create a systemd service file `/etc/systemd/system/rss-scraper.service`:

```ini
[Unit]
Description=RSS Feed Scraper
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/AAP_Mumbai_RSS_Feed
ExecStart=/usr/bin/python3 main.py --mode schedule
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable rss-scraper
sudo systemctl start rss-scraper
```

### Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py", "--mode", "schedule"]
```

Build and run:

```bash
docker build -t rss-scraper .
docker run -v $(pwd)/credentials.json:/app/credentials.json rss-scraper
```

## GitHub Actions

You can also run this scraper on GitHub Actions. Create `.github/workflows/scraper.yml`:

```yaml
name: RSS Feed Scraper

on:
  schedule:
    - cron: '0 * * * *'  # Run every hour
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python main.py --mode once
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
```

Store your credentials as a GitHub Secret.

## Troubleshooting

### Authentication Issues

If you get authentication errors:
1. Delete `token.pickle`
2. Re-run the script to re-authenticate

### RSS Feed Errors

If some feeds fail:
- Check if the RSS feed URL is still valid
- Some sites may block scrapers - try adding rate limiting
- Check the logs for specific error messages

### No Articles Found

If no articles are found:
- Check if your keywords are correct
- Try broadening your keyword list
- Verify RSS feeds are returning content

## Logs

All activities are logged to:
- Console output (real-time)
- `scraper.log` file (persistent)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues or questions, please create an issue on GitHub.

## Disclaimer

This tool is for monitoring publicly available RSS feeds. Please respect:
- Website terms of service
- Rate limits and server resources
- Copyright and content ownership

Always use responsibly and ethically.
