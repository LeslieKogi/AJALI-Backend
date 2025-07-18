import pytest
from datetime import datetime
from models import db, User, Incident, Media, StatusHistory, Notification
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_user_model(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashedpassword'
        )
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == 'testuser'
        assert user.created_at is not None

def test_incident_model(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashedpassword'
        )
        db.session.add(user)
        db.session.commit()

        incident = Incident(
            user_id=user.id,
            title='Test Incident',
            description='Test Description',
            type='accident',
            latitude=12.34,
            longitude=56.78
        )
        db.session.add(incident)
        db.session.commit()

        assert incident.id is not None
        assert incident.user_id == user.id
        assert incident.status == 'pending'

def test_media_model(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashedpassword'
        )
        incident = Incident(
            user_id=1,
            title='Test Incident',
            description='Test Description',
            type='accident',
            latitude=12.34,
            longitude=56.78
        )
        db.session.add_all([user, incident])
        db.session.commit()

        media = Media(
            incident_id=incident.id,
            file_url='/path/to/file.jpg',
            media_type='image'
        )
        db.session.add(media)
        db.session.commit()

        assert media.id is not None
        assert media.incident_id == incident.id

def test_status_history_model(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashedpassword'
        )
        incident = Incident(
            user_id=1,
            title='Test Incident',
            description='Test Description',
            type='accident',
            latitude=12.34,
            longitude=56.78
        )
        db.session.add_all([user, incident])
        db.session.commit()

        status_history = StatusHistory(
            incident_id=incident.id,
            old_status='pending',
            new_status='in_progress'
        )
        db.session.add(status_history)
        db.session.commit()

        assert status_history.id is not None
        assert status_history.changed_at is not None