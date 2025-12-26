import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = "sqlite:///db.sqlite3"
WEBAPP_URL = os.getenv("WEBAPP_URL")
