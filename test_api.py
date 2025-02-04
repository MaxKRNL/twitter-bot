#!/usr/bin/env python3
import tweepy
import os
import traceback
import time
from dotenv import load_dotenv

# Load environment variables from .env file if you're using one.
load_dotenv()

# Import your API credentials from config
# (Make sure your config file has the correct variable names or adjust accordingly)
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
CONSUMER_KEY = os.getenv("TWITTER_CLIENT_ID")
CONSUMER_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Optionally, print the credentials (or their lengths) for debugging purposes.
print("CONSUMER_KEY:", repr(CONSUMER_KEY))
print("CONSUMER_SECRET:", repr(CONSUMER_SECRET))
print("ACCESS_TOKEN:", repr(ACCESS_TOKEN))
print("ACCESS_SECRET:", repr(ACCESS_SECRET))
print("BEARER_TOKEN:", repr(BEARER_TOKEN))

# Create a Tweepy client using the provided credentials
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    wait_on_rate_limit=True
)

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
    Tests personalized trends functionality:
      1. Updates the personalized trends file.
      2. Reads and prints the trends.
    
    This example assumes you have functions to update and read personalized trends.
    For testing purposes, we simulate this by calling a dummy endpoint.
    """
    # In a production scenario, you might have a function like update_personalized_trends(file_path, max_results)
    # Here we simulate fetching personalized trends using a simple endpoint.
    print("Fetching personalized trends...")

    try:
        # For demonstration purposes, we fetch your own user information as a proxy.
        # Replace this with your actual personalized trends logic.
        response = client.get_me()
        if response.data:
            user = response.data
            print("Authenticated as:", user.username)
            # For example, pretend we have some trends based on the user's profile.
            simulated_trends = ["#Trend1", "#Trend2", "#Trend3"]
            print("Simulated Personalized Trends:")
            for trend in simulated_trends:
                print("-", trend)
        else:
            print("No user data found.")
    except Exception as e:
        print("Error fetching personalized trends:")
        print(e)
        print(traceback.format_exc())

if __name__ == "__main__":
    print("=== Testing Twitter API Functionality using tweepy.Client ===")
    
    # Test posting a tweet
    tweet_id = test_post_tweet()
    
    if tweet_id:
        input("Press Enter to delete the test tweet...")
        test_delete_tweet(tweet_id)
    else:
        print("Skipping tweet deletion since tweet was not posted.")
    
    print("\n=== Testing Personalized Trends Functionality ===")
    test_personalized_trends()
