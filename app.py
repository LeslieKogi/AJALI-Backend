from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import cloudinary

from extensions import db, jwt, migrate  # Import from extensions

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.logger.setLevel(logging.INFO)
    CORS(app, resources={r"/*": {"origins": "https://localhost:5173"}}, supports_credentials=True)


    @app.after_request
    def add_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "https://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response


    # Ensure instance folder exists
    db_path = Path(app.instance_path) / "ajali.db"
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # App config
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

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import models after db is initialized
    from models import User, Incident, Media, Notification, StatusHistory

    # Register blueprints
    from routes.auth import auth_bp
    from routes.incidents import incidents_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(incidents_bp, url_prefix="/incidents")

    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to Ajali API"}), 200

    return app

# Run the app
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5555)
