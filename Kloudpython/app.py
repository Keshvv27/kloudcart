from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"

#user
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

@app.route('/products')
def products():
    return render_template("products.html")

@app.route('/cart')
def cart():
    return render_template("cart.html")

@app.route('/checkout')
def checkout():
    return render_template("checkout.html")

#admin
@app.route('/admin')
def admin_dashboard():
    return render_template("admin.html")

#main
if __name__ == '__main__':
    app.run(debug=True)
