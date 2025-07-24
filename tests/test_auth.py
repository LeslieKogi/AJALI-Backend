import pytest
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    # Test successful registration
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'phone': '1234567890'
    })
    assert response.status_code == 201
    assert b'User created successfully' in response.data

    # Test duplicate email
    response = client.post('/auth/register', json={
        'username': 'testuser2',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    assert b'Email already exists' in response.data

def test_login(client):
    # First register a user
    client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })

    # Test successful login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b'access_token' in response.data

    # Test invalid credentials
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_get_current_user(client):
    # Register and login
    client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']

    # Test protected route
    response = client.get('/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert b'testuser' in response.data