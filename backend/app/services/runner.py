import threading
from datetime import datetime
from bson import ObjectId

from app.services.crawler_engine import CrawlerEngine

class CrawlerRunner:
    def __init__(self, db):
        self.db = db
        self.engine = CrawlerEngine(db)
        self._locks = threading.Lock()
        self._stops = {}
        self._threads = {}

    def _get_stop_event(self, source_id: str):
        with self._locks:
            if source_id not in self._stops:
                self._stops[source_id] = threading.Event()
            return self._stops[source_id]

    def start(self, source_id: str):
        source = self.db.sources.find_one({"_id": ObjectId(source_id)})
        if not source:
            return None, "Source not found"

        with self._locks:
            if source_id in self._threads and self._threads[source_id].is_alive():
                return None, "Already running"

        stop_event = self._get_stop_event(source_id)
        stop_event.clear()

        run_doc = {
            "source_id": source_id,
            "source_url": source["url"],
            "status": "running",
            "started_at": datetime.now(),
            "finished_at": None,
            "crawled_count": 0,
        }
        run_id = str(self.db.crawl_runs.insert_one(run_doc).inserted_id)

        def stop_check():
            return stop_event.is_set()

        def job():
            try:
                result = self.engine.crawl(source, run_id, stop_check)
                final_status = "stopped" if result.get("stopped") else "finished"
                crawled_count = result.get("crawled_count", 0)
            except Exception as e:
                # Log error and mark as failed
                print(f"Error in crawler job for {source_id}: {e}")
                import traceback
                traceback.print_exc()
                final_status = "failed"
                crawled_count = 0
            
            try:
                # Always update run status, even if there was an error
                self.db.crawl_runs.update_one(
                    {"_id": ObjectId(run_id)},
                    {
                        "$set": {
                            "status": final_status,
                            "finished_at": datetime.now(),
                            "crawled_count": crawled_count,
                        }
                    },
                )
                self.db.sources.update_one(
                    {"_id": ObjectId(source_id)},
                    {
                        "$set": {
                            "last_crawled": datetime.now(),
                            "runtime_status": "idle"
                        },
                        "$inc": {"crawl_count": 1}
                    },
                )
            except Exception as e:
                print(f"Error updating database for {source_id}: {e}")
            
            # Clean up thread reference
            with self._locks:
                if source_id in self._threads:
                    del self._threads[source_id]

        t = threading.Thread(target=job, daemon=True)
        with self._locks:
            self._threads[source_id] = t
        t.start()

        self.db.sources.update_one({"_id": ObjectId(source_id)}, {"$set": {"runtime_status": "running"}})
        return run_id, None

    def stop(self, source_id: str):
        stop_event = self._get_stop_event(source_id)
        stop_event.set()
        self.db.sources.update_one({"_id": ObjectId(source_id)}, {"$set": {"runtime_status": "stopping"}})
        return True

    def status(self, source_id: str):
        with self._locks:
            t = self._threads.get(source_id)
        running = bool(t and t.is_alive())
        
        # Clean up dead threads and update status
        if not running and source_id in self._threads:
            # Thread died unexpectedly, clean up
            del self._threads[source_id]
            try:
                # Update database status to idle if thread is dead
                source = self.db.sources.find_one({"_id": ObjectId(source_id)})
                if source and source.get("runtime_status") in ["running", "stopping"]:
                    self.db.sources.update_one(
                        {"_id": ObjectId(source_id)},
                        {"$set": {"runtime_status": "idle"}}
                    )
            except Exception as e:
                print(f"Error cleaning up thread for {source_id}: {e}")
        
        return {"running": running}
    
    def cleanup_stuck_threads(self):
        """Clean up threads that are marked as running but the thread is dead"""
        with self._locks:
            dead_threads = []
            for source_id, thread in list(self._threads.items()):
                if not thread.is_alive():
                    dead_threads.append(source_id)
            
            for source_id in dead_threads:
                del self._threads[source_id]
                try:
                    self.db.sources.update_one(
                        {"_id": ObjectId(source_id)},
                        {"$set": {"runtime_status": "idle"}}
                    )
                except Exception as e:
                    print(f"Error cleaning up stuck thread {source_id}: {e}")