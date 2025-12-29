"""
Simple test script to verify scraper functionality
Run this to test without Google Docs integration
"""

import logging
from scraper import RSSFeedScraper
import config

logging.basicConfig(level=logging.INFO)

def test_scraper():
    """Test the scraper without Google Docs"""
    print("Testing RSS Feed Scraper...")
    print(f"Keywords: {config.KEYWORDS}")
    print(f"Number of feeds: {sum(len(feeds) for feeds in config.RSS_FEEDS.values())}")
    print("\n" + "="*80 + "\n")
    
    # Initialize scraper
    scraper = RSSFeedScraper(config.KEYWORDS, config.RSS_FEEDS)
    
    # Scrape feeds
    articles = scraper.scrape_all_feeds(max_articles=10)
    
    print(f"\nFound {len(articles)} matching articles:\n")
    
    # Display articles
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']} ({article['language']})")
        print(f"   Link: {article['link']}")
        print(f"   Published: {article['published']}")
        
        # Show which keywords matched
        combined_text = f"{article['title']} {article['summary']}"
        matching_keywords = scraper.get_matching_keywords(combined_text)
        print(f"   Matched keywords: {', '.join(matching_keywords)}")
        print()
    
    print("="*80)
    print("Test completed successfully!")
    print("\nTo push to Google Docs, run: python main.py --mode once")

if __name__ == "__main__":
    test_scraper()
