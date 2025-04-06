"""
Script to run the Daily Article Selector application.
"""
import subprocess
import os
import sys

def main():
    """
    Run the Streamlit application.
    """
    print("Starting Daily Article Selector...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main app file
    app_path = os.path.join(script_dir, "app", "main.py")
    
    # Run the Streamlit app
    try:
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "run", app_path],
            check=True
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        return e.returncode
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 