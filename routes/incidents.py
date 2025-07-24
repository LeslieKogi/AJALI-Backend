# app/routes/incidents.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from models import db, Incident, Media, StatusHistory, User
from flask import current_app
import cloudinary.uploader

from send_incident_email import send_incident_confirmation_email

from datetime import datetime

incidents_bp = Blueprint('incidents', __name__, url_prefix='/incidents')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

@incidents_bp.route('/', methods=['GET'])
def get_incidents():
    status = request.args.get('status')
    query = Incident.query
    
    if status:
        query = query.filter_by(status=status)
    
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = query.order_by(Incident.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    incidents = pagination.items

    
    return jsonify({
    'total': pagination.total,
    'pages': pagination.pages,
    'current_page': pagination.page,
    'incidents': [{
        'id': incident.id,
        'title': incident.title,
        'description': incident.description,
        'latitude': float(incident.latitude),
        'longitude': float(incident.longitude),
        'status': incident.status,
        'created_at': incident.created_at.isoformat(),
        'reporter': incident.user.username
    } for incident in incidents]
    }), 200


@incidents_bp.route('', methods=['POST'])
@jwt_required()
def create_incident():
    current_user_id = get_jwt_identity()
    data = request.form

    required_fields = ['title', 'description', 'type', 'latitude', 'longitude']
    for field in required_fields:
        if field not in data or not data[field].strip():
            return jsonify({'message': f'{field} is required.'}), 400

    try:
        # Create incident
        new_incident = Incident(
            user_id=current_user_id,
            title=data['title'],
            description=data['description'],
            type=data['type'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        db.session.add(new_incident)
        db.session.commit()

        # Handle file uploads
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and allowed_file(file.filename):
                    upload_result = cloudinary.uploader.upload(file)
                    media_type = 'image' if upload_result["resource_type"] == "image" else 'video'
                    media = Media(
                        incident_id=new_incident.id,
                        file_url=upload_result["secure_url"],
                        media_type=media_type
                    )
                    db.session.add(media)
            db.session.commit()

        #  Send confirmation email
        user = User.query.get(current_user_id)
        if user and user.email:
            incident_data = {
                'title': new_incident.title,
                'description': new_incident.description,
                'location': f"{new_incident.latitude}, {new_incident.longitude}",
                'created_at': new_incident.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            status_code, response = send_incident_confirmation_email(user.email, user.username, incident_data)
            current_app.logger.info(f"Email sent: {status_code} - {response}")

        return jsonify({'message': 'Incident created successfully', 'id': new_incident.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

@incidents_bp.route('/<int:id>', methods=['PUT']) 
@jwt_required()
def update_incident(id):
    current_user = get_jwt_identity()
    incident = Incident.query.get_or_404(id)
    
    if incident.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            incident.title = data['title']
        if 'description' in data:
            incident.description = data['description']
        if 'latitude' in data and 'longitude' in data:
            incident.latitude = data['latitude']
            incident.longitude = data['longitude']
        
        db.session.commit()
        return jsonify({'message': 'Incident updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

@incidents_bp.route('/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_incident_status(id):
    current_user = User.query.get(get_jwt_identity())
    
    if not current_user.is_admin:
        return jsonify({'message': 'Unauthorized'}), 403
    
    incident = Incident.query.get_or_404(id)
    data = request.get_json()
    
    try:
        status_update = StatusHistory(
            incident_id=incident.id,
            old_status=incident.status,
            new_status=data['status'],
        )
        
        incident.status = data['status']
        
        db.session.add(status_update)
        db.session.commit()
        
        # add notification logic (email/SMS)
        
        return jsonify({'message': 'Status updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400