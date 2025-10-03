from flask import Blueprint, render_template, session, redirect, url_for, flash

products = Blueprint("products", __name__)  # previously "products"


# temporary "database"
products_db = [
    {"id": 1, "name": "Tomatoes", "price": 30},
    {"id": 2, "name": "Potatoes", "price": 20},
    {"id": 3, "name": "Onions", "price": 25},
]

# key = user_email, value = {product_id: quantity}
cart_db = {}


@products.route("/products")
def list_products():
    if "user" in session:
        user_email = session["user"]
        cart = cart_db.get(user_email, {})
    else:
        cart = {}
    return render_template("products.html", products=products_db, cart=cart)


@products.route("/cart")
def cart():
    if "user" not in session:
        flash("Please log in to access your cart.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart_items = cart_db.get(user_email, {})

    # Build a list of items with quantity
    items = []
    total = 0
    for product in products_db:
        if product["id"] in cart_items:
            qty = cart_items[product["id"]]
            subtotal = product["price"] * qty
            items.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": qty,
                "subtotal": subtotal
            })

            total += subtotal

    return render_template("cart.html", items=items, total=total)


@products.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "user" not in session:
        flash("Please log in first.")
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart = cart_db.setdefault(user_email, {})

    cart[product_id] = cart.get(product_id, 0) + 1
    flash("Item added to cart!")
    return redirect(url_for("products.list_products"))



@products.route("/increase-quantity/<int:product_id>", methods=["POST"])
def increase_quantity(product_id):
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart = cart_db.setdefault(user_email, {})

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    return redirect(url_for("products.list_products"))


@products.route("/decrease-quantity/<int:product_id>", methods=["POST"])
def decrease_quantity(product_id):
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user_email = session["user"]
    cart = cart_db.setdefault(user_email, {})

    if product_id in cart:
        cart[product_id] -= 1
        if cart[product_id] <= 0:
            del cart[product_id]

    return redirect(url_for("products.list_products"))



