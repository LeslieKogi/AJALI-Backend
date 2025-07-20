# send_incident_email.py
import os
from mailjet_rest import Client
from dotenv import load_dotenv

load_dotenv()

mailjet = Client(
    auth=(os.getenv("MJ_APIKEY_PUBLIC"), os.getenv("MJ_APIKEY_PRIVATE")),
    version='v3.1'
)

def send_incident_confirmation_email(to_email, username, incident_data):
    subject = "Incident Report Confirmation"
    message = f"""
        <h3>Hello {username},</h3>
        <p>Your incident has been successfully reported. Here are the details:</p>
        <ul>
            <li><strong>Title:</strong> {incident_data.get('title')}</li>
            <li><strong>Description:</strong> {incident_data.get('description')}</li>
            <li><strong>Location:</strong> {incident_data.get('location')}</li>
            <li><strong>Date Reported:</strong> {incident_data.get('created_at')}</li>
        </ul>
        <p>Thank you for using Ajali.</p>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "wariobaajona@gmail.com",
                    "Name": "Ajali Support"
                },
                "To": [
                    {
                        "Email": to_email,
                        "Name": username
                    }
                ],
                "Subject": subject,
                "TextPart": f"Your incident '{incident_data.get('title')}' has been reported.",
                "HTMLPart": message
            }
        ]
    }

    result = mailjet.send.create(data=data)
    return result.status_code, result.json()
