"""
Streamlit Cloud entry point for the Daily Articles app.
"""
import sys
import os
from pathlib import Path

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main app - no need to call main() as it's not a function anymore
import app.main 