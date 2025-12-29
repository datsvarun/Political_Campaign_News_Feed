"""
Unit tests for RSS Feed Scraper
Tests core functionality without requiring network access
"""

import unittest
from unittest.mock import Mock, patch
from scraper import RSSFeedScraper


class TestRSSFeedScraper(unittest.TestCase):
    """Test cases for RSSFeedScraper class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.keywords = ["AAP", "BJP", "Congress"]
        self.rss_feeds = {
            "english": ["http://example.com/rss"],
            "hindi": ["http://example.com/hindi/rss"]
        }
        self.scraper = RSSFeedScraper(self.keywords, self.rss_feeds)
    
    def test_initialization(self):
        """Test scraper initialization"""
        self.assertEqual(len(self.scraper.keywords), 3)
        self.assertEqual(self.scraper.keywords[0], "aap")  # Should be lowercase
        self.assertEqual(len(self.scraper.rss_feeds), 2)
        self.assertIsInstance(self.scraper.seen_urls, set)
    
    def test_matches_keywords_positive(self):
        """Test keyword matching with positive cases"""
        # Exact match
        self.assertTrue(self.scraper.matches_keywords("AAP announces new policy"))
        
        # Case insensitive
        self.assertTrue(self.scraper.matches_keywords("The BJP leader said"))
        self.assertTrue(self.scraper.matches_keywords("congress party meeting"))
        
        # Keywords in middle
        self.assertTrue(self.scraper.matches_keywords("The AAP government has decided"))
    
    def test_matches_keywords_negative(self):
        """Test keyword matching with negative cases"""
        self.assertFalse(self.scraper.matches_keywords("Weather update for Mumbai"))
        self.assertFalse(self.scraper.matches_keywords("Stock market closes higher"))
        self.assertFalse(self.scraper.matches_keywords(""))
    
    def test_matches_keywords_partial_words(self):
        """Test that partial word matches work"""
        # "AAP" should match in "KAAP" as substring search
        self.assertTrue(self.scraper.matches_keywords("KAAP"))
    
    def test_get_matching_keywords(self):
        """Test getting list of matched keywords"""
        text = "AAP and BJP leaders meet for discussion"
        matched = self.scraper.get_matching_keywords(text)
        self.assertEqual(len(matched), 2)
        self.assertIn("aap", matched)
        self.assertIn("bjp", matched)
    
    def test_get_matching_keywords_none(self):
        """Test getting matched keywords when none match"""
        text = "Weather is good today"
        matched = self.scraper.get_matching_keywords(text)
        self.assertEqual(len(matched), 0)
    
    @patch('feedparser.parse')
    def test_parse_feed_success(self, mock_parse):
        """Test successful feed parsing"""
        # Mock feed response
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.feed = {'title': 'Test Feed'}
        mock_feed.entries = [
            {
                'title': 'AAP announces policy',
                'summary': 'Details about the policy',
                'link': 'http://example.com/article1',
                'published': '2025-12-29T10:00:00Z'
            }
        ]
        mock_parse.return_value = mock_feed
        
        articles = self.scraper.parse_feed("http://example.com/rss", "english")
        
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['title'], 'AAP announces policy')
        self.assertEqual(articles[0]['language'], 'english')
        self.assertIn('http://example.com/article1', self.scraper.seen_urls)
    
    @patch('feedparser.parse')
    def test_parse_feed_no_matches(self, mock_parse):
        """Test feed parsing with no keyword matches"""
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.feed = {'title': 'Test Feed'}
        mock_feed.entries = [
            {
                'title': 'Weather Update',
                'summary': 'Sunny day expected',
                'link': 'http://example.com/article2',
                'published': '2025-12-29T10:00:00Z'
            }
        ]
        mock_parse.return_value = mock_feed
        
        articles = self.scraper.parse_feed("http://example.com/rss", "english")
        
        self.assertEqual(len(articles), 0)
    
    @patch('feedparser.parse')
    def test_parse_feed_duplicate_urls(self, mock_parse):
        """Test that duplicate URLs are filtered out"""
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.feed = {'title': 'Test Feed'}
        mock_feed.entries = [
            {
                'title': 'AAP policy',
                'summary': 'Details',
                'link': 'http://example.com/same-article',
                'published': '2025-12-29T10:00:00Z'
            }
        ]
        mock_parse.return_value = mock_feed
        
        # Add URL to seen_urls
        self.scraper.seen_urls.add('http://example.com/same-article')
        
        articles = self.scraper.parse_feed("http://example.com/rss", "english")
        
        # Should return 0 because URL was already seen
        self.assertEqual(len(articles), 0)


class TestConfig(unittest.TestCase):
    """Test configuration file"""
    
    def test_config_imports(self):
        """Test that config file can be imported"""
        try:
            import config
            self.assertTrue(hasattr(config, 'KEYWORDS'))
            self.assertTrue(hasattr(config, 'RSS_FEEDS'))
            self.assertTrue(hasattr(config, 'SCRAPE_INTERVAL_HOURS'))
        except ImportError:
            self.fail("Could not import config module")
    
    def test_config_structure(self):
        """Test config has proper structure"""
        import config
        
        self.assertIsInstance(config.KEYWORDS, list)
        self.assertGreater(len(config.KEYWORDS), 0)
        
        self.assertIsInstance(config.RSS_FEEDS, dict)
        self.assertIn('english', config.RSS_FEEDS)
        self.assertIn('hindi', config.RSS_FEEDS)
        self.assertIn('marathi', config.RSS_FEEDS)


if __name__ == '__main__':
    unittest.main()
