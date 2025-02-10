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
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    wait_on_rate_limit=True
)

# client = tweepy.Client(
#     bearer_token=BEARER_TOKEN
# )

def test_post_tweet():
    """Posts a test tweet using tweepy.Client and prints the response."""
    test_tweet_text = "Test tweet using tweepy.Client. This is a test message."
    try:
        response = client.create_tweet(text=test_tweet_text)
        tweet_id = response.data["id"]
        print("Tweet posted successfully!")
        print("Tweet ID:", tweet_id)
        return tweet_id
    except Exception as e:
        print("Error posting tweet:")
        print(e)
        print(traceback.format_exc())
        return None

def test_delete_tweet(tweet_id):
    """Deletes a tweet given its tweet_id using tweepy.Client and prints the result."""
    try:
        response = client.delete_tweet(tweet_id)
        print("Tweet deleted successfully!")
        print("Response:", response)
    except Exception as e:
        print("Error deleting tweet:")
        print(e)
        print(traceback.format_exc())

def test_personalized_trends():
    """
    Tests personalized trends functionality by calling get_me().
    (Replace this with your actual trends logic as needed.)
    """
    print("Fetching personalized trends...")

    try:
        response = client.get_me()
        if response.data:
            user = response.data
            print("Authenticated as:", user.username)
            # Simulate personalized trends (replace with actual logic)
            simulated_trends = ["Crypto", "Food", "Finance"]
            print("Simulated Personalized Trends:")
            for trend in simulated_trends:
                print("-", trend)
        else:
            print("No user data returned.")
    except Exception as e:
        print("Error fetching personalized trends:")
        print(e)
        print(traceback.format_exc())

if __name__ == "__main__":
    # print("=== Testing Twitter API Functionality using tweepy.Client ===")
    
    # Test posting a tweet
    tweet_id = test_post_tweet()
    
    if tweet_id:
        input("Press Enter to delete the test tweet...")
        test_delete_tweet(tweet_id)
    else:
        print("Skipping tweet deletion since tweet was not posted.")
    
    print("\n=== Testing Personalized Trends Functionality ===")
    test_personalized_trends()
