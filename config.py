import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API v2 credentials
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
CONSUMER_KEY = os.getenv("V2_CLIENT_ID")
CONSUMER_SECRET = os.getenv("V2_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("V2_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("V2_ACCESS_TOKEN_SECRET")

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")

# Scheduling intervals (in seconds)
POST_INTERVAL_MIN = 1800   # 30 min
POST_INTERVAL_MAX = 7200   # 2 hours

# Replies per user limit
MAX_REPLIES_PER_USER = 4

#Allowed DM Senders for adding new topics (use Twitter screen names, without @ sign)
ALLOWED_DM_USERS = ["JustMaxine1", "Myat292473"]