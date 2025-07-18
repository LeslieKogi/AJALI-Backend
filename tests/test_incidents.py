import pytest
import os
from io import BytesIO
from werkzeug.security import generate_password_hash
from app import create_app
from models import db, User, Incident, Media, StatusHistory

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4'}

    with app.app_context():
        db.create_all()
        # Create test user with properly hashed password
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            is_admin=False
        )
        db.session.add(test_user)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_token(client):
    # Login and get token
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    return response.json['access_token']

def test_get_incidents(client, auth_token):
    # Add test incidents
    incident1 = Incident(
        user_id=1,
        title='Test Incident 1',
        description='Description 1',
        type='type1',
        latitude=12.34,
        longitude=56.78
    )
    incident2 = Incident(
        user_id=1,
        title='Test Incident 2',
        description='Description 2',
        type='type2',
        latitude=23.45,
        longitude=67.89,
        status='resolved'
    )
    db.session.add_all([incident1, incident2])
    db.session.commit()

    # Test get all incidents
    response = client.get('/incidents/')
    assert response.status_code == 200
    assert len(response.json['incidents']) == 2

    # Test filter by status
    response = client.get('/incidents/?status=resolved')
    assert response.status_code == 200
    assert len(response.json['incidents']) == 1
    assert response.json['incidents'][0]['title'] == 'Test Incident 2'

def test_create_incident(client, auth_token):
    # Test successful creation
    data = {
        'title': 'New Incident',
        'description': 'Test description',
        'type': 'accident',
        'latitude': '12.34',
        'longitude': '56.78'
    }
    response = client.post(
        '/incidents/',
        data=data,
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    assert b'Incident created successfully' in response.data

    # Test missing required field
    data = {
        'title': 'New Incident',
        'description': 'Test description',
        'type': 'accident'
        # Missing latitude and longitude
    }
    response = client.post(
        '/incidents/',
        data=data,
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 400

def test_update_incident(client, auth_token):
    # Create test incident
    incident = Incident(
        user_id=1,
        title='Original Title',
        description='Original Description',
        type='type1',
        latitude=12.34,
        longitude=56.78
    )
    db.session.add(incident)
    db.session.commit()

    # Test successful update
    update_data = {
        'title': 'Updated Title',
        'description': 'Updated Description',
        'latitude': 23.45,
        'longitude': 67.89
    }
    response = client.put(
        f'/incidents/{incident.id}',
        json=update_data,
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert b'Incident updated successfully' in response.data

def test_update_incident_status(client, auth_token):
    # Create test admin user and incident
    admin_user = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('adminpassword'),
        is_admin=True
    )
    incident = Incident(
        user_id=1,
        title='Test Incident',
        description='Test Description',
        type='type1',
        latitude=12.34,
        longitude=56.78
    )
    db.session.add_all([admin_user, incident])
    db.session.commit()

    # Login as admin
    login_response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'adminpassword'
    })
    admin_token = login_response.json['access_token']

    # Test status update
    response = client.put(
        f'/incidents/{incident.id}/status',
        json={'status': 'in_progress'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    assert b'Status updated successfully' in response.data