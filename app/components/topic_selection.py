"""
Component for topic selection in the sidebar.
"""
import streamlit as st
from typing import Optional

def display_topic_selection() -> Optional[str]:
    """
    Display topic selection in the sidebar.
    
    Returns:
        Optional[str]: Selected topic or None if 'All Topics' is selected
    """
    topics = {
        "business": "Business & Finance",
        "technology": "Technology",
        "science": "Science",
        "environment": "Environment",
        "education": "Education",
        "health": "Health",
        None: "All Topics"
    }
    
    selected_topic = st.selectbox(
        "Select Topic",
        options=list(topics.keys()),
        format_func=lambda x: topics[x],
        index=len(topics)-1  # Default to "All Topics"
    )
    
    return selected_topic 