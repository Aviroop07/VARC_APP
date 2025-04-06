"""
Streamlit Cloud entry point for the Daily Article Selector.
"""
import sys
import os
from pathlib import Path

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main app
import app.main

# Run the main app
if __name__ == "__main__":
    app.main.main() 