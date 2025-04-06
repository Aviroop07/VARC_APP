"""
Factory module for creating scraper instances.
"""
from typing import Dict, List, Optional, Type

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.hindu_scraper import HinduScraper
from app.scrapers.telegraph_scraper import TelegraphScraper
from app.scrapers.bbc_scraper import BBCScraper
from app.scrapers.reuters_scraper import ReutersScraper


class ScraperFactory:
    """
    Factory class for creating scraper instances.
    """
    
    _scrapers = {
        "hindu": HinduScraper,
        "telegraph": TelegraphScraper,
        "bbc": BBCScraper,
        "reuters": ReutersScraper
    }
    
    # Define primary and backup sources
    _primary_sources = ["hindu", "telegraph"]
    _backup_sources = ["bbc", "reuters"]
    
    @classmethod
    def get_scraper(cls, source_name: str) -> Optional[BaseScraper]:
        """
        Get a scraper instance for the specified source.
        
        Args:
            source_name: Name of the news source
            
        Returns:
            BaseScraper instance or None if source not supported
        """
        scraper_class = cls._scrapers.get(source_name)
        if scraper_class:
            return scraper_class()
        return None
    
    @classmethod
    def get_all_scrapers(cls) -> List[BaseScraper]:
        """
        Get instances of all available scrapers.
        
        Returns:
            List of BaseScraper instances
        """
        return [scraper_class() for scraper_class in cls._scrapers.values()]
    
    @classmethod
    def get_primary_scrapers(cls) -> List[BaseScraper]:
        """
        Get instances of the primary news source scrapers.
        
        Returns:
            List of BaseScraper instances for primary sources
        """
        return [cls._scrapers[source]() for source in cls._primary_sources
                if source in cls._scrapers]
    
    @classmethod
    def get_backup_scrapers(cls) -> List[BaseScraper]:
        """
        Get instances of the backup news source scrapers.
        
        Returns:
            List of BaseScraper instances for backup sources
        """
        return [cls._scrapers[source]() for source in cls._backup_sources
                if source in cls._scrapers] 