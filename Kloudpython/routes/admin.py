from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .products import products_db  # reuse the same product list

admin = Blueprint("admin", __name__)  # previously "admin"


# Admin Dashboard
@admin.route("/admin/dashboard")
def admin_dashboard():
    if session.get("user") != "admin@kloudcart.com":
        flash("Access denied. Admins only!")
        return redirect(url_for("products.list_products"))
    return render_template("admin_dashboard.html", products=products_db)


# Add Product
@admin.route("/admin/add", methods=["GET", "POST"])
def add_product():
    if session.get("user") != "admin@kloudcart.com":
        flash("Access denied.")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        new_id = max(p["id"] for p in products_db) + 1 if products_db else 1
        products_db.append({"id": new_id, "name": name, "price": price})
        flash("✅ Product added successfully!")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("add_product.html")


# Edit Product
@admin.route("/admin/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if session.get("user") != "admin@kloudcart.com":
        flash("Access denied.")
        return redirect(url_for("products.list_products"))

    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        flash("Product not found.")
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        product["name"] = request.form["name"]
        product["price"] = int(request.form["price"])
        flash("✅ Product updated successfully!")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("edit_product.html", product=product)


#  Delete Product
@admin.route("/admin/delete/<int:product_id>")
def delete_product(product_id):
    if session.get("user") != "admin@kloudcart.com":
        flash("Access denied.")
        return redirect(url_for("products.list_products"))

    global products_db
    products_db[:] = [p for p in products_db if p["id"] != product_id]
    flash("🗑️ Product deleted successfully!")
    return redirect(url_for("admin.admin_dashboard"))
