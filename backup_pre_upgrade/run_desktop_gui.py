#!/usr/bin/env python3
"""
Run the Research Agent Desktop GUI

This script launches the PyQt6 desktop application for the Super Enhanced Research Agent.
"""

import subprocess
import sys
import os

def main():
    """Launch the desktop GUI"""
    gui_script = os.path.join(os.path.dirname(__file__), "desktop_gui.py")

    if not os.path.exists(gui_script):
        print(f"Error: {gui_script} not found")
        sys.exit(1)

    print("Starting Super Enhanced Research Agent Desktop GUI...")
    print("The desktop application will open in a new window")
    print("Close the window to exit the application")

    try:
        # Run the desktop GUI
        subprocess.run([
            sys.executable, gui_script
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Desktop GUI closed")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start desktop GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()