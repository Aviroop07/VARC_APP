"""
Component for loading articles from scrapers.
"""
from typing import List, Dict
from app.scrapers.base_scraper import BaseScraper

def load_articles(scraper: BaseScraper) -> List[Dict]:
    """
    Load articles from a scraper.
    
    Args:
        scraper: Scraper instance
        
    Returns:
        List[Dict]: List of articles
    """
    try:
        return scraper.scrape_articles()
    except Exception as e:
        print(f"Error loading articles from {scraper.source_name}: {str(e)}")
        return [] 