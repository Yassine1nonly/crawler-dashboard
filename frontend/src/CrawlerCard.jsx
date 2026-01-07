import { startCrawler, stopCrawler, fetchStats } from "./services/api";
import { useEffect, useState } from "react";

export default function CrawlerCard({ source, onUpdated }) {
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(false);

  // AUTO LOAD STATS ON MOUNT
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoadingStats(true);
    try {
      const data = await fetchStats(source.id);
      setStats(data);
    } catch (e) {
      console.error("Failed to fetch stats", e);
    } finally {
      setLoadingStats(false);
    }
  };

  return (
    <div className="crawlerCard">
      <div className="cardHeader">
        <div>
          <h3>{source.name}</h3>
          <a href={source.url} target="_blank" rel="noreferrer">
            {source.url}
          </a>
        </div>

        <span className={`status ${source.status}`}>
          {source.status?.toUpperCase()}
        </span>
      </div>

      <div className="statsGrid">
        <div className="statBox">
          <strong>Pages crawled</strong>
          <span>{stats?.pages ?? "0"}</span>
          <small>Total pages fetched</small>
        </div>

        <div className="statBox">
          <strong>Run duration</strong>
          <span>{stats?.duration ?? "0"} s</span>
          <small>Elapsed time</small>
        </div>

        <div className="statBox">
          <strong>Last crawl</strong>
          <span>{stats?.lastRun ?? "—"}</span>
          <small>Date & time</small>
        </div>
      </div>

      <div className="cardActions">
        <button onClick={() => startCrawler(source.id).then(onUpdated)}>
          Start
        </button>
        <button onClick={() => stopCrawler(source.id).then(onUpdated)}>
          Stop
        </button>
        <button onClick={loadStats} disabled={loadingStats}>
          Refresh stats
        </button>
      </div>
    </div>
  );
}
