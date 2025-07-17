from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from pathlib import Path
from dotenv import load_dotenv
import os

import cloudinary

from models import db
from extensions import jwt  

# Load env vars
load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

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

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    Migrate(app, db)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.incidents import incidents_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(incidents_bp, url_prefix="/incidents")

    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to Ajali API"}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5555)
