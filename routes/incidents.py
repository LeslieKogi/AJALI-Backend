from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from app.app import db, app
from app.models import Incident, Media, StatusUpdate, User
from datetime import datetime

incidents_bp = Blueprint('incidents', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@incidents_bp.route('/', methods=['GET'])
def get_incidents():
    status = request.args.get('status')
    query = Incident.query
    
    if status:
        query = query.filter_by(status=status)
    
    incidents = query.order_by(Incident.created_at.desc()).all()
    
    return jsonify([{
        'id': incident.id,
        'title': incident.title,
        'description': incident.description,
        'latitude': float(incident.latitude),
        'longitude': float(incident.longitude),
        'status': incident.status,
        'created_at': incident.created_at.isoformat(),
        'reporter': incident.reporter.username
    } for incident in incidents]), 200

@incidents_bp.route('/', methods=['POST'])
@jwt_required()
def create_incident():
    current_user = get_jwt_identity()
    data = request.form
    
    try:
        new_incident = Incident(
            user_id=current_user,
            title=data['title'],
            description=data['description'],
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
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    file_type = 'image' if filename.lower().endswith(('png', 'jpg', 'jpeg')) else 'video'
                    
                    media = Media(
                        incident_id=new_incident.id,
                        file_url=filepath,
                        file_type=file_type
                    )
                    db.session.add(media)
            
            db.session.commit()
        
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
        status_update = StatusUpdate(
            incident_id=incident.id,
            admin_id=current_user.id,
            old_status=incident.status,
            new_status=data['status'],
            notes=data.get('notes')
        )
        
        incident.status = data['status']
        
        db.session.add(status_update)
        db.session.commit()
        
        # Here you would add notification logic (email/SMS)
        
        return jsonify({'message': 'Status updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400