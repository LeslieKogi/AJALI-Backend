from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from flasgger.utils import swag_from
from extensions import db
from models import Incident, Media, StatusHistory, User
from datetime import datetime
import os

incidents_bp = Blueprint('incidents', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@incidents_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Incidents'],
    'parameters': [
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter incidents by status (e.g., pending, resolved)'
        }
    ],
    'responses': {
        200: {
            'description': 'List of incidents',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'title': {'type': 'string'},
                        'description': {'type': 'string'},
                        'latitude': {'type': 'number'},
                        'longitude': {'type': 'number'},
                        'status': {'type': 'string'},
                        'created_at': {'type': 'string'},
                        'reporter': {'type': 'string'}
                    }
                }
            }
        }
    }
})
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
        'reporter': incident.user.name if incident.user else 'Unknown'
    } for incident in incidents]), 200


@incidents_bp.route('/', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Incidents'],
    'consumes': ['multipart/form-data'],
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'title', 'in': 'formData', 'type': 'string', 'required': True},
        {'name': 'description', 'in': 'formData', 'type': 'string', 'required': True},
        {'name': 'latitude', 'in': 'formData', 'type': 'number', 'required': True},
        {'name': 'longitude', 'in': 'formData', 'type': 'number', 'required': True},
        {'name': 'files', 'in': 'formData', 'type': 'file', 'required': False, 'description': 'Incident media'}
    ],
    'responses': {
        201: {'description': 'Incident created successfully'},
        400: {'description': 'Error creating incident'},
        401: {'description': 'Unauthorized'}
    }
})
def create_incident():
    current_user = get_jwt_identity()
    data = request.form

    try:
        new_incident = Incident(
            user_id=current_user,
            title=data['title'],
            description=data['description'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            created_at=datetime.utcnow()
        )

        db.session.add(new_incident)
        db.session.commit()

        # Handle media uploads
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    ext = filename.rsplit('.', 1)[1].lower()
                    file_type = 'image' if ext in ['jpg', 'jpeg', 'png'] else 'video' if ext in ['mp4', 'avi', 'mov'] else 'file'

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
@swag_from({
    'tags': ['Incidents'],
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'latitude': {'type': 'number'},
                    'longitude': {'type': 'number'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Incident updated successfully'},
        403: {'description': 'Unauthorized'},
        404: {'description': 'Incident not found'},
        400: {'description': 'Error updating incident'}
    }
})
def update_incident(id):
    current_user = get_jwt_identity()
    incident = Incident.query.get_or_404(id)

    if incident.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()

    try:
        incident.title = data.get('title', incident.title)
        incident.description = data.get('description', incident.description)
        incident.latitude = data.get('latitude', incident.latitude)
        incident.longitude = data.get('longitude', incident.longitude)

        db.session.commit()
        return jsonify({'message': 'Incident updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@incidents_bp.route('/<int:id>/status', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Incidents'],
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'properties': {
                    'status': {'type': 'string'},
                    'notes': {'type': 'string'}
                },
                'required': ['status']
            }
        }
    ],
    'responses': {
        200: {'description': 'Status updated successfully'},
        403: {'description': 'Unauthorized (admin required)'},
        404: {'description': 'Incident not found'},
        400: {'description': 'Error updating status'}
    }
})
def update_incident_status(id):
    current_user = User.query.get(get_jwt_identity())

    if not current_user.is_admin:
        return jsonify({'message': 'Unauthorized'}), 403

    incident = Incident.query.get_or_404(id)
    data = request.get_json()

    try:
        status_update = StatusHistory(
            incident_id=incident.id,
            changed_by=current_user.email,
            old_status=incident.status,
            new_status=data['status'],
            note=data.get('notes', '')
        )

        incident.status = data['status']

        db.session.add(status_update)
        db.session.commit()

        return jsonify({'message': 'Status updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400
