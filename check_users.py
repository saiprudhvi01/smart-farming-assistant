#!/usr/bin/env python3
from database import DatabaseManager

db = DatabaseManager()
users = db.get_all_users()

print("Available users:")
for user in users:
    print(f"{user['role']}: {user['email']}")

# Test agent authentication
agent_user = db.authenticate_user("agent@smartfarm.com", "agent123")
print("\nAgent authentication test:")
if agent_user:
    print(f"✅ Success: {agent_user['name']} ({agent_user['role']})")
else:
    print("❌ Failed")
