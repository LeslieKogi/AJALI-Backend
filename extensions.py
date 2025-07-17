from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# ✅ Only define instances here — DO NOT initialize with app here
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# ✅ JWT callbacks should be defined in app.py after app is initialized,
#    not here to avoid circular imports





# from flask_jwt_extended import JWTManager
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flasgger import Swagger

# db = SQLAlchemy()
# migrate = Migrate()
# swagger = Swagger()
# jwt = JWTManager()

# @jwt.user_identity_loader
# def user_identity_lookup(user):
#     return user.id

# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     from app.models import User
#     identity = jwt_data["sub"]
#     return User.query.get(identity)