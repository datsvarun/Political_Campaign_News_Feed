"""
Main script for RSS Feed Scraper
Runs the scraper and pushes results to Google Docs
"""

import logging
import schedule
import time
import argparse
from datetime import datetime

from scraper import RSSFeedScraper
from google_docs import GoogleDocsWriter
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_scraper(doc_id=None):
    """
    Run the scraper and push results to Google Docs
    
    Args:
        doc_id: Optional Google Doc ID to append to
    """
    logger.info("="*80)
    logger.info(f"Starting scraper run at {datetime.now()}")
    logger.info("="*80)
    
    try:
        # Initialize scraper
        scraper = RSSFeedScraper(config.KEYWORDS, config.RSS_FEEDS)
        
        # Scrape all feeds
        articles = scraper.scrape_all_feeds(max_articles=config.MAX_ARTICLES_PER_RUN)
        
        if not articles:
            logger.info("No matching articles found in this run")
            return doc_id
        
        # Initialize Google Docs writer
        docs_writer = GoogleDocsWriter()
        
        # Use provided doc_id or create new document
        if not doc_id and config.GOOGLE_DOC_ID:
            doc_id = config.GOOGLE_DOC_ID
        
        # Write articles to Google Doc
        doc_id = docs_writer.write_articles(
            articles, 
            doc_id=doc_id,
            doc_title=f"AAP News Monitor - {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        logger.info(f"Successfully processed {len(articles)} articles")
        logger.info(f"Document ID: {doc_id}")
        logger.info(f"Document URL: https://docs.google.com/document/d/{doc_id}/edit")
        
        return doc_id
        
    except Exception as e:
        logger.error(f"Error in scraper run: {str(e)}", exc_info=True)
        return doc_id


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='RSS Feed Scraper for Political News')
    parser.add_argument(
        '--mode',
        choices=['once', 'schedule'],
        default='once',
        help='Run once or on schedule (default: once)'
    )
    parser.add_argument(
        '--doc-id',
        help='Google Doc ID to append articles to (optional)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=config.SCRAPE_INTERVAL_HOURS,
        help=f'Scraping interval in hours (default: {config.SCRAPE_INTERVAL_HOURS})'
    )
    
    args = parser.parse_args()
    
    logger.info("RSS Feed Scraper Started")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Keywords: {', '.join(config.KEYWORDS)}")
    logger.info(f"Feeds: {sum(len(feeds) for feeds in config.RSS_FEEDS.values())} total")
    
    if args.mode == 'once':
        # Run once and exit
        doc_id = run_scraper(doc_id=args.doc_id)
        logger.info("Scraper completed")
        
    else:
        # Run on schedule
        logger.info(f"Scheduling scraper to run every {args.interval} hour(s)")
        
        # Keep track of doc_id across runs
        doc_id = args.doc_id
        
        def scheduled_run():
            nonlocal doc_id
            doc_id = run_scraper(doc_id=doc_id)
        
        # Run immediately on start
        scheduled_run()
        
        # Schedule subsequent runs
        schedule.every(args.interval).hours.do(scheduled_run)
        
        logger.info("Scraper is running. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scraper stopped by user")


if __name__ == "__main__":
    main()
