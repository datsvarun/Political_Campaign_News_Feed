"""
Google Sheets Integration Module
Handles pushing articles to Google Sheets
"""

import logging
from datetime import datetime
from typing import List, Dict
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

logger = logging.getLogger(__name__)

# Scopes for Google Sheets API (includes Docs for compatibility)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents'
]


class GoogleSheetsWriter:
    """Handler for writing articles to Google Sheets"""
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize Google Sheets writer
        
        Args:
            credentials_file: Path to Google OAuth credentials file
        """
        self.credentials_file = credentials_file
        self.creds = None
        self.service = None
    
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        token_file = 'token.pickle'
        
        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Refreshing credentials...")
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    logger.error("Please download credentials.json from Google Cloud Console")
                    return False
                
                logger.info("Starting authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('sheets', 'v4', credentials=self.creds)
        logger.info("Successfully authenticated with Google Sheets API")
        return True
    
    def create_spreadsheet(self, title: str) -> str:
        """
        Create a new Google Spreadsheet
        
        Args:
            title: Title for the spreadsheet
            
        Returns:
            Spreadsheet ID
        """
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [{
                    'properties': {
                        'title': 'Articles',
                        'gridProperties': {
                            'frozenRowCount': 1
                        }
                    }
                }]
            }
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            logger.info(f"Created spreadsheet: {title} (ID: {spreadsheet_id})")
            
            # Add header row
            self._add_header_row(spreadsheet_id)
            
            return spreadsheet_id
            
        except HttpError as e:
            logger.error(f"Error creating spreadsheet: {e}")
            raise
    
    def _add_header_row(self, spreadsheet_id: str):
        """
        Add header row to the spreadsheet
        
        Args:
            spreadsheet_id: Google Spreadsheet ID
        """
        headers = [
            'Timestamp',
            'Title',
            'Link',
            'Summary',
            'Source',
            'Language',
            'Published Date',
            'Matched Keywords'
        ]
        
        try:
            # Add headers
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='Articles!A1:H1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            # Format header row (bold, background color)
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {
                                'red': 0.9,
                                'green': 0.9,
                                'blue': 0.9
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            }, {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 8
                    }
                }
            }]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
        except HttpError as e:
            logger.error(f"Error adding header row: {e}")
            raise
    
    def append_articles(self, spreadsheet_id: str, articles: List[Dict], scraper=None):
        """
        Append articles to a Google Sheet
        
        Args:
            spreadsheet_id: Google Spreadsheet ID
            articles: List of article dictionaries
            scraper: Optional scraper instance to get matched keywords
        """
        if not articles:
            logger.info("No articles to append")
            return
        
        try:
            # Prepare rows
            rows = []
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for article in articles:
                # Get matched keywords if scraper is provided
                matched_keywords = ''
                if scraper:
                    combined_text = f"{article['title']} {article.get('summary', '')}"
                    keywords = scraper.get_matching_keywords(combined_text)
                    matched_keywords = ', '.join(keywords)
                
                # Truncate summary if too long
                summary = article.get('summary', '')
                if len(summary) > 500:
                    summary = summary[:497] + "..."
                
                row = [
                    timestamp,
                    article['title'],
                    article['link'],
                    summary,
                    article['source'],
                    article['language'],
                    article.get('published', ''),
                    matched_keywords
                ]
                rows.append(row)
            
            # Append rows to sheet
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Articles!A:H',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()
            
            logger.info(f"Successfully appended {len(articles)} articles to spreadsheet")
            
        except HttpError as e:
            logger.error(f"Error appending articles: {e}")
            raise
    
    def write_articles(self, articles: List[Dict], spreadsheet_id: str = None,
                      spreadsheet_title: str = None, scraper=None) -> str:
        """
        Write articles to Google Sheet (create new or append to existing)
        
        Args:
            articles: List of article dictionaries
            spreadsheet_id: Existing spreadsheet ID (optional)
            spreadsheet_title: Title for new spreadsheet (optional)
            scraper: Optional scraper instance to get matched keywords
            
        Returns:
            Spreadsheet ID
        """
        if not self.service:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Google Sheets API")
        
        if not spreadsheet_id:
            if not spreadsheet_title:
                spreadsheet_title = f"News Articles - {datetime.now().strftime('%Y-%m-%d')}"
            spreadsheet_id = self.create_spreadsheet(spreadsheet_title)
        
        self.append_articles(spreadsheet_id, articles, scraper)
        
        # Return the spreadsheet URL
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        logger.info(f"Spreadsheet URL: {sheet_url}")
        
        return spreadsheet_id
