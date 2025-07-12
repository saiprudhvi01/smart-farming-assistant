from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Twilio credentials and configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_SMS_NUMBER = os.getenv('TWILIO_SMS_NUMBER')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Simple session storage (in production, use a database)
user_sessions = {}

# Location-based crop recommendations
def get_crop_recommendation(location):
    location_lower = location.lower()
    location_crops = {
        'mumbai': 'Rice - Best for coastal climate and monsoon season',
        'delhi': 'Wheat - Suitable for northern plains and winter season',
        'hyderabad': 'Cotton - Ideal for Deccan plateau and black soil',
        'chennai': 'Sugarcane - Good for tropical climate and water availability',
        'bangalore': 'Tomato - Perfect for moderate climate and hill stations',
        'kolkata': 'Rice - Excellent for delta region and high humidity',
        'pune': 'Sugarcane - Great for western ghats and adequate rainfall',
        'ahmedabad': 'Cotton - Best for semi-arid climate and cotton belt',
        'jaipur': 'Barley - Suitable for arid climate and drought resistance',
        'lucknow': 'Wheat - Ideal for fertile plains and winter crops',
        'nashik': 'Grapes - Perfect for wine production and climate',
        'coimbatore': 'Maize - Good for hill climate and food processing'
    }

    for city, crop in location_crops.items():
        if city in location_lower:
            return crop

    return 'Wheat - General recommendation for most Indian regions'

# Market price fetcher
def get_market_prices():
    try:
        market_data = pd.read_csv('data/market_prices.csv')
        prices = []
        for _, row in market_data.iterrows():
            prices.append(f"{row['Crop']}: Rs{row['Price']}/quintal")
        return "\n".join(prices)
    except:
        return ("Current Market Prices:\n"
                "Wheat: Rs2000/quintal\nRice: Rs1800/quintal\n"
                "Maize: Rs1500/quintal\nCotton: Rs5200/quintal\n"
                "Sugarcane: Rs280/quintal\nTomato: Rs3000/quintal\n"
                "Potato: Rs2200/quintal\nOnion: Rs1800/quintal")

# Shared SMS and WhatsApp chatbot logic
def handle_user_message(incoming_msg, sender):
    incoming_msg = incoming_msg.strip().lower()

    if sender not in user_sessions:
        user_sessions[sender] = {'state': 'start', 'data': {}}

    session = user_sessions[sender]

    if session['state'] == 'start' or incoming_msg in ['hi', 'hello', 'start', 'help']:
        reply = "Welcome to the Crop Assistant\nReply with 1 for crop prediction or 2 for market trends"
        session['state'] = 'menu'

    elif session['state'] == 'menu':
        if incoming_msg == "1":
            reply = "Please provide your location (e.g., Mumbai, Delhi, Hyderabad)"
            session['state'] = 'waiting_location'
        elif incoming_msg == "2":
            reply = get_market_prices()
            session['state'] = 'menu'
        else:
            reply = "Invalid option. Reply with 1 for crop prediction or 2 for market trends"

    elif session['state'] == 'waiting_location':
        if len(incoming_msg) > 2:
            recommendation = get_crop_recommendation(incoming_msg)
            reply = (f"Recommended crop for {incoming_msg.title()}:\n{recommendation}\n\n"
                     "Reply with 1 for another prediction or 2 for market trends")
            session['state'] = 'menu'
        else:
            reply = "Please provide a valid location name"

    else:
        reply = "Welcome to the Crop Assistant\nReply with 1 for crop prediction or 2 for market trends"
        session['state'] = 'menu'

    user_sessions[sender] = session
    return reply

@app.route("/sms", methods=["GET", "POST"])
def sms_reply():
    if request.method == "GET":
        return "SMS endpoint is live. Please send a POST request with message."

    incoming_msg = request.values.get("Body", "")
    sender = request.values.get("From", "")
    response_text = handle_user_message(incoming_msg, sender)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(response_text)
    return str(resp)

@app.route("/whatsapp", methods=["GET", "POST"])
def whatsapp_reply():
    if request.method == "GET":
        return "WhatsApp endpoint is live. Please send a POST request with message."

    incoming_msg = request.values.get("Body", "")
    sender = request.values.get("From", "")
    response_text = handle_user_message(incoming_msg, sender)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(response_text)
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "Crop Assistant Chatbot is running!"

if __name__ == "__main__":
    print("Starting Crop Assistant Chatbot...")
    print("SMS Webhook: http://localhost:5000/sms")
    print("WhatsApp Webhook: http://localhost:5000/whatsapp")
    app.run(host="0.0.0.0", port=5000, debug=True)
