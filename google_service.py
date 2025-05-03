import os
import base64
from dotenv import load_dotenv, find_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText

load_dotenv(find_dotenv())
# Load environment variables
CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('GMAIL_REFRESH_TOKEN')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')

print("CLIENT_ID:", CLIENT_ID)
print("CLIENT_SECRET:", CLIENT_SECRET)
print("REFRESH_TOKEN:", REFRESH_TOKEN)
print("SENDER_EMAIL:", SENDER_EMAIL)

# Gmail API scope
SCOPES = ['https://mail.google.com/']

def get_gmail_service():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )
    creds.refresh(Request())
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(to, subject, message_text):
    message = MIMEText(message_text, 'plain')
    message['to'] = to
    message['from'] = SENDER_EMAIL
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw.decode()}

def send_email(to, subject, body):
    service = get_gmail_service()
    message = create_message(to, subject, body)
    sent_message = service.users().messages().send(userId="me", body=message).execute()
    print(f"Message sent: {sent_message['id']}")
    return sent_message
