#!/usr/bin/env python3
"""
Simple SMS test for Twilio troubleshooting
"""

from twilio.rest import Client
import os

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

def check_twilio_account():
    """Check Twilio account status"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Check account info
        account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        print(f"✅ Account Status: {account.status}")
        print(f"📱 Account SID: {account.sid}")
        
        # Check balance
        balance = client.balance.fetch()
        print(f"💰 Account Balance: {balance.balance} {balance.currency}")
        
        return client
        
    except Exception as e:
        print(f"❌ Account check failed: {e}")
        return None

def send_test_sms(client, phone_number):
    """Send a simple test SMS"""
    try:
        # Simple test message
        test_message = "Test from Smart Farming Assistant: Rice is recommended for your farm!"
        
        print(f"📱 Sending test SMS to: {phone_number}")
        
        # Send SMS
        message = client.messages.create(
            body=test_message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        print(f"📋 Message SID: {message.sid}")
        print(f"📊 Status: {message.status}")
        
        # Wait and check status
        import time
        time.sleep(3)
        
        # Fetch updated message
        updated_message = client.messages(message.sid).fetch()
        print(f"📊 Updated Status: {updated_message.status}")
        
        if updated_message.error_code:
            print(f"❌ Error Code: {updated_message.error_code}")
            print(f"❌ Error Message: {updated_message.error_message}")
            
            if updated_message.error_code == 21614:
                print("")
                print("🚫 PHONE NUMBER NOT VERIFIED!")
                print("📋 SOLUTION:")
                print("1. Go to https://console.twilio.com/")
                print("2. Navigate: Phone Numbers → Manage → Verified Caller IDs")
                print("3. Click 'Add a new number'")
                print("4. Enter your number with country code: +919876543210")
                print("5. Verify via SMS or call")
                print("")
        else:
            if updated_message.status in ['sent', 'delivered', 'queued']:
                print("✅ SMS sent successfully! Check your phone.")
            else:
                print(f"⚠️ SMS status: {updated_message.status}")
        
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ SMS sending failed: {error_str}")
        
        if "unverified" in error_str.lower():
            print("")
            print("🚫 PHONE NUMBER NOT VERIFIED!")
            print("📋 SOLUTION:")
            print("1. Go to https://console.twilio.com/")
            print("2. Navigate: Phone Numbers → Manage → Verified Caller IDs")
            print("3. Click 'Add a new number'")
            print("4. Enter your number: +919876543210")
            print("5. Verify via SMS or call")
            print("")
        
        return False

def main():
    """Main test function"""
    print("🧪 Smart Farming Assistant - SMS Test")
    print("=" * 50)
    
    # Check account first
    client = check_twilio_account()
    if not client:
        return
    
    print("")
    
    # Get phone number from user
    phone = input("Enter your phone number (with country code, e.g., +919876543210): ")
    
    if not phone.startswith('+'):
        phone = '+91' + phone
    
    print("")
    
    # Send test SMS
    success = send_test_sms(client, phone)
    
    print("")
    if success:
        print("✅ Test completed! Check your phone for the SMS.")
    else:
        print("❌ Test failed. Please follow the troubleshooting steps above.")

if __name__ == "__main__":
    main()
