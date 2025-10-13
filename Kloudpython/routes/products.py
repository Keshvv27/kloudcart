from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_file, current_app
from ..db import get_products_collection, get_cart_collection, get_users_collection, get_receipts_collection, str_to_objectid, objectid_to_str
from ..models.user import Product, CartItem
from datetime import datetime
import os
from ..utils.pdf_generator import generate_receipt_pdf, create_receipts_directory
from ..utils.email_helper import send_receipt_email, get_user_email_from_db, cleanup_pdf_file

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
    
    # Prepare order data for email
    order_data = {
        'order_id': order_id,
        'user_email': user_email,
        'items': items,
        'total': total,
        'current_date': current_date
    }
    
    # Generate PDF receipt and send email
    email_sent = False
    try:
        # Create receipts directory
        receipts_dir = create_receipts_directory()
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        username_clean = user_email.replace("@", "_").replace(".", "_")
        filename = f"receipt_{username_clean}_{timestamp}.pdf"
        pdf_path = os.path.join(receipts_dir, filename)
        
        # Generate PDF
        generate_receipt_pdf(order_data, pdf_path)
        
        # Send email with PDF attachment
        email_sent = send_receipt_email(user_email, order_data, pdf_path)
        
        # Optionally cleanup PDF file after sending (uncomment if you want to delete)
        # cleanup_pdf_file(pdf_path)
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email receipt: {str(e)}")
        email_sent = False
    
    # Log receipt to MongoDB
    try:
        receipts_collection = get_receipts_collection()
        users_collection = get_users_collection()
        user_doc = users_collection.find_one({"email": user_email})
        username = user_doc.get("name", "") if user_doc else ""

        # Keep only the required fields for items
        items_for_log = []
        for item in items:
            items_for_log.append({
                "name": item.get("name"),
                "quantity": item.get("quantity"),
                "price": item.get("price"),
                "subtotal": item.get("subtotal")
            })

        receipts_collection.insert_one({
            "user_email": user_email,
            "username": username,
            "items": items_for_log,
            "total_amount": total,
            "timestamp": datetime.utcnow(),
            "receipt_filename": filename,
            "email_status": "sent" if email_sent else "failed"
        })
    except Exception as e:
        current_app.logger.error(f"Failed to log receipt: {str(e)}")

    # Flash message with email status
    if email_sent:
        flash(f"Order #{order_id} confirmed successfully! Total amount: ₹{total}. A copy of your receipt has been sent to your email.")
    else:
        flash(f"Order #{order_id} confirmed successfully! Total amount: ₹{total}. Note: Email receipt could not be sent.")
    
    return render_template("order_confirmed.html", items=items, total=total, order_id=order_id, user_email=user_email, current_date=current_date, email_sent=email_sent)


@products.route("/download-receipt")
def download_receipt():
    """Generate and download PDF receipt for the last order"""
    if "user" not in session:
        flash("Please log in to download your receipt.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    
    # Get order data from session or request parameters
    order_id = request.args.get('order_id')
    if not order_id:
        flash("No order ID provided.")
        return redirect(url_for("products.list_products"))
    
    # For this implementation, we'll recreate the order data from the order_id
    # In a real application, you might want to store order data in a separate orders collection
    try:
        # Create receipts directory
        receipts_dir = create_receipts_directory()
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        username_clean = user_email.replace("@", "_").replace(".", "_")
        filename = f"receipt_{username_clean}_{timestamp}.pdf"
        file_path = os.path.join(receipts_dir, filename)
        
        # For this demo, we'll create a sample order data
        # In a real app, you'd fetch this from an orders collection
        order_data = {
            'order_id': order_id,
            'user_email': user_email,
            'items': [],  # This would be fetched from orders collection
            'total': 0,   # This would be fetched from orders collection
            'current_date': datetime.utcnow().strftime("%B %d, %Y at %I:%M %p")
        }
        
        # Generate PDF
        generate_receipt_pdf(order_data, file_path)
        
        # Send file for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"KloudCart_Receipt_{order_id}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f"Error generating receipt: {str(e)}")
        return redirect(url_for("products.list_products"))


@products.route("/download-receipt-with-data", methods=["POST"])
def download_receipt_with_data():
    """Generate and download PDF receipt with order data from form"""
    if "user" not in session:
        flash("Please log in to download your receipt.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    
    try:
        # Get order data from form
        order_id = request.form.get('order_id')
        total = float(request.form.get('total', 0))
        current_date = request.form.get('current_date', datetime.utcnow().strftime("%B %d, %Y at %I:%M %p"))
        
        # Parse items from form data
        items = []
        item_count = int(request.form.get('item_count', 0))
        
        for i in range(item_count):
            item = {
                'name': request.form.get(f'item_{i}_name', ''),
                'category': request.form.get(f'item_{i}_category', ''),
                'quantity': int(request.form.get(f'item_{i}_quantity', 0)),
                'price': float(request.form.get(f'item_{i}_price', 0)),
                'subtotal': float(request.form.get(f'item_{i}_subtotal', 0))
            }
            items.append(item)
        
        # Create receipts directory
        receipts_dir = create_receipts_directory()
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        username_clean = user_email.replace("@", "_").replace(".", "_")
        filename = f"receipt_{username_clean}_{timestamp}.pdf"
        file_path = os.path.join(receipts_dir, filename)
        
        # Prepare order data
        order_data = {
            'order_id': order_id,
            'user_email': user_email,
            'items': items,
            'total': total,
            'current_date': current_date
        }
        
        # Generate PDF
        generate_receipt_pdf(order_data, file_path)
        
        # Send file for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"KloudCart_Receipt_{order_id}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f"Error generating receipt: {str(e)}")
        return redirect(url_for("products.list_products"))



