# tests/test_auth.py
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
try:
    from app.models import User
except ImportError:
    raise ImportError("Ensure 'app/models.py' exists and is properly structured.")

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/ajali_test'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_register(client):
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass',
        'phone': '0712345678'
    })
    assert response.status_code == 201
    assert b'User created successfully' in response.data

def test_login(client):
    # First register a user
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass'
    })
    
    # Then test login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'testpass'
    })
    assert response.status_code == 200
    assert b'access_token' in response.data