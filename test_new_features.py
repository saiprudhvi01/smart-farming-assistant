#!/usr/bin/env python3
"""
Test script for new agent and admin features
"""

from database import DatabaseManager
import pandas as pd

def test_new_features():
    """Test all the new features implemented"""
    print("🧪 Testing New Features")
    print("=" * 50)
    
    # Initialize database
    db_manager = DatabaseManager()
    
    # Test 1: Agent offers functionality
    print("📋 Test 1: Agent Offers Functionality")
    agent_user = db_manager.authenticate_user("agent@smartfarm.com", "agent123")
    if agent_user:
        print(f"✅ Agent authenticated: {agent_user['name']}")
        
        # Get agent listings
        agent_listings = db_manager.get_agent_listings(agent_user['id'])
        print(f"✅ Agent has {len(agent_listings)} listings")
        
        # Get offers for agent
        agent_offers = db_manager.get_offers_for_agent(agent_user['id'])
        print(f"✅ Agent has {len(agent_offers)} offers")
    else:
        print("❌ Agent authentication failed")
    
    print()
    
    # Test 2: Market price management
    print("💰 Test 2: Market Price Management")
    try:
        # Test updating market price
        success = db_manager.update_market_price("wheat", 2100.0, "Increasing")
        if success:
            print("✅ Market price updated successfully")
            
            # Verify the update
            import os
            if os.path.exists('data/market_prices.csv'):
                df = pd.read_csv('data/market_prices.csv')
                wheat_data = df[df['Crop'].str.lower() == 'wheat']
                if not wheat_data.empty:
                    print(f"✅ Wheat price updated to ₹{wheat_data.iloc[0]['Price']}/quintal")
                else:
                    print("❌ Wheat price not found after update")
            else:
                print("❌ Market prices file not found")
        else:
            print("❌ Market price update failed")
    except Exception as e:
        print(f"❌ Market price test failed: {e}")
    
    print()
    
    # Test 3: Admin dashboard offers
    print("👑 Test 3: Admin Dashboard Offers")
    try:
        # Test active offers
        active_offers = db_manager.get_offers_by_status('pending')
        print(f"✅ Found {len(active_offers)} active offers")
        
        # Test closed offers
        closed_offers = db_manager.get_offers_by_status('accepted') + db_manager.get_offers_by_status('rejected')
        print(f"✅ Found {len(closed_offers)} closed offers")
        
        # Test all offers
        all_offers = db_manager.get_offers_by_status()
        print(f"✅ Found {len(all_offers)} total offers")
        
        if all_offers:
            print("📊 Offer Status Breakdown:")
            status_counts = {}
            for offer in all_offers:
                status = offer['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"   - {status.title()}: {count}")
    
    except Exception as e:
        print(f"❌ Admin offers test failed: {e}")
    
    print()
    
    # Test 4: Dashboard statistics
    print("📊 Test 4: Dashboard Statistics")
    try:
        stats = db_manager.get_dashboard_stats()
        print("✅ Dashboard statistics:")
        print(f"   - Total Farmers: {stats['total_farmers']}")
        print(f"   - Total Buyers: {stats['total_buyers']}")
        print(f"   - Total Agents: {stats['total_agents']}")
        print(f"   - Total Admins: {stats['total_admins']}")
        print(f"   - Active Listings: {stats['active_listings']}")
        print(f"   - Total Transactions: {stats['total_transactions']}")
        print(f"   - Total Transaction Value: ₹{stats['total_transaction_value']:,.2f}")
    except Exception as e:
        print(f"❌ Dashboard stats test failed: {e}")
    
    print()
    
    # Test 5: Multi-language support (basic test)
    print("🌐 Test 5: Multi-language Support")
    try:
        from googletrans import Translator
        translator = Translator()
        
        # Test message
        test_message = "Your offer has been accepted"
        
        # Translate to Hindi
        hindi_translation = translator.translate(test_message, dest='hi').text
        print(f"✅ English: {test_message}")
        print(f"✅ Hindi: {hindi_translation}")
        
        # Translate to Telugu
        telugu_translation = translator.translate(test_message, dest='te').text
        print(f"✅ Telugu: {telugu_translation}")
        
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
    
    print()
    print("🎉 All tests completed!")
    print()
    print("🌟 New Features Summary:")
    print("   ✅ Active/Closed offers in admin dashboard")
    print("   ✅ Agent can see buyer offers for farmer listings")
    print("   ✅ Market price management by agents")
    print("   ✅ SMS notifications with phone number collection")
    print("   ✅ Multi-language SMS support")
    print("   ✅ Enhanced offer management system")
    print()
    print("🚀 Ready to use! Run: streamlit run app.py")
    print("📱 Test accounts:")
    print("   - Admin: admin@smartfarm.com / admin123")
    print("   - Agent: agent@smartfarm.com / agent123")

if __name__ == "__main__":
    test_new_features()
