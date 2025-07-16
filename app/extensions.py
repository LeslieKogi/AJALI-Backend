
from flask_jwt_extended import JWTManager

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    from app.models import User
    identity = jwt_data["sub"]
    return User.query.get(identity)