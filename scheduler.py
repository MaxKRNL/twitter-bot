import time
import random
import logging
import torch
from datetime import datetime, timedelta

# Import your bot functions
from bot import post_tweet, reply_to_mentions

# Import the two helper functions you provided
def can_post(last_post_time):
    """Check if the bot can post based on a randomized delay (45 to 90 min)."""
    return datetime.now() - last_post_time > timedelta(minutes=random.randint(45, 90))

def can_check_replies(last_reply_check_time):
    """Check if the bot can check replies after at least 1 minute."""
    return datetime.now() - last_reply_check_time > timedelta(minutes=1)

logging.basicConfig(filename="logs/bot.log", level=logging.INFO)

def run_bot():
    """
    This function continuously runs, checking:
      - can_post(): if True, post a new tweet
      - can_check_replies(): if True, check & reply to mentions
    """

    # Initialize times so the bot can start checking right away if desired
    last_post_time = datetime.now() - timedelta(minutes=60)   # or any offset
    last_reply_check_time = datetime.now() - timedelta(minutes=5)

    while True:
        logging.info("Scheduler loop running at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 1) Check if it's time to post a tweet
        if can_post(last_post_time):
            try:
                post_tweet()
                last_post_time = datetime.now()  # Update the time after posting
                logging.info("Posted a tweet at %s", last_post_time.strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                logging.error(f"Error in post_tweet: {e}")

        # 2) Check if it's time to check for replies
        if can_check_replies(last_reply_check_time):
            try:
                reply_to_mentions()
                last_reply_check_time = datetime.now()  # Update after checking
                logging.info("Checked for replies at %s", last_reply_check_time.strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                logging.error(f"Error in reply_to_mentions: {e}")

        # Sleep a short time to avoid busy-waiting
        time.sleep(30)


if __name__ == "__main__":
    torch.cuda.empty_cache()
    run_bot()
