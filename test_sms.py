#!/usr/bin/env python3
"""
Test script to verify SMS functionality
"""

from twilio.rest import Client
import sys
import os

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

def test_sms_functionality():
    """Test SMS sending functionality"""
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Test phone number (replace with your actual phone number)
        test_phone = input("Enter your phone number (with country code, e.g., +919876543210): ")
        
        # Test message
        test_message = """🌾 CROP RECOMMENDATION TEST

📍 Location: Test Location
🌱 Recommended Crop: Rice
📊 Confidence: 95.0%

🌡️ Temperature: 28°C
💧 Humidity: 75%

✨ This is a test message from Smart Farming Assistant.

🤖 Smart Farming Assistant"""
        
        print("Sending test SMS...")
        
        # Send SMS
        message = client.messages.create(
            body=test_message,
            from_=TWILIO_PHONE_NUMBER,
            to=test_phone
        )
        
        print(f"✅ SMS sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        print(f"To: {message.to}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending SMS: {str(e)}")
        return False

if __name__ == "__main__":
    print("🤖 Smart Farming Assistant - SMS Test")
    print("=" * 50)
    
    result = test_sms_functionality()
    
    if result:
        print("\n✅ SMS functionality is working correctly!")
        print("You can now use the SMS feature in your main application.")
    else:
        print("\n❌ SMS functionality test failed.")
        print("Please check your Twilio credentials and phone number.")
