"""
RSS Feed Scraper Module
Fetches and filters news articles based on keywords
"""

import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Set
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RSSFeedScraper:
    """Scraper for RSS feeds with keyword filtering"""
    
    def __init__(self, keywords: List[str], rss_feeds: Dict[str, List[str]]):
        """
        Initialize the scraper
        
        Args:
            keywords: List of keywords to filter articles
            rss_feeds: Dictionary of language -> list of RSS feed URLs
        """
        self.keywords = [k.lower() for k in keywords]
        self.rss_feeds = rss_feeds
        self.seen_urls: Set[str] = set()
    
    def matches_keywords(self, text: str) -> bool:
        """
        Check if text contains any of the keywords
        
        Args:
            text: Text to check
            
        Returns:
            True if any keyword is found, False otherwise
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)
    
    def parse_feed(self, feed_url: str, language: str) -> List[Dict]:
        """
        Parse a single RSS feed
        
        Args:
            feed_url: URL of the RSS feed
            language: Language of the feed
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        try:
            logger.info(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            for entry in feed.entries:
                # Get article details
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                link = entry.get('link', '')
                published = entry.get('published', '') or entry.get('updated', '')
                
                # Skip if we've already seen this URL
                if link in self.seen_urls:
                    continue
                
                # Check if article matches keywords
                combined_text = f"{title} {summary}"
                if self.matches_keywords(combined_text):
                    article = {
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'published': published,
                        'language': language,
                        'source': feed.feed.get('title', feed_url),
                        'fetched_at': datetime.now().isoformat()
                    }
                    articles.append(article)
                    self.seen_urls.add(link)
                    logger.info(f"Found matching article: {title[:50]}...")
            
        except Exception as e:
            logger.error(f"Error parsing feed {feed_url}: {str(e)}")
        
        return articles
    
    def scrape_all_feeds(self, max_articles: int = 50) -> List[Dict]:
        """
        Scrape all configured RSS feeds
        
        Args:
            max_articles: Maximum number of articles to return
            
        Returns:
            List of article dictionaries
        """
        all_articles = []
        
        for language, feeds in self.rss_feeds.items():
            logger.info(f"Scraping {language} feeds...")
            for feed_url in feeds:
                articles = self.parse_feed(feed_url, language)
                all_articles.extend(articles)
                
                # Rate limiting - be nice to the servers
                time.sleep(1)
        
        # Sort by published date (most recent first)
        all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        # Limit to max_articles
        all_articles = all_articles[:max_articles]
        
        logger.info(f"Total articles found: {len(all_articles)}")
        return all_articles
    
    def get_matching_keywords(self, text: str) -> List[str]:
        """
        Get list of keywords that match in the text
        
        Args:
            text: Text to check
            
        Returns:
            List of matching keywords
        """
        text_lower = text.lower()
        return [kw for kw in self.keywords if kw in text_lower]
