from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..db import get_products_collection, str_to_objectid, objectid_to_str
from ..models.user import Product

admin = Blueprint("admin", __name__)


# Admin Dashboard
@admin.route("/admin/dashboard")
def admin_dashboard():
    if session.get("user") != "admin@kloudcart.com":
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
            "price": product["price"]
        })
    
    return render_template("admin_dashboard.html", products=products_list)


# Add Product
@admin.route("/admin/add", methods=["GET", "POST"])
def add_product():
    if session.get("user") != "admin@kloudcart.com":
        flash("Access denied.")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        
        products_collection = get_products_collection()
        product = Product(name, price)
        products_collection.insert_one(product.to_dict())
        
        flash("✅ Product added successfully!")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("add_product.html")


# Edit Product
@admin.route("/admin/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if session.get("user") != "admin@kloudcart.com":
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
        
        products_collection.update_one(
            {"_id": product_object_id},
            {"$set": {"name": name, "price": price}}
        )
        
        flash("✅ Product updated successfully!")
        return redirect(url_for("admin.admin_dashboard"))

    # Convert ObjectId to string for template compatibility
    product = {
        "id": str(product_data["_id"]),
        "name": product_data["name"],
        "price": product_data["price"]
    }
    
    return render_template("edit_product.html", product=product)


#  Delete Product
@admin.route("/admin/delete/<product_id>")
def delete_product(product_id):
    if session.get("user") != "admin@kloudcart.com":
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
