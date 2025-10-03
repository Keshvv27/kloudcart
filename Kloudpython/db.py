from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI environment variable is required")
            
            self.client = MongoClient(mongo_uri)
            self.db = self.client.kloudcart
            
            # Test the connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB Atlas!")
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        return self.db[collection_name]
    
    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()

# Global database instance
db = MongoDB()

# Helper functions for ObjectId handling
def str_to_objectid(id_string):
    """Convert string to ObjectId"""
    try:
        return ObjectId(id_string)
    except:
        return None

def objectid_to_str(obj_id):
    """Convert ObjectId to string"""
    return str(obj_id) if obj_id else None

# Collections
def get_users_collection():
    return db.get_collection("users")

def get_products_collection():
    return db.get_collection("products")

def get_cart_collection():
    return db.get_collection("cart")
