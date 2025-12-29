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
from google_sheets import GoogleSheetsWriter
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


def run_scraper(doc_id=None, sheet_id=None):
    """
    Run the scraper and push results to Google Docs or Google Sheets
    
    Args:
        doc_id: Optional Google Doc ID to append to
        sheet_id: Optional Google Sheet ID to append to
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
            return doc_id, sheet_id
        
        # Determine output format
        output_format = config.OUTPUT_FORMAT.lower()
        
        if output_format == 'sheets':
            # Use Google Sheets
            sheets_writer = GoogleSheetsWriter()
            
            # Use provided sheet_id or create new spreadsheet
            if not sheet_id and config.GOOGLE_SHEET_ID:
                sheet_id = config.GOOGLE_SHEET_ID
            
            # Write articles to Google Sheet
            sheet_title = f"{config.SHEET_TITLE_PREFIX} - {datetime.now().strftime('%Y-%m-%d')}"
            sheet_id = sheets_writer.write_articles(
                articles,
                spreadsheet_id=sheet_id,
                spreadsheet_title=sheet_title,
                scraper=scraper
            )
            
            logger.info(f"Successfully processed {len(articles)} articles")
            logger.info(f"Spreadsheet ID: {sheet_id}")
            logger.info(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
            
        else:
            # Use Google Docs (default)
            docs_writer = GoogleDocsWriter()
            
            # Use provided doc_id or create new document
            if not doc_id and config.GOOGLE_DOC_ID:
                doc_id = config.GOOGLE_DOC_ID
            
            # Write articles to Google Doc
            doc_title = f"{config.DOC_TITLE_PREFIX} - {datetime.now().strftime('%Y-%m-%d')}"
            doc_id = docs_writer.write_articles(
                articles,
                doc_id=doc_id,
                doc_title=doc_title
            )
            
            logger.info(f"Successfully processed {len(articles)} articles")
            logger.info(f"Document ID: {doc_id}")
            logger.info(f"Document URL: https://docs.google.com/document/d/{doc_id}/edit")
        
        return doc_id, sheet_id
        
    except Exception as e:
        logger.error(f"Error in scraper run: {str(e)}", exc_info=True)
        return doc_id, sheet_id


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
        help='Google Doc ID to append articles to (optional, for docs output)'
    )
    parser.add_argument(
        '--sheet-id',
        help='Google Sheet ID to append articles to (optional, for sheets output)'
    )
    parser.add_argument(
        '--output',
        choices=['docs', 'sheets'],
        help='Output format: docs or sheets (overrides config.py setting)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=config.SCRAPE_INTERVAL_HOURS,
        help=f'Scraping interval in hours (default: {config.SCRAPE_INTERVAL_HOURS})'
    )
    
    args = parser.parse_args()
    
    # Override output format if specified
    if args.output:
        config.OUTPUT_FORMAT = args.output
    
    logger.info("RSS Feed Scraper Started")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Output: {config.OUTPUT_FORMAT}")
    logger.info(f"Keywords: {', '.join(config.KEYWORDS)}")
    logger.info(f"Feeds: {sum(len(feeds) for feeds in config.RSS_FEEDS.values())} total")
    
    if args.mode == 'once':
        # Run once and exit
        doc_id, sheet_id = run_scraper(doc_id=args.doc_id, sheet_id=args.sheet_id)
        logger.info("Scraper completed")
        
    else:
        # Run on schedule
        logger.info(f"Scheduling scraper to run every {args.interval} hour(s)")
        
        # Keep track of doc_id and sheet_id across runs
        doc_id = args.doc_id
        sheet_id = args.sheet_id
        
        def scheduled_run():
            nonlocal doc_id, sheet_id
            doc_id, sheet_id = run_scraper(doc_id=doc_id, sheet_id=sheet_id)
        
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
