#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
import os
from pathlib import Path

from app.models import db, User, Incident, Media, Notification, StatusHistory


app = Flask(__name__, instance_relative_config=True)

Path(app.instance_path).mkdir(parents=True, exist_ok=True)

db_path = Path(app.instance_path) / "ajali.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)
with app.app_context():
    db.create_all()


#Routes
@app.route('/', methods=['GET'])
def index():
    return make_response(jsonify({"message": "Welcome to Ajali API"}), 200)

if __name__ == '__main__':
    app.run(port=5555)