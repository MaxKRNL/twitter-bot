import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API v2 credentials
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
V2_CLIENT_ID = os.getenv("V2_CLIENT_ID")
V2_CLIENT_SECRET = os.getenv("V2_CLIENT_SECRET")
V2_ACCESS_TOKEN = os.getenv("V2_ACCESS_TOKEN")
V2_ACCESS_SECRET = os.getenv("V2_ACCESS_SECRET")

# Scheduling intervals (in seconds)
POST_INTERVAL_MIN = 1800   # 30 min
POST_INTERVAL_MAX = 7200   # 2 hours

# Replies per user limit
MAX_REPLIES_PER_USER = 4
