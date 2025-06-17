from flask import Flask
from flask_cors import CORS
from models import db
from services import register_routes
from dotenv import load_dotenv
import os
from firebase_admin import credentials, initialize_app

def init_firebase():
    firebase_cert_path = os.getenv("FIREBASE_CREDENTIALS")
    if not firebase_cert_path or not os.path.exists(firebase_cert_path):
        raise RuntimeError("FIREBASE_CREDENTIALS path is missing or invalid.")
    
    cred = credentials.Certificate(firebase_cert_path)
    initialize_app(cred)

def create_app():
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    init_firebase()

    # Register routes from services
    register_routes(app)

    return app
