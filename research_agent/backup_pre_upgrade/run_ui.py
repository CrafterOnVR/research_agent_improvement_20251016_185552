#!/usr/bin/env python3
"""
Run the Research Agent Web UI

This script launches the Streamlit web interface for the Super Enhanced Research Agent.
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit web UI"""
    # Get the parent directory (package root)
    package_root = os.path.dirname(__file__)

    print("Starting Super Enhanced Research Agent Web UI...")
    print("The web interface will open in your default browser")
    print("If it doesn't open automatically, visit: http://localhost:8501")
    print("Press Ctrl+C to stop the server")

    try:
        # Change to package directory and run as module
        os.chdir(package_root)

        # Run streamlit with the module
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_ui.py",
            "--server.headless", "true",
            "--server.address", "localhost",
            "--server.port", "8503"
        ], check=True)
    except KeyboardInterrupt:
        print("\nWeb UI stopped")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start web UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()