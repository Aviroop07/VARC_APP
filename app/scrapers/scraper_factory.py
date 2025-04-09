"""
Factory for creating article scrapers.
"""
from typing import List
from .base_scraper import BaseScraper
from .bbc_scraper import BBCScraper
from .reuters_scraper import ReutersScraper
from .guardian_scraper import GuardianScraper
from .toi_scraper import TOIScraper
from .hindu_scraper import HinduScraper
from .telegraph_scraper import TelegraphScraper

class ScraperFactory:
    """Factory class for creating article scrapers."""
    
    @staticmethod
    def get_all_scrapers() -> List[BaseScraper]:
        """Get all available scrapers with equal probability."""
        return [
            BBCScraper(),
            ReutersScraper(),
            GuardianScraper(),
            TOIScraper(),
            HinduScraper(),
            TelegraphScraper()
        ] 