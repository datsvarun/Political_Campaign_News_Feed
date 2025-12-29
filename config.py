"""
Configuration file for RSS Feed Scraper
Customize this file with your keywords and RSS feed URLs
"""

# Keywords to search for in articles (case-insensitive)
KEYWORDS = [
    # Party-related keywords
    "AAP",
    "Aam Aadmi Party",
    "आम आदमी पार्टी",
    "आम आदमी पक्ष",
    
    # Key political opponents (example - customize as needed)
    "BJP",
    "भाजपा",
    "Congress",
    "कांग्रेस",
    "Shiv Sena",
    "शिवसेना",
    
    # Add more keywords as needed
]

# RSS Feed URLs for different languages
RSS_FEEDS = {
    # English News Sources
    "english": [
        "https://timesofindia.indiatimes.com/rssfeeds/4118245.cms",  # Mumbai Times of India
        "https://indianexpress.com/section/cities/mumbai/feed/",  # Indian Express Mumbai
        "https://www.hindustantimes.com/feeds/rss/mumbai-news/rssfeed.xml",  # Hindustan Times Mumbai
        "https://www.ndtv.com/mumbai-news/rss",  # NDTV Mumbai
    ],
    
    # Hindi News Sources
    "hindi": [
        "https://www.bhaskar.com/rss-feed/1061/",  # Dainik Bhaskar Maharashtra
        "https://www.jagran.com/rss/maharashtra.xml",  # Dainik Jagran Maharashtra
        "https://navbharattimes.indiatimes.com/rssfeeds/-2129530452.cms",  # Navbharat Times
    ],
    
    # Marathi News Sources
    "marathi": [
        "https://maharashtratimes.com/rssfeedstopstories.cms",  # Maharashtra Times
        "https://www.loksatta.com/rss/",  # Loksatta
        "https://www.esakal.com/feed",  # Esakal
        "https://www.lokmat.com/feed/",  # Lokmat
    ]
}

# Google Docs Configuration
GOOGLE_DOC_ID = ""  # Leave empty if you want to create a new doc each time, or provide a specific document ID
DOC_TITLE_PREFIX = "AAP News Monitor"  # Prefix for document titles when creating new docs

# Scraping Configuration
SCRAPE_INTERVAL_HOURS = 1  # How often to scrape (in hours)
MAX_ARTICLES_PER_RUN = 50  # Maximum articles to fetch per scraping run
