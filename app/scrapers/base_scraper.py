"""
Base scraper class for all news sources.
"""
import json
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import feedparser
from ratelimit import limits, sleep_and_retry
from newspaper import Article, ArticleException

import requests
from bs4 import BeautifulSoup

from utils.config import REQUEST_HEADERS, TOPICS, ARTICLES_CACHE_FILE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ScraperException(Exception):
    """Custom exception for scraper-related errors."""
    pass

class BaseScraper(ABC):
    """
    Base class for all news source scrapers.
    """
    
    # Rate limit: 1 request per 2 seconds
    CALLS_PER_SECOND = 1/2
    CACHE_TTL_DAYS = 1
    
    def __init__(self, source_name: str, base_url: str):
        """
        Initialize the scraper.
        
        Args:
            source_name: Name of the news source
            base_url: Base URL of the news source
        """
        self.source_name = source_name
        self.base_url = base_url
        self.headers = REQUEST_HEADERS
        self.logger = logging.getLogger(f"scraper.{source_name}")
        
    @sleep_and_retry
    @limits(calls=1, period=1/CALLS_PER_SECOND)
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a page and return a BeautifulSoup object.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if request failed
        
        Raises:
            ScraperException: If the request fails
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            raise ScraperException(f"Failed to fetch {url}: {e}")
    
    @sleep_and_retry
    @limits(calls=1, period=1/CALLS_PER_SECOND)
    def fetch_rss_feed(self, feed_url: str) -> Optional[List[Dict]]:
        """
        Fetch and parse an RSS feed.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            List of entries or None if request failed
            
        Raises:
            ScraperException: If the feed cannot be parsed
        """
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.get('status', 200) != 200:
                raise ScraperException(f"RSS feed error: Status {feed.get('status')}")
                
            return feed.entries
        except Exception as e:
            self.logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            raise ScraperException(f"Failed to parse RSS feed {feed_url}: {e}")
    
    @sleep_and_retry
    @limits(calls=1, period=1/CALLS_PER_SECOND)
    def extract_article_content(self, url: str) -> Dict:
        """
        Extract article content using Newspaper3k.
        
        Args:
            url: URL of the article
            
        Returns:
            Dict: Article data including title, text, publish date, and top image
            
        Raises:
            ScraperException: If the article cannot be parsed
        """
        try:
            # Configure article
            article = Article(url)
            article.headers = self.headers
            
            # Download and parse
            article.download()
            article.parse()
            
            # Extract metadata
            result = {
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'images': list(article.images),
            }
            
            # Try to extract more data if NLP is available
            try:
                article.nlp()
                result.update({
                    'summary': article.summary,
                    'keywords': article.keywords,
                })
            except Exception as e:
                self.logger.warning(f"NLP extraction failed for {url}: {e}")
                
            return result
            
        except ArticleException as e:
            self.logger.error(f"Error extracting article content from {url}: {e}")
            raise ScraperException(f"Failed to extract article content from {url}: {e}")
    
    def classify_topic(self, title: str, content: str) -> str:
        """
        Classify an article into one of the predefined topics.
        
        Args:
            title: Article title
            content: Article content or summary
            
        Returns:
            Topic key (e.g., "business", "science", etc.)
        """
        text = (title + " " + content).lower()
        
        # Count weighted keyword matches for each topic
        topic_scores = {}
        for topic_key, topic_data in TOPICS.items():
            score = 0
            # Title matches are worth more
            for keyword in topic_data["keywords"]:
                keyword = keyword.lower()
                if keyword in title.lower():
                    score += 2
                if keyword in content.lower():
                    score += 1
            topic_scores[topic_key] = score * topic_data.get("probability", 1.0)
        
        # Get topic with highest score
        max_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
        return max_topic
    
    def save_articles_to_cache(self, articles: List[Dict]) -> None:
        """
        Save scraped articles to cache file with TTL.
        
        Args:
            articles: List of article dictionaries
        """
        existing_articles = []
        current_time = datetime.now()
        
        # Load and clean existing cache
        if os.path.exists(ARTICLES_CACHE_FILE):
            try:
                with open(ARTICLES_CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Filter out expired articles
                    for article in cache_data:
                        cached_time = datetime.fromisoformat(article.get('cached_time', '2000-01-01'))
                        if current_time - cached_time < timedelta(days=self.CACHE_TTL_DAYS):
                            existing_articles.append(article)
            except json.JSONDecodeError:
                self.logger.warning("Cache file corrupted, starting fresh")
                existing_articles = []
        
        # Add new articles with timestamp
        existing_urls = {article.get('url') for article in existing_articles}
        for article in articles:
            if article.get('url') not in existing_urls:
                article['cached_time'] = current_time.isoformat()
                existing_articles.append(article)
        
        # Save updated cache
        try:
            with open(ARTICLES_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_articles, f, indent=4)
        except IOError as e:
            self.logger.error(f"Failed to save cache: {e}")
    
    def load_cached_articles(self) -> List[Dict]:
        """
        Load non-expired articles from cache file.
        
        Returns:
            List of article dictionaries
        """
        if not os.path.exists(ARTICLES_CACHE_FILE):
            return []
        
        try:
            current_time = datetime.now()
            with open(ARTICLES_CACHE_FILE, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                # Filter out expired articles
                return [
                    article for article in articles
                    if current_time - datetime.fromisoformat(article.get('cached_time', '2000-01-01'))
                    < timedelta(days=self.CACHE_TTL_DAYS)
                ]
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Failed to load cache: {e}")
            return []
    
    @abstractmethod
    def scrape_articles(self) -> List[Dict]:
        """
        Scrape articles from the news source.
        
        Returns:
            List of article dictionaries
            
        Raises:
            ScraperException: If scraping fails
        """
        pass 