import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mongo import get_db, ensure_indexes
from app.api.routes import router
from app.services.runner import CrawlerRunner

app = FastAPI(title="Crawler Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cleanup_stuck_threads_periodically(runner, db):
    """Background task to periodically clean up stuck threads"""
    while True:
        try:
            time.sleep(30)  # Check every 30 seconds
            runner.cleanup_stuck_threads()
            
            # Also check for sources marked as running but no active thread
            from bson import ObjectId
            stuck_sources = db.sources.find({"runtime_status": {"$in": ["running", "stopping"]}})
            for source in stuck_sources:
                source_id = str(source["_id"])
                # Check if thread is actually alive
                status = runner.status(source_id)
                if not status["running"]:
                    # Thread is dead, already cleaned up by status() method
                    pass
        except Exception as e:
            print(f"Error in cleanup task: {e}")

@app.on_event("startup")
def startup():
    db = get_db()
    ensure_indexes()
    runner = CrawlerRunner(db)

    app.state.db = db
    app.state.runner = runner
    
    # Start background cleanup task
    cleanup_thread = threading.Thread(
        target=cleanup_stuck_threads_periodically,
        args=(runner, db),
        daemon=True
    )
    cleanup_thread.start()

@app.get("/api/health")
def health():
    return {"ok": True}

app.include_router(router, prefix="/api")
