"""
Scraper for The Telegraph.
"""
import re
from typing import Dict, List, Optional
import datetime
import html
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, ScraperException
from utils.config import NEWS_SOURCES


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
        Scrape articles from The Telegraph using RSS feeds and Newspaper3k.
        
        Returns:
            List of article dictionaries
        """
        articles = []
        
        # Iterate through the RSS feeds
        for category, feed_url in self.rss_feeds.items():
            try:
                entries = self.fetch_rss_feed(feed_url)
                
                if not entries:
                    self.logger.warning(f"No entries found for {category} feed")
                    continue
                
                # Process each entry from the feed
                for entry in entries[:5]:  # Limit to 5 articles per feed for efficiency
                    try:
                        # Extract basic metadata from RSS
                        title = entry.get('title', '')
                        article_url = entry.get('link', '')
                        
                        # Skip if no URL
                        if not article_url:
                            continue
                        
                        # Use Newspaper3k to extract detailed content
                        try:
                            article_data = self.extract_article_content(article_url)
                            
                            # In case Newspaper3k failed to extract a title, use the one from RSS
                            if not article_data.get('title') and title:
                                article_data['title'] = html.unescape(title)
                                
                            # Extract summary from RSS if available and not in Newspaper3k data
                            if 'summary' not in article_data and 'summary' in entry:
                                soup = BeautifulSoup(entry.summary, 'lxml')
                                article_data['summary'] = html.unescape(soup.get_text().strip())
                            elif 'summary' not in article_data and 'description' in entry:
                                soup = BeautifulSoup(entry.description, 'lxml')
                                article_data['summary'] = html.unescape(soup.get_text().strip())
                            
                            # Get content for classification
                            content_text = article_data.get('text', '')
                            summary_text = article_data.get('summary', '')
                            
                            # Use either newspaper extracted title or RSS title
                            title_text = article_data.get('title', title)
                            
                            # Classify topic
                            topic = self.classify_topic(title_text, content_text if content_text else summary_text)
                            
                            # Create final article data
                            final_article = {
                                "title": title_text,
                                "url": article_url,
                                "summary": summary_text,
                                "content": content_text,
                                "image_url": article_data.get('top_image', ''),
                                "images": article_data.get('images', []),
                                "authors": article_data.get('authors', []),
                                "publish_date": article_data.get('publish_date'),
                                "keywords": article_data.get('keywords', []),
                                "source": self.source_name,
                                "topic": topic,
                                "category": category,
                                "scraped_date": datetime.datetime.now().isoformat()
                            }
                            
                            # Convert datetime objects to strings for JSON serialization
                            if isinstance(final_article["publish_date"], datetime.datetime):
                                final_article["publish_date"] = final_article["publish_date"].isoformat()
                            
                            articles.append(final_article)
                            
                        except ScraperException:
                            # If Newspaper3k extraction fails, fall back to basic RSS data
                            self.logger.warning(f"Newspaper extraction failed for {article_url}, using RSS data only")
                            
                            # Extract summary from RSS
                            summary = ''
                            if 'summary' in entry:
                                soup = BeautifulSoup(entry.summary, 'lxml')
                                summary = html.unescape(soup.get_text().strip())
                            elif 'description' in entry:
                                soup = BeautifulSoup(entry.description, 'lxml')
                                summary = html.unescape(soup.get_text().strip())
                            
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
                            
                            # Clean up title
                            title = html.unescape(title)
                            
                            # Classify topic
                            topic = self.classify_topic(title, summary)
                            
                            # Create article data with basic information
                            article_data = {
                                "title": title,
                                "url": article_url,
                                "summary": summary,
                                "image_url": image_url,
                                "source": self.source_name,
                                "topic": topic,
                                "category": category,
                                "scraped_date": datetime.datetime.now().isoformat()
                            }
                            
                            articles.append(article_data)
                    
                    except Exception as e:
                        self.logger.error(f"Error extracting article data from Telegraph RSS: {str(e)}")
            
            except Exception as e:
                self.logger.error(f"Error processing feed {feed_url}: {str(e)}")
        
        # If RSS feeds didn't work, try to use the website scraping as a fallback
        if not articles:
            self.logger.info("Trying fallback method for The Telegraph...")
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
                
                for article_elem in article_elements[:10]:  # Limit to 10 articles
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
                        
                        # Use Newspaper3k for content extraction
                        try:
                            article_data = self.extract_article_content(article_url)
                            
                            # In case Newspaper3k failed to extract a title, use the one from HTML
                            if not article_data.get('title') and title:
                                article_data['title'] = title
                            
                            # Get content for classification
                            content_text = article_data.get('text', '')
                            summary_text = article_data.get('summary', '')
                            
                            # Use either newspaper extracted title or HTML title
                            title_text = article_data.get('title', title)
                            
                            # Classify topic
                            topic = self.classify_topic(title_text, content_text if content_text else summary_text)
                            
                            # Create final article data
                            final_article = {
                                "title": title_text,
                                "url": article_url,
                                "summary": summary_text,
                                "content": content_text,
                                "image_url": article_data.get('top_image', ''),
                                "images": article_data.get('images', []),
                                "authors": article_data.get('authors', []),
                                "publish_date": article_data.get('publish_date'),
                                "keywords": article_data.get('keywords', []),
                                "source": self.source_name,
                                "topic": topic,
                                "category": "general",
                                "scraped_date": datetime.datetime.now().isoformat()
                            }
                            
                            # Convert datetime objects to strings for JSON serialization
                            if isinstance(final_article["publish_date"], datetime.datetime):
                                final_article["publish_date"] = final_article["publish_date"].isoformat()
                            
                            articles.append(final_article)
                            
                        except ScraperException:
                            # If Newspaper3k extraction fails, fall back to basic HTML data
                            self.logger.warning(f"Newspaper extraction failed for {article_url}, using HTML data only")
                            
                            # Extract summary if available
                            summary_elem = article_elem.select_one("p, div.card-body")
                            summary = summary_elem.text.strip() if summary_elem else ""
                            
                            # Extract image URL if available
                            img_elem = article_elem.select_one("img")
                            image_url = img_elem.get("src") if img_elem else ""
                            
                            # Classify topic
                            topic = self.classify_topic(title, summary)
                            
                            # Create article data with basic information
                            article_data = {
                                "title": title,
                                "url": article_url,
                                "summary": summary,
                                "image_url": image_url,
                                "source": self.source_name,
                                "topic": topic,
                                "category": "general",
                                "scraped_date": datetime.datetime.now().isoformat()
                            }
                            
                            articles.append(article_data)
                    except Exception as e:
                        self.logger.error(f"Error extracting article data: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error scraping Telegraph homepage: {str(e)}")
        
        return articles 