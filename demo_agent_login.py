#!/usr/bin/env python3
"""
Demo script to show agent login functionality
"""

from database import DatabaseManager

def demo_agent_functionality():
    """Demonstrate agent functionality"""
    print("🤝 Agent Login Functionality Demo")
    print("=" * 50)
    
    # Initialize database
    db_manager = DatabaseManager()
    
    # Show available accounts
    print("📋 Available Test Accounts:")
    print("1. Admin: admin@smartfarm.com / admin123")
    print("2. Agent: agent@smartfarm.com / agent123")
    print()
    
    # Test agent authentication
    print("🔐 Testing Agent Authentication...")
    agent_email = "agent@smartfarm.com"
    agent_password = "agent123"
    
    agent_user = db_manager.authenticate_user(agent_email, agent_password)
    if agent_user:
        print(f"✅ Agent login successful!")
        print(f"   Name: {agent_user['name']}")
        print(f"   Role: {agent_user['role']}")
        print(f"   Email: {agent_user['email']}")
        print(f"   Phone: {agent_user['phone']}")
    else:
        print("❌ Agent login failed!")
        return
    
    print()
    
    # Create a sample crop listing for a farmer
    print("🌾 Creating Sample Crop Listing for Farmer...")
    listing_id = db_manager.create_crop_listing(
        farmer_id=0,  # Dummy farmer ID for agent listings
        crop_name="wheat",
        quantity=500,
        expected_price=25.0,
        description="High quality wheat, freshly harvested",
        location="Village ABC, District XYZ, State",
        farmer_name="Raman Singh",
        farmer_phone="+919876543210",
        agent_id=agent_user['id']
    )
    
    if listing_id:
        print(f"✅ Crop listing created successfully! ID: {listing_id}")
        print("   Crop: Wheat")
        print("   Quantity: 500 kg")
        print("   Price: ₹25.0/kg")
        print("   Farmer: Raman Singh")
        print("   Farmer Phone: +919876543210")
        print(f"   Agent: {agent_user['name']}")
    else:
        print("❌ Failed to create crop listing!")
        return
    
    print()
    
    # Get agent listings
    print("📋 Retrieving Agent Listings...")
    agent_listings = db_manager.get_agent_listings(agent_user['id'])
    
    if agent_listings:
        print(f"✅ Found {len(agent_listings)} listing(s) created by this agent:")
        for listing in agent_listings:
            print(f"   - {listing['crop_name'].title()}: {listing['quantity']} kg @ ₹{listing['expected_price']}/kg")
            print(f"     Farmer: {listing['farmer_name']} ({listing['farmer_phone']})")
            print(f"     Location: {listing['location']}")
            print(f"     Status: {listing['status']}")
    else:
        print("❌ No listings found for this agent!")
    
    print()
    
    # Show dashboard stats including agents
    print("📊 Dashboard Statistics:")
    stats = db_manager.get_dashboard_stats()
    print(f"   Total Farmers: {stats['total_farmers']}")
    print(f"   Total Buyers: {stats['total_buyers']}")
    print(f"   Total Agents: {stats['total_agents']}")
    print(f"   Total Admins: {stats['total_admins']}")
    print(f"   Active Listings: {stats['active_listings']}")
    print(f"   Total Transactions: {stats['total_transactions']}")
    
    print()
    print("🎉 Agent functionality demo completed successfully!")
    print()
    print("🌟 Key Features Implemented:")
    print("   ✅ Agent role added to user registration")
    print("   ✅ Agent dashboard with all farmer capabilities")
    print("   ✅ Agent can create crop listings for farmers")
    print("   ✅ Agent must collect farmer name and phone number")
    print("   ✅ Agent listings track both farmer and agent information")
    print("   ✅ Admin dashboard shows agent statistics")
    print("   ✅ Database schema updated to support agent functionality")
    print()
    print("🚀 To use the agent login in the web app:")
    print("   1. Run: streamlit run app.py")
    print("   2. Click 'Register' and select 'Agent' role")
    print("   3. Or login with: agent@smartfarm.com / agent123")
    print("   4. Access the 'Sell for Farmers' tab to list crops")

if __name__ == "__main__":
    demo_agent_functionality()
