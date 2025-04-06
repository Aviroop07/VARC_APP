"""
Configuration settings for the daily article selector application.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
ARTICLES_CACHE_FILE = os.path.join(DATA_DIR, "articles_cache.json")
DAILY_SELECTION_FILE = os.path.join(DATA_DIR, "daily_selection.json")

# News sources
NEWS_SOURCES = {
    "hindu": {
        "name": "The Hindu",
        "base_url": "https://www.thehindu.com",
        "rss_feeds": {
            "general": "https://www.thehindu.com/news/feeder/default.rss",
            "business": "https://www.thehindu.com/business/feeder/default.rss",
            "science": "https://www.thehindu.com/sci-tech/feeder/default.rss",
            "entertainment": "https://www.thehindu.com/entertainment/feeder/default.rss"
        }
    },
    "telegraph": {
        "name": "The Telegraph",
        "base_url": "https://www.telegraph.co.uk",
        "rss_feeds": {
            "general": "https://www.telegraph.co.uk/rss.xml",
            "news": "https://www.telegraph.co.uk/news/rss.xml",
            "business": "https://www.telegraph.co.uk/business/rss.xml",
            "technology": "https://www.telegraph.co.uk/technology/rss.xml",
            "culture": "https://www.telegraph.co.uk/culture/rss.xml",
            "science": "https://www.telegraph.co.uk/science/rss.xml"
        }
    },
    # Backup sources in case the above are blocked
    "bbc": {
        "name": "BBC News",
        "base_url": "https://www.bbc.com",
        "rss_feeds": {
            "general": "http://feeds.bbci.co.uk/news/rss.xml",
            "science": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
            "technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",
            "business": "http://feeds.bbci.co.uk/news/business/rss.xml",
            "entertainment": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
        }
    },
    "reuters": {
        "name": "Reuters",
        "base_url": "https://www.reuters.com",
        "rss_feeds": {
            "general": "https://www.reutersagency.com/feed/",
            "business": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
            "science": "https://www.reutersagency.com/feed/?best-topics=health&post_type=best"
        }
    }
}

# Topic categories with their probabilities
TOPICS = {
    "business": {
        "name": "Business and economics",
        "probability": 0.2,
        "keywords": ["business", "economy", "finance", "market", "trade", "industry", "investment"]
    },
    "science": {
        "name": "Science, environment, and technology",
        "probability": 0.5,
        "keywords": ["science", "technology", "environment", "climate", "research", "innovation", "discovery"]
    },
    "art": {
        "name": "Art and literary criticism",
        "probability": 0.2,
        "keywords": ["art", "literature", "book", "culture", "museum", "exhibition", "review", "artist"]
    },
    "philosophy": {
        "name": "Philosophy and sociology",
        "probability": 0.1,
        "keywords": ["philosophy", "sociology", "ethics", "society", "social", "theory", "community"]
    }
}

# Headers to mimic a browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
} 