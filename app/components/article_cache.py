"""
Component for caching articles.
"""
from typing import List, Dict
from datetime import datetime, timedelta

class ArticleCache:
    """Cache for storing and retrieving articles."""
    
    def __init__(self):
        self.cache = {}
        self.expiry_time = timedelta(hours=24)
        
    def get(self, key: str) -> List[Dict]:
        """Get cached articles if not expired."""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.expiry_time:
                return data
        return []
        
    def set(self, key: str, articles: List[Dict]):
        """Cache articles with current timestamp."""
        self.cache[key] = (articles, datetime.now()) 