"""
Scraper for The Telegraph newspaper.
"""
from typing import Dict, List, Optional
import datetime
import html
from bs4 import BeautifulSoup

from app.scrapers.base_scraper import BaseScraper
from app.utils.config import NEWS_SOURCES


class TelegraphScraper(BaseScraper):
    """
    Scraper for The Telegraph newspaper.
    """
    
    def __init__(self):
        """Initialize The Telegraph scraper."""
        source_config = NEWS_SOURCES["telegraph"]
        super().__init__(source_config["name"], source_config["base_url"])
        self.rss_feeds = source_config.get("rss_feeds", {})
    
    def scrape_articles(self) -> List[Dict]:
        """
        Scrape articles from The Telegraph using RSS feeds.
        
        Returns:
            List of article dictionaries
        """
        articles = []
        
        # Iterate through the RSS feeds
        for category, feed_url in self.rss_feeds.items():
            entries = self.fetch_rss_feed(feed_url)
            
            if not entries:
                print(f"No entries found for {category} feed")
                continue
            
            # Process each entry from the feed
            for entry in entries[:10]:  # Limit to 10 articles per feed
                try:
                    # Extract article data
                    title = entry.get('title', '')
                    article_url = entry.get('link', '')
                    
                    # Extract summary/content
                    summary = ''
                    if 'summary' in entry:
                        # Clean up HTML tags in summary
                        soup = BeautifulSoup(entry.summary, 'lxml')
                        summary = soup.get_text().strip()
                    elif 'description' in entry:
                        soup = BeautifulSoup(entry.description, 'lxml')
                        summary = soup.get_text().strip()
                    
                    # Decode HTML entities
                    title = html.unescape(title)
                    summary = html.unescape(summary)
                    
                    # Extract image URL if available
                    image_url = ""
                    if 'media_content' in entry and entry.media_content:
                        for media in entry.media_content:
                            if 'url' in media:
                                image_url = media['url']
                                break
                    elif 'media_thumbnail' in entry and entry.media_thumbnail:
                        for media in entry.media_thumbnail:
                            if 'url' in media:
                                image_url = media['url']
                                break
                    
                    # Fallback - try to find image in the summary
                    if not image_url and summary:
                        soup = BeautifulSoup(summary, 'lxml')
                        img_tag = soup.find('img')
                        if img_tag and img_tag.has_attr('src'):
                            image_url = img_tag['src']
                    
                    # Classify topic
                    topic = self.classify_topic(title, summary)
                    
                    # Create article data
                    article_data = {
                        "title": title,
                        "url": article_url,
                        "summary": summary,
                        "image_url": image_url,
                        "source": self.source_name,
                        "topic": topic,
                        "category": category,
                        "scraped_date": datetime.datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    print(f"Error extracting article data from Telegraph RSS: {e}")
        
        # If RSS feeds didn't work, try to use the website scraping as a fallback
        if not articles:
            print("Trying fallback method for The Telegraph...")
            articles = self._fallback_scrape()
        
        # Save articles to cache
        self.save_articles_to_cache(articles)
        
        return articles
    
    def _fallback_scrape(self) -> List[Dict]:
        """
        Fallback method to scrape articles from The Telegraph website directly.
        This is used only if RSS feeds don't work.
        
        Returns:
            List of article dictionaries
        """
        articles = []
        
        # Try to get articles from the homepage first
        try:
            soup = self.fetch_page(self.base_url)
            
            if soup:
                # Find featured articles on homepage
                article_elements = soup.select("div.card, article.article")
                
                for article_elem in article_elements[:20]:  # Limit to 20 articles
                    try:
                        # Extract article data
                        title_elem = article_elem.select_one("h3 a, h2 a")
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        article_url = title_elem.get("href")
                        
                        # Make URL absolute if it's relative
                        if article_url and not article_url.startswith("http"):
                            if article_url.startswith("/"):
                                article_url = self.base_url + article_url
                            else:
                                article_url = f"{self.base_url}/{article_url}"
                        
                        # Extract summary if available
                        summary_elem = article_elem.select_one("p, div.card-body")
                        summary = summary_elem.text.strip() if summary_elem else ""
                        
                        # Extract image URL if available
                        img_elem = article_elem.select_one("img")
                        image_url = img_elem.get("src") if img_elem else ""
                        
                        # Classify topic
                        topic = self.classify_topic(title, summary)
                        
                        # Create article data
                        article_data = {
                            "title": title,
                            "url": article_url,
                            "summary": summary,
                            "image_url": image_url,
                            "source": self.source_name,
                            "topic": topic,
                            "category": "general",
                            "scraped_date": datetime.datetime.now().strftime("%Y-%m-%d")
                        }
                        
                        articles.append(article_data)
                        
                    except Exception as e:
                        print(f"Error extracting article data: {e}")
        except Exception as e:
            print(f"Error scraping Telegraph homepage: {e}")
        
        # If we couldn't get articles from the homepage, try specific sections
        if not articles:
            # Main categories to scrape
            categories = [
                "news",
                "business",
                "technology",
                "culture",
                "science"
            ]
            
            for category in categories:
                try:
                    category_url = f"{self.base_url}/{category}/"
                    soup = self.fetch_page(category_url)
                    
                    if not soup:
                        continue
                    
                    # Find article elements
                    article_elements = soup.select("div.card, article")
                    
                    for article_elem in article_elements[:5]:  # Limit to 5 articles per category
                        try:
                            # Extract article data
                            title_elem = article_elem.select_one("h3 a, h2 a")
                            if not title_elem:
                                continue
                            
                            title = title_elem.text.strip()
                            article_url = title_elem.get("href")
                            
                            # Make URL absolute if it's relative
                            if article_url and not article_url.startswith("http"):
                                if article_url.startswith("/"):
                                    article_url = self.base_url + article_url
                                else:
                                    article_url = f"{self.base_url}/{article_url}"
                            
                            # Extract summary if available
                            summary_elem = article_elem.select_one("p, div.card-body")
                            summary = summary_elem.text.strip() if summary_elem else ""
                            
                            # Extract image URL if available
                            img_elem = article_elem.select_one("img")
                            image_url = img_elem.get("src") if img_elem else ""
                            
                            # Classify topic
                            topic = self.classify_topic(title, summary)
                            
                            # Create article data
                            article_data = {
                                "title": title,
                                "url": article_url,
                                "summary": summary,
                                "image_url": image_url,
                                "source": self.source_name,
                                "topic": topic,
                                "category": category,
                                "scraped_date": datetime.datetime.now().strftime("%Y-%m-%d")
                            }
                            
                            articles.append(article_data)
                            
                        except Exception as e:
                            print(f"Error extracting article data: {e}")
                except Exception as e:
                    print(f"Error scraping category {category}: {e}")
        
        return articles 