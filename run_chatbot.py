#!/usr/bin/env python3
"""
Startup script for Twilio Chatbot with ngrok tunneling
"""

import subprocess
import time
import threading
from pyngrok import ngrok
import os

def start_ngrok():
    """Start ngrok tunnel"""
    print("🚀 Starting ngrok tunnel...")
    
    # Create ngrok tunnel
    public_url = ngrok.connect(5000)
    print(f"🌐 Public URL: {public_url}")
    print(f"📱 SMS Webhook: {public_url}/sms")
    print(f"💬 WhatsApp Webhook: {public_url}/whatsapp")
    
    # Keep ngrok running
    try:
        ngrok_process = ngrok.get_ngrok_process()
        print("✅ ngrok tunnel is running...")
        return public_url
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None

def start_flask_app():
    """Start Flask application"""
    print("🌾 Starting Crop Assistant Chatbot...")
    os.system("python twilio_chatbot.py")

def main():
    """Main function to start both ngrok and Flask"""
    print("🤖 Twilio Crop Assistant Chatbot Setup")
    print("=" * 50)
    
    # Start ngrok tunnel
    public_url = start_ngrok()
    
    if public_url:
        print("\n📋 SETUP INSTRUCTIONS:")
        print("1. Go to Twilio Console (https://console.twilio.com/)")
        print("2. Configure SMS webhook:")
        print(f"   - URL: {public_url}/sms")
        print("   - Method: POST")
        print("3. Configure WhatsApp webhook:")
        print(f"   - URL: {public_url}/whatsapp")
        print("   - Method: POST")
        print("\n⚡ Starting Flask application...")
        
        # Start Flask app in a separate thread
        flask_thread = threading.Thread(target=start_flask_app)
        flask_thread.daemon = True
        flask_thread.start()
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            ngrok.disconnect(public_url)
            ngrok.kill()
    else:
        print("❌ Failed to start ngrok tunnel")

if __name__ == "__main__":
    main()
