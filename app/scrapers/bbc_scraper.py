"""
Scraper for BBC News.
"""
from typing import Dict, List, Optional
import datetime
import html
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.config import NEWS_SOURCES


class BBCScraper(BaseScraper):
    """
    Scraper for BBC News.
    """
    
    def __init__(self):
        """Initialize the BBC scraper."""
        source_config = NEWS_SOURCES["bbc"]
        super().__init__(source_config["name"], source_config["base_url"])
        self.rss_feeds = source_config.get("rss_feeds", {})
    
    def scrape_articles(self) -> List[Dict]:
        """
        Scrape articles from BBC News using RSS feeds.
        
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
            for entry in entries[:15]:  # Limit to 15 articles per feed
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
                    
                    # Extract published date if available
                    published_date = None
                    if 'published' in entry:
                        published_date = entry.published
                    
                    # Extract image URL if available
                    image_url = ""
                    # BBC feeds often include media in different formats
                    if 'media_content' in entry and entry.media_content:
                        for media in entry.media_content:
                            if 'url' in media:
                                image_url = media['url']
                                break
                    
                    # BBC sometimes includes thumbnails
                    if not image_url and 'media_thumbnail' in entry:
                        for media in entry.media_thumbnail:
                            if 'url' in media:
                                image_url = media['url']
                                break
                    
                    # Try to find an image in the summary
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
                        "scraped_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "published_date": published_date
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    print(f"Error extracting article data from BBC RSS: {e}")
        
        # Save articles to cache
        self.save_articles_to_cache(articles)
        
        return articles 