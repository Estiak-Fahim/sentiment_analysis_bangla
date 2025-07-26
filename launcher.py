# Build executable with PyInstaller
# Install PyInstaller first: pip install pyinstaller

# Build command for Windows:
# pyinstaller --onefile --windowed --add-data "C:\Users\User\Sentiment Project\bangla_bert_model;bangla_bert_model" bangla_sentiment_app_fixed.py

# For distribution, you would also need to include:
# 1. The bangla_bert_model folder
# 2. requirements.txt
# 3. This build script

# Alternative: Create a simpler standalone launcher
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install requirements")
        return False
    return True

def check_model_exists():
    """Check if model directory exists"""
    model_path = r"C:\Users\User\Sentiment Project\bangla_bert_model"
    if os.path.exists(model_path):
        print("✓ Model directory found")
        return True
    else:
        print("✗ Model directory not found at:", model_path)
        return False

def run_app():
    """Run the sentiment analysis app"""
    try:
        subprocess.run([sys.executable, "bangla_sentiment_app_fixed.py"])
    except KeyboardInterrupt:
        print("\n✓ Application stopped by user")
    except Exception as e:
        print(f"✗ Error running application: {e}")

if __name__ == "__main__":
    print("🚀 Bangla Sentiment Analysis Application Launcher")
    print("=" * 50)
    
    # Check and install requirements
    if not install_requirements():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check model
    if not check_model_exists():
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("\n🌟 Starting application...")
    print("The app will open in your web browser automatically.")
    print("Press Ctrl+C to stop the application.\n")
    
    run_app()
