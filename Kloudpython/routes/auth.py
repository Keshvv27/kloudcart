from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from ..db import get_users_collection
from ..models.user import User

auth = Blueprint("auth", __name__)


@auth.route("/")
def home():
    return render_template("home.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        users_collection = get_users_collection()
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email already registered. Please login.")
            return redirect(url_for("auth.login"))

        # Create new user
        user = User(email, name, password)
        users_collection.insert_one(user.to_dict())
        
        flash("Registration successful! Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users_collection = get_users_collection()
        user_data = users_collection.find_one({"email": email})

        if user_data and user_data["password"] == password:
            session["user"] = email
            flash("Login successful!")
            return redirect(url_for("auth.home"))
        else:
            flash("Invalid credentials. Try again.")

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.")
    return redirect(url_for("auth.home"))


@auth.route("/admin")
def admin_dashboard():
    if "user" not in session:
        flash("Please log in to access the admin panel.")
        return redirect(url_for("auth.login"))

    if session["user"] != "niteshyrai43@gmail.com":
        flash("Access denied. Admins only!")
        return redirect(url_for("auth.home"))

    return render_template("admin.html")
