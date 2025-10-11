from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from ..db import get_products_collection, get_cart_collection, str_to_objectid, objectid_to_str
from ..models.user import Product, CartItem
from datetime import datetime

products = Blueprint("products", __name__)  # previously "products"



@products.route("/products")
def list_products():
    products_collection = get_products_collection()
    products_data = list(products_collection.find())
    
    # Convert ObjectIds to strings for template compatibility
    products_list = []
    for product in products_data:
        products_list.append({
            "id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"],
            "category": product.get("category", ""),
            "description": product.get("description", ""),
            "image_url": product.get("image_url", "")
        })
    
    if "user" in session:
        user_email = session["user"]
        cart_collection = get_cart_collection()
        cart_items = cart_collection.find({"user_email": user_email})
        cart = {str(item["product_id"]): item["quantity"] for item in cart_items}
    else:
        cart = {}
    
    return render_template("products.html", products=products_list, cart=cart)


@products.route("/cart")
def cart():
    if "user" not in session:
        flash("Please log in to access your cart.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    products_collection = get_products_collection()
    cart_collection = get_cart_collection()
    
    # Get user's cart items
    cart_items = cart_collection.find({"user_email": user_email})
    
    # Build a list of items with quantity
    items = []
    total = 0
    
    for cart_item in cart_items:
        product_id = cart_item["product_id"]
        quantity = cart_item["quantity"]
        
        # Find the product
        product = products_collection.find_one({"_id": product_id})
        if product:
            subtotal = product["price"] * quantity
            items.append({
                "id": str(product["_id"]),
                "name": product["name"],
                "price": product["price"],
                "category": product.get("category", ""),
                "description": product.get("description", ""),
                "image_url": product.get("image_url", ""),
                "quantity": quantity,
                "subtotal": subtotal
            })
            total += subtotal

    return render_template("cart.html", items=items, total=total)


@products.route("/add-to-cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "user" not in session:
        flash("Please log in first.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart_collection = get_cart_collection()
    
    # Convert string product_id to ObjectId
    product_object_id = str_to_objectid(product_id)
    if not product_object_id:
        flash("Invalid product ID.")
        return redirect(url_for("products.list_products"))
    
    # Check if item already exists in cart
    existing_item = cart_collection.find_one({
        "user_email": user_email,
        "product_id": product_object_id
    })
    
    if existing_item:
        # Update quantity
        cart_collection.update_one(
            {"_id": existing_item["_id"]},
            {"$inc": {"quantity": 1}}
        )
    else:
        # Add new item
        cart_item = CartItem(user_email, product_object_id, 1)
        cart_collection.insert_one(cart_item.to_dict())
    
    flash("Item added to cart!")
    return redirect(url_for("products.list_products"))



@products.route("/increase-quantity/<product_id>", methods=["POST"])
def increase_quantity(product_id):
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart_collection = get_cart_collection()
    
    # Convert string product_id to ObjectId
    product_object_id = str_to_objectid(product_id)
    if not product_object_id:
        return redirect(url_for("products.list_products"))
    
    # Find existing cart item
    existing_item = cart_collection.find_one({
        "user_email": user_email,
        "product_id": product_object_id
    })
    
    if existing_item:
        cart_collection.update_one(
            {"_id": existing_item["_id"]},
            {"$inc": {"quantity": 1}}
        )
    else:
        # Add new item if it doesn't exist
        cart_item = CartItem(user_email, product_object_id, 1)
        cart_collection.insert_one(cart_item.to_dict())

    return redirect(url_for("products.list_products"))


@products.route("/decrease-quantity/<product_id>", methods=["POST"])
def decrease_quantity(product_id):
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart_collection = get_cart_collection()
    
    # Convert string product_id to ObjectId
    product_object_id = str_to_objectid(product_id)
    if not product_object_id:
        return redirect(url_for("products.list_products"))
    
    # Find existing cart item
    existing_item = cart_collection.find_one({
        "user_email": user_email,
        "product_id": product_object_id
    })
    
    if existing_item:
        if existing_item["quantity"] > 1:
            cart_collection.update_one(
                {"_id": existing_item["_id"]},
                {"$inc": {"quantity": -1}}
            )
        else:
            # Remove item if quantity becomes 0
            cart_collection.delete_one({"_id": existing_item["_id"]})

    return redirect(url_for("products.list_products"))


@products.route("/checkout")
def checkout():
    """Display checkout page with cart items"""
    if "user" not in session:
        flash("Please log in to access checkout.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    products_collection = get_products_collection()
    cart_collection = get_cart_collection()
    
    # Get user's cart items
    cart_items = cart_collection.find({"user_email": user_email})
    
    # Build a list of items with quantity
    items = []
    total = 0
    
    for cart_item in cart_items:
        product_id = cart_item["product_id"]
        quantity = cart_item["quantity"]
        
        # Find the product
        product = products_collection.find_one({"_id": product_id})
        if product:
            subtotal = product["price"] * quantity
            items.append({
                "id": str(product["_id"]),
                "name": product["name"],
                "price": product["price"],
                "category": product.get("category", ""),
                "description": product.get("description", ""),
                "image_url": product.get("image_url", ""),
                "quantity": quantity,
                "subtotal": subtotal
            })
            total += subtotal

    if not items:
        flash("Your cart is empty. Add some products first!")
        return redirect(url_for("products.cart"))

    current_date = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p")
    return render_template("checkout.html", items=items, total=total, user_email=user_email, current_date=current_date)


@products.route("/confirm-order", methods=["POST"])
def confirm_order():
    """Process order confirmation"""
    if "user" not in session:
        flash("Please log in to confirm your order.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    products_collection = get_products_collection()
    cart_collection = get_cart_collection()
    
    # Get user's cart items
    cart_items = cart_collection.find({"user_email": user_email})
    
    # Build order summary
    items = []
    total = 0
    order_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    
    for cart_item in cart_items:
        product_id = cart_item["product_id"]
        quantity = cart_item["quantity"]
        
        # Find the product
        product = products_collection.find_one({"_id": product_id})
        if product:
            subtotal = product["price"] * quantity
            items.append({
                "id": str(product["_id"]),
                "name": product["name"],
                "price": product["price"],
                "category": product.get("category", ""),
                "description": product.get("description", ""),
                "image_url": product.get("image_url", ""),
                "quantity": quantity,
                "subtotal": subtotal
            })
            total += subtotal

    if not items:
        flash("Your cart is empty. Add some products first!")
        return redirect(url_for("products.cart"))

    # Clear the cart after order confirmation
    cart_collection.delete_many({"user_email": user_email})
    
    current_date = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p")
    flash(f"Order #{order_id} confirmed successfully! Total amount: ₹{total}")
    return render_template("order_confirmed.html", items=items, total=total, order_id=order_id, user_email=user_email, current_date=current_date)



