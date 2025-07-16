from flask import Flask
from models import db, User, Incident, Media, StatusHistory, Notification
from datetime import datetime, timedelta
import random

# Create Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Sample data generators
        def random_phone():
            return f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"

        def random_coordinates():
            return round(random.uniform(-90, 90), 6), round(random.uniform(-180, 180), 6)

        # Create test users
        users = []
        for i in range(1, 6):
            is_admin = i == 1  # First user is admin
            user = User(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password_hash=f"hashed_password_{i}",
                phone_number=random_phone(),
                is_admin=is_admin
            )
            users.append(user)
            db.session.add(user)
        
        # Commit users first to ensure they have IDs
        db.session.commit()

        # Create test incidents - now with valid user IDs
        incident_types = ['Theft', 'Accident', 'Vandalism', 'Suspicious Activity', 'Other']
        statuses = ['pending', 'in_progress', 'resolved', 'rejected']

        incidents = []
        for i in range(1, 11):
            user = random.choice(users)
            lat, lng = random_coordinates()
            incident = Incident(
                user_id=user.id,  # Now using the committed user's ID
                title=f"Incident Case #{i}",
                description=f"Detailed description of incident #{i}",
                type=random.choice(incident_types),
                status=random.choice(statuses),
                latitude=lat,
                longitude=lng
            )
            incidents.append(incident)
            db.session.add(incident)

        # Commit incidents before creating related records
        db.session.commit()

        # Create media for incidents
        media_types = ['image', 'video', 'document']
        for incident in incidents[:5]:
            for m in range(1, random.randint(2, 4)):
                media = Media(
                    incident_id=incident.id,
                    media_type=random.choice(media_types),
                    file_url=f"https://example.com/media/{incident.id}_{m}.jpg"
                )
                db.session.add(media)

        # Create status history
        for incident in incidents:
            status_changes = random.randint(1, 3)
            current_status = 'pending'
            
            for change in range(status_changes):
                new_status = random.choice([s for s in statuses if s != current_status])
                history = StatusHistory(
                    incident_id=incident.id,
                    changed_by=f"admin@example.com",
                    old_status=current_status,
                    new_status=new_status,
                    note=f"Status changed from {current_status} to {new_status}"
                )
                db.session.add(history)
                current_status = new_status
            
            # Update incident to latest status
            incident.status = current_status

        # Create notifications
        for user in users[:3]:
            for n in range(1, random.randint(2, 5)):
                incident = random.choice(incidents) if random.choice([True, False]) else None
                notification = Notification(
                    user_id=user.id,
                    incident_id=incident.id if incident else None,
                    channel=random.choice(['email', 'sms']),
                    message=f"Notification {n} for {user.name}",
                    status='sent'
                )
                db.session.add(notification)

        # Final commit
        db.session.commit()

        print("Successfully seeded database with:")
        print(f"- {len(users)} users")
        print(f"- {len(incidents)} incidents")
        print(f"- {Media.query.count()} media items")
        print(f"- {StatusHistory.query.count()} status changes")
        print(f"- {Notification.query.count()} notifications")

if __name__ == '__main__':
    seed_database()