"""
Base scraper class for all news sources.
"""
import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import random
import time
import feedparser
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.utils.config import REQUEST_HEADERS, TOPICS, ARTICLES_CACHE_FILE


class BaseScraper(ABC):
    """
    Base class for all news source scrapers.
    """
    
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
        
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a page and return a BeautifulSoup object.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        try:
            # Add random delay to appear more human-like
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except (requests.RequestException, Exception) as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def fetch_rss_feed(self, feed_url: str) -> Optional[List[Dict]]:
        """
        Fetch and parse an RSS feed.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            List of entries or None if request failed
        """
        try:
            # Add random delay to appear more human-like
            time.sleep(random.uniform(0.5, 2))
            
            feed = feedparser.parse(feed_url)
            
            if feed.get('status', 200) != 200:
                print(f"Error fetching RSS feed {feed_url}: Status {feed.get('status')}")
                return None
                
            return feed.entries
        except Exception as e:
            print(f"Error parsing RSS feed {feed_url}: {e}")
            return None
    
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
        
        # Count keyword matches for each topic
        topic_scores = {}
        for topic_key, topic_data in TOPICS.items():
            score = 0
            for keyword in topic_data["keywords"]:
                if keyword.lower() in text:
                    score += 1
            topic_scores[topic_key] = score
        
        # Get topic with highest score
        max_score = 0
        max_topic = list(TOPICS.keys())[0]  # Default to first topic
        
        for topic, score in topic_scores.items():
            if score > max_score:
                max_score = score
                max_topic = topic
        
        return max_topic
    
    def save_articles_to_cache(self, articles: List[Dict]) -> None:
        """
        Save scraped articles to cache file.
        
        Args:
            articles: List of article dictionaries
        """
        existing_articles = []
        
        # Load existing cache if available
        if os.path.exists(ARTICLES_CACHE_FILE):
            try:
                with open(ARTICLES_CACHE_FILE, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except json.JSONDecodeError:
                existing_articles = []
        
        # Add new articles, avoiding duplicates by URL
        existing_urls = [article.get('url') for article in existing_articles]
        
        for article in articles:
            if article.get('url') not in existing_urls:
                existing_articles.append(article)
                existing_urls.append(article.get('url'))
        
        # Save updated cache
        with open(ARTICLES_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_articles, f, indent=4)
    
    def load_cached_articles(self) -> List[Dict]:
        """
        Load articles from cache file.
        
        Returns:
            List of article dictionaries
        """
        if not os.path.exists(ARTICLES_CACHE_FILE):
            return []
        
        try:
            with open(ARTICLES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    @abstractmethod
    def scrape_articles(self) -> List[Dict]:
        """
        Scrape articles from the news source.
        
        Returns:
            List of article dictionaries
        """
        pass 