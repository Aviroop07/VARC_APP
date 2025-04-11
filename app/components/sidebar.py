"""
Sidebar component for the Streamlit application.
"""
import streamlit as st
import datetime
from typing import Dict

from utils.config import TOPICS, NEWS_SOURCES
from scrapers.scraper_factory import ScraperFactory

def render_sidebar() -> None:
    """
    Render the sidebar for the application.
    """
    with st.sidebar:
        st.title("Daily Article Selector")
        st.markdown("---")
        
        # Display today's date
        today = datetime.datetime.now().strftime("%B %d, %Y")
        st.subheader(f"Today: {today}")
        
        st.markdown("---")
        
        # About this app
        with st.expander("About This App"):
            st.write("""
            This application selects a random article each day from various news sources based on predefined topic probabilities.
            
            You can view the daily recommendation or choose a specific topic of interest using the topic selection controls.
            """)
        
        # Topic probabilities section
        st.subheader("Topic Distribution")
        
        for topic_key, topic_data in TOPICS.items():
            topic_name = topic_data["name"]
            probability = topic_data["probability"]
            
            # Display progress bar for each topic
            st.caption(topic_name)
            st.progress(probability)
        
        st.markdown("---")
        
        # News sources section
        st.subheader("News Sources")
        
        # Get primary and backup sources
        primary_sources = ScraperFactory._primary_sources
        backup_sources = ScraperFactory._backup_sources
        
        # Display primary sources
        st.write("Primary Sources:")
        for source_key in primary_sources:
            if source_key in NEWS_SOURCES:
                source_name = NEWS_SOURCES[source_key]["name"]
                st.markdown(f"- {source_name}")
        
        # Display backup sources
        st.write("Backup Sources:")
        for source_key in backup_sources:
            if source_key in NEWS_SOURCES:
                source_name = NEWS_SOURCES[source_key]["name"]
                st.markdown(f"- {source_name}")
            
        st.markdown("---")
        
        # Footer
        st.caption("© 2025 Daily Article Selector") 