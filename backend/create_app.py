# server/create_app.py

# Importing necessary libraries
from flask import Flask
from flask_cors import CORS
from config import Config
from database import db, bcrypt
import os

# create_app function to initialize the Flask application
def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Apply configuration from Config class
    app.config.from_object(Config)


    # Initialize SQLAlchemy and Bcrypt with the app instance
    db.init_app(app)
    bcrypt.init_app(app)

    # Setup CORS configurations
    allowed_origins = os.getenv("CORS_ORIGINS")

    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/*": {"origins": allowed_origins}
        }
    )

    return app
