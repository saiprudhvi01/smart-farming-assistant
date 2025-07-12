#!/usr/bin/env python3
"""
Setup script for Smart Farming Assistant
This script installs dependencies and prepares the application for first run.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing packages: {e}")
        return False
    return True

def train_model():
    """Train the machine learning model"""
    print("Training machine learning model...")
    try:
        subprocess.check_call([sys.executable, "train_model.py"])
        print("✓ Model trained successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error training model: {e}")
        return False
    return True

def check_data_files():
    """Check if all required data files exist"""
    required_files = [
        "data/soil_data.csv",
        "data/market_prices.csv",
        "data/pesticides.csv"
    ]
    
    print("Checking data files...")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} found")
        else:
            print(f"✗ {file_path} not found")
            return False
    return True

def main():
    """Main setup function"""
    print("🌾 Smart Farming Assistant Setup")
    print("=" * 40)
    
    # Check data files
    if not check_data_files():
        print("❌ Setup failed: Missing data files")
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed: Could not install requirements")
        return
    
    # Train model
    if not train_model():
        print("❌ Setup failed: Could not train model")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Get your WeatherAPI key from: https://www.weatherapi.com/")
    print("2. Run the app with: streamlit run app.py")
    print("3. Enter your API key in the sidebar when the app opens")

if __name__ == "__main__":
    main()
