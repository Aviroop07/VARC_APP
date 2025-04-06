"""
Main Streamlit application file for the Daily Article Selector.
"""
import streamlit as st
import time
from typing import Dict, List, Optional
import random

from app.utils.config import TOPICS
from app.utils.article_selector import (
    get_random_topic,
    get_daily_selection,
    save_daily_selection,
    select_article_from_candidates,
    select_article_by_topic
)
from app.scrapers.scraper_factory import ScraperFactory
from app.components.sidebar import render_sidebar
from app.components.article_display import (
    display_article,
    display_no_article_message,
    display_loading_message
)

# Page configuration
st.set_page_config(
    page_title="Daily Article Selector",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure CSS
def apply_styles():
    """Apply custom styles to the app."""
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stProgress > div > div {
        height: 10px;
        border-radius: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# Main application function
def main():
    """Main application function."""
    # Apply custom styles
    apply_styles()
    
    # Initialize session state if not already done
    if 'cached_articles' not in st.session_state:
        st.session_state.cached_articles = []
    if 'current_article' not in st.session_state:
        st.session_state.current_article = None
    if 'is_custom_topic' not in st.session_state:
        st.session_state.is_custom_topic = False
    if 'reload_article' not in st.session_state:
        st.session_state.reload_article = False
    
    # Render sidebar
    render_sidebar()
    
    # App title and introduction
    st.title("📰 Your Daily Curated Article")
    st.markdown("Each day, we select one interesting article based on topic probabilities.")
    
    # Check if we need to reload an article (button was clicked)
    force_reload = st.session_state.reload_article
    if force_reload:
        # Reset the flag
        st.session_state.reload_article = False
        # Select a new random article
        with st.spinner("Finding a new article for you..."):
            article = select_daily_article()
            st.session_state.current_article = article
    else:
        # Get daily selected article or select a new one
        article = get_daily_selection()
                
        # If no article selected, get a new one
        if not article:
            with st.spinner("Selecting today's article..."):
                article = select_daily_article()
                
        st.session_state.current_article = article
    
    # If we have an article, add topic name to it
    if article and "topic" in article and "topic_name" not in article:
        topic_key = article["topic"]
        if topic_key in TOPICS:
            article["topic_name"] = TOPICS[topic_key]["name"]
    
    # Display article information
    st.markdown("---")
    
    # Display article or message
    if article:
        # Display the selected article
        display_article(article)
    else:
        # Display no article message
        display_no_article_message()

def fetch_all_articles() -> List[Dict]:
    """
    Fetch all articles from cache or by scraping.
    
    Returns:
        List of all available articles
    """
    all_articles = []
    
    # Get all scrapers
    scrapers = ScraperFactory.get_all_scrapers()
    
    # Step 1: Try to use cached articles first
    for scraper in scrapers:
        cached_articles = scraper.load_cached_articles()
        all_articles.extend(cached_articles)
    
    # Step 2: If no cached articles, try primary sources
    if not all_articles:
        # Get primary source scrapers
        primary_scrapers = ScraperFactory.get_primary_scrapers()
        
        for scraper in primary_scrapers:
            try:
                st.info(f"Fetching articles from {scraper.source_name}...")
                articles = scraper.scrape_articles()
                if articles:
                    st.success(f"Successfully fetched {len(articles)} articles from {scraper.source_name}")
                    all_articles.extend(articles)
                else:
                    st.warning(f"No articles found from {scraper.source_name}")
            except Exception as e:
                st.error(f"Error scraping from {scraper.source_name}: {e}")
    
    # Step 3: If primary sources failed, try backup sources
    if not all_articles:
        # Get backup source scrapers
        backup_scrapers = ScraperFactory.get_backup_scrapers()
        
        for scraper in backup_scrapers:
            try:
                st.info(f"Fetching articles from backup source: {scraper.source_name}...")
                articles = scraper.scrape_articles()
                if articles:
                    st.success(f"Successfully fetched {len(articles)} articles from {scraper.source_name}")
                    all_articles.extend(articles)
                else:
                    st.warning(f"No articles found from {scraper.source_name}")
            except Exception as e:
                st.error(f"Error scraping from backup source {scraper.source_name}: {e}")
    
    return all_articles

def select_daily_article() -> Optional[Dict]:
    """
    Select a new daily article using a robust approach.
    First tries to use cached articles, then primary sources, 
    and finally falls back to backup sources if needed.
    
    Returns:
        Dict or None: The selected article or None if no article could be selected
    """
    # Show loading message
    display_loading_message()
    
    # Get all articles
    all_articles = fetch_all_articles()
    
    # If still no articles after trying all sources, return None
    if not all_articles:
        st.error("Could not fetch articles from any source. Please try again later.")
        return None
    
    # Cache the articles in session state for topic selection
    st.session_state.cached_articles = all_articles
    
    # Get random topic based on probabilities
    selected_topic = get_random_topic()
    
    # Select an article from the candidates for the selected topic
    selected_article = select_article_from_candidates(all_articles, selected_topic)
    
    # Save the selected article for today
    if selected_article:
        save_daily_selection(selected_article)
        st.success(f"Selected an article about {TOPICS[selected_topic]['name']}")
    else:
        st.error("Could not select an appropriate article. Please try again.")
    
    return selected_article

if __name__ == "__main__":
    main() 