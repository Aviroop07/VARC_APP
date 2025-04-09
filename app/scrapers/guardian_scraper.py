"""
Scraper for The Guardian articles.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper

class GuardianScraper(BaseScraper):
    """Scraper for The Guardian articles."""
    
    def __init__(self):
        super().__init__("guardian", "https://www.theguardian.com")
        self.urls = {
            "business": "https://www.theguardian.com/business",
            "technology": "https://www.theguardian.com/technology",
            "science": "https://www.theguardian.com/science",
            "environment": "https://www.theguardian.com/environment",
            "education": "https://www.theguardian.com/education",
            "health": "https://www.theguardian.com/society/health"
        }
    
    def scrape_articles(self) -> List[Dict]:
        """Scrape articles from The Guardian."""
        articles = []
        for section, url in self.urls.items():
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                article_links = soup.find_all('a', class_='u-faux-block-link__overlay')
                
                for link in article_links[:5]:  # Limit to 5 articles per section
                    article_url = link.get('href')
                    if article_url and article_url.startswith('https://www.theguardian.com/'):
                        article = self._get_article_content(article_url)
                        if article:
                            article['topic'] = section
                            articles.append(article)
            except Exception as e:
                print(f"Error scraping Guardian {section}: {str(e)}")
                continue
        return articles
    
    def _get_article_content(self, url: str) -> Dict:
        """Get the content of a specific article."""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('h1')
            if not title:
                return None
                
            content = soup.find('div', class_='article-body-commercial-selector')
            if not content:
                return None
                
            # Remove unwanted elements
            for element in content.find_all(['script', 'style', 'iframe']):
                element.decompose()
                
            return {
                'title': title.text.strip(),
                'url': url,
                'content': content.get_text().strip(),
                'source': 'The Guardian'
            }
        except Exception as e:
            print(f"Error getting Guardian article content: {str(e)}")
            return None 