from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Import blueprints
    from .routes.auth import auth_bp
    from .routes.products import products

# Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(products)

    return app


