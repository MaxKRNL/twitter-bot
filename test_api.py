#!/usr/bin/env python3
import tweepy
import os
import traceback
from config import V2_CLIENT_ID, V2_CLIENT_SECRET, V2_ACCESS_TOKEN, V2_ACCESS_SECRET

def create_api():
    """
    Create and return a Tweepy API object authenticated via OAuthHandler.
    """
    try:
        auth = tweepy.OAuthHandler(V2_CLIENT_ID, V2_CLIENT_SECRET)
        auth.set_access_token(V2_ACCESS_TOKEN, V2_ACCESS_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        # Verify credentials
        api.verify_credentials()
        print("Authentication OK")
        return api
    except Exception as e:
        print("Error during authentication")
        print(e)
        print(traceback.format_exc())
        return None

def test_post_tweet(api):
    """
    Posts a test tweet using the Tweepy API and prints the result.
    """
    test_tweet_text = "Test tweet using OAuthHandler. This is a test message."
    try:
        tweet = api.update_status(status=test_tweet_text)
        print("Tweet posted successfully!")
        print("Tweet ID:", tweet.id)
        return tweet.id
    except Exception as e:
        print("Error posting tweet:")
        print(e)
        print(traceback.format_exc())
        return None

def test_delete_tweet(api, tweet_id):
    """
    Deletes a tweet given its tweet_id using the Tweepy API and prints the result.
    """
    try:
        api.destroy_status(tweet_id)
        print("Tweet deleted successfully!")
    except Exception as e:
        print("Error deleting tweet:")
        print(e)
        print(traceback.format_exc())

if __name__ == "__main__":
    api = create_api()
    if api is None:
        print("Failed to create API. Exiting.")
        exit(1)

    tweet_id = test_post_tweet(api)
    
    if tweet_id:
        input("Press Enter to delete the test tweet...")
        test_delete_tweet(api, tweet_id)
    else:
        print("Tweet was not posted; skipping deletion.")
