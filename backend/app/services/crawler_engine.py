import time
import requests
from collections import deque
from datetime import datetime
from urllib.parse import urlparse

from app.core.config import Config
from app.services.content_parser import ContentParser
from app.services.keyword_filter import matches_filter

class CrawlerEngine:
    def __init__(self, db):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": Config.USER_AGENT})

    def _fetch(self, url: str):
        for attempt in range(Config.MAX_RETRIES):
            try:
                r = self.session.get(url, timeout=Config.TIMEOUT)
                r.raise_for_status()
                return r
            except requests.RequestException as e:
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
                else:
                    # Log failure on final attempt
                    print(f"Failed to fetch {url} after {Config.MAX_RETRIES} attempts: {e}")
        return None

    def _detect_type(self, response, url: str):
        ct = (response.headers.get("Content-Type", "") or "").lower()
        if "application/pdf" in ct or url.lower().endswith(".pdf"):
            return "pdf"
        if "application/xml" in ct or "text/xml" in ct:
            return "xml"
        if "text/plain" in ct or url.lower().endswith(".txt"):
            return "txt"
        if "rss" in ct or "feed" in url.lower():
            return "rss"
        return "html"

    def crawl(self, source_doc: dict, run_id: str, stop_check):
        source_url = source_doc["url"]
        source_id = str(source_doc["_id"])
        max_hits = int(source_doc.get("max_hits", Config.DEFAULT_MAX_HITS))
        keyword_filter = source_doc.get("keyword_filter", "no_filter")

        crawled_count = 0
        visited = set()
        q = deque([source_url])

        while q and crawled_count < max_hits:
            if stop_check():
                break

            url = q.popleft()
            if url in visited:
                continue

            r = self._fetch(url)
            if r is None:
                visited.add(url)
                continue

            visited.add(url)
            ctype = self._detect_type(r, url)

            if stop_check():
                break

            try:
                if ctype == "rss":
                    items = ContentParser.parse_rss(url)
                    for item in items:
                        if stop_check():
                            break
                        
                        # Apply keyword filter
                        content_text = f"{item.get('title', '')} {item.get('content', '')} {item.get('description', '')}"
                        if not matches_filter(content_text, keyword_filter):
                            continue  # Skip this item if it doesn't match filter
                        
                        item["source_id"] = source_id
                        item["source_url"] = source_url
                        item["run_id"] = run_id
                        item["crawled_at"] = datetime.now()
                        self.db.crawled_data.insert_one(item)
                        crawled_count += 1
                        if crawled_count >= max_hits:
                            break

                elif ctype == "pdf":
                    parsed = ContentParser.parse_pdf(r.content, url)
                    
                    # Apply keyword filter
                    content_text = f"{parsed.get('title', '')} {parsed.get('content', '')} {parsed.get('text', '')}"
                    if not matches_filter(content_text, keyword_filter):
                        visited.add(url)
                        continue  # Skip if doesn't match filter
                    
                    parsed.update(
                        {
                            "url": url,
                            "source_id": source_id,
                            "source_url": source_url,
                            "run_id": run_id,
                            "crawled_at": datetime.now(),
                        }
                    )
                    self.db.crawled_data.insert_one(parsed)
                    crawled_count += 1

                elif ctype == "xml":
                    parsed = ContentParser.parse_xml(r.text, url)
                    
                    # Apply keyword filter
                    content_text = f"{parsed.get('title', '')} {parsed.get('content', '')} {parsed.get('text', '')}"
                    if not matches_filter(content_text, keyword_filter):
                        visited.add(url)
                        continue  # Skip if doesn't match filter
                    
                    parsed.update(
                        {
                            "url": url,
                            "source_id": source_id,
                            "source_url": source_url,
                            "run_id": run_id,
                            "crawled_at": datetime.now(),
                        }
                    )
                    self.db.crawled_data.insert_one(parsed)
                    crawled_count += 1

                elif ctype == "txt":
                    parsed = ContentParser.parse_text(r.text, url)
                    
                    # Apply keyword filter
                    content_text = f"{parsed.get('title', '')} {parsed.get('content', '')} {parsed.get('text', '')}"
                    if not matches_filter(content_text, keyword_filter):
                        visited.add(url)
                        continue  # Skip if doesn't match filter
                    
                    parsed.update(
                        {
                            "url": url,
                            "source_id": source_id,
                            "source_url": source_url,
                            "run_id": run_id,
                            "crawled_at": datetime.now(),
                        }
                    )
                    self.db.crawled_data.insert_one(parsed)
                    crawled_count += 1

                else:
                    parsed = ContentParser.parse_html(r.text, url)
                    
                    # Apply keyword filter
                    content_text = f"{parsed.get('title', '')} {parsed.get('content', '')} {parsed.get('text', '')}"
                    if not matches_filter(content_text, keyword_filter):
                        visited.add(url)
                        continue  # Skip if doesn't match filter
                    
                    parsed.update(
                        {
                            "url": url,
                            "source_id": source_id,
                            "source_url": source_url,
                            "run_id": run_id,
                            "crawled_at": datetime.now(),
                        }
                    )
                    self.db.crawled_data.insert_one(parsed)
                    crawled_count += 1

                    if url == source_url and crawled_count < max_hits:
                        for link in parsed.get("links", [])[:20]:
                            if link.startswith("http") and link not in visited:
                                q.append(link)

            except Exception as e:
                # Log error but continue crawling
                print(f"Error processing {url}: {e}")
                visited.add(url)  # Mark as visited to avoid retrying
                continue

        return {
            "crawled_count": crawled_count,
            "stopped": stop_check(),
        }
