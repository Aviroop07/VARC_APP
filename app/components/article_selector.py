"""
Component for selecting articles based on topic and source.
"""
from typing import List, Dict, Optional
from collections import defaultdict
import random

def select_article(articles: List[Dict], topic: Optional[str] = None, source: Optional[str] = None) -> Optional[Dict]:
    """
    Select an article based on topic and source with uniform probability across sources.
    
    Args:
        articles: List of available articles
        topic: Selected topic or None for all topics
        source: Selected source or None for all sources
        
    Returns:
        Optional[Dict]: Selected article or None if no match
    """
    if not articles:
        return None
    
    # Filter articles by topic and source
    filtered_articles = articles
    
    # Filter by topic if specified
    if topic:
        filtered_articles = [a for a in filtered_articles if a.get('topic') == topic]
        if not filtered_articles:
            return None
    
    # Filter by source if specified
    if source:
        filtered_articles = [a for a in filtered_articles if a.get('source_key', '').lower() == source.lower()]
        if not filtered_articles:
            return None
    
    # If source is specified, just select a random article from that source
    if source:
        return random.choice(filtered_articles)
    
    # Otherwise, ensure uniform selection across sources
    # Group articles by source
    articles_by_source = defaultdict(list)
    for article in filtered_articles:
        source_name = article.get('source', 'unknown')
        articles_by_source[source_name].append(article)
    
    # Early return if no articles found
    if not articles_by_source:
        return None
    
    # Select a random source that has articles
    available_sources = list(articles_by_source.keys())
    selected_source = random.choice(available_sources)
    
    # Select a random article from the selected source
    return random.choice(articles_by_source[selected_source]) 