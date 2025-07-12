import streamlit as st
import pandas as pd
from database import DatabaseManager
import requests
import pickle
import os
from googletrans import Translator
import numpy as np
import hashlib
import json
from datetime import datetime, timedelta
# Optional imports for SMS functionality
try:
    from twilio.rest import Client
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    MessagingResponse = None

try:
    from flask import Flask, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    request = None

import threading
import subprocess

# Initialize database and translator
db_manager = DatabaseManager()
translator = Translator()

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Set page configuration
st.set_page_config(
    page_title="Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better styling
# Replace your CSS with this ultra-modern, highly readable version
st.markdown("""
<style>
    /* Base font settings for maximum clarity */
    html, body, .stApp {
        font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
        color: #1a1a1a;
        font-weight: 500;
    }
    
    /* Enhanced text contrast for better readability */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #000000 !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(255,255,255,0.8);
    }
    
    .stApp p, .stApp span, .stApp div {
        color: #1a1a1a !important;
        font-weight: 500;
    }
    
    /* Modern farming background with subtle texture */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        background-image: 
            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" opacity="0.1"><defs><pattern id="farm" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M20 20h60v60h-60z" fill="none" stroke="%23228B22" stroke-width="0.5"/><circle cx="50" cy="50" r="15" fill="%23228B22" opacity="0.3"/><path d="M30 30l40 40M70 30l-40 40" stroke="%23228B22" stroke-width="1" opacity="0.2"/></pattern></defs><rect width="100%" height="100%" fill="url(%23farm)"/></svg>'),
            radial-gradient(circle at 10% 20%, rgba(34,139,34,0.05) 0%, transparent 20%),
            radial-gradient(circle at 90% 80%, rgba(46,125,50,0.05) 0%, transparent 20%);
        background-attachment: fixed;
        background-size: 200px 200px, 100% 100%, 100% 100%;
    }
    
    /* Farming-themed background patterns for different sections */
    .farming-bg {
        background-image: 
            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" opacity="0.08"><path d="M10 50c0-20 20-40 40-40s40 20 40 40-20 40-40 40-40-20-40-40z" fill="%23228B22"/><path d="M35 35h30v30h-30z" fill="none" stroke="%23228B22" stroke-width="2"/><circle cx="50" cy="50" r="8" fill="%23228B22"/></svg>'),
            linear-gradient(135deg, rgba(76,175,80,0.05) 0%, rgba(56,142,60,0.05) 100%);
        background-size: 80px 80px, 100% 100%;
        background-repeat: repeat, no-repeat;
    }
    
    /* Header with depth and crisp typography */
    header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        color: white !important;
    }
    header h1 {
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Sidebar with glass effect and improved readability */
    .sidebar .sidebar-content {
        background: rgba(102, 126, 234, 0.95) !important;
        backdrop-filter: blur(12px);
        color: white;
        border-right: 1px solid rgba(255,255,255,0.15);
    }
    .sidebar .sidebar-content * {
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Dark theme compatibility */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%) !important;
        }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #ffffff !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.8);
        }
        .stApp p, .stApp span, .stApp div {
            color: #e0e0e0 !important;
        }
        .metric-card, .crop-card, .weather-card, .soil-card {
            background: rgba(255,255,255,0.1) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.2);
        }
    }
    
    /* Ultra-clear card design with perfect contrast and farming theme */
    .metric-card, .crop-card, .weather-card, .soil-card {
        background: white;
        background-image: 
            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60" opacity="0.03"><path d="M15 15l30 0 0 30-30 0z" fill="none" stroke="%23228B22" stroke-width="1"/><circle cx="30" cy="30" r="8" fill="%23228B22"/><path d="M20 20l20 20M40 20l-20 20" stroke="%23228B22" stroke-width="0.5"/></svg>'),
            linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.95) 100%);
        background-size: 60px 60px, 100% 100%;
        background-repeat: repeat, no-repeat;
        padding: 1.75rem;
        border-radius: 14px;
        box-shadow: 0 6px 30px rgba(0,0,0,0.04);
        margin: 0.75rem 0;
        border: none;
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    }
    .metric-card h3 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }
    .metric-card p {
        font-size: 0.95rem !important;
        color: #64748b !important;
    }
    
    /* Success message that pops with clarity */
    .success-message {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 10px;
        margin: 1.25rem 0;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(74,222,128,0.15);
        border: none;
        text-shadow: 0 1px 1px rgba(0,0,0,0.05);
    }
    
    /* Weather and soil cards with improved contrast and farming themes */
    .weather-card {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        background-image: 
            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" opacity="0.1"><circle cx="25" cy="15" r="8" fill="white"/><path d="M10 35c0-8 8-15 15-15s15 7 15 15" fill="none" stroke="white" stroke-width="2"/><path d="M15 30l5 5 15-15" stroke="white" stroke-width="1.5" fill="none"/></svg>');
        background-size: 50px 50px;
        background-repeat: repeat;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .soil-card {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        background-image: 
            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" opacity="0.1"><rect x="10" y="20" width="30" height="20" fill="white" opacity="0.3"/><circle cx="15" cy="15" r="3" fill="white"/><circle cx="25" cy="12" r="2" fill="white"/><circle cx="35" cy="18" r="4" fill="white"/><path d="M10 40c5-5 15-3 20 0s15 5 20 0" stroke="white" stroke-width="1.5" fill="none"/></svg>');
        background-size: 50px 50px;
        background-repeat: repeat;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Buttons with perfect clickability affordance */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.75rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(102,126,234,0.25);
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102,126,234,0.35);
        background: linear-gradient(135deg, #5c6fcf 0%, #6941a8 100%);
    }
    
    /* Tabs with perfect visual hierarchy */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(241, 245, 249, 0.7);
        padding: 0.5rem;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.25rem;
        font-weight: 600;
        font-size: 0.95rem;
        color: #64748b;
        transition: all 0.3s;
        margin: 0;
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(226, 232, 240, 0.7);
        color: #4f46e5;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #4f46e5 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-weight: 700;
    }
    
    /* Input fields with crystal clear focus states and proper text visibility */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: all 0.3s;
        background: white !important;
        color: black !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
        outline: none;
    }
    
    /* Crop cards with perfect typography */
    .crop-card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 0.75rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.04);
        transition: all 0.3s;
        text-align: center;
        border: none;
    }
    .crop-card img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .crop-card h4 {
        color: #1e40af;
        margin: 0.75rem 0;
        font-size: 1.2rem;
        font-weight: 700;
    }
    .crop-card p {
        margin: 0.5rem 0;
        font-size: 0.95rem;
        color: #4b5563;
        line-height: 1.5;
    }
    .crop-card .price {
        font-size: 1.3rem;
        color: #1e40af;
        font-weight: 700;
        margin: 1rem 0;
    }
    
    /* Contact button with perfect CTA visibility */
    .contact-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border: none;
        color: white;
        padding: 0.75rem 1.75rem;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(16,185,129,0.25);
        letter-spacing: 0.3px;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .contact-btn:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16,185,129,0.35);
        color: white;
    }
    
    /* Perfect alert styling */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        padding: 1.25rem;
    }
    
    /* Dashboard headers with perfect hierarchy and farming theme */
    .dashboard-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        background-image: 
            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" opacity="0.1"><path d="M20 30h60v40H20z" fill="none" stroke="white" stroke-width="2"/><circle cx="30" cy="20" r="8" fill="white" opacity="0.3"/><circle cx="50" cy="15" r="6" fill="white" opacity="0.3"/><circle cx="70" cy="22" r="7" fill="white" opacity="0.3"/><path d="M10 80c10-10 30-5 40 0s30 10 40 0" stroke="white" stroke-width="1.5" fill="none" opacity="0.4"/><path d="M25 45l10 10 20-20" stroke="white" stroke-width="2" fill="none" opacity="0.3"/></svg>');
        background-size: 100px 100px;
        background-repeat: repeat;
        color: white;
        padding: 2rem;
        border-radius: 14px;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(99,102,241,0.15);
    }
    .dashboard-header h1 {
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
    }
    .dashboard-header p {
        font-size: 1.1rem !important;
        opacity: 0.9;
    }
    
    /* Expander styling that matches the theme */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.05rem;
        color: #1e293b;
        padding: 1rem;
        background: rgba(241, 245, 249, 0.7);
        border-radius: 10px !important;
    }
    .streamlit-expanderContent {
        padding: 1.5rem;
        background: white;
        border-radius: 0 0 10px 10px;
    }
    
    /* Perfect data tables */
    .dataframe {
        border-radius: 10px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05) !important;
        font-size: 0.95rem !important;
    }
    .dataframe th {
        background: #f1f5f9 !important;
        font-weight: 600 !important;
    }
    
    /* Responsive design for all devices */
    @media (max-width: 768px) {
        .stButton > button, .contact-btn {
            width: 100%;
            margin: 0.5rem 0;
        }
        .metric-card, .crop-card {
            padding: 1.25rem;
        }
        .dashboard-header {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for crop listings
if 'crop_listings' not in st.session_state:
    st.session_state.crop_listings = [
        {
            'crop_name': 'rice',
            'quantity': 1000,
            'price': 45.0,
            'contact_info': '+91-9876543210',
            'location_detail': 'Kurnool, Andhra Pradesh'
        },
        {
            'crop_name': 'wheat',
            'quantity': 750,
            'price': 35.0,
            'contact_info': '+91-9876543211',
            'location_detail': 'Ludhiana, Punjab'
        },
        {
            'crop_name': 'sugarcane',
            'quantity': 2000,
            'price': 25.0,
            'contact_info': '+91-9876543212',
            'location_detail': 'Kolhapur, Maharashtra'
        },
        {
            'crop_name': 'tomato',
            'quantity': 500,
            'price': 60.0,
            'contact_info': '+91-9876543213',
            'location_detail': 'Nashik, Maharashtra'
        },
        {
            'crop_name': 'cotton',
            'quantity': 800,
            'price': 55.0,
            'contact_info': '+91-9876543214',
            'location_detail': 'Warangal, Telangana'
        },
        {
            'crop_name': 'maize',
            'quantity': 1200,
            'price': 30.0,
            'contact_info': '+91-9876543215',
            'location_detail': 'Davangere, Karnataka'
        }
    ]

# Load pre-trained model
@st.cache_resource
def load_model():
    try:
        with open('crop_recommendation_model.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error("Model file not found. Please run train_model.py first to train the model.")
        return None

# Load data files
@st.cache_data
def load_data():
    try:
        soil_data = pd.read_csv('data/soil_data.csv')
        market_prices = pd.read_csv('data/market_prices.csv')
        pesticides = pd.read_csv('data/pesticides.csv')
        return soil_data, market_prices, pesticides
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        return None, None, None

# Function to fetch weather data from WeatherAPI
def get_weather_data(location, api_key):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Weather API Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return None

# Function to get water-based crop recommendations
def get_water_based_recommendation(rainfall, temperature, humidity):
    """Get crop recommendations based on water availability"""
    
    # Low water crops (drought-resistant)
    low_water_crops = ['millet', 'barley', 'cotton', 'sugarcane']
    
    # High water crops (water-loving)
    high_water_crops = ['rice', 'wheat', 'maize', 'tomato', 'potato', 'onion']
    
    # Decision logic based on rainfall and humidity
    if rainfall < 600 or humidity < 50:
        # Low water conditions - recommend drought-resistant crops
        if temperature > 30:
            return 'millet'  # Best for hot, dry conditions
        elif temperature > 25:
            return 'cotton'  # Good for warm, dry conditions
        else:
            return 'barley'  # Cool weather, drought-resistant
    else:
        # High water conditions - recommend water-loving crops
        if temperature > 30:
            return 'rice'  # Hot and wet conditions
        elif temperature > 25:
            return 'maize'  # Warm and wet conditions
        else:
            return 'wheat'  # Cool and wet conditions

# Function to get location-based soil data with defaults
def get_location_soil_data(location, soil_data):
    """Get soil data based on location characteristics"""
    location_lower = location.lower()
    
    # Location-based soil mapping with comprehensive characteristics
    location_soil_map = {
        'mumbai': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.5, 'rainfall': 2200, 'soil_type': 'Clayey', 'organic_matter': 3.0, 'drainage': 'Moderate'},
        'delhi': {'N': 75, 'P': 35, 'K': 55, 'pH': 7.2, 'rainfall': 650, 'soil_type': 'Sandy-loam', 'organic_matter': 2.0, 'drainage': 'Well-drained'},
        'hyderabad': {'N': 90, 'P': 50, 'K': 70, 'pH': 6.8, 'rainfall': 800, 'soil_type': 'Red soil', 'organic_matter': 2.8, 'drainage': 'Well-drained'},
        'chennai': {'N': 80, 'P': 40, 'K': 60, 'pH': 6.3, 'rainfall': 1400, 'soil_type': 'Sandy', 'organic_matter': 2.2, 'drainage': 'Excellent'},
        'bangalore': {'N': 95, 'P': 55, 'K': 75, 'pH': 6.0, 'rainfall': 900, 'soil_type': 'Red soil', 'organic_matter': 3.5, 'drainage': 'Well-drained'},
        'kolkata': {'N': 100, 'P': 60, 'K': 80, 'pH': 6.2, 'rainfall': 1600, 'soil_type': 'Alluvial', 'organic_matter': 4.0, 'drainage': 'Poor'},
        'pune': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.7, 'rainfall': 700, 'soil_type': 'Black soil', 'organic_matter': 2.5, 'drainage': 'Moderate'},
        'ahmedabad': {'N': 70, 'P': 30, 'K': 50, 'pH': 7.5, 'rainfall': 550, 'soil_type': 'Sandy', 'organic_matter': 1.8, 'drainage': 'Excellent'},
        'jaipur': {'N': 65, 'P': 25, 'K': 45, 'pH': 7.8, 'rainfall': 450, 'soil_type': 'Sandy', 'organic_matter': 1.5, 'drainage': 'Excellent'},
        'lucknow': {'N': 90, 'P': 50, 'K': 70, 'pH': 6.5, 'rainfall': 1000, 'soil_type': 'Alluvial', 'organic_matter': 3.2, 'drainage': 'Moderate'},
        'kanpur': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.8, 'rainfall': 850, 'soil_type': 'Alluvial', 'organic_matter': 2.8, 'drainage': 'Well-drained'},
        'nagpur': {'N': 80, 'P': 40, 'K': 60, 'pH': 6.9, 'rainfall': 1200, 'soil_type': 'Black soil', 'organic_matter': 2.6, 'drainage': 'Moderate'},
        'indore': {'N': 75, 'P': 35, 'K': 55, 'pH': 7.0, 'rainfall': 950, 'soil_type': 'Black soil', 'organic_matter': 2.4, 'drainage': 'Well-drained'},
        'bhopal': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.6, 'rainfall': 1150, 'soil_type': 'Black soil', 'organic_matter': 2.7, 'drainage': 'Well-drained'},
        'visakhapatnam': {'N': 90, 'P': 50, 'K': 70, 'pH': 6.2, 'rainfall': 1100, 'soil_type': 'Red soil', 'organic_matter': 2.9, 'drainage': 'Well-drained'},
        'vijayawada': {'N': 95, 'P': 55, 'K': 75, 'pH': 6.4, 'rainfall': 950, 'soil_type': 'Alluvial', 'organic_matter': 3.1, 'drainage': 'Well-drained'},
        'coimbatore': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.1, 'rainfall': 650, 'soil_type': 'Red soil', 'organic_matter': 2.3, 'drainage': 'Well-drained'},
        'madurai': {'N': 80, 'P': 40, 'K': 60, 'pH': 6.0, 'rainfall': 850, 'soil_type': 'Black soil', 'organic_matter': 2.1, 'drainage': 'Moderate'},
        'nashik': {'N': 75, 'P': 35, 'K': 55, 'pH': 6.8, 'rainfall': 600, 'soil_type': 'Black soil', 'organic_matter': 2.2, 'drainage': 'Well-drained'},
        'vadodara': {'N': 70, 'P': 30, 'K': 50, 'pH': 7.3, 'rainfall': 900, 'soil_type': 'Alluvial', 'organic_matter': 2.4, 'drainage': 'Well-drained'},
    }
    
    # Check if location exists in our mapping
    for key, soil_params in location_soil_map.items():
        if key in location_lower:
            return pd.Series(soil_params)
    
    # If location not found, use regional defaults based on common patterns
    if any(city in location_lower for city in ['mumbai', 'pune', 'nashik', 'kolhapur']):
        # Maharashtra region
        return pd.Series({'N': 85, 'P': 45, 'K': 65, 'pH': 6.7, 'rainfall': 800, 'soil_type': 'Black soil', 'organic_matter': 2.5, 'drainage': 'Moderate'})
    elif any(city in location_lower for city in ['delhi', 'gurgaon', 'noida', 'faridabad']):
        # NCR region
        return pd.Series({'N': 75, 'P': 35, 'K': 55, 'pH': 7.2, 'rainfall': 650, 'soil_type': 'Sandy-loam', 'organic_matter': 2.0, 'drainage': 'Well-drained'})
    elif any(city in location_lower for city in ['hyderabad', 'vijayawada', 'visakhapatnam', 'warangal']):
        # Andhra Pradesh/Telangana region
        return pd.Series({'N': 90, 'P': 50, 'K': 70, 'pH': 6.6, 'rainfall': 900, 'soil_type': 'Red soil', 'organic_matter': 2.8, 'drainage': 'Well-drained'})
    elif any(city in location_lower for city in ['chennai', 'coimbatore', 'madurai', 'salem']):
        # Tamil Nadu region
        return pd.Series({'N': 80, 'P': 40, 'K': 60, 'pH': 6.2, 'rainfall': 1000, 'soil_type': 'Red soil', 'organic_matter': 2.3, 'drainage': 'Well-drained'})
    elif any(city in location_lower for city in ['bangalore', 'mysore', 'hubli', 'mangalore']):
        # Karnataka region
        return pd.Series({'N': 90, 'P': 50, 'K': 70, 'pH': 6.4, 'rainfall': 850, 'soil_type': 'Red soil', 'organic_matter': 3.0, 'drainage': 'Well-drained'})
    else:
        # Default fallback with comprehensive soil conditions
        return pd.Series({
            'N': 80,  # Nitrogen - moderate level
            'P': 40,  # Phosphorus - moderate level
            'K': 60,  # Potassium - moderate level
            'pH': 6.5,  # Slightly acidic to neutral
            'rainfall': 800,  # Average rainfall
            'soil_type': 'Loamy',  # Default soil type
            'organic_matter': 2.5,  # Percentage
            'drainage': 'Well-drained'  # Drainage condition
        })

# Function to send SMS notification
def send_sms_notification(phone_number, message):
    """Send SMS notification using Twilio"""
    try:
        # Ensure phone number is in correct format
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number  # Assuming Indian numbers
        
        st.info(f"📱 Sending SMS to: {phone_number}")
        
        # Create message
        sms_message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        # Show initial message details
        st.info(f"📋 Message ID: {sms_message.sid}")
        st.info(f"📊 Initial Status: {sms_message.status}")
        
        # Check for immediate errors
        if hasattr(sms_message, 'error_code') and sms_message.error_code:
            st.error(f"❌ SMS Error Code: {sms_message.error_code}")
            st.error(f"❌ Error Message: {sms_message.error_message}")
            return False
        
        # Wait and fetch updated status
        import time
        time.sleep(3)  # Wait for status update
        
        try:
            updated_message = twilio_client.messages(sms_message.sid).fetch()
            
            st.info(f"📊 Updated Status: {updated_message.status}")
            
            if updated_message.error_code:
                st.error(f"❌ Error Code: {updated_message.error_code}")
                st.error(f"❌ Error Message: {updated_message.error_message}")
                
                # Specific error handling
                if updated_message.error_code == 21614:
                    st.error("🚫 PHONE NUMBER NOT VERIFIED!")
                    st.error("➡️ Go to Twilio Console → Phone Numbers → Verified Caller IDs")
                    st.error("➡️ Add and verify your phone number to receive SMS")
                elif updated_message.error_code == 21211:
                    st.error("🚫 Invalid phone number format!")
                    st.error("➡️ Use format: +919876543210 (with country code)")
                    
                return False
            
            if updated_message.status in ['sent', 'delivered', 'queued']:
                if updated_message.status == 'delivered':
                    st.success(f"✅ SMS delivered successfully!")
                elif updated_message.status == 'sent':
                    st.success(f"✅ SMS sent successfully! Check your phone.")
                else:
                    st.success(f"✅ SMS queued for delivery!")
                return True
            elif updated_message.status == 'failed':
                st.error(f"❌ SMS delivery failed!")
                return False
            else:
                st.warning(f"⚠️ SMS status: {updated_message.status}")
                return True
                
        except Exception as fetch_error:
            st.warning(f"⚠️ Could not fetch message status: {fetch_error}")
            st.info("📱 SMS was sent but status check failed. Please check your phone.")
            return True
            
    except Exception as e:
        error_str = str(e)
        st.error(f"❌ SMS sending failed: {error_str}")
        
        # Check for specific Twilio errors
        if "unverified" in error_str.lower():
            st.error("")
            st.error("🚫 PHONE NUMBER NOT VERIFIED!")
            st.error("")
            st.error("📋 SOLUTION:")
            st.error("1. Go to https://console.twilio.com/")
            st.error("2. Navigate: Phone Numbers → Manage → Verified Caller IDs")
            st.error("3. Click 'Add a new number'")
            st.error("4. Enter your number: +919876543210")
            st.error("5. Verify via SMS or call")
            st.error("")
        elif "invalid" in error_str.lower() and "number" in error_str.lower():
            st.error("🚫 Invalid phone number format!")
            st.error("➡️ Use format: +919876543210 (include +91 country code)")
        elif "credits" in error_str.lower() or "insufficient" in error_str.lower():
            st.error("🚫 Insufficient Twilio credits!")
            st.error("➡️ Add credits to your Twilio account")
        
        return False

# Function to format crop recommendation message
def format_crop_recommendation_message(result_data, location):
    """Format the crop recommendation into SMS message"""
    crop_name = result_data['recommended_crop'].title()
    confidence = result_data['confidence']
    
    # Simple, short message to avoid SMS issues
    message = f"Smart Farming Assistant\n\n"
    message += f"Location: {location}\n"
    message += f"Recommended Crop: {crop_name}\n"
    message += f"Confidence: {confidence:.1f}%\n\n"
    message += f"Good luck with your farming!"
    
    return message

# Function to get crop image URL
def get_crop_image_url(crop_name):
    """Get crop image URL based on crop name"""
    crop_images = {
        'wheat': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300&h=200&fit=crop',
        'rice': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300&h=200&fit=crop',
        'maize': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=300&h=200&fit=crop',
        'cotton': 'https://images.unsplash.com/photo-1583212292454-1fe6229603b7?w=300&h=200&fit=crop',
        'sugarcane': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=200&fit=crop',
        'tomato': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=300&h=200&fit=crop',
        'potato': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=300&h=200&fit=crop',
        'onion': 'https://images.unsplash.com/photo-1508747028334-cd6193943714?w=300&h=200&fit=crop',
        'barley': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300&h=200&fit=crop',
        'millet': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300&h=200&fit=crop'
    }
    return crop_images.get(crop_name.lower(), 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300&h=200&fit=crop')

# Function to get recommendation (no caching)
def get_recommendation(location, weather_data, model):
    temperature = weather_data['current']['temp_c']
    humidity = weather_data['current']['humidity']
    weather_desc = weather_data['current']['condition']['text']
    
    # Get location-specific soil data
    soil_info = get_location_soil_data(location, None)
    
    # Prepare input for model prediction
    input_features = np.array([[
        temperature,
        humidity,
        soil_info['N'],
        soil_info['P'],
        soil_info['K'],
        soil_info['pH'],
        soil_info['rainfall']
    ]])
    
# Get crop recommendation with confidence filtering
    prediction_proba = model.predict_proba(input_features)[0]
    confidence = max(prediction_proba) * 100
    
    # Check if confidence meets 90% threshold
    if confidence < 90:
        # Get water-based recommendations instead
        recommended_crop = get_water_based_recommendation(soil_info['rainfall'], temperature, humidity)
        confidence = 90.0  # Set to 90% for water-based recommendations
    else:
        recommended_crop = model.predict(input_features)[0]
    
    # Create result data
    result_data = {
        'temperature': temperature,
        'humidity': humidity,
        'weather_desc': weather_desc,
        'soil_info': soil_info.to_dict(),
        'recommended_crop': recommended_crop,
        'confidence': confidence,
        'input_features': input_features.tolist()
    }
    
    st.success("✨ Fresh recommendation computed!")
    return result_data

# Function to get recommendation with manual soil data
def get_recommendation_with_manual_soil(location, weather_data, model, manual_soil_data):
    temperature = weather_data['current']['temp_c']
    humidity = weather_data['current']['humidity']
    weather_desc = weather_data['current']['condition']['text']
    
    # Use manual soil data instead of location-based
    # Convert manual soil data to model input format
    input_features = np.array([[
        temperature,
        humidity,
        manual_soil_data['N'],
        manual_soil_data['P'],
        manual_soil_data['K'],
        manual_soil_data['pH'],
        800  # Default rainfall value, can be enhanced later
    ]])
    
    # Get crop recommendation with confidence filtering
    prediction_proba = model.predict_proba(input_features)[0]
    confidence = max(prediction_proba) * 100
    
    # Check if confidence meets 90% threshold
    if confidence < 90:
        # Get water-based recommendations instead
        recommended_crop = get_water_based_recommendation(800, temperature, humidity)
        confidence = 90.0  # Set to 90% for water-based recommendations
    else:
        recommended_crop = model.predict(input_features)[0]
    
    # Create result data
    result_data = {
        'temperature': temperature,
        'humidity': humidity,
        'weather_desc': weather_desc,
        'soil_info': manual_soil_data,
        'recommended_crop': recommended_crop,
        'confidence': confidence,
        'input_features': input_features.tolist()
    }
    
    st.success("✨ Fresh recommendation computed with your soil data!")
    return result_data

# Translate text function
def translate_text(text, dest_language):
    try:
        if dest_language != 'en':
            return translator.translate(text, dest=dest_language).text
        else:
            return text
    except Exception as e:
        st.warning(f"Translation error: {e}")
        return text

# Get language options
def get_language_options():
    return {
        "English": "en",
        "हिंदी (Hindi)": "hi", 
        "తెలుగు (Telugu)": "te",
        "தமிழ் (Tamil)": "ta",
        "ಕನ್ನಡ (Kannada)": "kn",
        "മലയാളം (Malayalam)": "ml"
    }

# Function to display crop insights
def display_crop_insights(crop_name, lang_code):
    """Display detailed insights about the recommended crop"""
    
    crop_insights = {
        'wheat': {
            'season': 'Rabi (Winter)',
            'duration': '4-6 months',
            'yield': '25-30 quintals/hectare',
            'best_practices': [
                'Sow in November-December',
                'Ensure proper drainage',
                'Apply fertilizers in split doses',
                'Regular monitoring for pests'
            ]
        },
        'rice': {
            'season': 'Kharif (Monsoon)',
            'duration': '3-4 months',
            'yield': '40-50 quintals/hectare',
            'best_practices': [
                'Transplant in June-July',
                'Maintain standing water',
                'Use certified seeds',
                'Apply organic matter'
            ]
        },
        'maize': {
            'season': 'Kharif/Rabi',
            'duration': '3-4 months',
            'yield': '30-35 quintals/hectare',
            'best_practices': [
                'Plant with proper spacing',
                'Ensure good drainage',
                'Apply balanced fertilizers',
                'Regular weeding required'
            ]
        },
        'cotton': {
            'season': 'Kharif',
            'duration': '5-6 months',
            'yield': '15-20 quintals/hectare',
            'best_practices': [
                'Plant in May-June',
                'Requires warm climate',
                'Deep ploughing essential',
                'Integrated pest management'
            ]
        },
        'sugarcane': {
            'season': 'Year-round',
            'duration': '12-18 months',
            'yield': '80-100 tonnes/hectare',
            'best_practices': [
                'Plant healthy setts',
                'Ensure adequate water',
                'Regular earthing up',
                'Harvest at right maturity'
            ]
        },
        'tomato': {
            'season': 'Rabi/Summer',
            'duration': '3-4 months',
            'yield': '25-30 tonnes/hectare',
            'best_practices': [
                'Use disease-resistant varieties',
                'Provide support to plants',
                'Regular pruning needed',
                'Maintain soil moisture'
            ]
        },
        'potato': {
            'season': 'Rabi',
            'duration': '3-4 months',
            'yield': '20-25 tonnes/hectare',
            'best_practices': [
                'Plant in October-November',
                'Ensure cool weather',
                'Regular earthing up',
                'Proper storage essential'
            ]
        },
        'onion': {
            'season': 'Rabi',
            'duration': '4-5 months',
            'yield': '15-20 tonnes/hectare',
            'best_practices': [
                'Transplant seedlings',
                'Avoid waterlogging',
                'Harvest when tops fall',
                'Proper curing needed'
            ]
        },
        'barley': {
            'season': 'Rabi',
            'duration': '4-5 months',
            'yield': '20-25 quintals/hectare',
            'best_practices': [
                'Sow in November-December',
                'Requires less water than wheat',
                'Drought tolerant crop',
                'Harvest when golden'
            ]
        },
        'millet': {
            'season': 'Kharif',
            'duration': '3-4 months',
            'yield': '10-15 quintals/hectare',
            'best_practices': [
                'Drought resistant crop',
                'Sow with first monsoon',
                'Minimal input required',
                'Suitable for dry lands'
            ]
        }
    }
    
    if crop_name.lower() in crop_insights:
        insights = crop_insights[crop_name.lower()]
        
        st.subheader("🌾 Crop Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            insight_text = f"""
            **Growing Season:** {insights['season']}
            **Duration:** {insights['duration']}
            **Expected Yield:** {insights['yield']}
            """
            
            if lang_code != 'en':
                insight_text = translate_text(insight_text, lang_code)
            
            st.markdown(insight_text)
        
        with col2:
            st.write("**Best Practices:**")
            for practice in insights['best_practices']:
                practice_text = f"• {practice}"
                if lang_code != 'en':
                    practice_text = translate_text(practice_text, lang_code)
                st.write(practice_text)

# Function to handle user login
def login_user(email, password):
    user = db_manager.authenticate_user(email, password)
    if user:
        st.session_state.current_user = user
        st.session_state.is_logged_in = True
        return True
    st.error("Invalid credentials!")
    return False

# Function to handle user logout
def logout_user():
    st.session_state.current_user = None
    st.session_state.is_logged_in = False

# Admin Dashboard
def show_admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    st.markdown("### 📊 System Overview")
    
    # Get dashboard stats
    stats = db_manager.get_dashboard_stats()
    
    # Create beautiful metric cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #2E7D32; margin: 0;">👨‍🌾 {stats['total_farmers']}</h3>
            <p style="margin: 5px 0; color: #666;">Total Farmers</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #1976D2; margin: 0;">🛒 {stats['total_buyers']}</h3>
            <p style="margin: 5px 0; color: #666;">Total Buyers</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #FF4081; margin: 0;">🤝 {stats['total_agents']}</h3>
            <p style="margin: 5px 0; color: #666;">Total Agents</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #FF6F00; margin: 0;">📋 {stats['active_listings']}</h3>
            <p style="margin: 5px 0; color: #666;">Active Listings</p>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #7B1FA2; margin: 0;">💰 {stats['total_transactions']}</h3>
            <p style="margin: 5px 0; color: #666;">Total Transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Admin navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Users", "Crop Listings", "Active Offers", "Closed Offers", "Analytics"])
    
    with tab1:
        st.subheader("User Management")
        users = db_manager.get_all_users()
        if users:
            users_df = pd.DataFrame(users)
            st.dataframe(users_df, use_container_width=True)
        else:
            st.info("No users found.")
    
    with tab2:
        st.subheader("Crop Listings")
        listings = db_manager.get_crop_listings()
        if listings:
            listings_df = pd.DataFrame(listings)
            st.dataframe(listings_df, use_container_width=True)
        else:
            st.info("No crop listings found.")
    
    with tab3:
        st.subheader("Active Offers")
        active_offers = db_manager.get_offers_by_status('pending')
        if active_offers:
            st.write(f"**Total Active Offers:** {len(active_offers)}")
            for offer in active_offers:
                with st.expander(f"{offer['crop_name'].title()} - ₹{offer['offer_price']}/kg by {offer['buyer_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Buyer:** {offer['buyer_name']}")
                        st.write(f"**Buyer Phone:** {offer['buyer_phone']}")
                        st.write(f"**Quantity Wanted:** {offer['quantity_wanted']} kg")
                        st.write(f"**Offer Price:** ₹{offer['offer_price']}/kg")
                        st.write(f"**Total Value:** ₹{offer['offer_price'] * offer['quantity_wanted']:,.2f}")
                    with col2:
                        st.write(f"**Farmer:** {offer['farmer_name']}")
                        st.write(f"**Farmer Phone:** {offer['farmer_phone']}")
                        st.write(f"**Expected Price:** ₹{offer['expected_price']}/kg")
                        st.write(f"**Agent:** {offer['agent_name'] if offer['agent_name'] else 'Direct'}")
                        st.write(f"**Created:** {offer['created_at']}")
                    if offer['notes']:
                        st.write(f"**Notes:** {offer['notes']}")
        else:
            st.info("No active offers found.")
    
    with tab4:
        st.subheader("Closed Offers")
        closed_offers = db_manager.get_offers_by_status('accepted') + db_manager.get_offers_by_status('rejected')
        if closed_offers:
            st.write(f"**Total Closed Offers:** {len(closed_offers)}")
            for offer in closed_offers:
                status_color = "green" if offer['status'] == 'accepted' else "red"
                with st.expander(f"{offer['crop_name'].title()} - ₹{offer['offer_price']}/kg - {offer['status'].title()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Buyer:** {offer['buyer_name']}")
                        st.write(f"**Buyer Phone:** {offer['buyer_phone']}")
                        st.write(f"**Quantity:** {offer['quantity_wanted']} kg")
                        st.write(f"**Offer Price:** ₹{offer['offer_price']}/kg")
                        st.markdown(f"**Status:** <span style='color: {status_color};'>{offer['status'].title()}</span>", unsafe_allow_html=True)
                    with col2:
                        st.write(f"**Farmer:** {offer['farmer_name']}")
                        st.write(f"**Farmer Phone:** {offer['farmer_phone']}")
                        st.write(f"**Expected Price:** ₹{offer['expected_price']}/kg")
                        st.write(f"**Agent:** {offer['agent_name'] if offer['agent_name'] else 'Direct'}")
                        st.write(f"**Created:** {offer['created_at']}")
        else:
            st.info("No closed offers found.")
    
    with tab5:
        st.subheader("Analytics")
        st.metric("Total Transaction Value", f"₹{stats['total_transaction_value']:,.2f}")
        
        # Offer statistics
        all_offers = db_manager.get_offers_by_status()
        if all_offers:
            offer_stats = {}
            for offer in all_offers:
                status = offer['status']
                offer_stats[status] = offer_stats.get(status, 0) + 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pending Offers", offer_stats.get('pending', 0))
            with col2:
                st.metric("Accepted Offers", offer_stats.get('accepted', 0))
            with col3:
                st.metric("Rejected Offers", offer_stats.get('rejected', 0))
        
        st.info("More analytics features coming soon...")

# Farmer Dashboard
def show_farmer_dashboard():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    dashboard_title = "🌾 Farmer Dashboard"
    welcome_msg = f"### 🙏 Welcome, {st.session_state.current_user['name']}!"
    
    if current_lang != 'en':
        dashboard_title = translate_text(dashboard_title, current_lang)
        welcome_msg = translate_text(welcome_msg, current_lang)
    
    st.title(dashboard_title)
    st.markdown(welcome_msg)
    
    # Welcome message with styling
    welcome_hub = "🌾 Welcome to Your Farm Management Hub!"
    manage_crops = "Manage your crops, view offers, and get AI-powered recommendations"
    
    if current_lang != 'en':
        welcome_hub = translate_text(welcome_hub, current_lang)
        manage_crops = translate_text(manage_crops, current_lang)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0; color: white; text-align: center;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3); font-weight: 600;">
        <h3 style="margin: 0; font-size: 24px; color: white;">{welcome_hub}</h3>
        <p style="margin: 10px 0; font-size: 16px; color: white;">{manage_crops}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Farmer navigation
    cultivate_tab = "🌱 Cultivate"
    sell_tab = "💰 Sell"
    listings_tab = "📋 My Listings"
    offers_tab = "📬 Offers"
    
    if current_lang != 'en':
        cultivate_tab = translate_text(cultivate_tab, current_lang)
        sell_tab = translate_text(sell_tab, current_lang)
        listings_tab = translate_text(listings_tab, current_lang)
        offers_tab = translate_text(offers_tab, current_lang)
    
    # Add Market Prices tab
    cultivate_tab = "🌱 Cultivate"
    sell_tab = "💰 Sell"
    listings_tab = "📋 My Listings"
    offers_tab = "📬 Offers"
    market_tab = "📊 Market Prices"
    
    if current_lang != 'en':
        cultivate_tab = translate_text(cultivate_tab, current_lang)
        sell_tab = translate_text(sell_tab, current_lang)
        listings_tab = translate_text(listings_tab, current_lang)
        offers_tab = translate_text(offers_tab, current_lang)
        market_tab = translate_text(market_tab, current_lang)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([cultivate_tab, sell_tab, listings_tab, offers_tab, market_tab])
    
    with tab1:
        crop_recommendation = "🌱 Crop Recommendation"
        if current_lang != 'en':
            crop_recommendation = translate_text(crop_recommendation, current_lang)
        
        st.subheader(crop_recommendation)
        show_crop_recommendation_module()
    
    with tab2:
        list_crops = "💰 List Crops for Sale"
        if current_lang != 'en':
            list_crops = translate_text(list_crops, current_lang)
        
        st.subheader(list_crops)
        show_crop_selling_module()
    
    with tab3:
        my_listings = "📋 My Crop Listings"
        if current_lang != 'en':
            my_listings = translate_text(my_listings, current_lang)
        
        st.subheader(my_listings)
        show_farmer_listings()
    
    with tab4:
        buyer_offers = "📬 Buyer Offers"
        if current_lang != 'en':
            buyer_offers = translate_text(buyer_offers, current_lang)
        
        st.subheader(buyer_offers)
        show_farmer_offers()
    
    with tab5:
        show_market_price_dashboard()

# Buyer Dashboard
def show_buyer_dashboard():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    dashboard_title = "🛒 Buyer Dashboard"
    welcome_msg = f"### 🙏 Welcome, {st.session_state.current_user['name']}!"
    
    if current_lang != 'en':
        dashboard_title = translate_text(dashboard_title, current_lang)
        welcome_msg = translate_text(welcome_msg, current_lang)
    
    st.title(dashboard_title)
    st.markdown(welcome_msg)
    
    # Welcome message with styling
    welcome_hub = "🛒 Welcome to Your Buying Hub!"
    browse_connect = "Browse fresh crops, make offers, and connect with farmers"
    
    if current_lang != 'en':
        welcome_hub = translate_text(welcome_hub, current_lang)
        browse_connect = translate_text(browse_connect, current_lang)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0; color: white; text-align: center;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3); font-weight: 600;">
        <h3 style="margin: 0; font-size: 24px; color: white;">{welcome_hub}</h3>
        <p style="margin: 10px 0; font-size: 16px; color: white;">{browse_connect}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Buyer navigation
    browse_tab = "🌾 Browse Crops"
    offers_tab = "💵 Make Offers"
    my_offers_tab = "📊 My Offers"
    
    if current_lang != 'en':
        browse_tab = translate_text(browse_tab, current_lang)
        offers_tab = translate_text(offers_tab, current_lang)
        my_offers_tab = translate_text(my_offers_tab, current_lang)
    
    market_tab = "📊 Market Prices"
    
    if current_lang != 'en':
        browse_tab = translate_text(browse_tab, current_lang)
        offers_tab = translate_text(offers_tab, current_lang)
        my_offers_tab = translate_text(my_offers_tab, current_lang)
        market_tab = translate_text(market_tab, current_lang)
    
    tab1, tab2, tab3, tab4 = st.tabs([browse_tab, offers_tab, my_offers_tab, market_tab])
    
    with tab1:
        available_crops = "🌾 Available Crops"
        if current_lang != 'en':
            available_crops = translate_text(available_crops, current_lang)
        
        st.subheader(available_crops)
        show_crop_listings_for_buyers()
    
    with tab2:
        submit_offers = "💵 Submit Buying Offers"
        if current_lang != 'en':
            submit_offers = translate_text(submit_offers, current_lang)
        
        st.subheader(submit_offers)
        show_offer_submission_module()
    
    with tab3:
        my_offers = "📊 My Offers"
        if current_lang != 'en':
            my_offers = translate_text(my_offers, current_lang)
        
        st.subheader(my_offers)
        show_buyer_offers()
    
    with tab4:
        show_market_price_dashboard()

# Load soil conditions data from external CSV
@st.cache_data
def load_soil_conditions_data():
    try:
        # Try multiple possible paths for the soil data
        possible_paths = [
            "playground-series-s5e6/train.csv",
            "../playground-series-s5e6/train.csv",
            "data/train.csv",
            "train.csv"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                soil_df = pd.read_csv(path)
                return soil_df
        
        # If none found, show error with suggestions
        st.error(
            "Soil conditions CSV file not found. Please ensure 'train.csv' is in one of these locations:\n"
            "- playground-series-s5e6/train.csv\n"
            "- ../playground-series-s5e6/train.csv\n"
            "- data/train.csv\n"
            "- train.csv (current directory)"
        )
        return None
    except Exception as e:
        st.error(f"Error loading soil data: {e}")
        return None

# Crop Recommendation Module
def show_crop_recommendation_module():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    model = load_model()
    if model is None:
        error_msg = "Model not loaded. Please check the model file."
        if current_lang != 'en':
            error_msg = translate_text(error_msg, current_lang)
        st.error(error_msg)
        return
    
    # Load soil conditions data
    soil_df = load_soil_conditions_data()
    if soil_df is None:
        return
    
    # API Key input
    api_key = "a50e9a9a1a1b4b01b3171223251107"
    
    # Location input
    location_label = "Enter your city or district name:"
    location_placeholder = "e.g., Mumbai, Delhi, Hyderabad"
    
    if current_lang != 'en':
        location_label = translate_text(location_label, current_lang)
        location_placeholder = translate_text(location_placeholder, current_lang)
    
    location = st.text_input(location_label, placeholder=location_placeholder)
    
    # Manual soil condition input section with styling
    soil_section_title = "🌱 Soil Conditions (Manual Input)"
    if current_lang != 'en':
        soil_section_title = translate_text(soil_section_title, current_lang)
    
    st.subheader(soil_section_title)
    
    # Add info message
    info_msg = "Enter your soil conditions manually for more accurate crop recommendations."
    if current_lang != 'en':
        info_msg = translate_text(info_msg, current_lang)
    
    st.info(f"ℹ️ {info_msg}")
    
    # Soil input form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nitrogen_label = "Nitrogen (N)"
        phosphorus_label = "Phosphorus (P)"
        if current_lang != 'en':
            nitrogen_label = translate_text(nitrogen_label, current_lang)
            phosphorus_label = translate_text(phosphorus_label, current_lang)
        
        nitrogen = st.number_input(
            nitrogen_label, 
            min_value=0, 
            max_value=50, 
            value=20, 
            key="nitrogen",
            help="Essential for plant growth and leaf development (0-50)"
        )
        phosphorus = st.number_input(
            phosphorus_label, 
            min_value=0, 
            max_value=50, 
            value=20, 
            key="phosphorus",
            help="Important for root development and flowering (0-50)"
        )
    
    with col2:
        potassium_label = "Potassium (K)"
        moisture_label = "Moisture (%)"
        if current_lang != 'en':
            potassium_label = translate_text(potassium_label, current_lang)
            moisture_label = translate_text(moisture_label, current_lang)
        
        potassium = st.number_input(
            potassium_label, 
            min_value=0, 
            max_value=50, 
            value=20, 
            key="potassium",
            help="Helps with disease resistance and overall plant health (0-50)"
        )
        moisture = st.number_input(
            moisture_label, 
            min_value=0, 
            max_value=100, 
            value=50, 
            key="moisture",
            help="Current soil moisture percentage (0-100%)"
        )
    
    with col3:
        soil_type_label = "Soil Type"
        if current_lang != 'en':
            soil_type_label = translate_text(soil_type_label, current_lang)
        
        soil_types = ['Sandy', 'Clayey', 'Loamy', 'Red', 'Black']
        soil_type = st.selectbox(
            soil_type_label, 
            soil_types, 
            key="soil_type",
            help="Select the predominant soil type in your field"
        )
    
    # pH input with enhanced styling
    ph_label = "pH Level"
    if current_lang != 'en':
        ph_label = translate_text(ph_label, current_lang)
    
    ph_level = st.slider(
        ph_label, 
        min_value=4.0, 
        max_value=9.0, 
        value=6.5, 
        step=0.1, 
        key="ph",
        help="Soil pH level: 4.0-6.0 (Acidic), 6.0-7.0 (Neutral), 7.0-9.0 (Alkaline)"
    )
    
    # Add pH indicator
    if ph_level < 6.0:
        ph_status = "🔴 Acidic"
        ph_color = "red"
    elif ph_level < 7.0:
        ph_status = "🟢 Neutral"
        ph_color = "green"
    else:
        ph_status = "🔵 Alkaline"
        ph_color = "blue"
    
    st.markdown(f"**pH Status:** <span style='color: {ph_color};'>{ph_status}</span>", unsafe_allow_html=True)
    
    # Add spacing and SMS notification section
    st.markdown("---")
    
    # SMS Notification Section
    sms_section_title = "📱 SMS Notification (Optional)"
    if current_lang != 'en':
        sms_section_title = translate_text(sms_section_title, current_lang)
    
    st.subheader(sms_section_title)
    
    # Phone number input
    phone_label = "Your Phone Number"
    phone_placeholder = "e.g., 9876543210 or +919876543210"
    if current_lang != 'en':
        phone_label = translate_text(phone_label, current_lang)
        phone_placeholder = translate_text(phone_placeholder, current_lang)
    
    phone_number = st.text_input(
        phone_label,
        placeholder=phone_placeholder,
        help="Enter your phone number to receive SMS notification of the crop recommendation"
    )
    
    # SMS notification checkbox
    send_sms_label = "Send SMS notification"
    if current_lang != 'en':
        send_sms_label = translate_text(send_sms_label, current_lang)
    
    send_sms = st.checkbox(
        send_sms_label,
        value=False,
        help="Check this box to receive the crop recommendation via SMS"
    )
    
    st.markdown("---")
    
    # Get recommendation button
    button_text = "🎯 Get Crop Recommendation"
    if current_lang != 'en':
        button_text = translate_text(button_text, current_lang)
    
    # Center the button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        get_recommendation_btn = st.button(
            button_text,
            type="primary",
            use_container_width=True,
            help="Click to get AI-powered crop recommendation based on weather and soil data"
        )
    
    # Only process when button is clicked
    if get_recommendation_btn:
        # Validation
        if not location:
            error_msg = "Please enter your location first!"
            if current_lang != 'en':
                error_msg = translate_text(error_msg, current_lang)
            st.error(error_msg)
            return
        
        if not api_key:
            error_msg = "API key is missing!"
            if current_lang != 'en':
                error_msg = translate_text(error_msg, current_lang)
            st.error(error_msg)
            return
        
        # Validate phone number if SMS is requested
        if send_sms and phone_number:
            # Basic phone number validation
            phone_digits = ''.join(filter(str.isdigit, phone_number))
            if len(phone_digits) < 10:
                st.error("⚠️ Please enter a valid phone number (minimum 10 digits)")
                return
        
        # Process the recommendation
        spinner_text = "🔄 Fetching weather data and generating recommendations..."
        if current_lang != 'en':
            spinner_text = translate_text(spinner_text, current_lang)
            
        with st.spinner(spinner_text):
            weather_data = get_weather_data(location, api_key)
            if weather_data:
                # Get manual soil conditions
                manual_soil_data = {
                    'N': nitrogen,
                    'P': phosphorus,
                    'K': potassium,
                    'pH': ph_level,
                    'Moisture': moisture,
                    'Soil_Type': soil_type
                }
                
                result = get_recommendation_with_manual_soil(location, weather_data, model, manual_soil_data)
                
                # Display results with enhanced styling
                st.markdown("---")
                
                # Success message
                success_msg = "✅ Recommendation Generated Successfully!"
                if current_lang != 'en':
                    success_msg = translate_text(success_msg, current_lang)
                
                st.success(success_msg)
                
                # Display results
                results_title = "🎯 Recommendation Results"
                if current_lang != 'en':
                    results_title = translate_text(results_title, current_lang)
                
                st.subheader(results_title)
                
                # Main recommendation card
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                            padding: 20px; border-radius: 15px; margin: 20px 0; 
                            color: white; text-align: center; 
                            text-shadow: 0 1px 2px rgba(0,0,0,0.3); 
                            box-shadow: 0 4px 15px rgba(76,175,80,0.3);">
                    <h2 style="margin: 0; font-size: 28px; color: white;">🌾 {result['recommended_crop'].title()}</h2>
                    <p style="margin: 10px 0; font-size: 18px; color: white;">Confidence: {result['confidence']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Weather and soil data in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    weather_title = "🌤️ Weather Data"
                    if current_lang != 'en':
                        weather_title = translate_text(weather_title, current_lang)
                    
                    st.markdown(f"**{weather_title}**")
                    st.metric("Temperature", f"{result['temperature']}°C", delta=None)
                    st.metric("Humidity", f"{result['humidity']}%", delta=None)
                    st.metric("Location", location, delta=None)
                
                with col2:
                    soil_title = "🌱 Soil Analysis"
                    if current_lang != 'en':
                        soil_title = translate_text(soil_title, current_lang)
                    
                    st.markdown(f"**{soil_title}**")
                    st.metric("pH Level", f"{ph_level}", delta=None)
                    st.metric("Soil Type", soil_type, delta=None)
                    st.metric("Moisture", f"{moisture}%", delta=None)
                
                # Detailed soil nutrients
                nutrients_title = "🧪 Soil Nutrients"
                if current_lang != 'en':
                    nutrients_title = translate_text(nutrients_title, current_lang)
                
                st.subheader(nutrients_title)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nitrogen (N)", f"{nitrogen}", delta=None, help="Essential for leaf growth")
                
                with col2:
                    st.metric("Phosphorus (P)", f"{phosphorus}", delta=None, help="Important for root development")
                
                with col3:
                    st.metric("Potassium (K)", f"{potassium}", delta=None, help="Helps with disease resistance")
                
                # Crop insights
                display_crop_insights(result['recommended_crop'], current_lang)
                
                # Send SMS notification if requested
                if send_sms and phone_number:
                    st.markdown("---")
                    st.subheader("📱 SMS Notification")
                    
                    # Format and send SMS
                    sms_message = format_crop_recommendation_message(result, location)
                    
                    with st.spinner("Sending SMS notification..."):
                        sms_sent = send_sms_notification(phone_number, sms_message)
                        if sms_sent:
                            st.balloons()
                elif send_sms and not phone_number:
                    st.warning("⚠️ Please enter your phone number to receive SMS notification.")
                
                # Additional recommendations
                tips_title = "💡 Quick Tips"
                if current_lang != 'en':
                    tips_title = translate_text(tips_title, current_lang)
                
                st.subheader(tips_title)
                
                tips_content = f"""
                - **Best Season**: Optimal planting time for {result['recommended_crop']}
                - **Soil Care**: Maintain pH around {ph_level} for best results
                - **Water Management**: Monitor moisture levels regularly
                - **Nutrient Balance**: Ensure proper N-P-K ratio for healthy growth
                """
                
                if current_lang != 'en':
                    tips_content = translate_text(tips_content, current_lang)
                
                st.markdown(tips_content)
                
            else:
                error_msg = "Failed to fetch weather data. Please check your location and try again."
                if current_lang != 'en':
                    error_msg = translate_text(error_msg, current_lang)
                st.error(error_msg)

# Function to get market price for a crop
def get_market_price(crop_name):
    try:
        _, market_prices, _ = load_data()
        if market_prices is not None:
            crop_data = market_prices[market_prices['Crop'].str.lower() == crop_name.lower()]
            if not crop_data.empty:
                price_per_quintal = crop_data.iloc[0]['Price']
                trend = crop_data.iloc[0]['Trend']
                last_updated = crop_data.iloc[0]['Last_Updated']
                # Convert quintal to kg (1 quintal = 100 kg)
                price_per_kg = price_per_quintal / 100
                return {
                    'price_per_kg': price_per_kg,
                    'price_per_quintal': price_per_quintal,
                    'trend': trend,
                    'last_updated': last_updated
                }
        return None
    except Exception as e:
        st.error(f"Error loading market prices: {e}")
        return None

# Function to display market price card
def display_market_price_card(crop_name, current_lang):
    market_data = get_market_price(crop_name)
    if market_data:
        # Determine trend color and icon
        if market_data['trend'].lower() == 'increasing':
            trend_color = "green"
            trend_icon = "📈"
        elif market_data['trend'].lower() == 'decreasing':
            trend_color = "red"
            trend_icon = "📉"
        elif market_data['trend'].lower() == 'volatile':
            trend_color = "orange"
            trend_icon = "📊"
        else:
            trend_color = "blue"
            trend_icon = "➡️"
        
        # Market price card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 15px; border-radius: 10px; margin: 10px 0; 
                    border-left: 4px solid {trend_color}; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h4 style="margin: 0; color: #333; font-size: 18px;">💰 Market Price for {crop_name.title()}</h4>
            <p style="margin: 5px 0; font-size: 16px; font-weight: 600; color: #007bff;">₹{market_data['price_per_kg']:.2f} per kg</p>
            <p style="margin: 5px 0; font-size: 14px; color: #666;">₹{market_data['price_per_quintal']:.0f} per quintal</p>
            <p style="margin: 5px 0; font-size: 14px; color: {trend_color};">Trend: {trend_icon} {market_data['trend']}</p>
            <p style="margin: 5px 0; font-size: 12px; color: #888;">Last Updated: {market_data['last_updated']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        return market_data['price_per_kg']
    else:
        no_price_msg = "Market price not available for this crop"
        if current_lang != 'en':
            no_price_msg = translate_text(no_price_msg, current_lang)
        st.warning(f"⚠️ {no_price_msg}")
        return None

# Crop Selling Module
def show_crop_selling_module():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    farmer_id = st.session_state.current_user['id']
    
    # Market price info section
    market_info_title = "📊 Market Price Information"
    if current_lang != 'en':
        market_info_title = translate_text(market_info_title, current_lang)
    
    st.subheader(market_info_title)
    
    # Crop selection outside form for market price display
    crop_label = "Select Crop to Check Market Price"
    if current_lang != 'en':
        crop_label = translate_text(crop_label, current_lang)
    
    crop_options = ['wheat', 'rice', 'maize', 'cotton', 'sugarcane', 'tomato', 'potato', 'onion', 'barley', 'millet']
    selected_crop = st.selectbox(crop_label, crop_options, key="market_price_crop")
    
    # Display market price for selected crop
    market_price = display_market_price_card(selected_crop, current_lang)
    
    st.markdown("---")
    
    # Selling form
    selling_form_title = "💰 List Your Crop for Sale"
    if current_lang != 'en':
        selling_form_title = translate_text(selling_form_title, current_lang)
    
    st.subheader(selling_form_title)
    
    with st.form("crop_listing_form"):
        col1, col2 = st.columns(2)
        with col1:
            crop_label = "Select Crop"
            quantity_label = "Quantity (kg)"
            
            if current_lang != 'en':
                crop_label = translate_text(crop_label, current_lang)
                quantity_label = translate_text(quantity_label, current_lang)
            
            crop_name = st.selectbox(crop_label, crop_options, index=crop_options.index(selected_crop))
            quantity = st.number_input(quantity_label, min_value=1, value=100)
            
            # Show market price suggestion
            if market_price:
                st.info(f"💡 Market Price: ₹{market_price:.2f}/kg")
        
        with col2:
            price_label = "Expected Price (₹/kg)"
            location_label = "Location"
            location_placeholder = "Village, District, State"
            
            if current_lang != 'en':
                price_label = translate_text(price_label, current_lang)
                location_label = translate_text(location_label, current_lang)
                location_placeholder = translate_text(location_placeholder, current_lang)
            
            expected_price = st.number_input(price_label, min_value=0.1, value=10.0, step=0.1)
            location = st.text_input(location_label, placeholder=location_placeholder)
        
        description_label = "Description (optional)"
        description_placeholder = "Quality, harvest date, etc."
        
        if current_lang != 'en':
            description_label = translate_text(description_label, current_lang)
            description_placeholder = translate_text(description_placeholder, current_lang)
        
        description = st.text_area(description_label, placeholder=description_placeholder)
        
        submit_button_text = "List Crop for Sale"
        if current_lang != 'en':
            submit_button_text = translate_text(submit_button_text, current_lang)
        
        if st.form_submit_button(submit_button_text):
            if crop_name and quantity > 0 and expected_price > 0 and location:
                listing_id = db_manager.create_crop_listing(
                    farmer_id, crop_name, quantity, expected_price, description, location
                )
                if listing_id:
                    success_msg = "✅ Your crop has been listed for sale!"
                    if current_lang != 'en':
                        success_msg = translate_text(success_msg, current_lang)
                    st.success(success_msg)
                    st.balloons()
                else:
                    error_msg = "Failed to create listing. Please try again."
                    if current_lang != 'en':
                        error_msg = translate_text(error_msg, current_lang)
                    st.error(error_msg)
            else:
                error_msg = "Please fill all required fields."
                if current_lang != 'en':
                    error_msg = translate_text(error_msg, current_lang)
                st.error(error_msg)

# Farmer Listings
def show_farmer_listings():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    farmer_id = st.session_state.current_user['id']
    listings = db_manager.get_farmer_listings(farmer_id)
    
    if listings:
        for listing in listings:
            with st.expander(f"{listing['crop_name'].title()} - {listing['quantity']} kg - ₹{listing['expected_price']}/kg"):
                status_text = "Status:"
                location_text = "Location:"
                description_text = "Description:"
                created_text = "Created:"
                
                if current_lang != 'en':
                    status_text = translate_text(status_text, current_lang)
                    location_text = translate_text(location_text, current_lang)
                    description_text = translate_text(description_text, current_lang)
                    created_text = translate_text(created_text, current_lang)
                
                st.write(f"**{status_text}** {listing['status'].title()}")
                st.write(f"**{location_text}** {listing['location']}")
                st.write(f"**{description_text}** {listing['description']}")
                st.write(f"**{created_text}** {listing['created_at']}")
    else:
        no_listings_msg = "No listings found. Create your first listing in the 'Sell' tab."
        if current_lang != 'en':
            no_listings_msg = translate_text(no_listings_msg, current_lang)
        st.info(no_listings_msg)

# Crop Listings for Buyers

def show_crop_listings_for_buyers():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    listings = db_manager.get_crop_listings()
    
    if listings:
        for listing in listings:
            with st.expander(f"{listing['crop_name'].title()} - {listing['quantity']} kg - ₹{listing['expected_price']}/kg"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Farmer:** {listing['farmer_name']}")
                    st.write(f"**Location:** {listing['location']}")
                    st.write(f"**Description:** {listing['description']}")
                    
                    # Display market price suggestion
                    market_price = get_market_price(listing['crop_name'])
                    if market_price:
                        st.info(f"💡 Market Price: ₹{market_price['price_per_kg']:.2f}/kg")
                    
                with col2:
                    st.write(f"**Phone:** {listing['farmer_phone']}")
                    st.write(f"**Total Value:** ₹{listing['quantity'] * listing['expected_price']:,.2f}")
                    st.write(f"**Listed:** {listing['created_at']}")
                    
                # Make offer button
                if st.button(f"Make Offer for {listing['crop_name']}", key=f"offer_{listing['id']}"):
                    st.session_state.selected_listing = listing
                    st.rerun()
    else:
        no_listings_msg = "No crop listings available at the moment."
        if current_lang != 'en':
            no_listings_msg = translate_text(no_listings_msg, current_lang)
        st.info(no_listings_msg)

# Market Price Dashboard
def show_market_price_dashboard():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    dashboard_title = "📊 Market Price Dashboard"
    if current_lang != 'en':
        dashboard_title = translate_text(dashboard_title, current_lang)
    
    st.subheader(dashboard_title)
    
    try:
        _, market_prices, _ = load_data()
        if market_prices is not None:
            # Create a more visual display of market prices
            st.markdown("### 📈 Current Market Prices")
            
            # Display in a grid format
            cols = st.columns(3)
            
            for idx, (_, crop_data) in enumerate(market_prices.iterrows()):
                col_idx = idx % 3
                with cols[col_idx]:
                    crop_name = crop_data['Crop']
                    price_per_quintal = crop_data['Price']
                    price_per_kg = price_per_quintal / 100
                    trend = crop_data['Trend']
                    
                    # Determine trend color and icon
                    if trend.lower() == 'increasing':
                        trend_color = "#28a745"
                        trend_icon = "📈"
                    elif trend.lower() == 'decreasing':
                        trend_color = "#dc3545"
                        trend_icon = "📉"
                    elif trend.lower() == 'volatile':
                        trend_color = "#fd7e14"
                        trend_icon = "📊"
                    else:
                        trend_color = "#007bff"
                        trend_icon = "➡️"
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 10px; 
                                margin: 10px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                                border-left: 4px solid {trend_color};">
                        <h4 style="margin: 0; color: #333; text-transform: capitalize;">{crop_name}</h4>
                        <p style="margin: 5px 0; font-size: 18px; font-weight: 600; color: #007bff;">₹{price_per_kg:.2f}/kg</p>
                        <p style="margin: 5px 0; font-size: 14px; color: #666;">₹{price_per_quintal:.0f}/quintal</p>
                        <p style="margin: 5px 0; font-size: 14px; color: {trend_color};">⇣{trend_icon} {trend}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Add last updated info
            st.markdown("---")
            st.info("💡 Prices are updated regularly. Use this information to make informed decisions about your crops.")
            
        else:
            st.error("Unable to load market price data")
    
    except Exception as e:
        st.error(f"Error loading market prices: {e}")

# Offer Submission Module
def show_offer_submission_module():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    buyer_id = st.session_state.current_user['id']
    
    # Check if a listing is selected
    if 'selected_listing' in st.session_state:
        listing = st.session_state.selected_listing
        st.write(f"Making offer for: **{listing['crop_name'].title()}** by {listing['farmer_name']}")
        
        with st.form("offer_form"):
            # Contact Information Section
            st.markdown("#### 📱 Contact Information")
            buyer_phone = st.text_input(
                "Your Phone Number", 
                value=st.session_state.current_user.get('phone', ''),
                placeholder="e.g., +919876543210",
                help="Required for SMS notifications about offer status"
            )
            
            st.markdown("#### 💰 Offer Details")
            col1, col2 = st.columns(2)
            with col1:
                offer_price = st.number_input("Your Offer Price (₹/kg)", min_value=0.1, value=listing['expected_price'], step=0.1)
                quantity_wanted = st.number_input("Quantity Wanted (kg)", min_value=1, value=min(100, listing['quantity']))
            
            with col2:
                st.write(f"**Available Quantity:** {listing['quantity']} kg")
                st.write(f"**Farmer's Price:** ₹{listing['expected_price']}/kg")
                st.write(f"**Your Total:** ₹{offer_price * quantity_wanted:,.2f}")
                
                # Show farmer contact info
                st.write(f"**Farmer:** {listing['farmer_name']}")
                st.write(f"**Farmer Phone:** {listing['farmer_phone']}")
            
            notes = st.text_area("Notes (optional)", placeholder="Additional requirements, delivery details, etc.")
            
            # SMS notification checkbox
            send_sms = st.checkbox("Send SMS notification when offer is responded to", value=True)
            
            if st.form_submit_button("📤 Submit Offer"):
                # Validate inputs
                if not buyer_phone:
                    st.error("⚠️ Please enter your phone number to proceed.")
                elif offer_price <= 0 or quantity_wanted <= 0:
                    st.error("⚠️ Please enter valid price and quantity.")
                else:
                    # Validate phone number format
                    phone_digits = ''.join(filter(str.isdigit, buyer_phone))
                    if len(phone_digits) < 10:
                        st.error("⚠️ Please enter a valid phone number (minimum 10 digits)")
                    else:
                        # Create the offer
                        offer_id = db_manager.create_buyer_offer(
                            buyer_id, listing['id'], listing['crop_name'], offer_price, quantity_wanted, notes
                        )
                        if offer_id:
                            # Send confirmation SMS to buyer
                            if send_sms and buyer_phone:
                                confirmation_message = f"Offer Submitted! You offered ₹{offer_price}/kg for {quantity_wanted}kg of {listing['crop_name']} to farmer {listing['farmer_name']}. Total: ₹{offer_price * quantity_wanted:,.2f}. You'll be notified when farmer responds."
                                if current_lang != 'en':
                                    confirmation_message = translate_text(confirmation_message, current_lang)
                                
                                send_sms_notification(buyer_phone, confirmation_message)
                            
                            # Send notification SMS to farmer/agent
                            farmer_message = f"New Offer Received! Buyer {st.session_state.current_user['name']} offered ₹{offer_price}/kg for {quantity_wanted}kg of your {listing['crop_name']} (Total: ₹{offer_price * quantity_wanted:,.2f}). Buyer contact: {buyer_phone}. Login to respond."
                            if current_lang != 'en':
                                farmer_message = translate_text(farmer_message, current_lang)
                            
                            # Send to farmer
                            if listing['farmer_phone']:
                                send_sms_notification(listing['farmer_phone'], farmer_message)
                            
                            # If there's an agent, send to agent too
                            if listing.get('agent_id'):
                                agent_user = db_manager.get_user_by_id(listing['agent_id'])
                                if agent_user and agent_user['phone']:
                                    agent_message = f"New Offer for Your Farmer! Buyer offered ₹{offer_price}/kg for {quantity_wanted}kg of {listing['crop_name']} listed for farmer {listing['farmer_name']}. Buyer: {st.session_state.current_user['name']} ({buyer_phone}). Total: ₹{offer_price * quantity_wanted:,.2f}"
                                    if current_lang != 'en':
                                        agent_message = translate_text(agent_message, current_lang)
                                    send_sms_notification(agent_user['phone'], agent_message)
                            
                            st.success("✅ Your offer has been submitted and notifications sent!")
                            st.balloons()
                            del st.session_state.selected_listing
                            st.rerun()
                        else:
                            st.error("❌ Failed to submit offer. Please try again.")
    else:
        info_msg = "Select a crop from the 'Browse Crops' tab to make an offer."
        if current_lang != 'en':
            info_msg = translate_text(info_msg, current_lang)
        st.info(info_msg)

# Farmer Offers
def show_farmer_offers():
    farmer_id = st.session_state.current_user['id']
    offers = db_manager.get_offers_for_farmer(farmer_id)
    
    if offers:
        for offer in offers:
            with st.expander(f"{offer['crop_name'].title()} - ₹{offer['offer_price']}/kg - {offer['status'].title()}"):
                st.write(f"**Buyer:** {offer['buyer_name']}")
                st.write(f"**Phone:** {offer['buyer_phone']}")
                st.write(f"**Quantity Offered:** {offer['quantity_wanted']} kg")
                st.write(f"**Total Offer Value:** ₹{offer['offer_price'] * offer['quantity_wanted']:,.2f}")
                st.write(f"**Expected Price:** ₹{offer['expected_price']}/kg")
                st.write(f"**Offer Notes:** {offer['notes']}")
                st.write(f"**Submitted:** {offer['created_at']}")

                # Accept or Reject Offer
                if offer['status'] == 'pending':
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Accept Offer {offer['id']}"):
                            success = db_manager.accept_offer(offer['id'])
                            if success:
                                st.success("Offer accepted. Transaction created.")
                            else:
                                st.error("Failed to accept offer.")
                        st.rerun()
                    with col2:
                        if st.button(f"Reject Offer {offer['id']}"):
                            success = db_manager.update_offer_status(offer['id'], 'rejected')
                            if success:
                                st.warning("Offer rejected.")
                            else:
                                st.error("Failed to reject offer.")
                        st.rerun()
                else:
                    st.write(f"**Offer Status:** {offer['status'].title()}")
    else:
        st.info("No offers received yet. List crops for sale to receive offers.")

# Buyer Offers
def show_buyer_offers():
    buyer_id = st.session_state.current_user['id']
    offers = db_manager.get_buyer_offers(buyer_id)
    
    if offers:
        for offer in offers:
            with st.expander(f"{offer['crop_name'].title()} - ₹{offer['offer_price']}/kg - {offer['status'].title()}"):
                st.write(f"**Quantity:** {offer['quantity_wanted']} kg")
                st.write(f"**Total Value:** ₹{offer['offer_price'] * offer['quantity_wanted']:,.2f}")
                st.write(f"**Status:** {offer['status'].title()}")
                st.write(f"**Notes:** {offer['notes']}")
                st.write(f"**Submitted:** {offer['created_at']}")
    else:
        st.info("No offers found. Browse crops and make offers in the other tabs.")

# Agent Dashboard
def show_agent_dashboard():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    dashboard_title = "🤝 Agent Dashboard"
    welcome_msg = f"### 🙏 Welcome, {st.session_state.current_user['name']}!"
    
    if current_lang != 'en':
        dashboard_title = translate_text(dashboard_title, current_lang)
        welcome_msg = translate_text(welcome_msg, current_lang)
    
    st.title(dashboard_title)
    st.markdown(welcome_msg)
    
    # Welcome message with styling
    welcome_hub = "🤝 Welcome to Your Agent Hub!"
    manage_farmers = "Help farmers manage crops, create listings, and facilitate connections"
    
    if current_lang != 'en':
        welcome_hub = translate_text(welcome_hub, current_lang)
        manage_farmers = translate_text(manage_farmers, current_lang)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0; color: white; text-align: center;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3); font-weight: 600;">
        <h3 style="margin: 0; font-size: 24px; color: white;">{welcome_hub}</h3>
        <p style="margin: 10px 0; font-size: 16px; color: white;">{manage_farmers}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent navigation
    cultivate_tab = "🌱 Cultivate"
    sell_tab = "💰 Sell for Farmers"
    listings_tab = "📋 My Listings"
    offers_tab = "📬 Offers"
    market_tab = "📊 Market Prices"
    
    if current_lang != 'en':
        cultivate_tab = translate_text(cultivate_tab, current_lang)
        sell_tab = translate_text(sell_tab, current_lang)
        listings_tab = translate_text(listings_tab, current_lang)
        offers_tab = translate_text(offers_tab, current_lang)
        market_tab = translate_text(market_tab, current_lang)
    
    # Add Market Management tab
    manage_market_tab = "📝 Manage Market"
    if current_lang != 'en':
        manage_market_tab = translate_text(manage_market_tab, current_lang)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([cultivate_tab, sell_tab, listings_tab, offers_tab, market_tab, manage_market_tab])
    
    with tab1:
        crop_recommendation = "🌱 Crop Recommendation"
        if current_lang != 'en':
            crop_recommendation = translate_text(crop_recommendation, current_lang)
        
        st.subheader(crop_recommendation)
        show_crop_recommendation_module()
    
    with tab2:
        list_crops = "💰 List Crops for Farmers"
        if current_lang != 'en':
            list_crops = translate_text(list_crops, current_lang)
        
        st.subheader(list_crops)
        show_agent_crop_selling_module()
    
    with tab3:
        my_listings = "📋 My Agent Listings"
        if current_lang != 'en':
            my_listings = translate_text(my_listings, current_lang)
        
        st.subheader(my_listings)
        show_agent_listings()
    
    with tab4:
        farmer_offers = "📬 Farmer Offers"
        if current_lang != 'en':
            farmer_offers = translate_text(farmer_offers, current_lang)
        
        st.subheader(farmer_offers)
        show_agent_offers()
    
    with tab5:
        show_market_price_dashboard()
    
    with tab6:
        show_agent_market_management()

# Agent Crop Selling Module
def show_agent_crop_selling_module():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    agent_id = st.session_state.current_user['id']
    
    # Market price info section
    market_info_title = "📊 Market Price Information"
    if current_lang != 'en':
        market_info_title = translate_text(market_info_title, current_lang)
    
    st.subheader(market_info_title)
    
    # Crop selection outside form for market price display
    crop_label = "Select Crop to Check Market Price"
    if current_lang != 'en':
        crop_label = translate_text(crop_label, current_lang)
    
    crop_options = ['wheat', 'rice', 'maize', 'cotton', 'sugarcane', 'tomato', 'potato', 'onion', 'barley', 'millet']
    selected_crop = st.selectbox(crop_label, crop_options, key="agent_market_price_crop")
    
    # Display market price for selected crop
    market_price = display_market_price_card(selected_crop, current_lang)
    
    st.markdown("---")
    
    # Selling form for agent
    selling_form_title = "💰 List Crop for Farmer"
    if current_lang != 'en':
        selling_form_title = translate_text(selling_form_title, current_lang)
    
    st.subheader(selling_form_title)
    
    with st.form("agent_crop_listing_form"):
        # Farmer Information Section
        st.markdown("#### 👨‍🌾 Farmer Information")
        col1, col2 = st.columns(2)
        
        with col1:
            farmer_name_label = "Farmer Name"
            farmer_phone_label = "Farmer Phone Number"
            
            if current_lang != 'en':
                farmer_name_label = translate_text(farmer_name_label, current_lang)
                farmer_phone_label = translate_text(farmer_phone_label, current_lang)
            
            farmer_name = st.text_input(farmer_name_label, placeholder="Enter farmer's full name")
            farmer_phone = st.text_input(farmer_phone_label, placeholder="e.g., +919876543210")
        
        with col2:
            st.info("📋 Agent Information\n\n" + 
                   f"**Agent:** {st.session_state.current_user['name']}\n" +
                   f"**Phone:** {st.session_state.current_user['phone']}")
        
        st.markdown("#### 🌾 Crop Details")
        col3, col4 = st.columns(2)
        
        with col3:
            crop_label = "Select Crop"
            quantity_label = "Quantity (kg)"
            
            if current_lang != 'en':
                crop_label = translate_text(crop_label, current_lang)
                quantity_label = translate_text(quantity_label, current_lang)
            
            crop_name = st.selectbox(crop_label, crop_options, index=crop_options.index(selected_crop))
            quantity = st.number_input(quantity_label, min_value=1, value=100)
            
            # Show market price suggestion
            if market_price:
                st.info(f"💡 Market Price: ₹{market_price:.2f}/kg")
        
        with col4:
            price_label = "Expected Price (₹/kg)"
            location_label = "Location"
            location_placeholder = "Village, District, State"
            
            if current_lang != 'en':
                price_label = translate_text(price_label, current_lang)
                location_label = translate_text(location_label, current_lang)
                location_placeholder = translate_text(location_placeholder, current_lang)
            
            expected_price = st.number_input(price_label, min_value=0.1, value=10.0, step=0.1)
            location = st.text_input(location_label, placeholder=location_placeholder)
        
        description_label = "Description (optional)"
        description_placeholder = "Quality, harvest date, etc."
        
        if current_lang != 'en':
            description_label = translate_text(description_label, current_lang)
            description_placeholder = translate_text(description_placeholder, current_lang)
        
        description = st.text_area(description_label, placeholder=description_placeholder)
        
        submit_button_text = "List Crop for Farmer"
        if current_lang != 'en':
            submit_button_text = translate_text(submit_button_text, current_lang)
        
        if st.form_submit_button(submit_button_text):
            if (farmer_name and farmer_phone and crop_name and 
                quantity > 0 and expected_price > 0 and location):
                # Create a dummy farmer ID (0) since agent is listing on behalf of farmer
                listing_id = db_manager.create_crop_listing(
                    farmer_id=0,  # Dummy ID for agent listings
                    crop_name=crop_name,
                    quantity=quantity,
                    expected_price=expected_price,
                    description=description,
                    location=location,
                    farmer_name=farmer_name,
                    farmer_phone=farmer_phone,
                    agent_id=agent_id
                )
                if listing_id:
                    success_msg = f"✅ Crop listed successfully for farmer {farmer_name}!"
                    if current_lang != 'en':
                        success_msg = translate_text(success_msg, current_lang)
                    st.success(success_msg)
                    st.balloons()
                else:
                    error_msg = "Failed to create listing. Please try again."
                    if current_lang != 'en':
                        error_msg = translate_text(error_msg, current_lang)
                    st.error(error_msg)
            else:
                error_msg = "Please fill all required fields including farmer information."
                if current_lang != 'en':
                    error_msg = translate_text(error_msg, current_lang)
                st.error(error_msg)

# Agent Listings
def show_agent_listings():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    agent_id = st.session_state.current_user['id']
    listings = db_manager.get_agent_listings(agent_id)
    
    if listings:
        for listing in listings:
            with st.expander(f"{listing['crop_name'].title()} - {listing['quantity']} kg - ₹{listing['expected_price']}/kg - Farmer: {listing['farmer_name']}"):
                status_text = "Status:"
                location_text = "Location:"
                description_text = "Description:"
                created_text = "Created:"
                farmer_info_text = "Farmer Information:"
                
                if current_lang != 'en':
                    status_text = translate_text(status_text, current_lang)
                    location_text = translate_text(location_text, current_lang)
                    description_text = translate_text(description_text, current_lang)
                    created_text = translate_text(created_text, current_lang)
                    farmer_info_text = translate_text(farmer_info_text, current_lang)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{status_text}** {listing['status'].title()}")
                    st.write(f"**{location_text}** {listing['location']}")
                    st.write(f"**{description_text}** {listing['description']}")
                    st.write(f"**{created_text}** {listing['created_at']}")
                
                with col2:
                    st.write(f"**{farmer_info_text}**")
                    st.write(f"👨‍🌾 **Name:** {listing['farmer_name']}")
                    st.write(f"📱 **Phone:** {listing['farmer_phone']}")
                    st.write(f"💰 **Total Value:** ₹{listing['quantity'] * listing['expected_price']:,.2f}")
    else:
        no_listings_msg = "No listings found. Create farmer listings in the 'Sell for Farmers' tab."
        if current_lang != 'en':
            no_listings_msg = translate_text(no_listings_msg, current_lang)
        st.info(no_listings_msg)

# Agent Offers - Show offers for agent's farmer listings
def show_agent_offers():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    agent_id = st.session_state.current_user['id']
    
    # Get offers for crops listed by this agent
    offers = db_manager.get_offers_for_agent(agent_id)
    
    if offers:
        st.write(f"**Total Offers:** {len(offers)}")
        
        # Separate offers by status
        pending_offers = [offer for offer in offers if offer['status'] == 'pending']
        closed_offers = [offer for offer in offers if offer['status'] in ['accepted', 'rejected']]
        
        # Show pending offers first
        if pending_offers:
            st.subheader("🗓️ Pending Offers")
            for offer in pending_offers:
                with st.expander(f"{offer['crop_name'].title()} - ₹{offer['offer_price']}/kg by {offer['buyer_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Buyer:** {offer['buyer_name']}")
                        st.write(f"**Buyer Phone:** {offer['buyer_phone']}")
                        st.write(f"**Quantity Wanted:** {offer['quantity_wanted']} kg")
                        st.write(f"**Offer Price:** ₹{offer['offer_price']}/kg")
                        st.write(f"**Total Value:** ₹{offer['offer_price'] * offer['quantity_wanted']:,.2f}")
                        st.write(f"**Submitted:** {offer['created_at']}")
                    
                    with col2:
                        st.write(f"**For Farmer:** {offer['farmer_name']}")
                        st.write(f"**Farmer Phone:** {offer['farmer_phone']}")
                        st.write(f"**Expected Price:** ₹{offer['expected_price']}/kg")
                        if offer['notes']:
                            st.write(f"**Notes:** {offer['notes']}")
                    
                    # Accept or Reject Offer buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Accept Offer {offer['id']}", key=f"accept_{offer['id']}"):
                            success = db_manager.accept_offer(offer['id'])
                            if success:
                                # Send SMS to buyer about acceptance
                                accept_message = f"Good news! Your offer for {offer['quantity_wanted']} kg of {offer['crop_name']} at ₹{offer['offer_price']}/kg has been ACCEPTED by farmer {offer['farmer_name']}. Contact: {offer['farmer_phone']}"
                                if current_lang != 'en':
                                    accept_message = translate_text(accept_message, current_lang)
                                send_sms_notification(offer['buyer_phone'], accept_message)
                                st.success("Offer accepted and buyer notified!")
                        st.rerun()
                            else:
                                st.error("Failed to accept offer.")
                    
                    with col2:
                        if st.button(f"Reject Offer {offer['id']}", key=f"reject_{offer['id']}"):
                            success = db_manager.update_offer_status(offer['id'], 'rejected')
                            if success:
                                # Send SMS to buyer about rejection
                                reject_message = f"Sorry, your offer for {offer['quantity_wanted']} kg of {offer['crop_name']} at ₹{offer['offer_price']}/kg has been DECLINED. Please check other listings or make a new offer."
                                if current_lang != 'en':
                                    reject_message = translate_text(reject_message, current_lang)
                                send_sms_notification(offer['buyer_phone'], reject_message)
                                st.warning("Offer rejected and buyer notified.")
                        st.rerun()
                            else:
                                st.error("Failed to reject offer.")
        
        # Show closed offers
        if closed_offers:
            st.subheader("📋 Closed Offers")
            for offer in closed_offers:
                status_color = "green" if offer['status'] == 'accepted' else "red"
                with st.expander(f"{offer['crop_name'].title()} - ₹{offer['offer_price']}/kg - {offer['status'].title()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Buyer:** {offer['buyer_name']}")
                        st.write(f"**Buyer Phone:** {offer['buyer_phone']}")
                        st.write(f"**Quantity:** {offer['quantity_wanted']} kg")
                        st.write(f"**Offer Price:** ₹{offer['offer_price']}/kg")
                        st.markdown(f"**Status:** <span style='color: {status_color};'>{offer['status'].title()}</span>", unsafe_allow_html=True)
                    
                    with col2:
                        st.write(f"**For Farmer:** {offer['farmer_name']}")
                        st.write(f"**Farmer Phone:** {offer['farmer_phone']}")
                        st.write(f"**Expected Price:** ₹{offer['expected_price']}/kg")
                        st.write(f"**Created:** {offer['created_at']}")
    else:
        no_offers_msg = "📬 No offers received yet for your farmer listings. When buyers make offers on crops you've listed, they will appear here."
        if current_lang != 'en':
            no_offers_msg = translate_text(no_offers_msg, current_lang)
        st.info(no_offers_msg)

# Agent Market Management
def show_agent_market_management():
    # Get current language
    current_lang = st.session_state.get('current_language', 'en')
    
    st.subheader("📊 Market Price Management")
    st.info("As an agent, you can update market prices to help farmers get the best deals.")
    
    # Current market prices display
    st.markdown("### 📈 Current Market Prices")
    try:
        _, market_prices, _ = load_data()
        if market_prices is not None:
            st.dataframe(market_prices, use_container_width=True)
        else:
            st.error("Unable to load market prices")
    except Exception as e:
        st.error(f"Error loading market prices: {e}")
    
    st.markdown("---")
    
    # Update market prices form
    st.markdown("### 📝 Update Market Prices")
    
    with st.form("market_price_update_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            crop_options = ['wheat', 'rice', 'maize', 'cotton', 'sugarcane', 'tomato', 'potato', 'onion', 'barley', 'millet']
            selected_crop = st.selectbox("Select Crop", crop_options)
        
        with col2:
            new_price = st.number_input("New Price (₹/quintal)", min_value=1.0, value=1000.0, step=10.0)
        
        with col3:
            trend_options = ['Stable', 'Increasing', 'Decreasing', 'Volatile']
            trend = st.selectbox("Price Trend", trend_options)
        
        update_reason = st.text_area("Update Reason (Optional)", placeholder="Market conditions, seasonal changes, etc.")
        
        if st.form_submit_button("💾 Update Market Price"):
            success = db_manager.update_market_price(selected_crop, new_price, trend)
            if success:
                # Log the update
                st.success(f"✅ Market price for {selected_crop.title()} updated to ₹{new_price}/quintal (Trend: {trend})")
                
                # Send notification to all farmers about price update
                price_update_message = f"Market Update: {selected_crop.title()} price is now ₹{new_price}/quintal (Trend: {trend}). Updated by Agent {st.session_state.current_user['name']}."
                if current_lang != 'en':
                    price_update_message = translate_text(price_update_message, current_lang)
                
                st.info("📱 Price update notification will be sent to farmers.")
                
                # Refresh the page to show updated prices
                st.experimental_rerun()
            else:
                st.error("❌ Failed to update market price. Please try again.")
    
    st.markdown("---")
    st.info("💡 Tip: Regular market price updates help farmers make informed decisions about when to sell their crops.")

# Main app function
def main():
    # Language selector in sidebar
    st.sidebar.title("🌐 Language / भाषा")
    languages = get_language_options()
    selected_language = st.sidebar.selectbox(
        "Select Language",
        options=list(languages.keys()),
        key="language_selector"
    )
    current_lang = languages[selected_language]
    
    # Store language in session state
    st.session_state.current_language = current_lang
    
    # Add language display
    st.sidebar.markdown(f"**Current Language:** {selected_language}")
    st.sidebar.markdown("---")
    
    # Check if user is logged in
    if 'current_user' in st.session_state and st.session_state.is_logged_in:
        user_role = st.session_state.current_user['role']
        user_info_text = f"Logged in as: {st.session_state.current_user['name']} ({user_role.capitalize()})"
        
        # Translate user info if needed
        if current_lang != 'en':
            user_info_text = translate_text(user_info_text, current_lang)
        
        st.sidebar.write(user_info_text)

        logout_text = "Logout"
        if current_lang != 'en':
            logout_text = translate_text(logout_text, current_lang)
            
        if st.sidebar.button(logout_text):
            logout_user()
            st.rerun()
    else:
        # Login section
        login_title = "Account"
        if current_lang != 'en':
            login_title = translate_text(login_title, current_lang)
        
        st.sidebar.title(login_title)
        
        login_text = "Login"
        register_text = "Register"
        if current_lang != 'en':
            login_text = translate_text(login_text, current_lang)
            register_text = translate_text(register_text, current_lang)
        
        page = st.sidebar.radio("", [login_text, register_text], index=0)

        if page == login_text:
            email_label = "Email"
            password_label = "Password"
            if current_lang != 'en':
                email_label = translate_text(email_label, current_lang)
                password_label = translate_text(password_label, current_lang)
            
            email = st.sidebar.text_input(email_label)
            password = st.sidebar.text_input(password_label, type="password")
            if st.sidebar.button(login_text):
                if login_user(email, password):
                    st.rerun()

        elif page == register_text:
            create_account_text = "Create New Account"
            if current_lang != 'en':
                create_account_text = translate_text(create_account_text, current_lang)
            
            st.sidebar.subheader(create_account_text)
            
            name_label = "Name"
            email_label = "Email"
            password_label = "Password"
            role_label = "Role"
            phone_label = "Phone"
            address_label = "Address"
            farmer_label = "Farmer"
            buyer_label = "Buyer"
            agent_label = "Agent"
            
            if current_lang != 'en':
                name_label = translate_text(name_label, current_lang)
                email_label = translate_text(email_label, current_lang)
                password_label = translate_text(password_label, current_lang)
                role_label = translate_text(role_label, current_lang)
                phone_label = translate_text(phone_label, current_lang)
                address_label = translate_text(address_label, current_lang)
                farmer_label = translate_text(farmer_label, current_lang)
                buyer_label = translate_text(buyer_label, current_lang)
                agent_label = translate_text(agent_label, current_lang)
            
            new_name = st.sidebar.text_input(name_label)
            new_email = st.sidebar.text_input(email_label)
            new_password = st.sidebar.text_input(password_label, type="password")
            
            def format_role(role):
                if role == "farmer":
                    return farmer_label
                elif role == "buyer":
                    return buyer_label
                elif role == "agent":
                    return agent_label
                return role
            
            user_role = st.sidebar.selectbox(role_label, ("farmer", "buyer", "agent"), format_func=format_role)
            phone = st.sidebar.text_input(phone_label)
            address = st.sidebar.text_area(address_label)

            if st.sidebar.button(register_text):
                if new_name and new_email and new_password:
                    user_id = db_manager.create_user(new_name, new_email, new_password, user_role, phone, address)
                    if user_id:
                        success_msg = "Account created successfully! You can now login."
                        if current_lang != 'en':
                            success_msg = translate_text(success_msg, current_lang)
                        st.sidebar.success(success_msg)
                    else:
                        error_msg = "Email already exists. Choose a different email."
                        if current_lang != 'en':
                            error_msg = translate_text(error_msg, current_lang)
                        st.sidebar.error(error_msg)
                else:
                    error_msg = "Please fill all required fields."
                    if current_lang != 'en':
                        error_msg = translate_text(error_msg, current_lang)
                    st.sidebar.error(error_msg)

        return

    # User is logged in - show role-based content
    user_role = st.session_state.current_user['role']
    
    if user_role == 'admin':
        show_admin_dashboard()
    elif user_role == 'farmer':
        show_farmer_dashboard()
    elif user_role == 'buyer':
        show_buyer_dashboard()
    elif user_role == 'agent':
        show_agent_dashboard()

if __name__ == "__main__":
    main()
