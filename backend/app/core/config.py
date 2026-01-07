import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "webcrawler_lab")

    USER_AGENT = "WebCrawler-Dashboard/1.0"
    TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    DEFAULT_MAX_HITS = 50
    DEFAULT_FREQUENCY = 3600
