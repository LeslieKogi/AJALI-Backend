import sys
import os
import pytest
from werkzeug.security import generate_password_hash

# Ensure the parent directory (containing 'app') is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from app import create_app
from app import db as _db
from app.models import User, Incident, Media, StatusUpdate

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.from_object('config.TestConfig')
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def test_db(test_app):
    _db.create_all()
    yield _db
    _db.drop_all()

@pytest.fixture
def client(test_app, test_db):
    with test_app.test_client() as client:
        yield client

@pytest.fixture
def auth_tokens(client):
    # Create test user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass'
    }
    client.post('/api/auth/register', json=user_data)
    
    # Login and get token
    res = client.post('/api/auth/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    return res.json['access_token']

@pytest.fixture
def admin_tokens(client, test_db):
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('adminpass'),
        is_admin=True
    )
    test_db.session.add(admin)
    test_db.session.commit()
    
    # Login and get token
    res = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': 'adminpass'
    })
    return res.json['access_token']