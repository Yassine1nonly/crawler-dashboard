from pymongo import MongoClient, ASCENDING, TEXT
from app.core.config import Config

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        _client.server_info()
    return _client[Config.DATABASE_NAME]

def ensure_indexes():
    db = get_db()
    sources = db.sources
    crawled_data = db.crawled_data
    crawl_runs = db.crawl_runs

    sources.create_index([("url", ASCENDING)], unique=True)
    sources.create_index([("status", ASCENDING)])

    crawled_data.create_index([("source_id", ASCENDING)])
    crawled_data.create_index([("source_url", ASCENDING)])
    crawled_data.create_index([("crawled_at", ASCENDING)])
    crawled_data.create_index([("content_type", ASCENDING)])

    crawled_data.create_index([("title", TEXT), ("content", TEXT), ("url", TEXT)])

    crawl_runs.create_index([("source_id", ASCENDING)])
    crawl_runs.create_index([("started_at", ASCENDING)])
