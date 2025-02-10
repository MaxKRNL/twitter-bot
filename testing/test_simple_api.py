#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import tweepy
import traceback

# Load your environment variables
load_dotenv()

# Use the variable names from your config
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
CONSUMER_KEY = os.getenv("V2_CLIENT_ID")
CONSUMER_SECRET = os.getenv("V2_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("V2_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("V2_ACCESS_TOKEN_SECRET")

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")

# Print out the credentials (or parts of them) for debugging purposes.
print("CONSUMER_KEY:", repr(CONSUMER_KEY))
print("CONSUMER_SECRET:", repr(CONSUMER_SECRET))
print("ACCESS_TOKEN:", repr(ACCESS_TOKEN))
print("ACCESS_SECRET:", repr(ACCESS_SECRET))
print("BEARER_TOKEN:", repr(BEARER_TOKEN))


try:
    # Create a Tweepy client using the provided credentials
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET,
        wait_on_rate_limit=True
    )
    # Try a simple call to verify authentication:
    response = client.get_me()
    if response.data:
        print("Authenticated as:", response.data.username)
    else:
        print("No user data returned.")
except Exception as e:
    print("Error during authentication:")
    print(e)
    print(traceback.format_exc())
