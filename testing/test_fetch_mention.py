#!/usr/bin/env python3
import tweepy
import os
import traceback
import time
from dotenv import load_dotenv


# Load environment variables from .env file if you're using one.
load_dotenv()

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
# CONSUMER_KEY = os.getenv("V2_CLIENT_ID")
# CONSUMER_SECRET = os.getenv("V2_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("V2_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("V2_ACCESS_TOKEN_SECRET")

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")

# Print out the credentials (or parts of them) for debugging purposes.
# print("CONSUMER_KEY:", repr(CONSUMER_KEY))
# print("CONSUMER_SECRET:", repr(CONSUMER_SECRET))
print("ACCESS_TOKEN:", repr(ACCESS_TOKEN))
print("ACCESS_SECRET:", repr(ACCESS_SECRET))
print("BEARER_TOKEN:", repr(BEARER_TOKEN))

# Create a Tweepy client using the provided credentials
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    wait_on_rate_limit=True
)

def fetch_tweet():
    # try:
    #     me = client.get_me()
    #     my_user_id = me.data.id
    #     print(f"My ID: {my_user_id}")
    # except Exception as e:
    #     print(f"Couldn't fetch user info: {e}")
    #     return

    try:
        my_user_id = client.get_me().data.id
        print("Before getting mentions")

        response = client.get_users_mentions(my_user_id, tweet_fields=["created_at", "author_id"])
        print('successful')

        # By default, only the ID and text fields of each Tweet will be returned
        # for tweet in response.data:
        #     print(tweet.id)
        #     print(tweet.text)

    except Exception as e:
        print(f"Error fetching mentions: {e}")
        return


if __name__ == "__main__":
    print("=== Testing Twitter Mention fetching using tweepy == ")
    fetch_tweet()