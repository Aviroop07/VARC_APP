"""
Component for selecting articles based on topic.
"""
from typing import List, Dict, Optional, DefaultDict
from collections import defaultdict
import random

def select_article(articles: List[Dict], topic: Optional[str] = None) -> Optional[Dict]:
    """
    Select an article based on topic with uniform probability across sources.
    
    Args:
        articles: List of available articles
        topic: Selected topic or None for all topics
        
    Returns:
        Optional[Dict]: Selected article or None if no match
    """
    if not articles:
        return None
    
    # First filter by topic if specified
    if topic:
        filtered_articles = [a for a in articles if a.get('topic') == topic]
        if not filtered_articles:
            return None
    else:
        filtered_articles = articles
    
    # Group articles by source
    articles_by_source = defaultdict(list)
    for article in filtered_articles:
        source = article.get('source', 'unknown')
        articles_by_source[source].append(article)
    
    # Early return if no articles found
    if not articles_by_source:
        return None
    
    # Select a random source that has articles
    available_sources = list(articles_by_source.keys())
    selected_source = random.choice(available_sources)
    
    # Select a random article from the selected source
    return random.choice(articles_by_source[selected_source]) 