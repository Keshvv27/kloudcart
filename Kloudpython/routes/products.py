from flask import Blueprint, render_template, session, redirect, url_for, flash

products = Blueprint("products", __name__)

# temporary "database"
products_db = [
    {"id": 1, "name": "Tomatoes", "price": 30},
    {"id": 2, "name": "Potatoes", "price": 20},
    {"id": 3, "name": "Onions", "price": 25},
]

cart_db = {}  # key = user_email, value = list of product_ids


@products.route("/products")
def list_products():
    return render_template("products.html", products=products_db)


@products.route("/cart")
def cart():
    if "user" not in session:
        flash("Please log in to access your cart.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart_items = cart_db.get(user_email, [])

    items = [p for p in products_db if p["id"] in cart_items]
    total = sum(p["price"] for p in items)

    return render_template("cart.html", items=items, total=total)


@products.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    if "user" not in session:
        flash("Please log in first.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart_db.setdefault(user_email, []).append(product_id)
    flash("Item added to cart!")
    return redirect(url_for("products.list_products"))
