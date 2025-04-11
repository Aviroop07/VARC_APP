"""
Sidebar component for the Streamlit application.
"""
import streamlit as st
import datetime
from typing import Dict

from utils.config import TOPICS, NEWS_SOURCES

def render_sidebar() -> None:
    """
    Render the sidebar for the application.
    Note: This function is currently not called directly from main.py,
    but is kept for future integration or reference.
    
    Returns:
        None
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
        
        # Display all news sources
        for source_key, source_data in NEWS_SOURCES.items():
            source_name = source_data["name"]
            st.markdown(f"- {source_name}")
            
        st.markdown("---")
        
        # Footer
        st.caption("© 2025 Daily Article Selector") 