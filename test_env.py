# test_env.py

from dotenv import load_dotenv, find_dotenv
import os

print("Looking for .env at:", find_dotenv())
load_dotenv(find_dotenv())

print("GMAIL_CLIENT_ID:", os.getenv("GMAIL_CLIENT_ID"))
print("GMAIL_CLIENT_SECRET:", os.getenv("GMAIL_CLIENT_SECRET"))
print("GMAIL_REFRESH_TOKEN:", os.getenv("GMAIL_REFRESH_TOKEN"))
print("SENDER_EMAIL:", os.getenv("SENDER_EMAIL"))
