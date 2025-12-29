"""
Google Docs Integration Module
Handles pushing articles to Google Docs
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

# Scopes for Google Docs API (includes Sheets for compatibility)
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]


class GoogleDocsWriter:
    """Handler for writing articles to Google Docs"""
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize Google Docs writer
        
        Args:
            credentials_file: Path to Google OAuth credentials file
        """
        self.credentials_file = credentials_file
        self.creds = None
        self.service = None
    
    def authenticate(self):
        """Authenticate with Google Docs API"""
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
        
        self.service = build('docs', 'v1', credentials=self.creds)
        logger.info("Successfully authenticated with Google Docs API")
        return True
    
    def create_document(self, title: str) -> str:
        """
        Create a new Google Doc
        
        Args:
            title: Title for the document
            
        Returns:
            Document ID
        """
        try:
            document = self.service.documents().create(body={'title': title}).execute()
            doc_id = document.get('documentId')
            logger.info(f"Created document: {title} (ID: {doc_id})")
            return doc_id
        except HttpError as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    def append_articles(self, doc_id: str, articles: List[Dict]):
        """
        Append articles to a Google Doc
        
        Args:
            doc_id: Google Doc ID
            articles: List of article dictionaries
        """
        if not articles:
            logger.info("No articles to append")
            return
        
        try:
            # Get current document content length
            document = self.service.documents().get(documentId=doc_id).execute()
            content = document.get('body').get('content')
            end_index = content[-1].get('endIndex', 1)
            
            # Build requests for batch update
            requests = []
            
            # Add header with timestamp
            header_text = f"\n\n{'='*80}\nArticles scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*80}\n\n"
            requests.append({
                'insertText': {
                    'location': {'index': end_index - 1},
                    'text': header_text
                }
            })
            
            current_index = end_index - 1 + len(header_text)
            
            # Add each article
            for i, article in enumerate(articles, 1):
                article_text = self._format_article(i, article)
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': article_text
                    }
                })
                current_index += len(article_text)
            
            # Execute batch update
            self.service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            logger.info(f"Successfully appended {len(articles)} articles to document")
            
        except HttpError as e:
            logger.error(f"Error appending articles: {e}")
            raise
    
    def _format_article(self, index: int, article: Dict) -> str:
        """
        Format an article for display in Google Docs
        
        Args:
            index: Article number
            article: Article dictionary
            
        Returns:
            Formatted article text
        """
        text = f"{index}. {article['title']}\n"
        text += f"   Source: {article['source']} ({article['language']})\n"
        text += f"   Published: {article['published']}\n"
        text += f"   Link: {article['link']}\n"
        
        if article.get('summary'):
            # Truncate summary if too long
            summary = article['summary']
            if len(summary) > 300:
                summary = summary[:297] + "..."
            text += f"   Summary: {summary}\n"
        
        text += "\n"
        return text
    
    def write_articles(self, articles: List[Dict], doc_id: str = None, 
                      doc_title: str = None) -> str:
        """
        Write articles to Google Doc (create new or append to existing)
        
        Args:
            articles: List of article dictionaries
            doc_id: Existing document ID (optional)
            doc_title: Title for new document (optional)
            
        Returns:
            Document ID
        """
        if not self.service:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Google Docs API")
        
        if not doc_id:
            if not doc_title:
                doc_title = f"News Articles - {datetime.now().strftime('%Y-%m-%d')}"
            doc_id = self.create_document(doc_title)
        
        self.append_articles(doc_id, articles)
        
        # Return the document URL
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        logger.info(f"Document URL: {doc_url}")
        
        return doc_id
