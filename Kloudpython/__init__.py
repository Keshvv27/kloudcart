from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    # Initialize Flask-Mail
    mail = Mail(app)

    # Initialize MongoDB connection
    from .db import db
    try:
        db.connect()
        print("MongoDB connection initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize MongoDB connection: {e}")

    # Import blueprints
    from .routes.auth import auth
    from .routes.products import products
    from .routes.admin import admin
    
    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(products)
    app.register_blueprint(admin)
    
    return app


