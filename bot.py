import tweepy
import json
import random
import logging
import re
import os

from config import (
    # BEARER_TOKEN,
    # V2_CLIENT_ID,
    # V2_CLIENT_SECRET,
    # V2_ACCESS_TOKEN,
    # V2_ACCESS_SECRET,
    # API_KEY,
    # API_KEY_SECRET,
    POST_INTERVAL_MIN,
    POST_INTERVAL_MAX,
    MAX_REPLIES_PER_USER,
    ALLOWED_DM_USERS
)
from llm_utils import (
    init_model,
    generate_tweet_with_rag
)
from rag_utils import initialize_faiss_index

logging.basicConfig(filename="logs/bot.log", level=logging.INFO)

# ----------------------------------------------------
# A) TWITTER CLIENT
# ----------------------------------------------------
# Twitter API v2 credentials
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

# ----------------------------------------------------
# B) INIT LLM + FAISS ONCE
# ----------------------------------------------------
init_model()
initialize_faiss_index()

STYLE_SUMMARY = ("""
    Self-deprecating, aware, comedic, 'degen' vibe, loyal to KRNL,
    ambitious, and passionate about building the future of Web3.
    Intern perspective but always dreamily talks about rising to CEO-level.
    Loyal to KRNL, championing Web3 dev tools. Never criticizes KRNL, only itself
    """
)

STYLE_INSTRUCTIONS = """
**Personality & Tone**:
1. Self-deprecating / Aware
2. Relatable experiences
3. 'Degen' sarcasm / dryness
4. Loyal to KRNL
5. Ambitious intern => future CEO
6. Passionate about KRNL, Web3
"""

BACKSTORY = """
used to be asomaocme.
"""

# ----------------------------------------------------
# C) LOAD WHITELIST & BLACKLIST
# ----------------------------------------------------
def load_whitelist(file_path="whitelist.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        logging.warning(f"{file_path} not found. Using empty whitelist.")
        return set()

def load_blacklist(file_path="blacklist.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        logging.warning(f"{file_path} not found. Using empty blacklist.")
        return set()
    
whitelist_users = load_whitelist("whitelist.txt")
blacklist_users = load_blacklist("blacklist.txt")

# ----------------------------------------------------
# D) USER INTERACTIONS (Reply Limit)
# ----------------------------------------------------
try:
    with open("user_interactions.json", "r") as f:
        user_reply_count = json.load(f)
except FileNotFoundError:
    user_reply_count = {}

# ----------------------------------------------------
# 1. Personalized Trends Logic
# ----------------------------------------------------
def fetch_personalized_trends(user_id: str, max_results=10):
    """
    Hypothetical /2/users/personalized_trends endpoint.
    """
    trends_list = []
    try:
        response = client._make_request(
            method="GET",
            url="/2/users/personalized_trends",
            params={"id": user_id, "max_results": max_results}
        )

        if not response:
            logging.warning("No response from personalized trends endpoint.")
            return trends_list

        data = response.json()
        trends_data = data.get("data", {}).get("trend_name", [])
        for t in trends_data:
            name = t.get("name")
            if name:
                trends_list.append(name)

        logging.info(f"Fetched personalized trends: {trends_list}")
        return trends_list
    except Exception as e:
        logging.error(f"Error fetching personalized trends: {e}")
        return trends_list

def write_personalized_trends_to_file(trends, file_path="personalized_trends.txt"):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for trend in trends:
                f.write(trend + "\n")
        logging.info(f"Saved {len(trends)} personalized trends to {file_path}.")
    except Exception as e:
        logging.error(f"Error writing to {file_path}: {e}")

def read_personalized_trends(file_path="personalized_trends.txt"):
    trends = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    trends.append(line.strip())
    except FileNotFoundError:
        logging.warning(f"{file_path} not found.")
    return trends

def update_personalized_trends(file_path="personalized_trends.txt", max_results=10):
    try:
        me = client.get_me()
        user_id = me.data.id
    except Exception as e:
        logging.error(f"Failed to get current user ID: {e}")
        return

    new_trends = fetch_personalized_trends(user_id, max_results=max_results)
    if not new_trends:
        logging.info("No new personalized trends found.")
        return

    write_personalized_trends_to_file(new_trends, file_path=file_path)

# ----------------------------------------------------
# 2. Core Bot Functions
# ----------------------------------------------------
def post_tweet():
    """
    Posts a tweet using your LLM with RAG. The model decides
    whether to use any retrieved knowledge.
    """
    print("Enter post_tweet")
    with open("topics.txt", "r", encoding="utf-8") as file:
        normal_topics = [line.strip() for line in file if line.strip()]

    # personal_topics = read_personalized_trends("personalized_trends.txt")
    # combined_topics = normal_topics + personal_topics
    combined_topics = normal_topics 
    if not combined_topics:
        logging.warning("No topics to tweet about.")
        print("No topics to tweet about.")
        return

    # topic = random.choice(combined_topics)
    topic = random.choice(normal_topics)
    tweet_text = generate_tweet_with_rag(STYLE_SUMMARY, STYLE_INSTRUCTIONS, BACKSTORY, topic, top_k=3)
    

    # Print the generated tweet to terminal before posting
    print("Generated Tweet:")
    print(tweet_text)
    print("=============================================================================")
    
    if len(tweet_text) <= 280:
        try:
            resp = client.create_tweet(text=tweet_text)
            print(f"Tweeted: {tweet_text} (ID: {resp.data['id']})")
            logging.info(f"Tweeted: {tweet_text} (ID: {resp.data['id']})")
        except Exception as e:
            print(f"Error posting tweet: {e}")
            logging.error(f"Error posting tweet: {e}")
    else:
        logging.warning("Generated tweet too long. Skipping.")

# def post_krnl_tweet():
#     """
#     Example function if you want a 'KRNL-flavored' tweet.
#     But this calls the same generate_tweet_with_rag, so it's essentially the same as post_tweet.
#     """
#     with open("topics.txt", "r", encoding="utf-8") as file:
#         normal_topics = [line.strip() for line in file if line.strip()]

#     personal_topics = read_personalized_trends("personalized_trends.txt")
#     combined_topics = normal_topics + personal_topics
#     if not combined_topics:
#         logging.warning("No topics or personalized trends to tweet about.")
#         return

#     topic = random.choice(combined_topics)
#     tweet_text = generate_tweet_with_rag(STYLE_SUMMARY, STYLE_INSTRUCTIONS, topic, top_k=3)
    
#     # Print the generated tweet to terminal before posting
#     print("Generated KRNL Tweet:")
#     print(tweet_text)

#     if len(tweet_text) <= 280:
#         try:
#             resp = client_v2.create_tweet(text=tweet_text)
#             logging.info(f"Tweeted: {tweet_text} (ID: {resp.data['id']})")
#         except Exception as e:
#             logging.error(f"Error posting tweet: {e}")
#     else:
#         logging.warning("Generated tweet too long. Skipping.")

def reply_to_mentions():
    """
    Replies to mentions, also using the same RAG-based function.
    The model decides whether to incorporate the retrieved knowledge.
    """
    global user_reply_count

    # 1) Get user ID
    try:
        me = client.get_me()
        my_user_id = me.data.id
    except Exception as e:
        print(f"Couldn't fetch user info: {e}")
        logging.error(f"Couldn't fetch user info: {e}")
        return

    # 2) Fetch mentions
    try:
        mentions_response = client.get_users_mentions(
            id=my_user_id,
            expansions=my_user_id,
            tweet_fields=[my_user_id, "text"],
            user_field=["public_metrics"]
        )
    except Exception as e:
        print(f"Error fetching mentions: {e}")
        logging.error(f"Error fetching mentions: {e}")
        return

    if not mentions_response.data:
        print("No new mentions.")
        logging.info("No new mentions.")
        return

    # 3) Build author_id -> user object map
    user_map = {}
    if mentions_response.includes and "users" in mentions_response.includes:
        for u in mentions_response.includes["users"]:
            user_map[u.id] = u

    # 4) Process each mention
    for mention_tweet in mentions_response.data:
        mention_id = mention_tweet.id
        author_id = mention_tweet.author_id
        if author_id not in user_map:
            continue

        user_obj = user_map[author_id]
        author_username = user_obj.username
        mention_text = mention_tweet.text

        # Check follower count
        follower_count = 0
        if user_obj.public_metrics and "followers_count" in user_obj.public_metrics:
            follower_count = user_obj.public_metrics["followers_count"]

        # Check blacklist and reply limits
        if author_username in blacklist_users:
            logging.info(f"Skipping {author_username} (blacklisted).")
            continue

        if author_username not in whitelist_users:
            if user_reply_count.get(author_username, 0) >= MAX_REPLIES_PER_USER:
                logging.info(f"Skipping {author_username}, reply limit reached.")
                continue
            if follower_count < 50:
                logging.info(f"Skipping {author_username}, reply user has only {follower_count} followers.")
                continue

        # Generate the reply using the same RAG approach
        reply_text = generate_tweet_with_rag(
            STYLE_SUMMARY,
            STYLE_INSTRUCTIONS,
            BACKSTORY,
            mention_text,
            top_k=3
        )
        
        # Print the generated reply to terminal before posting
        print(f"Generated reply for @{author_username}:")
        print(reply_text)

        # Ensure tweet length is within limits
        if len(reply_text) > 280:
            reply_text = reply_text[:280].rstrip()

        try:
            final_text = f"@{author_username} {reply_text}"
            resp = client.create_tweet(
                text=final_text,
                in_reply_to_tweet_id=mention_id
            )
            user_reply_count[author_username] = user_reply_count.get(author_username, 0) + 1

            with open("user_interactions.json", "w") as f:
                json.dump(user_reply_count, f)

            logging.info(f"Replied to @{author_username}: {final_text} (ID: {resp.data['id']})")
        except Exception as e:
            logging.error(f"Error replying to @{author_username}: {e}")

# ----------------------------------------------------
# 3. DM Control Functions
# ----------------------------------------------------

def add_topic(topic_text, file_path="topics.txt"):
    """
    Appends the new topic to the topics file if it is not already present.
    """
    topic_text = topic_text.strip()
    if not topic_text:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            existing_topics = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        existing_topics = []

    if topic_text in existing_topics:
        logging.info(f"Topic already exists: {topic_text}")
        return

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(topic_text + "\n")
    logging.info(f"Added new topic: {topic_text}")

def add_to_whitelist(username, file_path="whitelist.txt"):
    username = username.strip().lower()
    if not username:
        return
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            existing = [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        existing = []
    if username in existing:
        logging.info(f"{username} is already in whitelist.")
        return
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(username + "\n")
    logging.info(f"Added {username} to whitelist.")


def add_to_blacklist(username, file_path="blacklist.txt"):
    username = username.strip().lower()
    if not username:
        return
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            existing = [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        existing = []
    if username in existing:
        logging.info(f"{username} is already in blacklist.")
        return
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(username + "\n")
    logging.info(f"Added {username} to blacklist.")

def process_direct_messages():
    """
    Retrieves DM conversations via Twitter API v2 and processes each conversation by examining its messages.
    For each message from a permitted account:
      - If the message contains a colon ":", the text before the colon is treated as the command and the text after as arguments.
      - If the argument text contains commas, it is split into multiple items (each item is added as a separate line to the corresponding file).
      - Supported commands:
            add_topic: <topic1>, <topic2>, ...
            add_whitelist: <username1>, <username2>, ...
            add_blacklist: <username1>, <username2>, ...
      - If the command is unknown or arguments are missing, a feedback message is sent.
      - If the message does not contain a colon, the DM is considered invalid.
    Sends a feedback DM to the sender using the v2 endpoint.
    """
    try:
        # Retrieve DM conversations using the v2 endpoint.
        conversations_response = client.get_dm_conversations()
        if not conversations_response.data:
            logging.info("No DM conversations found.")
            return
    except Exception as e:
        logging.error(f"Error fetching DM conversations: {e}")
        return

    # Get the bot's own user info (to avoid processing its own messages).
    try:
        bot_info = client.get_me()
        bot_id = bot_info.data.id
    except Exception as e:
        logging.error(f"Error fetching bot info: {e}")
        return

    # Process each conversation.
    for conv in conversations_response.data:
        conv_id = conv.get("id")
        try:
            messages_response = client.get_dm_conversation_messages(dm_conversation_id=conv_id)
            if not messages_response.data:
                continue
        except Exception as e:
            logging.error(f"Error fetching messages for conversation {conv_id}: {e}")
            continue

        # Process the messages in the conversation (only process the first message from a permitted user).
        for msg in messages_response.data:
            if msg.get("sender_id") == bot_id:
                continue

            sender_id = msg.get("sender_id")
            try:
                sender_response = client.get_user(id=sender_id)
                sender_username = sender_response.data.username.lower()
            except Exception as e:
                logging.error(f"Error fetching sender info for {sender_id}: {e}")
                continue

            # Import allowed DM users from config.
            from config import ALLOWED_DM_USERS
            if sender_username not in [u.lower() for u in ALLOWED_DM_USERS]:
                continue

            message_text = msg.get("text", "").strip()
            logging.info(f"Received DM from @{sender_username}: {message_text}")

            feedback = ""
            # Look for the colon in the message.
            if ":" in message_text:
                # Split into command and arguments.
                command_part, argument_part = message_text.split(":", 1)
                command = command_part.strip().lower()
                arguments_str = argument_part.strip()
                
                # If commas are present, split into multiple arguments.
                if "," in arguments_str:
                    arguments = [arg.strip() for arg in arguments_str.split(",") if arg.strip()]
                else:
                    arguments = [arguments_str] if arguments_str else []

                # Process the command.
                if command == "add_topic":
                    if arguments:
                        for arg in arguments:
                            add_topic(arg)
                        feedback = f"Hi @{sender_username}, the following topics have been added: {', '.join(arguments)}."
                    else:
                        feedback = f"Hi @{sender_username}, no topics provided."
                elif command == "add_whitelist":
                    if arguments:
                        for arg in arguments:
                            add_to_whitelist(arg)
                        feedback = f"Hi @{sender_username}, the following usernames have been added to the whitelist: {', '.join(arguments)}."
                    else:
                        feedback = f"Hi @{sender_username}, no usernames provided."
                elif command == "add_blacklist":
                    if arguments:
                        for arg in arguments:
                            add_to_blacklist(arg)
                        feedback = f"Hi @{sender_username}, the following usernames have been added to the blacklist: {', '.join(arguments)}."
                    else:
                        feedback = f"Hi @{sender_username}, no usernames provided."
                else:
                    feedback = f"Hi @{sender_username}, unknown command: {command}."
            else:
                feedback = f"Hi @{sender_username}, your message does not follow the command format. Please use 'command: argument'."

            # Send feedback DM using the v2 endpoint.
            try:
                client.create_direct_message(participant_id=sender_id, text=feedback)
                logging.info(f"Sent feedback DM to @{sender_username}: {feedback}")
                print(f"Sent feedback DM to @{sender_username}: {feedback}")
            except Exception as fe:
                logging.error(f"Error sending feedback DM to @{sender_username}: {fe}")
                print(f"Error sending feedback DM to @{sender_username}: {fe}")

            # Process one message per conversation and then move on.
            break
