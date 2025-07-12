# Smart Farming Assistant Configuration
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
