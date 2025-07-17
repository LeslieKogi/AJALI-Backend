from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
from flasgger import Swagger

# Load environment variables
load_dotenv()

# Import extension instances
from extensions import db, migrate, jwt
from swagger_config import swagger_template, swagger_config

# Import blueprints
from routes.auth import auth_bp
from routes.incidents import incidents_bp

# Initialize Flask app
app = Flask(__name__, instance_relative_config=True)
CORS(app)

# Database configuration
Path(app.instance_path).mkdir(parents=True, exist_ok=True)
db_path = Path(app.instance_path) / "ajali.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Cloudinary configuration
cloudinary.config(
    cloud_name="ddmykppxn",
    api_key="936797567636992",
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Swagger configuration
app.config['SWAGGER'] = {
    "title": "AJALI API Docs",
    "uiversion": 3
}
swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# Import models after db is initialized
from models import User, Incident, Media, Notification, StatusHistory

# Set up JWT after importing User
jwt.init_app(app)
@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return user_id  # it's already an integer, no .id needed


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(incidents_bp, url_prefix="/incidents")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"message": "Internal server error"}), 500

# Root endpoint
@app.route('/', methods=['GET'])
def index():
    """
    Welcome endpoint
    ---
    responses:
      200:
        description: Welcome to Ajali API
    """
    return jsonify({"message": "Welcome to Ajali API"}), 200

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)
