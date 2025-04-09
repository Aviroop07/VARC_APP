"""
Component for news source selection in the sidebar.
"""
import streamlit as st
from typing import Optional

def display_source_selection() -> Optional[str]:
    """
    Display news source selection in the sidebar.
    
    Returns:
        Optional[str]: Selected source or None if 'All Sources' is selected
    """
    sources = {
        "hindu": "The Hindu",
        "telegraph": "The Telegraph",
        "bbc": "BBC News",
        "reuters": "Reuters",
        "guardian": "The Guardian",
        "toi": "Times of India",
        None: "All Sources"
    }
    
    selected_source = st.selectbox(
        "Select News Source",
        options=list(sources.keys()),
        format_func=lambda x: sources[x],
        index=len(sources)-1  # Default to "All Sources"
    )
    
    return selected_source 