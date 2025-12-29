"""
Example configuration file
Copy this to config.py and customize for your needs
"""

# Keywords to search for in articles (case-insensitive)
KEYWORDS = [
    # Your party
    "AAP",
    "Aam Aadmi Party",
    "आम आदमी पार्टी",
    
    # Key leaders (example)
    "Arvind Kejriwal",
    "अरविंद केजरीवाल",
    
    # Opponents
    "BJP",
    "Congress",
    "Shiv Sena",
    
    # Campaign issues (example)
    "Mumbai",
    "Maharashtra",
]

# RSS Feed URLs
RSS_FEEDS = {
    "english": [
        "https://timesofindia.indiatimes.com/rssfeeds/4118245.cms",
        "https://indianexpress.com/section/cities/mumbai/feed/",
    ],
    "hindi": [
        "https://www.bhaskar.com/rss-feed/1061/",
    ],
    "marathi": [
        "https://maharashtratimes.com/rssfeedstopstories.cms",
        "https://www.loksatta.com/rss/",
    ]
}

# Leave empty to create new doc, or provide ID to append
GOOGLE_DOC_ID = ""
DOC_TITLE_PREFIX = "AAP News Monitor"

# Scraping configuration
SCRAPE_INTERVAL_HOURS = 1
MAX_ARTICLES_PER_RUN = 50
