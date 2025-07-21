from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy  # <-- Add this import
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
import cloudinary

# Load env vars
load_dotenv()

app = Flask(__name__, instance_relative_config=True)
app.logger.setLevel(logging.INFO)

# Config
db_path = Path(app.instance_path) / "ajali.db"
Path(app.instance_path).mkdir(parents=True, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=7)
app.config["UPLOAD_FOLDER"] = "./uploads"

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Initialize extensions
db = SQLAlchemy(app)  # Now this will work
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Import models after db is initialized
from models import User, Incident, Media, Notification, StatusHistory

def register_blueprints():
    """Register blueprints after all initializations"""
    from routes.auth import auth_bp
    from routes.incidents import incidents_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(incidents_bp, url_prefix="/incidents")

register_blueprints()

@app.route('/')
def index():
    return jsonify({"message": "Welcome to Ajali API"}), 200

if __name__ == '__main__':
    app.run(port=5555)