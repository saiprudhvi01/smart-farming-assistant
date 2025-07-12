import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path: str = "smart_farming.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'farmer', 'buyer', 'agent')),
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Crop listings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crop_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER NOT NULL,
                crop_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                expected_price REAL NOT NULL,
                description TEXT,
                location TEXT,
                status TEXT DEFAULT 'available' CHECK (status IN ('available', 'sold', 'cancelled')),
                farmer_name TEXT,
                farmer_phone TEXT,
                agent_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farmer_id) REFERENCES users (id),
                FOREIGN KEY (agent_id) REFERENCES users (id)
            )
        ''')
        
        # Buyer offers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buyer_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER NOT NULL,
                crop_listing_id INTEGER,
                crop_name TEXT NOT NULL,
                offer_price REAL NOT NULL,
                quantity_wanted REAL NOT NULL,
                notes TEXT,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'cancelled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (buyer_id) REFERENCES users (id),
                FOREIGN KEY (crop_listing_id) REFERENCES crop_listings (id)
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER NOT NULL,
                farmer_id INTEGER NOT NULL,
                crop_listing_id INTEGER NOT NULL,
                crop_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                price_per_unit REAL NOT NULL,
                total_amount REAL NOT NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed' CHECK (status IN ('completed', 'pending', 'cancelled')),
                notes TEXT,
                FOREIGN KEY (buyer_id) REFERENCES users (id),
                FOREIGN KEY (farmer_id) REFERENCES users (id),
                FOREIGN KEY (crop_listing_id) REFERENCES crop_listings (id)
            )
        ''')
        
        # User sessions table for session management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create default admin user if doesn't exist
        self.create_default_admin()
        self.create_default_agent()
        self.create_sample_data()
    
    def create_default_admin(self):
        """Create a default admin user"""
        admin_email = "admin@smartfarm.com"
        admin_password = "admin123"
        
        if not self.get_user_by_email(admin_email):
            self.create_user(
                name="System Administrator",
                email=admin_email,
                password=admin_password,
                role="admin",
                phone="9999999999",
                address="System Admin"
            )
            print(f"Default admin created: {admin_email} / {admin_password}")
    
    def create_default_agent(self):
        """Create a default agent user"""
        agent_email = "agent@smartfarm.com"
        agent_password = "agent123"
        
        if not self.get_user_by_email(agent_email):
            self.create_user(
                name="Farm Agent",
                email=agent_email,
                password=agent_password,
                role="agent",
                phone="8888888888",
                address="Agent Office"
            )
            print(f"Default agent created: {agent_email} / {agent_password}")
    
    def create_sample_data(self):
        """Create sample data for demonstration (only if no data exists)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if sample data already exists
        cursor.execute('SELECT COUNT(*) FROM crop_listings')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return  # Data already exists
        
        try:
            # Create sample farmers
            farmer_users = [
                ("Ramesh Kumar", "farmer1@test.com", "farmer123", "farmer", "+919876543210", "Village Ramgarh, Rajasthan"),
                ("Sunita Devi", "farmer2@test.com", "farmer123", "farmer", "+919876543211", "Village Khetri, Haryana"),
                ("Mohan Singh", "farmer3@test.com", "farmer123", "farmer", "+919876543212", "Village Bhiwani, Punjab")
            ]
            
            farmer_ids = []
            for farmer in farmer_users:
                farmer_id = self.create_user(*farmer)
                if farmer_id:
                    farmer_ids.append(farmer_id)
            
            # Create sample buyers
            buyer_users = [
                ("Anil Traders", "buyer1@test.com", "buyer123", "buyer", "+919876543220", "Mumbai, Maharashtra"),
                ("Grain Merchants", "buyer2@test.com", "buyer123", "buyer", "+919876543221", "Delhi, India")
            ]
            
            for buyer in buyer_users:
                self.create_user(*buyer)
            
            # Create sample crop listings
            if farmer_ids:
                sample_listings = [
                    (farmer_ids[0], "wheat", 1000, 20.0, "Premium quality wheat, organic", "Ramgarh, Rajasthan"),
                    (farmer_ids[0], "rice", 800, 25.0, "Basmati rice, excellent quality", "Ramgarh, Rajasthan"),
                    (farmer_ids[1] if len(farmer_ids) > 1 else farmer_ids[0], "cotton", 500, 55.0, "High quality cotton", "Khetri, Haryana"),
                    (farmer_ids[2] if len(farmer_ids) > 2 else farmer_ids[0], "sugarcane", 2000, 28.0, "Fresh sugarcane", "Bhiwani, Punjab"),
                    (farmer_ids[0], "tomato", 300, 40.0, "Fresh tomatoes", "Ramgarh, Rajasthan")
                ]
                
                for listing in sample_listings:
                    self.create_crop_listing(*listing)
            
            print("Sample data created successfully!")
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
        finally:
            conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, name: str, email: str, password: str, role: str, phone: str = None, address: str = None) -> Optional[int]:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, role, phone, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, password_hash, role, phone, address))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, name, email, role, phone, address, is_active
            FROM users
            WHERE email = ? AND password_hash = ? AND is_active = 1
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'role': user[3],
                'phone': user[4],
                'address': user[5],
                'is_active': user[6]
            }
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, role, phone, address, is_active
            FROM users
            WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'role': user[3],
                'phone': user[4],
                'address': user[5],
                'is_active': user[6]
            }
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, role, phone, address, is_active
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'role': user[3],
                'phone': user[4],
                'address': user[5],
                'is_active': user[6]
            }
        return None
    
    def create_crop_listing(self, farmer_id: int, crop_name: str, quantity: float, 
                          expected_price: float, description: str = None, location: str = None,
                          farmer_name: str = None, farmer_phone: str = None, agent_id: int = None) -> Optional[int]:
        """Create a new crop listing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO crop_listings (farmer_id, crop_name, quantity, expected_price, description, location, farmer_name, farmer_phone, agent_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (farmer_id, crop_name, quantity, expected_price, description, location, farmer_name, farmer_phone, agent_id))
            
            listing_id = cursor.lastrowid
            conn.commit()
            return listing_id
        except Exception as e:
            print(f"Error creating crop listing: {e}")
            return None
        finally:
            conn.close()
    
    def get_crop_listings(self, status: str = 'available') -> List[Dict[str, Any]]:
        """Get all crop listings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cl.id, cl.farmer_id, 
                   COALESCE(cl.farmer_name, u.name) as farmer_name, 
                   COALESCE(cl.farmer_phone, u.phone) as farmer_phone, 
                   cl.crop_name, cl.quantity, cl.expected_price, cl.description, 
                   cl.location, cl.status, cl.created_at, cl.updated_at, cl.agent_id
            FROM crop_listings cl
            LEFT JOIN users u ON cl.farmer_id = u.id
            WHERE cl.status = ?
            ORDER BY cl.created_at DESC
        ''', (status,))
        
        listings = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': listing[0],
                'farmer_id': listing[1],
                'farmer_name': listing[2],
                'farmer_phone': listing[3],
                'crop_name': listing[4],
                'quantity': listing[5],
                'expected_price': listing[6],
                'description': listing[7],
                'location': listing[8],
                'status': listing[9],
                'created_at': listing[10],
                'updated_at': listing[11],
                'agent_id': listing[12]
            }
            for listing in listings
        ]
    
    def get_farmer_listings(self, farmer_id: int) -> List[Dict[str, Any]]:
        """Get crop listings for a specific farmer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, crop_name, quantity, expected_price, description, location, status, created_at
            FROM crop_listings
            WHERE farmer_id = ?
            ORDER BY created_at DESC
        ''', (farmer_id,))
        
        listings = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': listing[0],
                'crop_name': listing[1],
                'quantity': listing[2],
                'expected_price': listing[3],
                'description': listing[4],
                'location': listing[5],
                'status': listing[6],
                'created_at': listing[7]
            }
            for listing in listings
        ]
    
    def get_agent_listings(self, agent_id: int) -> List[Dict[str, Any]]:
        """Get crop listings created by a specific agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, crop_name, quantity, expected_price, description, location, status, 
                   created_at, farmer_name, farmer_phone
            FROM crop_listings
            WHERE agent_id = ?
            ORDER BY created_at DESC
        ''', (agent_id,))
        
        listings = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': listing[0],
                'crop_name': listing[1],
                'quantity': listing[2],
                'expected_price': listing[3],
                'description': listing[4],
                'location': listing[5],
                'status': listing[6],
                'created_at': listing[7],
                'farmer_name': listing[8],
                'farmer_phone': listing[9]
            }
            for listing in listings
        ]
    
    def create_buyer_offer(self, buyer_id: int, crop_listing_id: int, crop_name: str,
                          offer_price: float, quantity_wanted: float, notes: str = None) -> Optional[int]:
        """Create a new buyer offer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO buyer_offers (buyer_id, crop_listing_id, crop_name, offer_price, quantity_wanted, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (buyer_id, crop_listing_id, crop_name, offer_price, quantity_wanted, notes))
            
            offer_id = cursor.lastrowid
            conn.commit()
            return offer_id
        except Exception as e:
            print(f"Error creating buyer offer: {e}")
            return None
        finally:
            conn.close()
    
    def get_buyer_offers(self, buyer_id: int = None) -> List[Dict[str, Any]]:
        """Get buyer offers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if buyer_id:
            cursor.execute('''
                SELECT bo.id, bo.buyer_id, u.name as buyer_name, bo.crop_listing_id, 
                       bo.crop_name, bo.offer_price, bo.quantity_wanted, bo.notes, 
                       bo.status, bo.created_at
                FROM buyer_offers bo
                JOIN users u ON bo.buyer_id = u.id
                WHERE bo.buyer_id = ?
                ORDER BY bo.created_at DESC
            ''', (buyer_id,))
        else:
            cursor.execute('''
                SELECT bo.id, bo.buyer_id, u.name as buyer_name, bo.crop_listing_id, 
                       bo.crop_name, bo.offer_price, bo.quantity_wanted, bo.notes, 
                       bo.status, bo.created_at
                FROM buyer_offers bo
                JOIN users u ON bo.buyer_id = u.id
                ORDER BY bo.created_at DESC
            ''')
        
        offers = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': offer[0],
                'buyer_id': offer[1],
                'buyer_name': offer[2],
                'crop_listing_id': offer[3],
                'crop_name': offer[4],
                'offer_price': offer[5],
                'quantity_wanted': offer[6],
                'notes': offer[7],
                'status': offer[8],
                'created_at': offer[9]
            }
            for offer in offers
        ]
    
    def get_offers_for_farmer(self, farmer_id: int) -> List[Dict[str, Any]]:
        """Get all offers for a farmer's listings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bo.id, bo.buyer_id, u.name as buyer_name, u.phone as buyer_phone,
                   bo.crop_listing_id, bo.crop_name, bo.offer_price, bo.quantity_wanted, 
                   bo.notes, bo.status, bo.created_at, cl.expected_price
            FROM buyer_offers bo
            JOIN users u ON bo.buyer_id = u.id
            JOIN crop_listings cl ON bo.crop_listing_id = cl.id
            WHERE cl.farmer_id = ?
            ORDER BY bo.created_at DESC
        ''', (farmer_id,))
        
        offers = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': offer[0],
                'buyer_id': offer[1],
                'buyer_name': offer[2],
                'buyer_phone': offer[3],
                'crop_listing_id': offer[4],
                'crop_name': offer[5],
                'offer_price': offer[6],
                'quantity_wanted': offer[7],
                'notes': offer[8],
                'status': offer[9],
                'created_at': offer[10],
                'expected_price': offer[11]
            }
            for offer in offers
        ]
    
    def get_offers_for_agent(self, agent_id: int) -> List[Dict[str, Any]]:
        """Get all offers for agent's farmer listings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bo.id, bo.buyer_id, u.name as buyer_name, u.phone as buyer_phone,
                   bo.crop_listing_id, bo.crop_name, bo.offer_price, bo.quantity_wanted, 
                   bo.notes, bo.status, bo.created_at, cl.expected_price, cl.farmer_name, cl.farmer_phone
            FROM buyer_offers bo
            JOIN users u ON bo.buyer_id = u.id
            JOIN crop_listings cl ON bo.crop_listing_id = cl.id
            WHERE cl.agent_id = ?
            ORDER BY bo.created_at DESC
        ''', (agent_id,))
        
        offers = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': offer[0],
                'buyer_id': offer[1],
                'buyer_name': offer[2],
                'buyer_phone': offer[3],
                'crop_listing_id': offer[4],
                'crop_name': offer[5],
                'offer_price': offer[6],
                'quantity_wanted': offer[7],
                'notes': offer[8],
                'status': offer[9],
                'created_at': offer[10],
                'expected_price': offer[11],
                'farmer_name': offer[12],
                'farmer_phone': offer[13]
            }
            for offer in offers
        ]
    
    def get_offers_by_status(self, status: str = None) -> List[Dict[str, Any]]:
        """Get offers by status (for admin dashboard)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT bo.id, bo.buyer_id, ub.name as buyer_name, ub.phone as buyer_phone,
                       bo.crop_listing_id, bo.crop_name, bo.offer_price, bo.quantity_wanted, 
                       bo.notes, bo.status, bo.created_at, cl.expected_price,
                       COALESCE(cl.farmer_name, uf.name) as farmer_name,
                       COALESCE(cl.farmer_phone, uf.phone) as farmer_phone,
                       ua.name as agent_name
                FROM buyer_offers bo
                JOIN users ub ON bo.buyer_id = ub.id
                JOIN crop_listings cl ON bo.crop_listing_id = cl.id
                LEFT JOIN users uf ON cl.farmer_id = uf.id
                LEFT JOIN users ua ON cl.agent_id = ua.id
                WHERE bo.status = ?
                ORDER BY bo.created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT bo.id, bo.buyer_id, ub.name as buyer_name, ub.phone as buyer_phone,
                       bo.crop_listing_id, bo.crop_name, bo.offer_price, bo.quantity_wanted, 
                       bo.notes, bo.status, bo.created_at, cl.expected_price,
                       COALESCE(cl.farmer_name, uf.name) as farmer_name,
                       COALESCE(cl.farmer_phone, uf.phone) as farmer_phone,
                       ua.name as agent_name
                FROM buyer_offers bo
                JOIN users ub ON bo.buyer_id = ub.id
                JOIN crop_listings cl ON bo.crop_listing_id = cl.id
                LEFT JOIN users uf ON cl.farmer_id = uf.id
                LEFT JOIN users ua ON cl.agent_id = ua.id
                ORDER BY bo.created_at DESC
            ''')
        
        offers = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': offer[0],
                'buyer_id': offer[1],
                'buyer_name': offer[2],
                'buyer_phone': offer[3],
                'crop_listing_id': offer[4],
                'crop_name': offer[5],
                'offer_price': offer[6],
                'quantity_wanted': offer[7],
                'notes': offer[8],
                'status': offer[9],
                'created_at': offer[10],
                'expected_price': offer[11],
                'farmer_name': offer[12],
                'farmer_phone': offer[13],
                'agent_name': offer[14]
            }
            for offer in offers
        ]
    
    def update_market_price(self, crop_name: str, price: float, trend: str) -> bool:
        """Update market price for a crop (this would typically update the CSV file)"""
        try:
            import pandas as pd
            import os
            import tempfile
            import shutil
            
            csv_path = 'data/market_prices.csv'
            if os.path.exists(csv_path):
                # Read the current data
                df = pd.read_csv(csv_path)
                
                # Update existing crop or add new one
                crop_index = df[df['Crop'].str.lower() == crop_name.lower()].index
                if len(crop_index) > 0:
                    df.loc[crop_index[0], 'Price'] = price
                    df.loc[crop_index[0], 'Trend'] = trend
                    df.loc[crop_index[0], 'Last_Updated'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                else:
                    # Add new crop
                    new_row = {
                        'Crop': crop_name.lower(),
                        'Price': price,
                        'Unit': 'quintal',
                        'Trend': trend,
                        'Last_Updated': pd.Timestamp.now().strftime('%Y-%m-%d')
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                # Try to write to a temporary file first, then replace
                try:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
                        tmp_path = tmp_file.name
                        df.to_csv(tmp_path, index=False)
                    
                    # Replace the original file
                    shutil.move(tmp_path, csv_path)
                    return True
                except:
                    # Fallback: try direct write
                    df.to_csv(csv_path, index=False)
                    return True
            return False
        except Exception as e:
            print(f"Error updating market price: {e}")
            return False
    
    def create_transaction(self, buyer_id: int, farmer_id: int, crop_listing_id: int,
                          crop_name: str, quantity: float, price_per_unit: float, 
                          total_amount: float, notes: str = None) -> Optional[int]:
        """Create a new transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO transactions (buyer_id, farmer_id, crop_listing_id, crop_name, 
                                        quantity, price_per_unit, total_amount, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (buyer_id, farmer_id, crop_listing_id, crop_name, quantity, price_per_unit, total_amount, notes))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            return transaction_id
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (for admin)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, role, phone, address, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'role': user[3],
                'phone': user[4],
                'address': user[5],
                'is_active': user[6],
                'created_at': user[7]
            }
            for user in users
        ]
    
    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions (for admin)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.id, t.buyer_id, ub.name as buyer_name, t.farmer_id, uf.name as farmer_name,
                   t.crop_name, t.quantity, t.price_per_unit, t.total_amount, t.transaction_date, t.status
            FROM transactions t
            JOIN users ub ON t.buyer_id = ub.id
            JOIN users uf ON t.farmer_id = uf.id
            ORDER BY t.transaction_date DESC
        ''')
        
        transactions = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': transaction[0],
                'buyer_id': transaction[1],
                'buyer_name': transaction[2],
                'farmer_id': transaction[3],
                'farmer_name': transaction[4],
                'crop_name': transaction[5],
                'quantity': transaction[6],
                'price_per_unit': transaction[7],
                'total_amount': transaction[8],
                'transaction_date': transaction[9],
                'status': transaction[10]
            }
            for transaction in transactions
        ]
    
    def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """Update user active status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET is_active = ? WHERE id = ?
            ''', (is_active, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user status: {e}")
            return False
        finally:
            conn.close()
    
    def update_crop_listing_status(self, listing_id: int, status: str) -> bool:
        """Update crop listing status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE crop_listings SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, listing_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating crop listing status: {e}")
            return False
        finally:
            conn.close()
    
    def update_offer_status(self, offer_id: int, status: str) -> bool:
        """Update offer status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE buyer_offers SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, offer_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating offer status: {e}")
            return False
        finally:
            conn.close()
    
    def get_offer_details(self, offer_id: int) -> Optional[Dict[str, Any]]:
        """Get offer details by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bo.id, bo.buyer_id, bo.crop_listing_id, bo.crop_name, 
                   bo.offer_price, bo.quantity_wanted, bo.notes, bo.status,
                   cl.farmer_id, cl.quantity as available_quantity, cl.expected_price
            FROM buyer_offers bo
            JOIN crop_listings cl ON bo.crop_listing_id = cl.id
            WHERE bo.id = ?
        ''', (offer_id,))
        
        offer = cursor.fetchone()
        conn.close()
        
        if offer:
            return {
                'id': offer[0],
                'buyer_id': offer[1],
                'crop_listing_id': offer[2],
                'crop_name': offer[3],
                'offer_price': offer[4],
                'quantity_wanted': offer[5],
                'notes': offer[6],
                'status': offer[7],
                'farmer_id': offer[8],
                'available_quantity': offer[9],
                'expected_price': offer[10]
            }
        return None
    
    def accept_offer(self, offer_id: int) -> bool:
        """Accept an offer and create transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get offer details
            offer = self.get_offer_details(offer_id)
            if not offer:
                return False
            
            # Update offer status to accepted
            cursor.execute('''
                UPDATE buyer_offers SET status = 'accepted', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (offer_id,))
            
            # Create transaction
            total_amount = offer['offer_price'] * offer['quantity_wanted']
            cursor.execute('''
                INSERT INTO transactions (buyer_id, farmer_id, crop_listing_id, crop_name, 
                                        quantity, price_per_unit, total_amount, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (offer['buyer_id'], offer['farmer_id'], offer['crop_listing_id'], 
                  offer['crop_name'], offer['quantity_wanted'], offer['offer_price'], 
                  total_amount, f"Accepted offer - {offer['notes']}"))
            
            # Update crop listing - reduce quantity or mark as sold
            remaining_quantity = offer['available_quantity'] - offer['quantity_wanted']
            if remaining_quantity <= 0:
                cursor.execute('''
                    UPDATE crop_listings SET status = 'sold', updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (offer['crop_listing_id'],))
            else:
                cursor.execute('''
                    UPDATE crop_listings SET quantity = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (remaining_quantity, offer['crop_listing_id']))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error accepting offer: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total users by role
        cursor.execute('SELECT role, COUNT(*) FROM users WHERE is_active = 1 GROUP BY role')
        user_stats = dict(cursor.fetchall())
        
        # Total active crop listings
        cursor.execute('SELECT COUNT(*) FROM crop_listings WHERE status = "available"')
        active_listings = cursor.fetchone()[0]
        
        # Total transactions
        cursor.execute('SELECT COUNT(*) FROM transactions')
        total_transactions = cursor.fetchone()[0]
        
        # Total transaction value
        cursor.execute('SELECT SUM(total_amount) FROM transactions')
        total_value = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_farmers': user_stats.get('farmer', 0),
            'total_buyers': user_stats.get('buyer', 0),
            'total_agents': user_stats.get('agent', 0),
            'total_admins': user_stats.get('admin', 0),
            'active_listings': active_listings,
            'total_transactions': total_transactions,
            'total_transaction_value': total_value
        }
