import streamlit as st
import pandas as pd
import requests
import pickle
import os
from googletrans import Translator
import numpy as np
import hashlib
import json
from datetime import datetime, timedelta

# Initialize translator
translator = Translator()

# Set page configuration
st.set_page_config(
    page_title="Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for caching
if 'location_cache' not in st.session_state:
    st.session_state.location_cache = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = {}

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

# Function to get location-based soil data
def get_location_soil_data(location, soil_data):
    """Get soil data based on location characteristics"""
    location_lower = location.lower()
    
    # Location-based soil mapping (simplified)
    location_soil_map = {
        'mumbai': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.5, 'rainfall': 2200},
        'delhi': {'N': 75, 'P': 35, 'K': 55, 'pH': 7.2, 'rainfall': 650},
        'hyderabad': {'N': 90, 'P': 50, 'K': 70, 'pH': 6.8, 'rainfall': 800},
        'chennai': {'N': 80, 'P': 40, 'K': 60, 'pH': 6.3, 'rainfall': 1400},
        'bangalore': {'N': 95, 'P': 55, 'K': 75, 'pH': 6.0, 'rainfall': 900},
        'kolkata': {'N': 100, 'P': 60, 'K': 80, 'pH': 6.2, 'rainfall': 1600},
        'pune': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.7, 'rainfall': 700},
        'ahmedabad': {'N': 70, 'P': 30, 'K': 50, 'pH': 7.5, 'rainfall': 550},
        'jaipur': {'N': 65, 'P': 25, 'K': 45, 'pH': 7.8, 'rainfall': 450},
        'lucknow': {'N': 90, 'P': 50, 'K': 70, 'pH': 6.5, 'rainfall': 1000},
        'kanpur': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.8, 'rainfall': 850},
        'nagpur': {'N': 80, 'P': 40, 'K': 60, 'pH': 6.9, 'rainfall': 1200},
        'indore': {'N': 75, 'P': 35, 'K': 55, 'pH': 7.0, 'rainfall': 950},
        'bhopal': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.6, 'rainfall': 1150},
        'visakhapatnam': {'N': 90, 'P': 50, 'K': 70, 'pH': 6.2, 'rainfall': 1100},
        'vijayawada': {'N': 95, 'P': 55, 'K': 75, 'pH': 6.4, 'rainfall': 950},
        'coimbatore': {'N': 85, 'P': 45, 'K': 65, 'pH': 6.1, 'rainfall': 650},
        'madurai': {'N': 80, 'P': 40, 'K': 60, 'pH': 6.0, 'rainfall': 850},
        'nashik': {'N': 75, 'P': 35, 'K': 55, 'pH': 6.8, 'rainfall': 600},
        'vadodara': {'N': 70, 'P': 30, 'K': 50, 'pH': 7.3, 'rainfall': 900},
    }
    
    # Check if location exists in our mapping
    for key, soil_params in location_soil_map.items():
        if key in location_lower:
            return pd.Series(soil_params)
    
    # If location not found, use regional defaults based on common patterns
    if any(city in location_lower for city in ['mumbai', 'pune', 'nashik', 'kolhapur']):
        # Maharashtra region
        return pd.Series({'N': 85, 'P': 45, 'K': 65, 'pH': 6.7, 'rainfall': 800})
    elif any(city in location_lower for city in ['delhi', 'gurgaon', 'noida', 'faridabad']):
        # NCR region
        return pd.Series({'N': 75, 'P': 35, 'K': 55, 'pH': 7.2, 'rainfall': 650})
    elif any(city in location_lower for city in ['hyderabad', 'vijayawada', 'visakhapatnam', 'warangal']):
        # Andhra Pradesh/Telangana region
        return pd.Series({'N': 90, 'P': 50, 'K': 70, 'pH': 6.6, 'rainfall': 900})
    elif any(city in location_lower for city in ['chennai', 'coimbatore', 'madurai', 'salem']):
        # Tamil Nadu region
        return pd.Series({'N': 80, 'P': 40, 'K': 60, 'pH': 6.2, 'rainfall': 1000})
    elif any(city in location_lower for city in ['bangalore', 'mysore', 'hubli', 'mangalore']):
        # Karnataka region
        return pd.Series({'N': 90, 'P': 50, 'K': 70, 'pH': 6.4, 'rainfall': 850})
    else:
        # Default fallback
        return pd.Series({'N': 80, 'P': 40, 'K': 60, 'pH': 6.5, 'rainfall': 800})

# Function to check if cache is valid (within 10 minutes)
def is_cache_valid(location):
    if location in st.session_state.last_update:
        last_update = st.session_state.last_update[location]
        return datetime.now() - last_update < timedelta(minutes=10)
    return False

# Function to get or compute recommendation
def get_recommendation(location, weather_data, model):
    location_key = location.lower()
    
    # Check if we have a valid cached result
    if location_key in st.session_state.location_cache and is_cache_valid(location_key):
        cached_data = st.session_state.location_cache[location_key]
        st.info("🔄 Using cached recommendation (valid for 10 minutes)")
        return cached_data
    
    # Compute new recommendation
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
    
    # Get crop recommendation
    recommended_crop = model.predict(input_features)[0]
    prediction_proba = model.predict_proba(input_features)[0]
    confidence = max(prediction_proba) * 100
    
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
    
    # Cache the result
    st.session_state.location_cache[location_key] = result_data
    st.session_state.last_update[location_key] = datetime.now()
    
    st.success("✨ New recommendation computed and cached!")
    return result_data

# Translate text function
def translate_text(text, dest_language):
    try:
        if dest_language == 'hi':
            return translator.translate(text, dest='hi').text
        elif dest_language == 'te':
            return translator.translate(text, dest='te').text
        else:
            return text
    except Exception as e:
        st.warning(f"Translation error: {e}")
        return text

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

# Main app function
def main():
    # Load model and data
    model = load_model()
    soil_data, market_prices, pesticides = load_data()
    
    if model is None or soil_data is None:
        st.stop()
    
    # Sidebar configuration
    st.sidebar.header("🔧 Configuration")
    
    # API Key input
    api_key = st.sidebar.text_input(
        "WeatherAPI Key",
        type="password",
        help="Get your free API key from weatherapi.com"
    )
    
    # Language selection
    language_options = {
        'English': 'en',
        'Hindi': 'hi',
        'Telugu': 'te'
    }
    selected_language = st.sidebar.selectbox(
        "Select Language",
        list(language_options.keys())
    )
    lang_code = language_options[selected_language]
    
    # Cache management
    st.sidebar.subheader("🗂️ Cache Management")
    if st.sidebar.button("Clear Cache"):
        st.session_state.location_cache = {}
        st.session_state.last_update = {}
        st.sidebar.success("Cache cleared!")
    
    # Show cache status
    if st.session_state.location_cache:
        st.sidebar.write(f"**Cached Locations:** {len(st.session_state.location_cache)}")
        for loc in st.session_state.location_cache.keys():
            last_update = st.session_state.last_update.get(loc, datetime.now())
            time_diff = datetime.now() - last_update
            if time_diff < timedelta(minutes=10):
                st.sidebar.write(f"• {loc.title()} ✅")
            else:
                st.sidebar.write(f"• {loc.title()} ⏰")
    
    # Main content
    st.title("🌾 Smart Farming Assistant")
    st.subheader("Helping farmers increase income and avoid losses - Supporting SDG Goal 2: Zero Hunger")
    
    # Location input
    location = st.text_input(
        "Enter your city or district name:",
        placeholder="e.g., Mumbai, Delhi, Hyderabad, Vijayawada"
    )
    
    if location and api_key:
        with st.spinner("Fetching data and generating recommendations..."):
            # Fetch weather data
            weather_data = get_weather_data(location, api_key)
            
            if weather_data:
                # Get recommendation (cached or computed)
                result = get_recommendation(location, weather_data, model)
                
                # Extract results
                temperature = result['temperature']
                humidity = result['humidity']
                weather_desc = result['weather_desc']
                soil_info = result['soil_info']
                recommended_crop = result['recommended_crop']
                confidence = result['confidence']
                
                # Display results in sidebar
                st.sidebar.subheader("🎯 Crop Recommendation")
                
                # Display recommended crop
                crop_text = f"**Recommended Crop:** {recommended_crop.title()}"
                confidence_text = f"**Confidence:** {confidence:.1f}%"
                
                if lang_code != 'en':
                    crop_text = translate_text(crop_text, lang_code)
                    confidence_text = translate_text(confidence_text, lang_code)
                
                st.sidebar.markdown(crop_text)
                st.sidebar.markdown(confidence_text)
                
                # Get pesticide information
                pesticide_info = pesticides[pesticides['Crop'].str.lower() == recommended_crop.lower()]
                
                if not pesticide_info.empty:
                    st.sidebar.subheader("🧪 Pesticide Recommendation")
                    pesticide_text = f"""
                    **Type:** {pesticide_info.iloc[0]['Type']}
                    **Amount:** {pesticide_info.iloc[0]['Amount']}
                    **Application:** {pesticide_info.iloc[0]['Application']}
                    """
                    
                    if lang_code != 'en':
                        pesticide_text = translate_text(pesticide_text, lang_code)
                    
                    st.sidebar.markdown(pesticide_text)
                
                # Get market price information
                price_info = market_prices[market_prices['Crop'].str.lower() == recommended_crop.lower()]
                
                if not price_info.empty:
                    st.sidebar.subheader("💰 Market Price Information")
                    price_text = f"""
                    **Current Price:** ₹{price_info.iloc[0]['Price']} per {price_info.iloc[0]['Unit']}
                    **Market Trend:** {price_info.iloc[0]['Trend']}
                    **Last Updated:** {price_info.iloc[0]['Last_Updated']}
                    """
                    
                    if lang_code != 'en':
                        price_text = translate_text(price_text, lang_code)
                    
                    st.sidebar.markdown(price_text)
                
                # Display main content
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🌤️ Current Weather Conditions")
                    weather_text = f"""
                    **Location:** {location.title()}
                    **Temperature:** {temperature}°C
                    **Humidity:** {humidity}%
                    **Condition:** {weather_desc.title()}
                    """
                    
                    if lang_code != 'en':
                        weather_text = translate_text(weather_text, lang_code)
                    
                    st.markdown(weather_text)
                
                with col2:
                    st.subheader("🌱 Soil Conditions")
                    soil_text = f"""
                    **Nitrogen (N):** {soil_info['N']}
                    **Phosphorus (P):** {soil_info['P']}
                    **Potassium (K):** {soil_info['K']}
                    **pH Level:** {soil_info['pH']}
                    **Rainfall:** {soil_info['rainfall']}mm
                    """
                    
                    if lang_code != 'en':
                        soil_text = translate_text(soil_text, lang_code)
                    
                    st.markdown(soil_text)
                
                # Display crop insights
                display_crop_insights(recommended_crop, lang_code)
                
                # Analysis Summary
                st.subheader("📊 Analysis Summary")
                
                summary_text = f"""
                Based on the current weather conditions in {location} and soil analysis, 
                **{recommended_crop.title()}** is the most suitable crop for cultivation. 
                The recommendation is made with {confidence:.1f}% confidence based on:
                
                - Temperature: {temperature}°C
                - Humidity: {humidity}%
                - Soil nutrients and pH levels
                - Expected rainfall patterns
                
                This recommendation aligns with sustainable farming practices and can help 
                maximize yield while minimizing risks.
                """
                
                if lang_code != 'en':
                    summary_text = translate_text(summary_text, lang_code)
                
                st.markdown(summary_text)
                
                # Farming Tips
                st.subheader("💡 Farming Tips")
                tips_text = f"""
                - Monitor weather conditions regularly
                - Test soil pH periodically
                - Use recommended pesticides judiciously
                - Keep track of market prices for better profits
                - Consider crop rotation for soil health
                - Maintain proper irrigation schedules
                - Store produce properly to avoid post-harvest losses
                """
                
                if lang_code != 'en':
                    tips_text = translate_text(tips_text, lang_code)
                
                st.markdown(tips_text)
            
            else:
                st.error("Unable to fetch weather data. Please check your location and API key.")
    
    elif location and not api_key:
        st.warning("Please enter your WeatherAPI key in the sidebar.")
    
    # Footer
    st.markdown("---")
    footer_text = """
    **Smart Farming Assistant** - Supporting SDG Goal 2: Zero Hunger
    
    This app helps farmers make informed decisions about crop selection based on 
    real-time weather and soil conditions, ultimately helping to increase income 
    and reduce agricultural losses.
    
    💡 **Pro Tip:** Results are cached for 10 minutes to ensure consistency for the same location.
    """
    
    if lang_code != 'en':
        footer_text = translate_text(footer_text, lang_code)
    
    st.markdown(footer_text)

if __name__ == "__main__":
    main()
