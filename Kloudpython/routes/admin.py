from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from ..db import get_products_collection, get_receipts_collection, str_to_objectid, objectid_to_str
from ..models.user import Product
import os
import uuid

admin = Blueprint("admin", __name__)

# Allowed file extensions for images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file to static/uploads directory with unique filename"""
    if file and allowed_file(file.filename):
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}-{uuid.uuid4().hex[:8]}{ext}"
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Return the URL path for database storage
        return f"/static/uploads/{unique_filename}"
    return None


# Admin Dashboard
@admin.route("/admin/dashboard")
def admin_dashboard():
    if session.get("user") != "niteshyrai43@gmail.com":
        flash("Access denied. Admins only!")
        return redirect(url_for("products.list_products"))
    
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
    
    return render_template("admin_dashboard.html", products=products_list)


# Admin Receipts Logs
@admin.route("/admin/receipts")
def admin_receipts():
    if session.get("user") != "niteshyrai43@gmail.com":
        flash("Access denied. Admins only!")
        return redirect(url_for("products.list_products"))

    receipts_collection = get_receipts_collection()
    logs = list(receipts_collection.find().sort("timestamp", -1))

    # Transform for template
    entries = []
    for doc in logs:
        entries.append({
            "id": str(doc.get("_id")),
            "username": doc.get("username", ""),
            "user_email": doc.get("user_email", ""),
            "total_amount": doc.get("total_amount", 0),
            "timestamp": doc.get("timestamp"),
            "email_status": doc.get("email_status", ""),
            "items": doc.get("items", []),
            "receipt_filename": doc.get("receipt_filename", "")
        })

    return render_template("admin_receipts.html", entries=entries)


# Add Product
@admin.route("/admin/add", methods=["GET", "POST"])
def add_product():
    if session.get("user") != "niteshyrai43@gmail.com":
        flash("Access denied.")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        category = request.form.get("category", "")
        description = request.form.get("description", "")
        
        # Handle file upload
        image_file = request.files.get("image")
        image_url = ""
        
        if image_file and image_file.filename:
            saved_path = save_uploaded_file(image_file)
            if saved_path:
                image_url = saved_path
            else:
                flash("⚠️ Invalid image file. Please upload a valid image (PNG, JPG, JPEG, GIF, WebP).")
                return render_template("add_product.html")
        else:
            # Use default placeholder image if no image uploaded
            image_url = "/static/images/placeholder.svg"
        
        products_collection = get_products_collection()
        product = Product(name, price, category, description, image_url)
        products_collection.insert_one(product.to_dict())
        
        flash("✅ Product added successfully!")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("add_product.html")


# Edit Product
@admin.route("/admin/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if session.get("user") != "niteshyrai43@gmail.com":
        flash("Access denied.")
        return redirect(url_for("products.list_products"))

    products_collection = get_products_collection()
    product_object_id = str_to_objectid(product_id)
    
    if not product_object_id:
        flash("Invalid product ID.")
        return redirect(url_for("admin.admin_dashboard"))
    
    product_data = products_collection.find_one({"_id": product_object_id})
    if not product_data:
        flash("Product not found.")
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        category = request.form.get("category", "")
        description = request.form.get("description", "")
        
        # Handle file upload - only update if new image is uploaded
        image_file = request.files.get("image")
        update_data = {
            "name": name, 
            "price": price,
            "category": category,
            "description": description
        }
        
        if image_file and image_file.filename:
            saved_path = save_uploaded_file(image_file)
            if saved_path:
                update_data["image_url"] = saved_path
            else:
                flash("⚠️ Invalid image file. Please upload a valid image (PNG, JPG, JPEG, GIF, WebP).")
                return render_template("edit_product.html", product=product)
        
        products_collection.update_one(
            {"_id": product_object_id},
            {"$set": update_data}
        )
        
        flash("✅ Product updated successfully!")
        return redirect(url_for("admin.admin_dashboard"))

    # Convert ObjectId to string for template compatibility
    product = {
        "id": str(product_data["_id"]),
        "name": product_data["name"],
        "price": product_data["price"],
        "category": product_data.get("category", ""),
        "description": product_data.get("description", ""),
        "image_url": product_data.get("image_url", "")
    }
    
    return render_template("edit_product.html", product=product)


#  Delete Product
@admin.route("/admin/delete/<product_id>")
def delete_product(product_id):
    if session.get("user") != "niteshyrai43@gmail.com":
        flash("Access denied.")
        return redirect(url_for("products.list_products"))

    products_collection = get_products_collection()
    product_object_id = str_to_objectid(product_id)
    
    if not product_object_id:
        flash("Invalid product ID.")
        return redirect(url_for("admin.admin_dashboard"))
    
    # Check if product exists
    product_data = products_collection.find_one({"_id": product_object_id})
    if not product_data:
        flash("Product not found.")
        return redirect(url_for("admin.admin_dashboard"))
    
    # Delete the product
    products_collection.delete_one({"_id": product_object_id})
    
    flash("🗑️ Product deleted successfully!")
    return redirect(url_for("admin.admin_dashboard"))
