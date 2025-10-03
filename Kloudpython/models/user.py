from bson import ObjectId
from datetime import datetime

class User:
    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert user to dictionary for MongoDB storage"""
        return {
            "email": self.email,
            "name": self.name,
            "password": self.password,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user from MongoDB document"""
        user = cls(data["email"], data["name"], data["password"])
        user.created_at = data.get("created_at", datetime.utcnow())
        return user

class Product:
    def __init__(self, name, price, _id=None):
        self._id = _id or ObjectId()
        self.name = name
        self.price = price
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert product to dictionary for MongoDB storage"""
        return {
            "_id": self._id,
            "name": self.name,
            "price": self.price,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create product from MongoDB document"""
        product = cls(data["name"], data["price"], data["_id"])
        product.created_at = data.get("created_at", datetime.utcnow())
        return product

class CartItem:
    def __init__(self, user_email, product_id, quantity):
        self.user_email = user_email
        self.product_id = product_id
        self.quantity = quantity
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert cart item to dictionary for MongoDB storage"""
        return {
            "user_email": self.user_email,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create cart item from MongoDB document"""
        cart_item = cls(data["user_email"], data["product_id"], data["quantity"])
        cart_item.updated_at = data.get("updated_at", datetime.utcnow())
        return cart_item
