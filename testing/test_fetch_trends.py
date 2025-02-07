import sys
import logging
from bot import fetch_personalized_trends
import tweepy

from config import (
    BEARER_TOKEN,
    V2_CLIENT_ID,
    V2_CLIENT_SECRET,
    V2_ACCESS_TOKEN,
    V2_ACCESS_SECRET,
    POST_INTERVAL_MIN,
    POST_INTERVAL_MAX,
    MAX_REPLIES_PER_USER
)

def main():
    print("=== Testing Real Twitter API for Personalized Trends ===")

    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=V2_CLIENT_ID,
        consumer_secret=V2_CLIENT_SECRET,
        access_token=V2_ACCESS_TOKEN,
        access_token_secret=V2_ACCESS_SECRET,
        wait_on_rate_limit=True
    )

    me = client.get_me()
    user_id = me.data.id
    
    if not user_id:
        print("User ID is required!")
        sys.exit(1)
    
    try:
        trends = fetch_personalized_trends(user_id, max_results=10)
        if trends:
            print("\nFetched Personalized Trends:")
            for trend in trends:
                print("-", trend)
        else:
            print("\nNo trends found or an error occurred.")
    except Exception as e:
        print(f"\nAn exception occurred: {e}")

if __name__ == "__main__":
    main()
