#!/usr/bin/env python3
"""
Portable Setup Script for Smart Farming Assistant
This script makes the project portable by handling path dependencies
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def setup_project_structure():
    """Create proper project structure for portability"""
    print("🏗️  Setting up project structure...")
    
    # Create directories if they don't exist
    directories = [
        "data",
        "models",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created/verified directory: {directory}")

def find_and_copy_data_files():
    """Find and copy data files to the proper location"""
    print("📁 Looking for data files...")
    
    # Files to find and copy
    data_files = [
        ("train.csv", "data/train.csv"),
        ("test.csv", "data/test.csv"),
        ("sample_submission.csv", "data/sample_submission.csv")
    ]
    
    # Search locations
    search_locations = [
        "playground-series-s5e6",
        "../playground-series-s5e6",
        "../../playground-series-s5e6",
        ".",
        "../",
        "../../"
    ]
    
    for filename, target_path in data_files:
        found = False
        for location in search_locations:
            source_path = Path(location) / filename
            if source_path.exists():
                try:
                    shutil.copy2(source_path, target_path)
                    print(f"✓ Copied {filename} to {target_path}")
                    found = True
                    break
                except Exception as e:
                    print(f"⚠️  Error copying {filename}: {e}")
        
        if not found:
            print(f"❌ Could not find {filename}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split("\n")
        
        missing_packages = []
        for req in requirements:
            if req.strip():
                package = req.split("==")[0].strip()
                try:
                    __import__(package.replace("-", "_"))
                    print(f"✓ {package} is installed")
                except ImportError:
                    missing_packages.append(req)
                    print(f"❌ {package} is missing")
        
        if missing_packages:
            print(f"\n📦 Installing missing packages...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✓ All dependencies installed!")
        else:
            print("✓ All dependencies are already installed!")
            
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False
    
    return True

def check_model_files():
    """Check if model files exist and create if needed"""
    print("🤖 Checking model files...")
    
    model_files = [
        "crop_recommendation_model.pkl",
        "enhanced_crop_model.pkl",
        "water_resource_encoder.pkl"
    ]
    
    missing_models = []
    for model_file in model_files:
        if not Path(model_file).exists():
            missing_models.append(model_file)
            print(f"❌ Missing: {model_file}")
        else:
            print(f"✓ Found: {model_file}")
    
    if missing_models:
        print("🏋️  Training missing models...")
        try:
            # Try to run the training script
            if Path("train_model.py").exists():
                subprocess.check_call([sys.executable, "train_model.py"])
                print("✓ Models trained successfully!")
            else:
                print("❌ train_model.py not found. Please train models manually.")
        except Exception as e:
            print(f"❌ Error training models: {e}")
            return False
    
    return True

def create_run_script():
    """Create platform-specific run scripts"""
    print("🚀 Creating run scripts...")
    
    # Windows batch script
    windows_script = """@echo off
echo Starting Smart Farming Assistant...
python -m streamlit run app.py
pause
"""
    
    with open("run_windows.bat", "w") as f:
        f.write(windows_script)
    print("✓ Created run_windows.bat")
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting Smart Farming Assistant..."
python3 -m streamlit run app.py
"""
    
    with open("run_unix.sh", "w") as f:
        f.write(unix_script)
    
    # Make it executable on Unix systems
    try:
        os.chmod("run_unix.sh", 0o755)
        print("✓ Created run_unix.sh (executable)")
    except:
        print("✓ Created run_unix.sh")

def create_portable_config():
    """Create a configuration file for portable settings"""
    print("⚙️  Creating portable configuration...")
    
    config_content = """# Smart Farming Assistant Configuration
# This file contains portable settings

# Data paths (relative to project root)
DATA_DIR = "data"
MODEL_DIR = "models"
LOG_DIR = "logs"

# API Configuration
WEATHER_API_KEY = "your_api_key_here"

# Database Configuration
DATABASE_PATH = "smart_farming.db"

# Supported file paths for soil data
SOIL_DATA_PATHS = [
    "data/train.csv",
    "playground-series-s5e6/train.csv",
    "../playground-series-s5e6/train.csv",
    "train.csv"
]
"""
    
    with open("config.py", "w") as f:
        f.write(config_content)
    print("✓ Created config.py")

def verify_portability():
    """Verify that the project is now portable"""
    print("🔍 Verifying portability...")
    
    checks = [
        ("requirements.txt", "Dependencies file"),
        ("app.py", "Main application"),
        ("database.py", "Database module"),
        ("config.py", "Configuration file"),
        ("data", "Data directory"),
        ("smart_farming.db", "Database file (will be created on first run)")
    ]
    
    all_good = True
    for item, description in checks:
        if Path(item).exists():
            print(f"✓ {description}: Found")
        else:
            if item == "smart_farming.db":
                print(f"ℹ️  {description}: Will be created on first run")
            else:
                print(f"❌ {description}: Missing")
                all_good = False
    
    return all_good

def main():
    """Main setup function"""
    print("🌾 Smart Farming Assistant - Portable Setup")
    print("=" * 50)
    
    try:
        # Step 1: Setup project structure
        setup_project_structure()
        print()
        
        # Step 2: Find and copy data files
        find_and_copy_data_files()
        print()
        
        # Step 3: Check dependencies
        if not check_dependencies():
            print("❌ Setup failed: Dependencies issue")
            return
        print()
        
        # Step 4: Check model files
        if not check_model_files():
            print("❌ Setup failed: Model files issue")
            return
        print()
        
        # Step 5: Create run scripts
        create_run_script()
        print()
        
        # Step 6: Create portable config
        create_portable_config()
        print()
        
        # Step 7: Verify portability
        if verify_portability():
            print("🎉 Project is now portable!")
            print("\nNext steps:")
            print("1. Copy the entire project folder to any location")
            print("2. Run the appropriate script:")
            print("   - Windows: run_windows.bat")
            print("   - Linux/Mac: ./run_unix.sh")
            print("3. Get your WeatherAPI key from: https://www.weatherapi.com/")
            print("4. Enter your API key in the app when it starts")
        else:
            print("❌ Portability verification failed")
            
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        return

if __name__ == "__main__":
    main()
