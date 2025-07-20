from mailjet_rest import Client
import os

mailjet = Client(
    auth=(os.getenv("MJ_APIKEY_PUBLIC"), os.getenv("MJ_APIKEY_PRIVATE")),
    version='v3.1'
)

def send_welcome_email(email, username):
    data = {
        "Messages": [
            {
                "From": {
                    "Email": "wariobaajona@gmail.com",
                    "Name": "Ajali App"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": username
                    }
                ],
                "Subject": "Welcome to Ajali!",
                "TextPart": f"Hello {username}, welcome to Ajali!",
                "HTMLPart": f"<h3>Hello {username},</h3><p>Welcome to Ajali, your safety partner.</p>"
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code, result.json()
