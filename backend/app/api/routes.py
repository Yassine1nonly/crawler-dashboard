from fastapi import APIRouter, HTTPException, Request, Body
from bson import ObjectId
from datetime import datetime

router = APIRouter()


def _oid(x: str):
    try:
        return ObjectId(x)
    except Exception:
        return None


@router.get("/sources")
def list_sources(request: Request):
    db = request.app.state.db
    runner = request.app.state.runner

    sources_raw = list(db.sources.find().sort("created_at", -1))
    sources = []
    for s_raw in sources_raw:
        # Convert MongoDB document to regular dict
        s = dict(s_raw)
        s["id"] = str(s["_id"])
        source_id = s["id"]
        s.pop("_id", None)
        
        # Add stats for each source
        try:
            total_pages = db.crawled_data.count_documents({"source_id": source_id})
            last_run = db.crawl_runs.find_one(
                {"source_id": source_id},
                sort=[("started_at", -1)]
            )
            
            running = runner.status(source_id)["running"]
            
            # Get current run's crawled count from database (real-time)
            current_run_crawled = 0
            runtime_seconds = None
            rate = None
            
            if last_run:
                run_id = str(last_run["_id"]) if "_id" in last_run else None
                # Count actual documents crawled in this run for real-time stats
                if run_id:
                    current_run_crawled = db.crawled_data.count_documents({"run_id": run_id})
                
                # Calculate runtime if currently running
                if running and last_run.get("started_at"):
                    started_at = last_run["started_at"]
                    # MongoDB datetime objects work directly with Python datetime
                    runtime_seconds = (datetime.now() - started_at).total_seconds()
                    # Calculate rate (pages per second)
                    rate = current_run_crawled / runtime_seconds if runtime_seconds > 0 else None
                else:
                    # Use the stored crawled_count for finished runs
                    current_run_crawled = last_run.get("crawled_count", current_run_crawled)
            
            # Add stats object that frontend expects
            s["stats"] = {
                "pages": total_pages,
                "pages_crawled": current_run_crawled,
                "documents": current_run_crawled,  # Alias for compatibility
                "queued": 0,  # Could be calculated if queue is tracked
                "errors": 0,  # Could be tracked if errors are stored
                "rate": rate,
                "pages_per_min": rate * 60 if rate else None,  # Convert to pages per minute
                "throughput": rate,
                "uptime": runtime_seconds,
                "runtime_seconds": runtime_seconds,
            }
        except Exception as e:
            # Fallback stats if there's an error
            s["stats"] = {
                "pages": 0,
                "pages_crawled": 0,
                "documents": 0,
                "queued": 0,
                "errors": 0,
                "rate": None,
                "pages_per_min": None,
                "throughput": None,
                "uptime": None,
                "runtime_seconds": None,
            }
        
        # Also add last_run info at top level for compatibility
        try:
            if last_run:
                s["last_run"] = {
                    "status": last_run.get("status"),
                    "started_at": last_run.get("started_at"),
                    "finished_at": last_run.get("finished_at"),
                    "crawled_count": last_run.get("crawled_count", 0),
                }
        except:
            pass
        
        sources.append(s)

    return sources


@router.post("/sources")
def create_source(
    request: Request,
    payload: dict = Body(...)
):
    db = request.app.state.db

    url = payload.get("url")
    name = payload.get("name")

    if not url or not name:
        raise HTTPException(status_code=400, detail="url and name are required")

    source_type = payload.get("source_type")
    if source_type is None or source_type == "auto":
        source_type = "html"  # Default, will be auto-detected during crawl
    
    keyword_filter = payload.get("keyword_filter", "no_filter")
    
    doc = {
        "url": url,
        "name": name,
        "source_type": source_type,
        "description": payload.get("description"),
        "keyword_filter": keyword_filter,
        "frequency": payload.get("frequency"),
        "max_hits": payload.get("max_hits", 50),
        "status": payload.get("status", "active"),  # Can be "active" or "inactive"
        "created_at": datetime.now(),
        "last_crawled": None,
        "crawl_count": 0,
        "runtime_status": "idle",
        "request_delay": payload.get("request_delay", 0),
    }

    try:
        inserted = db.sources.insert_one(doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create source: {e}")

    doc["id"] = str(inserted.inserted_id)
    doc.pop("_id", None)

    return doc


@router.post("/sources/{source_id}/start")
def start_source(source_id: str, request: Request):
    runner = request.app.state.runner

    run_id, err = runner.start(source_id)
    if err:
        raise HTTPException(status_code=400, detail=err)

    return {"run_id": run_id}


@router.post("/sources/{source_id}/stop")
def stop_source(source_id: str, request: Request):
    runner = request.app.state.runner

    runner.stop(source_id)
    return {"ok": True}


@router.get("/sources/{source_id}/stats")
def source_stats(source_id: str, request: Request):
    db = request.app.state.db
    runner = request.app.state.runner

    oid = _oid(source_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid source id")

    source = db.sources.find_one({"_id": oid})
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    total_pages = db.crawled_data.count_documents({"source_id": source_id})
    last_run = db.crawl_runs.find_one(
        {"source_id": source_id},
        sort=[("started_at", -1)]
    )

    running = runner.status(source_id)["running"]
    
    # Get real-time crawled count for current run
    current_run_crawled = 0
    runtime_seconds = None
    rate = None
    
    if last_run:
        run_id = str(last_run["_id"]) if "_id" in last_run else None
        # Count actual documents crawled in this run for real-time stats
        if run_id:
            current_run_crawled = db.crawled_data.count_documents({"run_id": run_id})
        
        # Calculate runtime if currently running
        if running and last_run.get("started_at"):
            started_at = last_run["started_at"]
            runtime_seconds = (datetime.now() - started_at).total_seconds()
            rate = current_run_crawled / runtime_seconds if runtime_seconds > 0 else None
        else:
            # Use stored count for finished runs
            current_run_crawled = last_run.get("crawled_count", current_run_crawled)

    return {
        "source_id": source_id,
        "name": source.get("name"),
        "url": source.get("url"),
        "runtime_status": source.get("runtime_status", "idle"),
        "running": running,
        "total_pages": total_pages,
        "last_crawled": source.get("last_crawled"),
        "crawl_count": source.get("crawl_count", 0),
        "current_run_crawled": current_run_crawled,
        "runtime_seconds": runtime_seconds,
        "rate": rate,
        "last_run": {
            "status": last_run.get("status") if last_run else None,
            "started_at": last_run.get("started_at") if last_run else None,
            "finished_at": last_run.get("finished_at") if last_run else None,
            "crawled_count": current_run_crawled,  # Return real-time count
        },
    }


@router.get("/runs")
def list_runs(request: Request, limit: int = 50):
    db = request.app.state.db

    runs = list(
        db.crawl_runs.find()
        .sort("started_at", -1)
        .limit(limit)
    )

    for r in runs:
        r["id"] = str(r["_id"])
        r.pop("_id", None)

    return runs
