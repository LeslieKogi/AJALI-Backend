from datetime import datetime
import random

from models import db, User, Incident, Media, StatusHistory, Notification
from app import create_app  
from werkzeug.security import generate_password_hash

app = create_app()  # app instance here

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        def random_phone():
            return f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"

        def random_coordinates():
            return round(random.uniform(-90, 90), 6), round(random.uniform(-180, 180), 6)

        # Create users
        users = []
        for i in range(1, 6):
            is_admin = i == 1
            user = User(
                username=f"User {i}",
                email=f"user{i}@example.com",
                password_hash=generate_password_hash(f"password{i}"),
                phone=random_phone(),
                is_admin=is_admin
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()

        # Create incidents
        incident_types = ['Theft', 'Accident', 'Vandalism', 'Suspicious Activity', 'Other']
        statuses = ['pending', 'in_progress', 'resolved', 'rejected']
        incidents = []

        for i in range(10):
            lat, lng = random_coordinates()
            incident = Incident(
                user_id=random.choice(users).id,
                title=f"Incident Case #{i+1}",
                description=f"Detailed description of incident #{i+1}",
                type=random.choice(incident_types),
                status=random.choice(statuses),
                latitude=lat,
                longitude=lng
            )
            db.session.add(incident)
            incidents.append(incident)

        db.session.commit()

        # Add media
        media_types = ['image', 'video', 'document']
        for incident in incidents[:5]:
            for m in range(random.randint(1, 3)):
                media = Media(
                    incident_id=incident.id,
                    media_type=random.choice(media_types),
                    file_url=f"https://example.com/media/{incident.id}_{m}.jpg"
                )
                db.session.add(media)

        # Add status history
        for incident in incidents:
            current_status = 'pending'
            for _ in range(random.randint(1, 3)):
                new_status = random.choice([s for s in statuses if s != current_status])
                history = StatusHistory(
                    incident_id=incident.id,
                    changed_by="admin@example.com",
                    old_status=current_status,
                    new_status=new_status,
                    note=f"Changed from {current_status} to {new_status}"
                )
                db.session.add(history)
                current_status = new_status
            incident.status = current_status

        # Add notifications
        for user in users[:3]:
            for _ in range(random.randint(2, 4)):
                incident = random.choice(incidents)
                notification = Notification(
                    user_id=user.id,
                    incident_id=incident.id,
                    channel=random.choice(['email', 'sms']),
                    message=f"Notification for {user.username}",
                    status='sent'
                )
                db.session.add(notification)

        db.session.commit()

        print(f"Seeded: {len(users)} users, {len(incidents)} incidents")
        print(f"Media: {Media.query.count()},  StatusHistories: {StatusHistory.query.count()}")
        print(f"Notifications: {Notification.query.count()}")

if __name__ == '__main__':
    seed_database()