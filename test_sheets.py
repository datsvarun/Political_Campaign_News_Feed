"""
Simple test script to verify Google Sheets integration
Run this to test Google Sheets without full scraping
"""

import logging
from datetime import datetime
from google_sheets import GoogleSheetsWriter

logging.basicConfig(level=logging.INFO)

def test_sheets():
    """Test Google Sheets writer"""
    print("Testing Google Sheets Integration...")
    print("\n" + "="*80 + "\n")
    
    # Sample articles
    articles = [
        {
            'title': 'AAP announces new policy for Mumbai',
            'link': 'https://example.com/article1',
            'summary': 'The Aam Aadmi Party announced a new policy framework for Mumbai focusing on infrastructure development.',
            'source': 'Times of India',
            'language': 'english',
            'published': '2025-12-29T10:30:00Z',
            'fetched_at': datetime.now().isoformat()
        },
        {
            'title': 'भाजपा ने AAP पर लगाए आरोप',
            'link': 'https://example.com/article2',
            'summary': 'भारतीय जनता पार्टी ने आम आदमी पार्टी पर भ्रष्टाचार के आरोप लगाए हैं।',
            'source': 'Dainik Bhaskar',
            'language': 'hindi',
            'published': '2025-12-29T09:15:00Z',
            'fetched_at': datetime.now().isoformat()
        }
    ]
    
    # Initialize writer
    writer = GoogleSheetsWriter()
    
    # Write articles
    sheet_id = writer.write_articles(
        articles,
        spreadsheet_title="Test News Articles"
    )
    
    print(f"\n{'='*80}")
    print("Test completed successfully!")
    print(f"Spreadsheet ID: {sheet_id}")
    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    print("\nCheck the spreadsheet to verify articles are formatted correctly.")

if __name__ == "__main__":
    test_sheets()
