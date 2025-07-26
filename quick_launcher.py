#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Launcher for Bangla Sentiment Analysis App
This script will automatically clean up previous sessions and start the app
"""

import subprocess
import sys
import os

def main():
    """Main launcher function"""
    print("🚀 Bangla Sentiment Analysis App Launcher")
    print("=" * 50)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(script_dir, "Bangla_Sentiment_App.py")
    
    # Check if the app file exists
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found!")
        input("Press Enter to exit...")
        return
    
    print("✅ Found application file")
    print("🔄 Starting application with automatic cleanup...")
    print()
    
    try:
        # Run the application
        subprocess.run([sys.executable, app_file], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
