from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Import blueprints
    from .routes.auth import auth
    from .routes.products import products
    from .routes.admin import admin
# Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(products)
    app.register_blueprint(admin)
    return app


