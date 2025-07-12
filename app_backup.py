import streamlit as st
import pandas as pd
import requests
import pickle
import os
from googletrans import Translator
import numpy as np

# Initialize translator
translator = Translator()

# Set page configuration
st.set_page_config(
    page_title="Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load pre-trained model
@st.cache_resource
def load_model():
    try:
        with open('crop_recommendation_model.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error("Model file not found. Please run model.py first to train the model.")
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

# Function to get soil data (dummy implementation)
def get_soil_data(location, soil_data):
    return soil_data.sample(1).iloc[0]

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

# Main app function
def main():
    model = load_model()
    soil_data, market_prices, pesticides = load_data()
    
    if model is None or soil_data is None:
        st.stop()

    st.sidebar.header("Configuration")

    api_key = st.sidebar.text_input(
        "WeatherAPI Key",
        type="password",
        help="Get your free API key from weatherapi.com"
    )

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

    st.title("🌾 Smart Farming Assistant")
    st.subheader("Helping farmers increase income and avoid losses - Supporting SDG Goal 2: Zero Hunger")

    location = st.text_input(
        "Enter your city or district name:",
        placeholder="e.g., Mumbai, Delhi, Hyderabad"
    )

    if location and api_key:
        with st.spinner("Fetching data and generating recommendations..."):
            weather_data = get_weather_data(location, api_key)

            if weather_data:
                temperature = weather_data['current']['temp_c']
                humidity = weather_data['current']['humidity']
                weather_desc = weather_data['current']['condition']['text']

                soil_info = get_soil_data(location, soil_data)

                input_features = np.array([[temperature, humidity, soil_info['N'], soil_info['P'],
                                            soil_info['K'], soil_info['pH'], soil_info['rainfall']]])

                recommended_crop = model.predict(input_features)[0]
                prediction_proba = model.predict_proba(input_features)[0]
                confidence = max(prediction_proba) * 100

                st.sidebar.subheader("🎯 Crop Recommendation")
                crop_text = f"**Recommended Crop:** {recommended_crop.title()}"
                confidence_text = f"**Confidence:** {confidence:.1f}%"

                if lang_code != 'en':
                    crop_text = translate_text(crop_text, lang_code)
                    confidence_text = translate_text(confidence_text, lang_code)

                st.sidebar.markdown(crop_text)
                st.sidebar.markdown(confidence_text)

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

                st.subheader("💡 Farming Tips")
                tips_text = """
                - Monitor weather conditions regularly
                - Test soil pH periodically
                - Use recommended pesticides judiciously
                - Keep track of market prices for better profits
                - Consider crop rotation for soil health
                """
                if lang_code != 'en':
                    tips_text = translate_text(tips_text, lang_code)
                st.markdown(tips_text)

            else:
                st.error("Unable to fetch weather data. Please check your location and API key.")

    elif location and not api_key:
        st.warning("Please enter your WeatherAPI key in the sidebar.")

    st.markdown("---")
    footer_text = """
    **Smart Farming Assistant** - Supporting SDG Goal 2: Zero Hunger
    
    This app helps farmers make informed decisions about crop selection based on 
    real-time weather and soil conditions, ultimately helping to increase income 
    and reduce agricultural losses.
    """
    if lang_code != 'en':
        footer_text = translate_text(footer_text, lang_code)
    st.markdown(footer_text)

if __name__ == "__main__":
    main()
