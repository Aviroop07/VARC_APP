"""
Component for displaying the selected daily article.
"""
import streamlit as st
from typing import Dict
import requests
from bs4 import BeautifulSoup
import re
import datetime

def display_article(article: Dict) -> None:
    """
    Display the selected article in the Streamlit UI.
    
    Args:
        article: Dictionary containing article information
    """
    # Add CSS to hide any "Related Topics" sections
    st.markdown("""
    <style>
    /* Hide any Related Topics sections */
    h2:contains("Related Topics"), 
    h3:contains("Related Topics"),
    h4:contains("Related Topics"),
    h5:contains("Related Topics"),
    h6:contains("Related Topics"),
    p:contains("Related Topics"),
    .stMarkdown:contains("Related Topics"),
    div:contains("Related Topics"),
    section:contains("Related Topics"),
    *[class*="related-topics"],
    *[id*="related-topics"],
    *[class*="relatedTopics"],
    *[id*="relatedTopics"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not article:
        st.error("No article selected for today. Please try again later.")
        
        # Add a refresh button when no article is available
        if st.button("Load Another Article", type="primary"):
            st.session_state.reload_article = True
            st.rerun()
        return
    
    # Create a card-like container
    with st.container():
        # Button to load another article at the top right
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("New Article", type="primary"):
                st.session_state.reload_article = True
                st.rerun()
        
        with col1:
            # Get the article category (use this as the primary label)
            category = article.get("category", "General")
            
            # Display category badge instead of topic
            st.markdown(f"<div style='display:inline-block; background-color:#1E88E5; color:white; padding:4px 12px; border-radius:20px; font-size:0.8em'>{category}</div>", unsafe_allow_html=True)
        
        # Display article title
        st.markdown(f"## {article.get('title', 'Untitled Article')}")
        
        # Get publication date
        pub_date = article.get("pub_date", "")
        if not pub_date and "date" in article:
            pub_date = article.get("date", "")
        
        # Format the date nicely if it exists
        date_display = ""
        if pub_date:
            # Try to parse the date if it's a string
            if isinstance(pub_date, str):
                try:
                    # Try common date formats
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            parsed_date = datetime.datetime.strptime(pub_date, fmt)
                            date_display = f"📅 {parsed_date.strftime('%B %d, %Y')}"
                            break
                        except ValueError:
                            continue
                except:
                    # If parsing fails, just use the string as is
                    date_display = f"📅 {pub_date}"
            else:
                # If it's already a datetime object
                date_display = f"📅 {pub_date.strftime('%B %d, %Y') if hasattr(pub_date, 'strftime') else str(pub_date)}"
        
        # Source info with date if available
        source_line = f"**Source:** {article.get('source', 'Unknown')}"
        if date_display:
            source_line += f" | {date_display}"
        st.markdown(source_line)
        
        # Display image if available
        image_url = article.get("image_url")
        if image_url:
            st.image(image_url, use_container_width=True)
        
        # Get the article URL
        article_url = article.get("url")
        
        # Display article content directly
        if article_url:
            # Show article content right away
            display_full_article_content(article_url)
        else:
            st.warning("No article URL available to extract content.")
        
        st.markdown("---")
        
        # Add a button at the bottom to load another article
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Load Another Article", key="bottom_reload"):
                st.session_state.reload_article = True
                st.rerun()

def display_full_article_content(url: str) -> None:
    """
    Display the full article content with original website option.
    
    Args:
        url: URL of the article to display
    """
    if not url:
        st.warning("No URL available for this article.")
        return
    
    # Show extracted article text by default with minimal spacing
    st.markdown("<style>.article-header { margin-bottom: 0; padding-bottom: 0; }</style>", unsafe_allow_html=True)
    
    cols = st.columns([5, 1])
    with cols[0]:
        st.markdown("<h3 class='article-header'>📄 Article Content</h3>", unsafe_allow_html=True)
    with cols[1]:
        # Open in browser button
        if st.button("View Original Website", type="primary"):
            # Open in new tab using JavaScript
            js = f"""
            <script>
            window.open('{url}', '_blank').focus();
            </script>
            """
            st.components.v1.html(js, height=0)
    
    # Display the full article text immediately with no gap
    display_text_only_article(url)

def display_article_content(url: str) -> None:
    """
    Display article content with viewing options.
    This function is no longer used directly but kept for compatibility.
    
    Args:
        url: URL of the article to display
    """
    if not url:
        st.warning("No URL available for this article.")
        return
    
    # Show extracted article text by default
    st.subheader("📄 Article Content")
    
    # Display the extracted article text immediately
    display_text_only_article(url)
    
    # Open in browser option below the article text
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("View Original Website", type="primary"):
            # Open in new tab using JavaScript
            js = f"""
            <script>
            window.open('{url}', '_blank').focus();
            </script>
            """
            st.components.v1.html(js, height=0)
    with col2:
        st.markdown(f"👆 Click to open [the original article]({url}) in a new browser tab")

def display_text_only_article(url: str) -> None:
    """
    Display a text-only version of the article by extracting main content.
    
    Args:
        url: URL of the article to extract text from
    """
    try:
        with st.spinner("Extracting article content..."):
            # Add user agent to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
            
            # Fetch article content
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Remove script, style, and nav elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
                    element.decompose()
                
                # Remove all Related Topics sections before processing
                for element in soup.find_all(string=re.compile("Related Topics", re.IGNORECASE)):
                    parent = element.parent
                    if parent:
                        # Try to find the container or section that contains this heading
                        container = parent
                        for _ in range(5):  # Look up to 5 levels up
                            if container and (container.name in ['div', 'section', 'article', 'aside']):
                                container.decompose()
                                break
                            container = container.parent if container.parent else None
                        
                        # If no suitable container was found, just remove the parent element
                        if parent and parent.name:
                            parent.decompose()
                
                # Try to find the main content using multiple strategies
                main_content = None
                
                # Strategy 1: Look for semantic elements
                for selector in ['article', 'main', '.article', '.story', '.content', '.post-content', '[itemprop="articleBody"]']:
                    content = soup.select(selector)
                    if content:
                        main_content = content[0]
                        break
                
                # Strategy 2: If still not found, look for largest div with most paragraphs
                if not main_content:
                    paragraphs_by_parent = {}
                    for p in soup.find_all('p'):
                        parent = p.parent
                        if parent not in paragraphs_by_parent:
                            paragraphs_by_parent[parent] = []
                        paragraphs_by_parent[parent].append(p)
                    
                    if paragraphs_by_parent:
                        main_content = max(paragraphs_by_parent.items(), key=lambda x: len(x[1]))[0]
                
                # If we found content, display it
                if main_content:
                    # Get all paragraphs and headings
                    paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    
                    # Create styled container with reduced top margin to minimize gap
                    st.markdown("""
                    <style>
                    .article-text-container {
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        max-height: 600px;
                        overflow-y: auto;
                        border: 1px solid #e9ecef;
                        margin-top: 0;
                        margin-bottom: 20px;
                    }
                    .article-text-container p {
                        margin-bottom: 15px;
                        line-height: 1.6;
                    }
                    .article-text-container h1, 
                    .article-text-container h2,
                    .article-text-container h3,
                    .article-text-container h4,
                    .article-text-container h5,
                    .article-text-container h6 {
                        margin-top: 20px;
                        margin-bottom: 10px;
                        color: #333;
                    }
                    /* Minimize spacing in Streamlit containers */
                    .block-container {
                        padding-top: 0;
                        padding-bottom: 0;
                    }
                    .stSpinner {
                        margin-top: 0;
                        margin-bottom: 0;
                        padding-top: 0;
                        padding-bottom: 0;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Start the container with no gap
                    st.markdown('<div class="article-text-container">', unsafe_allow_html=True)
                    
                    # Process and display paragraphs and headings
                    content_added = False
                    skip_until_next_heading = False
                    
                    for elem in paragraphs:
                        text = elem.get_text().strip()
                        
                        # Skip this element and all following elements until next heading if it contains "Related Topics"
                        if "Related Topics" in text or "related topics" in text.lower():
                            skip_until_next_heading = True
                            continue
                        
                        # If we're skipping and encounter a heading, stop skipping
                        if skip_until_next_heading and elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            skip_until_next_heading = False
                        
                        # Skip this element if in skip mode
                        if skip_until_next_heading:
                            continue
                        
                        # Only render substantial content or headings
                        if len(text) > 40 or elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            tag = elem.name if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] else 'p'
                            st.markdown(f"<{tag}>{text}</{tag}>", unsafe_allow_html=True)
                            content_added = True
                    
                    # If no paragraphs found, display all text
                    if not content_added:
                        full_text = main_content.get_text().strip()
                        # Remove any sections starting with "Related Topics" and going to the end of line
                        full_text = re.sub(r'Related Topics.*?(\n|$)', '', full_text, flags=re.IGNORECASE|re.MULTILINE)
                        if full_text:
                            st.markdown(f"<p>{full_text}</p>", unsafe_allow_html=True)
                            content_added = True
                    
                    # Close the container
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if not content_added:
                        st.warning("No meaningful text content could be extracted from this article.")
                else:
                    st.warning("Could not identify the main content of the article.")
            else:
                st.error(f"Failed to fetch article (HTTP {response.status_code}). The site may be blocking requests.")
    
    except Exception as e:
        st.error(f"Error extracting article text: {e}")
        st.info("Try opening the article in a new tab instead.") 