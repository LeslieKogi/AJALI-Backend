from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    JWTManager
)
from mail import send_welcome_email
from models import User

auth_bp = Blueprint('auth', __name__)

# Initialize JWTManager (if needed here)
jwt = JWTManager()

# Access db through Flask's context
def get_db():
    return current_app.extensions['sqlalchemy'].db

@auth_bp.route('/register', methods=['POST'])
def register():
    db = get_db()
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        phone=data.get('phone')
    )
    
    db.session.add(new_user)
    db.session.commit()

    # Send welcome email
    status_code, response = send_welcome_email(new_user.email, new_user.username)
    if status_code != 200:
        current_app.logger.error(f"Failed to send welcome email: {response}")

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    db = get_db()
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    db = get_db()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin
    }), 200

# JWT Callbacks (if they need to be here)
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    db = get_db()
    identity = jwt_data["sub"]
    return User.query.get(identity)