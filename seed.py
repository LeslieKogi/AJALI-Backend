import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from random import uniform, choice
from faker import Faker
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app import create_app, db
from .models import User, Incident, Media, StatusUpdate

app = create_app()
app.app_context().push()

fake = Faker()

def seed_users():
    print("Seeding users...")
    #Admin user
    admin = User(
        username='admin',
        email='admin@ajali.com',
        password_hash=generate_password_hash('Admin123!'),
        phone='+254700000000',
        is_admin=True
    )
    db.session.add(admin)

    #users
    for i in range(1, 6):
        user = User(
            username=f'user{i}',
            email=f'user{i}@ajali.com',
            password_hash=generate_password_hash(f'User{i}123!'),
            phone=fake.phone_number()
        )
        db.session.add(user)
    
    db.session.commit()

def seed_incidents():
    print("Seeding incidents...")
    users = User.query.all()
    statuses = ['reported', 'under_investigation', 'resolved', 'rejected']
    
    # Nairobi coordinates boundaries
    min_lat, max_lat = -1.35, -1.20
    min_lng, max_lng = 36.75, 36.90

    for i in range(1, 21):
        incident = Incident(
            user_id=choice(users).id,
            title=fake.sentence(),
            description=fake.paragraph(),
            latitude=uniform(min_lat, max_lat),
            longitude=uniform(min_lng, max_lng),
            status=choice(statuses),
            created_at=datetime.utcnow() - timedelta(days=uniform(0, 30))
        )
        db.session.add(incident)
    
    db.session.commit()

def seed_status_updates():
    print("Seeding status updates...")
    incidents = Incident.query.all()
    admin = User.query.filter_by(is_admin=True).first()

    for incident in incidents:
        if incident.status != 'reported':
            update = StatusUpdate(
                incident_id=incident.id,
                admin_id=admin.id,
                old_status='reported',
                new_status=incident.status,
                notes=fake.sentence(),
                created_at=incident.created_at + timedelta(hours=2)
            )
            db.session.add(update)
    
    db.session.commit()

def seed_media():
    print("Seeding media...")
    incidents = Incident.query.all()
    media_types = ['image', 'video']
    
    for incident in incidents:
        # 50% chance to add media
        if choice([True, False]):
            media = Media(
                incident_id=incident.id,
                file_url=f"uploads/{fake.file_name(extension=choice(['jpg', 'png', 'mp4']))}",
                file_type=choice(media_types),
                created_at=incident.created_at + timedelta(minutes=30)
            )
            db.session.add(media)
    
    db.session.commit()

def main():
    print("Starting database seeding...")
    seed_users()
    seed_incidents()
    seed_status_updates()
    seed_media()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    main()