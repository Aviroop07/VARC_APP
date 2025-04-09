"""
Component for selecting articles based on topic.
"""
from typing import List, Dict, Optional
import random

def select_article(articles: List[Dict], topic: Optional[str] = None) -> Optional[Dict]:
    """
    Select an article based on topic.
    
    Args:
        articles: List of available articles
        topic: Selected topic or None for all topics
        
    Returns:
        Optional[Dict]: Selected article or None if no match
    """
    if not articles:
        return None
        
    if topic:
        filtered_articles = [a for a in articles if a.get('topic') == topic]
        if filtered_articles:
            return random.choice(filtered_articles)
        return None
        
    return random.choice(articles) 