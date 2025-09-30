from flask import Blueprint, render_template, redirect, url_for, request, session, flash

auth_bp = Blueprint("auth", __name__)

# in-memory "database"(later to Mongo)
users_db = {
    "admin@kloudcart.com": {"name": "Admin", "password": "admin123"}
}

@auth_bp.route("/")
def home():
    return render_template("home.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if email in users_db:
            flash("Email already registered. Please login.")
            return redirect(url_for("auth.login"))

        users_db[email] = {"name": name, "password": password}
        flash("Registration successful! Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users_db.get(email)

        if user and user["password"] == password:
            session["user"] = email
            flash("Login successful!")
            return redirect(url_for("auth.home"))
        else:
            flash("Invalid credentials. Try again.")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.")
    return redirect(url_for("auth.home"))

@auth_bp.route("/admin")
def admin_dashboard():
    if "user" not in session:
        flash("Please log in to access the admin panel.")
        return redirect(url_for("auth.login"))

    if session["user"] != "admin@kloudcart.com":
        flash("Access denied. Admins only!")
        return redirect(url_for("auth.home"))

    return render_template("admin.html")
