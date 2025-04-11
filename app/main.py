"""
Main Streamlit application for displaying daily articles.
"""
import streamlit as st
from datetime import datetime
from scrapers.scraper_factory import ScraperFactory
from components.article_display import display_article
from components.topic_selection import display_topic_selection
from components.source_selection import display_source_selection
from components.article_loader import load_articles
from components.article_selector import select_article
from components.article_processor import process_article
from components.article_cache import ArticleCache

# Initialize session state
if "articles" not in st.session_state:
    st.session_state.articles = []
if "selected_article" not in st.session_state:
    st.session_state.selected_article = None
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "selected_source" not in st.session_state:
    st.session_state.selected_source = None
if "last_update" not in st.session_state:
    st.session_state.last_update = None
if "article_cache" not in st.session_state:
    st.session_state.article_cache = ArticleCache()

# Set page config
st.set_page_config(
    page_title="Daily Articles",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .article-container {
        padding: 2rem;
    }
    .article-header {
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .article-text-container {
        margin-top: 0;
    }
    .block-container {
        padding: 1rem 1rem 0;
    }
    .stSpinner > div {
        margin-top: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("📰 Daily Articles")
    st.markdown("---")
    
    # Topic selection
    st.markdown("### 🔍 Filter Articles")
    selected_topic = display_topic_selection()
    st.session_state.selected_topic = selected_topic
    
    # Source selection
    selected_source = display_source_selection()
    st.session_state.selected_source = selected_source
    
    # Source information
    st.markdown("### 📋 News Sources")
    st.markdown("""
    Articles are fetched from multiple sources:
    - The Hindu
    - The Telegraph
    - BBC News
    - Reuters
    - The Guardian
    - Times of India
    """)
    
    st.markdown("---")
    st.markdown("""
    ### ℹ️ About
    This app provides daily articles for VARC preparation.
    Articles are automatically updated daily at 6 AM IST.
    """)

# Main content
st.title("📰 Daily Articles")

# Check if we need to update articles
current_time = datetime.now()
if (st.session_state.last_update is None or 
    (current_time - st.session_state.last_update).days >= 1 or
    current_time.hour >= 6 and st.session_state.last_update.day < current_time.day):
    
    with st.spinner("Fetching latest articles..."):
        # Get all scrapers
        scrapers = ScraperFactory.get_all_scrapers()
        
        # Load articles from all sources
        all_articles = []
        for scraper in scrapers:
            try:
                articles = load_articles(scraper)
                # Add source_key for filtering
                for article in articles:
                    article['source_key'] = scraper.source_name
                all_articles.extend(articles)
            except Exception as e:
                st.error(f"Error loading articles from {scraper.source_name}: {str(e)}")
                continue
        
        if all_articles:
            st.session_state.articles = all_articles
            st.session_state.last_update = current_time
            st.success("Articles updated successfully!")
        else:
            st.error("No articles could be loaded. Please try again later.")

# Display articles if available
if st.session_state.articles:
    # Select article based on topic and source
    selected_article = select_article(
        st.session_state.articles, 
        st.session_state.selected_topic,
        st.session_state.selected_source
    )
    
    if selected_article:
        # Process article content
        processed_article = process_article(selected_article)
        
        # Display article
        display_article(processed_article)
        
        # Add note about filters
        filters_applied = []
        if st.session_state.selected_topic:
            filters_applied.append(f"topic '{st.session_state.selected_topic}'")
        if st.session_state.selected_source:
            filters_applied.append(f"source '{st.session_state.selected_source}'")
            
        if filters_applied:
            st.info(f"""
            ℹ️ You're viewing articles filtered by {' and '.join(filters_applied)}. 
            To see all available articles, select 'All Topics' and 'All Sources' in the sidebar.
            """)
    else:
        st.info("No articles available for the selected filters. Please try different topic or source options.")
else:
    st.info("No articles available at the moment. Please check back later.") 