#!/usr/bin/env python3
import tweepy
import os
import traceback
import time
from dotenv import load_dotenv

# Load environment variables from .env file if you're using one.
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

# Create a Tweepy client using the provided credentials
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    # consumer_key=API_KEY,
    # consumer_secret=API_KEY_SECRET,
    # access_token=ACCESS_TOKEN,
    # access_token_secret=ACCESS_SECRET,
    # wait_on_rate_limit=True
)

def fetch_tweet():
    try:
        me = client.get_me()
        my_user_id = me.data.id
    except Exception as e:
        print(f"Couldn't fetch user info: {e}")
        return

    try:
        mentions_response = client.get_users_mentions(
            id=my_user_id,
            # expansions="author_id",
            # tweet_fields=["author_id", "text"],
            # user_field=["public_metrics"]
        )
    except Exception as e:
        print(f"Error fetching mentions: {e}")
        return
    
    user_map = {}
    if mentions_response.includes and "users" in mentions_response.includes:
        for u in mentions_response.includes["users"]:
            user_map[u.id] = u

    for mention_tweet in mentions_response.data:
        mention_id = mention_tweet.id
        print(f"mention id: {mention_id}")

        author_id = mention_tweet.author_id
        print(f"author_id: {author_id}")
        if author_id not in user_map:
            continue

        user_obj = user_map[author_id]
        author_username = user_obj.username
        mention_text = mention_tweet.text

        print(f"Author_username: {author_username}")
        print(f"Mention text: {mention_text}")

    
    follower_count = 0
    if user_obj.public_metrics and "followers_count" in user_obj.public_metrics:
        follower_count = user_obj.public_metrics["followers_count"]

    print(f"The follower counts: {follower_count}")

if __name__ == "__main__":
    print("=== Testing Twitter Mention fetching using tweepy == ")
    fetch_tweet()