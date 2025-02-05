import tweepy
from dotenv import load_dotenv
import os

# Load environment variables from .env file if you're using one.
load_dotenv()

# Use the variable names from your config
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
CONSUMER_KEY = os.getenv("V2_CLIENT_ID")
CONSUMER_SECRET = os.getenv("V2_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("V2_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("V2_ACCESS_SECRET")

# Print out the credentials (or parts of them) for debugging purposes.
print("CONSUMER_KEY:", repr(CONSUMER_KEY))
print("CONSUMER_SECRET:", repr(CONSUMER_SECRET))
print("ACCESS_TOKEN:", repr(ACCESS_TOKEN))
print("ACCESS_SECRET:", repr(ACCESS_SECRET))
print("BEARER_TOKEN:", repr(BEARER_TOKEN))

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication OK")
except Exception as e:
    print("Error during authentication:", e)

response = client.create_tweet(text="This tweet is from tweepy simple post testing.")

print(f"https://x.com/user/status/{response.data['id']}")