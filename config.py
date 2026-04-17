import dotenv
import os
import google.generativeai as genai
from pymongo import MongoClient

dotenv.load_dotenv()

# telgram api setup.
TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE = f"https://api.telegram.org/bot{TOKEN}"

# google gemini setup
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
genai.configure(api_key=GEMINI_TOKEN)
model = genai.GenerativeModel("gemini-2.5-flash")

# Notion setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_BASE_URL = "https://api.notion.com/v1/"

PAGES_END_POINT = f"{NOTION_BASE_URL}pages/"
DATABASE_END_POINT = f"{NOTION_BASE_URL}databases/"
DATA_SOURCE_END_POINT = f"{NOTION_BASE_URL}data_sources/"

SCORES_NOTION = "319a3f0633bf804e8b11daf99bb2bb9e"
DAILY_WINNERS_NOTION = "319a3f0633bf801ca8afe8a104d36ef8"
WEEKLY_WINNERS_NOTION = "319a3f0633bf802e9aa7e53fca9fcaff"
MOVIES_NOTION = "320a3f0633bf80ac8389d7f394a82f28"
CLOUD_NOTION = "319a3f06-33bf-8018-853d-fa1355520fa4"

headers = {
        "Notion-Version": "2025-09-03",
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json"
    }

# mongodb setup
MONGO_DB_URI = os.getenv("MONGODB_TOKEN")
client = MongoClient(MONGO_DB_URI)
db = client["cluster0"]
scores = db["scores"]
daily_winners = db["daily_winners"]
weekly_winners = db["weekly_winners"]
