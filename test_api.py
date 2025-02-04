#!/usr/bin/env python3
import tweepy
import traceback
import time
from config import (
    BEARER_TOKEN,
    V2_CLIENT_ID,
    V2_CLIENT_SECRET,
    V2_ACCESS_TOKEN,
    V2_ACCESS_SECRET
)
from bot import (
    fetch_personalized_trends,
    update_personalized_trends,
    read_personalized_trends
)

# Initialize the Twitter client using your credentials
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=V2_CLIENT_ID,
    consumer_secret=V2_CLIENT_SECRET,
    access_token=V2_ACCESS_TOKEN,
    access_token_secret=V2_ACCESS_SECRET,
    wait_on_rate_limit=True
)

def test_post_tweet():
    """Posts a test tweet and prints the response."""
    test_tweet_text = "Test tweet from API. This is a test message."
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
    """Deletes a tweet given its tweet_id and prints the result."""
    try:
        response = client.delete_tweet(tweet_id)
        print("Tweet deleted successfully!")
        print("Response:", response)
    except Exception as e:
        print("Error deleting tweet:")
        print(e)
        print(traceback.format_exc())

def test_personalized_trends():
    """Tests personalized trends functionality:
       1. Updates the personalized trends file.
       2. Reads and prints the trends.
    """
    # Use a temporary file name for testing so we don't overwrite production trends.
    test_trends_file = "personalized_trends_test.txt"
    print("Updating personalized trends...")
    try:
        update_personalized_trends(file_path=test_trends_file, max_results=10)
    except Exception as e:
        print("Error updating personalized trends:")
        print(e)
        print(traceback.format_exc())
        return

    # Give it a moment if necessary (some endpoints may be slow)
    time.sleep(2)
    
    trends = read_personalized_trends(file_path=test_trends_file)
    if trends:
        print("Personalized Trends:")
        for trend in trends:
            print("-", trend)
    else:
        print("No personalized trends found.")

if __name__ == "__main__":
    print("=== Testing Twitter API Functionality ===")
    
    # Test posting a tweet
    tweet_id = test_post_tweet()
    
    if tweet_id:
        input("Press Enter to delete the test tweet...")
        test_delete_tweet(tweet_id)
    else:
        print("Skipping tweet deletion since tweet was not posted.")
    
    print("\n=== Testing Personalized Trends Functionality ===")
    test_personalized_trends()
