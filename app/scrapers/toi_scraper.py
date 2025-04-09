"""
Scraper for Times of India articles.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .base_scraper import BaseScraper

class TOIScraper(BaseScraper):
    """Scraper for Times of India articles."""
    
    def __init__(self):
        super().__init__("toi", "https://timesofindia.indiatimes.com")
        self.article_url = "https://timesofindia.indiatimes.com/topic/{topic}"
        
    def scrape_articles(self) -> List[Dict]:
        """Scrape articles from Times of India."""
        articles = []
        try:
            # Get articles from different sections
            sections = [
                "business",
                "technology",
                "science",
                "environment",
                "education",
                "health"
            ]
            
            for section in sections:
                url = self.article_url.format(topic=section)
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    article_elements = soup.find_all('div', class_='uwU81')
                    
                    for element in article_elements[:5]:  # Limit to 5 articles per section
                        try:
                            title_elem = element.find('div', class_='fHv_i')
                            if not title_elem:
                                continue
                                
                            title = title_elem.text.strip()
                            link = element.find('a')['href']
                            if not link.startswith('http'):
                                link = self.base_url + link
                                
                            # Get article content
                            article_content = self._get_article_content(link)
                            if not article_content:
                                continue
                                
                            articles.append({
                                'title': title,
                                'url': link,
                                'source': self.source_name,
                                'content': article_content,
                                'topic': section
                            })
                            
                        except Exception as e:
                            print(f"Error processing TOI article: {e}")
                            continue
                            
        except Exception as e:
            print(f"Error scraping TOI: {e}")
            
        return articles
        
    def _get_article_content(self, url: str) -> Optional[str]:
        """Get the content of a specific article."""
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content_div = soup.find('div', class_='_3WlLe')
                if content_div:
                    # Remove unwanted elements
                    for element in content_div.find_all(['script', 'style', 'iframe']):
                        element.decompose()
                    return content_div.get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Error getting TOI article content: {e}")
        return None 