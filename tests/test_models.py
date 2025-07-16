from ..models import User, Incident

def test_user_model(test_db):
    user = User(
        username='modeltest',
        email='model@test.com',
        password_hash='hashedpass'
    )
    test_db.session.add(user)
    test_db.session.commit()
    
    assert user.id is not None
    assert user.created_at is not None

def test_incident_model(test_db):
    user = User(username='test', email='test@test.com', password_hash='test')
    test_db.session.add(user)
    test_db.session.commit()
    
    incident = Incident(
        user_id=user.id,
        title='Model Test',
        description='Testing model',
        latitude=0.0,
        longitude=0.0
    )
    test_db.session.add(incident)
    test_db.session.commit()
    
    assert incident.id is not None
    assert incident.status == 'reported'