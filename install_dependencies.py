#!/usr/bin/env python
"""
Helper script to install dependencies for the VARC app, particularly for fixing
the lxml.html.clean module issue with Newspaper3k.
"""
import subprocess
import sys
import os
import platform

def install_dependencies():
    """Install required dependencies, especially fixing the lxml HTML cleaning issue."""
    print("Installing required dependencies...")
    
    # Install basic requirements first
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Base requirements installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install base requirements")
        return False
    
    # Try to install lxml with HTML cleaning extension
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "lxml[html_clean]"])
        print("✅ lxml with HTML cleaning installed")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to install lxml[html_clean], trying lxml_html_clean separately...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "lxml_html_clean"])
            print("✅ lxml_html_clean installed separately")
        except subprocess.CalledProcessError:
            print("❌ Failed to install lxml_html_clean")
            print("⚠️ The application will use fallback BeautifulSoup extraction")
            
    # Try to install newspaper3k with fallback options
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "newspaper3k"])
        print("✅ newspaper3k installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install newspaper3k")
        print("⚠️ The application will use fallback BeautifulSoup extraction")
        
    print("\nSetup complete! The application should now run with the necessary dependencies.")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("VARC App Dependency Installer")
    print("=" * 50)
    print(f"Python version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print("-" * 50)
    
    success = install_dependencies()
    
    if success:
        print("\nYou can now run the application with:")
        print("   streamlit run app/main.py")
    else:
        print("\nSome errors occurred during installation.")
        print("The application may still run but with limited functionality.")
        print("Please check the error messages above for details.")
    
    print("-" * 50) 