"""
Utility for selecting articles based on topic.
"""
import os
import json
import random
import datetime
from typing import Dict, Optional, List

import numpy as np

from utils.config import TOPICS, DAILY_SELECTION_FILE

def get_random_topic() -> str:
    """
    Select a random topic based on the configured probabilities.
    
    Returns:
        str: The selected topic key
    """
    topic_keys = list(TOPICS.keys())
    probabilities = [TOPICS[topic]["probability"] for topic in topic_keys]
    
    # Select topic based on probabilities
    selected_topic = np.random.choice(topic_keys, p=probabilities)
    return selected_topic

def save_daily_selection(article_data: Dict) -> None:
    """
    Save the selected article for today.
    
    Args:
        article_data: Dictionary containing article information
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    selection_data = {
        "date": today,
        "article": article_data
    }
    
    with open(DAILY_SELECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(selection_data, f, indent=4)

def get_daily_selection() -> Optional[Dict]:
    """
    Get the selected article for today.
    
    Returns:
        Dict or None: The article data if available for today, None otherwise
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Check if selection file exists
    if not os.path.exists(DAILY_SELECTION_FILE):
        return None
    
    # Load the selection data
    try:
        with open(DAILY_SELECTION_FILE, "r", encoding="utf-8") as f:
            selection_data = json.load(f)
            
        # Check if selection is for today
        if selection_data.get("date") == today:
            return selection_data.get("article")
    except (json.JSONDecodeError, KeyError):
        # If file is empty or corrupted
        return None
    
    return None

def select_article_from_candidates(candidates: List[Dict], topic: str) -> Optional[Dict]:
    """
    Select a random article from the list of candidates for the given topic.
    
    Args:
        candidates: List of article dictionaries
        topic: The topic to select from
        
    Returns:
        Dict or None: The selected article or None if no suitable candidates
    """
    if not candidates:
        return None
    
    # Filter candidates with the specified topic
    topic_candidates = [article for article in candidates if article.get("topic") == topic]
    
    # If no articles found for the specified topic, use all candidates
    if not topic_candidates:
        topic_candidates = candidates
    
    # Select a random article from the candidates
    if topic_candidates:
        return random.choice(topic_candidates)
    
    return None

def select_article_by_topic(candidates: List[Dict], topic: str) -> Optional[Dict]:
    """
    Select a random article with the specified topic.
    Unlike the regular selection process, this doesn't save the selection as the daily article.
    
    Args:
        candidates: List of article dictionaries
        topic: The specific topic to select (e.g., "business", "science")
        
    Returns:
        Dict or None: The selected article or None if no suitable candidates
    """
    if not candidates:
        return None
    
    # Filter candidates by the specified topic
    topic_candidates = [article for article in candidates if article.get("topic") == topic]
    
    # If we found candidates with the requested topic, select one randomly
    if topic_candidates:
        selected_article = random.choice(topic_candidates)
        
        # Add topic name to the article data
        if topic in TOPICS:
            selected_article["topic_name"] = TOPICS[topic]["name"]
            
        return selected_article
    
    return None 