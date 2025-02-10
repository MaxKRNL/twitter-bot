import time
import random
import logging
import torch
from datetime import datetime, timedelta

# Import your bot functions
from bot import post_tweet, reply_to_mentions, process_direct_messages

def can_post(last_post_time):
    """Check if the bot can post based on a randomized delay (45 to 90 min)."""
    return datetime.now() - last_post_time > timedelta(minutes=random.randint(45, 90))

def can_check_mentions(last_mention_check_time):
    """Check if the bot can check mentions after at least 15 minute."""
    return datetime.now() - last_mention_check_time > timedelta(minutes=15)

def can_check_dm(last_dm_check_time):
    """Check if the bot can check dm interaction with admin account """
    return datetime.now() - last_dm_check_time > timedelta(minutes=15)

logging.basicConfig(filename="logs/bot.log", level=logging.INFO)

def run_bot():
    """
    Continuously runs, checking:
      - can_post(): if True, post a new tweet (after printing it to terminal)
      - can_check_mentions(): if True, check & reply to mentions (printing replies to terminal)
    """
    # Initialize times so the bot can start checking right away if desired
    last_post_time = datetime.now() - timedelta(minutes=60)
    last_mention_check_time = datetime.now() - timedelta(minutes=15)
    last_dm_check_time = datetime.now() - timedelta(minutes=15)

    while True:
        logging.info("Scheduler loop running at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("Scheduler loop running at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if can_post(last_post_time):
            try:
                post_tweet()
                last_post_time = datetime.now()  # Update the time after posting
                logging.info("Posted a tweet at %s", last_post_time.strftime("%Y-%m-%d %H:%M:%S"))
                print("Posted a tweet at %s", last_post_time.strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                logging.error(f"Error in post_tweet: {e}")

        if can_check_mentions(last_mention_check_time):
            try:
                reply_to_mentions()
                last_mention_check_time = datetime.now()  # Update after checking
                logging.info("Checked for replies at %s", last_mention_check_time.strftime("%Y-%m-%d %H:%M:%S"))
                print("Checked for replies at %s", last_mention_check_time.strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                logging.error(f"Error in reply_to_mentions: {e}")

        if can_check_dm(last_dm_check_time):
            try:
                process_direct_messages()
                last_dm_check_time = datetime.now()
                logging.info("Checked for dm at %s", last_dm_check_time.strftime("%Y-%m-%d %H:%M:%S"))
                print("Checked for dm at %s", last_dm_check_time.strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                logging.error(f"Error in process_direct_messages: {e}")


        time.sleep(30)

if __name__ == "__main__":
    torch.cuda.empty_cache()
    run_bot()
