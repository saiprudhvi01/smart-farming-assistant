#!/usr/bin/env python3
"""
Simple Streamlit startup script
"""

import subprocess
import sys
import os

def main():
    """Start Streamlit application"""
    print("🌾 Starting Smart Farming Assistant...")
    print("=" * 50)
    
    try:
        # Change to current directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start Streamlit
        print("📱 Starting Streamlit Frontend...")
        print("🌐 Will open in browser automatically...")
        print("📍 URL: http://localhost:8503")
        print("\n✋ Press Ctrl+C to stop the application")
        
        # Run streamlit with specific port to avoid conflicts
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.port", "8503",
            "--server.headless", "false",
            "--browser.serverAddress", "localhost"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        print("💡 Try running manually: streamlit run app.py --server.port 8503")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
