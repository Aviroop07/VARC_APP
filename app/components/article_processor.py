"""
Component for processing article content.
"""
from typing import Dict

def process_article(article: Dict) -> Dict:
    """
    Process article content for display.
    
    Args:
        article: Raw article data
        
    Returns:
        Dict: Processed article data
    """
    if not article:
        return {}
        
    # Clean and format content
    content = article.get('content', '').strip()
    content = ' '.join(content.split())  # Normalize whitespace
    
    return {
        'title': article.get('title', ''),
        'url': article.get('url', ''),
        'content': content,
        'source': article.get('source', ''),
        'topic': article.get('topic', '')
    } 