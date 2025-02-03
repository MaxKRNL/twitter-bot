import tweepy
import json
import random
import logging
import re

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
from llm_utils import (
    init_model,
    generate_tweet_with_rag
)
from rag_utils import initialize_faiss_index

logging.basicConfig(filename="logs/bot.log", level=logging.INFO)

# ----------------------------------------------------
# A) TWITTER CLIENT
# ----------------------------------------------------
client_v2 = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=V2_CLIENT_ID,
    consumer_secret=V2_CLIENT_SECRET,
    access_token=V2_ACCESS_TOKEN,
    access_token_secret=V2_ACCESS_SECRET,
    wait_on_rate_limit=True
)

# ----------------------------------------------------
# B) INIT LLM + FAISS ONCE
# ----------------------------------------------------
init_model("meta-llama/Llama-3.1-7B-Instruct")
initialize_faiss_index()

STYLE_SUMMARY = (
    "Self-deprecating, aware, comedic, 'degen' vibe, loyal to KRNL, "
    "ambitious, and passionate about building the future of Web3. "
    "Intern perspective but always dreamingly talks about rising to CEO-level."
)

STYLE_INSTRUCTIONS = """
**Personality & Tone**:
1. Self-deprecating / Aware
2. Relatable experiences
3. 'Degen' sarcasm / dryness
4. Loyal to KRNL
5. Ambitious intern => future CEO
6. Passionate about KRNL, Web3
Overall style:
- Sarcastic, comedic, self-aware, 'degen'
- Loyal to KRNL, championing Web3 dev tools
- Never criticizes KRNL, only itself
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
        response = client_v2._make_request(
            method="GET",
            url="/2/users/personalized_trends",
            params={"id": user_id, "max_results": max_results}
        )
        if not response:
            logging.warning("No response from personalized trends endpoint.")
            return trends_list

        data = response.json()
        trends_data = data.get("data", {}).get("trends", [])
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
        me = client_v2.get_me()
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
    with open("topics.txt", "r", encoding="utf-8") as file:
        normal_topics = [line.strip() for line in file if line.strip()]

    personal_topics = read_personalized_trends("personalized_trends.txt")
    combined_topics = normal_topics + personal_topics
    if not combined_topics:
        logging.warning("No topics to tweet about.")
        return

    topic = random.choice(combined_topics)
    tweet_text = generate_tweet_with_rag(STYLE_SUMMARY, STYLE_INSTRUCTIONS, topic, top_k=3)

    if len(tweet_text) <= 280:
        try:
            resp = client_v2.create_tweet(text=tweet_text)
            logging.info(f"Tweeted: {tweet_text} (ID: {resp.data['id']})")
        except Exception as e:
            logging.error(f"Error posting tweet: {e}")
    else:
        logging.warning("Generated tweet too long. Skipping.")

def post_krnl_tweet():
    """
    Example function if you want a 'KRNL-flavored' tweet.
    But this calls the same generate_tweet_with_rag, so it's essentially the same as post_tweet.
    """
    with open("topics.txt", "r", encoding="utf-8") as file:
        normal_topics = [line.strip() for line in file if line.strip()]

    personal_topics = read_personalized_trends("personalized_trends.txt")
    combined_topics = normal_topics + personal_topics
    if not combined_topics:
        logging.warning("No topics or personalized trends to tweet about.")
        return

    topic = random.choice(combined_topics)
    # The same approach, top_k=3
    tweet_text = generate_tweet_with_rag(STYLE_SUMMARY, STYLE_INSTRUCTIONS, topic, top_k=3)

    if len(tweet_text) <= 280:
        try:
            resp = client_v2.create_tweet(text=tweet_text)
            logging.info(f"Tweeted: {tweet_text} (ID: {resp.data['id']})")
        except Exception as e:
            logging.error(f"Error posting tweet: {e}")
    else:
        logging.warning("Generated tweet too long. Skipping.")

def reply_to_mentions():
    """
    Replies to mentions, also using the same RAG-based function.
    The model decides whether to incorporate the retrieved knowledge.
    """
    global user_reply_count

    # 1) Get user ID
    try:
        me = client_v2.get_me()
        my_user_id = me.data.id
    except Exception as e:
        logging.error(f"Couldn't fetch user info: {e}")
        return

    # 2) Fetch mentions
    try:
        mentions_response = client_v2.get_users_mentions(
            id=my_user_id,
            expansions="author_id",
            tweet_fields=["author_id", "text"],
            user_field=["public_metrics"]
        )
    except Exception as e:
        logging.error(f"Error fetching mentions: {e}")
        return

    if not mentions_response.data:
        logging.info("No new mentions.")
        return

    # 3) Build author_id -> username + public_metrics map
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

        # Make sure we have public_metrics
        follower_count = 0
        if user_obj.public_metrics and "followers_count" in user_obj.public_metrics:
                follower_count = user_obj.public_metrics["followers_count"]

        # 1) Check blacklist
        if author_username in blacklist_users:
            logging.info(f"Skipping {author_username} (blacklisted).")
            continue

        # 2) Check whitelist (if whitelisted, bypass normal reply count limit)
        if author_username not in whitelist_users:
            # Not whitelisted => enforce normal reply limit
            if user_reply_count.get(author_username, 0) >= MAX_REPLIES_PER_USER:
                logging.info(f"Skipping {author_username}, reply limit reached.")
                continue

            if follower_count < 50:
                logging.info(f"Skipping {author_username}, reply user has only {follower_count}")

        # Generate the reply using the same RAG approach
        reply_text = generate_tweet_with_rag(
            STYLE_SUMMARY,
            STYLE_INSTRUCTIONS,
            mention_text,
            top_k=3
        )

        # Ensure 280 chars
        if len(reply_text) > 280:
            reply_text = reply_text[:280].rstrip()

        try:
            final_text = f"@{author_username} {reply_text}"
            resp = client_v2.create_tweet(
                text=final_text,
                in_reply_to_tweet_id=mention_id
            )
            user_reply_count[author_username] = user_reply_count.get(author_username, 0) + 1

            with open("user_interactions.json", "w") as f:
                json.dump(user_reply_count, f)

            logging.info(f"Replied to @{author_username}: {final_text} (ID: {resp.data['id']})")
        except Exception as e:
            logging.error(f"Error replying to @{author_username}: {e}")
