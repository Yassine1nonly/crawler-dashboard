import { useEffect, useMemo, useState, useRef } from "react";
import {
  Play,
  Square,
  Plus,
  Loader2,
  Globe,
  Settings,
  Activity,
  Timer,
  Hash,
  Database,
  Save,
  X,
  RefreshCw,
} from "lucide-react";

const API = "http://127.0.0.1:8000/api";

function safeNum(v, fallback = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}

function pick(obj, keys, fallback = undefined) {
  for (const k of keys) {
    if (obj && obj[k] !== undefined && obj[k] !== null) return obj[k];
  }
  return fallback;
}

const FILTER_NAMES = {
  "no_filter": "No Filter",
  "finance": "Finance",
  "education": "Education",
  "technology": "Technology",
  "economy": "Economy",
  "politics": "Politics",
  "esg": "ESG",
  "health": "Health",
  "business": "Business",
  "exclude": "Exclude"
};

function normalizeSource(raw) {
  const runtimeStatus = pick(raw, ["runtime_status", "status", "state"], "idle");
  const options =
    pick(raw, ["options", "config", "params", "settings"], {}) || {};

  const stats = pick(raw, ["stats", "metrics", "live_stats"], {}) || {};
  const keywordFilter = raw.keyword_filter || raw.options?.keyword_filter || "no_filter";

  return {
    id: raw.id,
    name: raw.name || raw.title || "Unnamed",
    url: raw.url || raw.start_url || raw.seed_url || "",
    runtime_status: runtimeStatus,
    keyword_filter: keywordFilter,
    options,
    stats,
    raw,
  };
}

export default function App() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const sourcesRef = useRef([]);

  const [showAdd, setShowAdd] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [editing, setEditing] = useState(null);

  // Add form
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [sourceType, setSourceType] = useState("html");
  const [description, setDescription] = useState("");
  const [enabled, setEnabled] = useState(true);
  const [keywordFilter, setKeywordFilter] = useState("no_filter");

  const [maxHits, setMaxHits] = useState(50);
  const [maxDepth, setMaxDepth] = useState(2);
  const [concurrency, setConcurrency] = useState(3);
  const [respectRobots, setRespectRobots] = useState(true);
  const [userAgent, setUserAgent] = useState("CrawlerDashboardBot/1.0");
  const [includeSubdomains, setIncludeSubdomains] = useState(true);
  const [requestDelay, setRequestDelay] = useState(0);

  // UI controls
  const [search, setSearch] = useState("");

  async function loadSources(silent = false) {
    try {
      if (!silent) {
        setLoading(true);
      }
      const res = await fetch(`${API}/sources`);
      const data = await res.json();
      const normalized = Array.isArray(data)
        ? data.map(normalizeSource)
        : [];
      
      // Only update if data actually changed (deep comparison)
      setSources(prev => {
        // Quick check: same length and IDs
        if (prev.length !== normalized.length) {
          sourcesRef.current = normalized;
          return normalized;
        }
        
        // Deep comparison of key fields that matter for UI
        const prevKey = prev.map(s => `${s.id}:${s.runtime_status}:${JSON.stringify(s.stats || {})}`).join('|');
        const newKey = normalized.map(s => `${s.id}:${s.runtime_status}:${JSON.stringify(s.stats || {})}`).join('|');
        
        if (prevKey === newKey) {
          return prev; // No change, prevent re-render
        }
        
        sourcesRef.current = normalized;
        return normalized;
      });
    } catch (e) {
      console.error(e);
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }

  // Fetch stats for running crawlers
  async function loadStatsForRunning() {
    // Check both sourcesRef and current sources state
    const currentSources = sources.length > 0 ? sources : sourcesRef.current;
    const runningSources = currentSources.filter(s => 
      s.runtime_status === "running" || s.runtime_status === "stopping"
    );
    if (runningSources.length === 0) return;

    const statsPromises = runningSources.map(async (source) => {
      try {
        const res = await fetch(`${API}/sources/${source.id}/stats`);
        const statsData = await res.json();
        
        // Convert stats API response to the format expected by renderStats
        // Use real-time crawled count from backend
        const pagesCrawled = statsData.current_run_crawled !== undefined 
          ? statsData.current_run_crawled 
          : (statsData.last_run?.crawled_count || 0);
        
        // Calculate runtime and rate if crawler is running
        let runtimeSeconds = statsData.runtime_seconds || null;
        let rate = statsData.rate || null;
        
        // Check if running by runtime_status or running flag
        const isRunning = statsData.running || statsData.runtime_status === "running";
        
        if (isRunning && statsData.last_run?.started_at) {
          const started = new Date(statsData.last_run.started_at);
          const now = new Date();
          runtimeSeconds = (now - started) / 1000;
          
          // Calculate rate from pages crawled and runtime
          if (runtimeSeconds > 0 && pagesCrawled > 0) {
            rate = pagesCrawled / runtimeSeconds;
          }
        }
        
        const stats = {
          pages: statsData.total_pages || 0,
          pages_crawled: pagesCrawled,
          documents: pagesCrawled,
          queued: 0,
          errors: 0,
          rate: rate,
          pages_per_min: rate ? rate * 60 : null,
          throughput: rate,
          uptime: runtimeSeconds,
          runtime_seconds: runtimeSeconds,
        };

        return { id: source.id, stats };
      } catch (e) {
        console.error(`Failed to fetch stats for ${source.id}:`, e);
        return null;
      }
    });

    const statsResults = await Promise.all(statsPromises);
    
    // Update sources with new stats
    setSources(prev => {
      const updated = prev.map(source => {
        const statsResult = statsResults.find(s => s && s.id === source.id);
        if (statsResult) {
          return { ...source, stats: statsResult.stats };
        }
        return source;
      });
      sourcesRef.current = updated;
      return updated;
    });
  }

  useEffect(() => {
    loadSources(false); // Initial load with loading indicator
    
    // Smart polling: check if we should poll
    const pollInterval = setInterval(() => {
      // Only poll if there are running crawlers, or poll less frequently if idle
      const hasRunning = sourcesRef.current.some(s => s.runtime_status === "running");
      if (hasRunning) {
        loadSources(true); // Poll every interval when running
        loadStatsForRunning(); // Also fetch detailed stats for running crawlers
      } else {
        // Poll less frequently when idle (every 3rd interval = 30 seconds)
        const shouldPoll = Math.random() < 0.33; // 33% chance = roughly every 30 seconds
        if (shouldPoll) {
          loadSources(true);
        }
      }
    }, 10000); // Check every 10 seconds
    
    return () => clearInterval(pollInterval);
  }, []);

  // Also fetch stats when sources change and there are running crawlers
  useEffect(() => {
    const hasRunning = sources.some(s => s.runtime_status === "running");
    if (hasRunning) {
      loadStatsForRunning();
    }
  }, [sources]);

  const filtered = useMemo(() => {
    const s = search.trim().toLowerCase();
    if (!s) return sources;
    return sources.filter(
      (x) =>
        x.name.toLowerCase().includes(s) || x.url.toLowerCase().includes(s)
    );
  }, [sources, search]);

  function resetAddForm() {
    setName("");
    setUrl("");
    setSourceType("html");
    setDescription("");
    setEnabled(true);
    setKeywordFilter("no_filter");
    setMaxHits(50);
    setMaxDepth(2);
    setConcurrency(3);
    setRespectRobots(true);
    setUserAgent("CrawlerDashboardBot/1.0");
    setIncludeSubdomains(true);
    setRequestDelay(0);
  }

  async function createSource() {
    if (!name || !url) return;

    const payload = {
      name,
      url,
      source_type: sourceType === "auto" ? null : sourceType, // null means auto-detect
      description: description.trim() || null,
      keyword_filter: keywordFilter,
      status: enabled ? "active" : "inactive",
      // we send both common styles so your backend can pick what it expects
      max_hits: safeNum(maxHits, 50),
      max_depth: safeNum(maxDepth, 2),
      concurrency: safeNum(concurrency, 3),
      respect_robots: !!respectRobots,
      user_agent: userAgent,
      include_subdomains: !!includeSubdomains,
      request_delay: safeNum(requestDelay, 0),
      options: {
        max_hits: safeNum(maxHits, 50),
        max_depth: safeNum(maxDepth, 2),
        concurrency: safeNum(concurrency, 3),
        respect_robots: !!respectRobots,
        user_agent: userAgent,
        include_subdomains: !!includeSubdomains,
        request_delay: safeNum(requestDelay, 0),
        keyword_filter: keywordFilter,
      },
    };

    await fetch(`${API}/sources`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    resetAddForm();
    setShowAdd(false);
    loadSources();
  }

  async function start(id) {
    await fetch(`${API}/sources/${id}/start`, { method: "POST" });
    loadSources();
  }

  async function stop(id) {
    await fetch(`${API}/sources/${id}/stop`, { method: "POST" });
    loadSources();
  }

  function openEdit(source) {
    setEditing(source);

    // prefill edit form from existing options when present
    const o = source.options || {};
    setMaxHits(safeNum(pick(o, ["max_hits", "maxHits"], 50), 50));
    setMaxDepth(safeNum(pick(o, ["max_depth", "maxDepth"], 2), 2));
    setConcurrency(safeNum(pick(o, ["concurrency", "workers"], 3), 3));
    setRespectRobots(!!pick(o, ["respect_robots", "robots"], true));
    setUserAgent(pick(o, ["user_agent", "userAgent"], "CrawlerDashboardBot/1.0"));
    setIncludeSubdomains(!!pick(o, ["include_subdomains", "subdomains"], true));
    setKeywordFilter(source.keyword_filter || pick(o, ["keyword_filter"], "no_filter"));

    setShowEdit(true);
  }

  async function saveEdit() {
    if (!editing) return;

    const payload = {
      // do not change name and url here unless your backend supports it
      keyword_filter: keywordFilter,
      options: {
        max_hits: safeNum(maxHits, 50),
        max_depth: safeNum(maxDepth, 2),
        concurrency: safeNum(concurrency, 3),
        respect_robots: !!respectRobots,
        user_agent: userAgent,
        include_subdomains: !!includeSubdomains,
        keyword_filter: keywordFilter,
      },
      max_hits: safeNum(maxHits, 50),
      max_depth: safeNum(maxDepth, 2),
      concurrency: safeNum(concurrency, 3),
      respect_robots: !!respectRobots,
      user_agent: userAgent,
      include_subdomains: !!includeSubdomains,
    };

    // Try common update endpoints without crashing
    // 1) PUT /sources/{id}
    // 2) PATCH /sources/{id}
    // 3) PUT /sources/{id}/config
    const tryReq = async (method, url) => {
      const r = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      return r.ok;
    };

    let ok = false;
    try {
      ok = await tryReq("PUT", `${API}/sources/${editing.id}`);
      if (!ok) ok = await tryReq("PATCH", `${API}/sources/${editing.id}`);
      if (!ok) ok = await tryReq("PUT", `${API}/sources/${editing.id}/config`);
      if (!ok) ok = await tryReq("PATCH", `${API}/sources/${editing.id}/config`);
    } catch (e) {
      console.error(e);
    }

    setShowEdit(false);
    setEditing(null);
    loadSources();
  }

  function StatPill({ icon: Icon, label, value }) {
    return (
      <div className="pill">
        <Icon size={14} />
        <span className="pill-label">{label}</span>
        <span className="pill-value">{value}</span>
      </div>
    );
  }

  function renderStats(s) {
    const st = s.stats || {};
    const pages = pick(st, ["pages", "pages_crawled", "documents"], null);
    const queued = pick(st, ["queued", "queue_size", "pending"], null);
    const errors = pick(st, ["errors", "error_count"], null);
    const rate = pick(st, ["rate", "pages_per_min", "throughput"], null);
    const uptime = pick(st, ["uptime", "runtime_seconds"], null);

    // If nothing exists, still show placeholders to avoid "empty card"
    const pagesVal = pages !== null ? safeNum(pages) : "—";
    const queuedVal = queued !== null ? safeNum(queued) : "—";
    const errorsVal = errors !== null ? safeNum(errors) : "—";
    
    // Format rate - show pages per second with 2 decimals, or pages per minute if very small
    let rateVal = "—";
    if (rate !== null && rate !== undefined) {
      const rateNum = safeNum(rate);
      if (rateNum > 0) {
        if (rateNum < 0.01) {
          // Very slow, show as pages per minute
          rateVal = `${(rateNum * 60).toFixed(2)}/min`;
        } else {
          // Show as pages per second
          rateVal = `${rateNum.toFixed(2)}/s`;
        }
      } else {
        rateVal = "0/s";
      }
    }
    
    const uptimeVal =
      uptime !== null && uptime !== undefined ? `${Math.round(safeNum(uptime))}s` : "—";

    return (
      <div className="pills">
        <StatPill icon={Activity} label="Crawled" value={pagesVal} />
        <StatPill icon={Hash} label="Queued" value={queuedVal} />
        <StatPill icon={Database} label="Errors" value={errorsVal} />
        <StatPill icon={Timer} label="Rate" value={rateVal} />
        <StatPill icon={Timer} label="Uptime" value={uptimeVal} />
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div className="title">
          <Globe size={26} />
          <div>
            <h1>Crawler Dashboard</h1>
            <p className="subtitle">Manage sources, options, and live stats</p>
          </div>
        </div>

        <div className="header-actions">
          <input
            className="search"
            placeholder="Search crawlers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button className="icon-btn" onClick={() => loadSources(false)} title="Refresh">
            <RefreshCw size={16} />
          </button>
          <button className="primary" onClick={() => setShowAdd(true)}>
            <Plus size={16} />
            Add source
          </button>
        </div>
      </header>

      <main className="content">
        {loading && (
          <div className="center">
            <Loader2 className="spin" />
            Loading crawlers...
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <div className="empty">
            <p>No crawlers found</p>
            <span>Create one or adjust your search</span>
          </div>
        )}

        <div className="grid">
          {filtered.map((s) => (
            <div key={s.id} className="card">
              <div className="card-header">
                <div className="card-title">
                  <h3>{s.name}</h3>
                  <span
                    className={`status ${
                      s.runtime_status === "running" ? "running" : "idle"
                    }`}
                  >
                    {s.runtime_status}
                  </span>
                </div>

                <button
                  className="icon-btn"
                  title="Edit options"
                  onClick={() => openEdit(s)}
                  disabled={s.runtime_status === "running"}
                >
                  <Settings size={16} />
                </button>
              </div>

              <p className="url">{s.url}</p>
              
              {s.keyword_filter && s.keyword_filter !== "no_filter" && (
                <p className="filter-badge" style={{ 
                  fontSize: "12px", 
                  color: "#888", 
                  marginTop: "4px",
                  fontStyle: "italic"
                }}>
                  Filter: {FILTER_NAMES[s.keyword_filter] || s.keyword_filter}
                </p>
              )}

              {renderStats(s)}

              <div className="actions">
                <button onClick={() => start(s.id)} disabled={s.runtime_status === "running"}>
                  <Play size={14} />
                  Start
                </button>
                <button className="danger" onClick={() => stop(s.id)} disabled={s.runtime_status !== "running"}>
                  <Square size={14} />
                  Stop
                </button>
              </div>

              {s.runtime_status === "running" ? (
                <p className="hint">Options locked while running</p>
              ) : (
                <p className="hint">You can edit options before starting</p>
              )}
            </div>
          ))}
        </div>
      </main>

      {/* Add Source Modal */}
      {showAdd && (
        <div className="modal-backdrop" onMouseDown={() => setShowAdd(false)}>
          <div className="modal wide" onMouseDown={(e) => e.stopPropagation()}>
            <div className="modal-top">
              <h2>Add crawler</h2>
              <button className="icon-btn" onClick={() => setShowAdd(false)}>
                <X size={16} />
              </button>
            </div>

            <div className="form-grid">
              <div className="field">
                <label>Crawler name *</label>
                <input
                  placeholder="e.g. News crawler"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="field">
                <label>Start URL *</label>
                <input
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                />
              </div>

              <div className="field">
                <label>Source Type</label>
                <select
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value)}
                >
                  <option value="auto">Auto-detect</option>
                  <option value="html">HTML</option>
                  <option value="rss">RSS Feed</option>
                  <option value="xml">XML</option>
                  <option value="pdf">PDF</option>
                  <option value="txt">Text</option>
                </select>
              </div>

              <div className="field">
                <label>Description</label>
                <input
                  placeholder="Optional description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div className="field">
                <label>Keyword Filter</label>
                <select
                  value={keywordFilter}
                  onChange={(e) => setKeywordFilter(e.target.value)}
                >
                  <option value="no_filter">No Filter (Store All Content)</option>
                  <option value="finance">Finance</option>
                  <option value="education">Education</option>
                  <option value="technology">Technology</option>
                  <option value="economy">Economy</option>
                  <option value="politics">Politics</option>
                  <option value="esg">ESG (Sustainability)</option>
                  <option value="health">Health</option>
                  <option value="business">Business</option>
                  <option value="exclude">Exclude (Celebrity, Sports, etc.)</option>
                </select>
                <small>
                  {keywordFilter === "no_filter" 
                    ? "All content will be stored" 
                    : keywordFilter === "exclude"
                    ? "Content matching these keywords will be excluded"
                    : "Only content matching these keywords will be stored"}
                </small>
              </div>

              <div className="field">
                <label>Max hits</label>
                <input
                  type="number"
                  min="1"
                  value={maxHits}
                  onChange={(e) => setMaxHits(e.target.value)}
                />
              </div>

              <div className="field">
                <label>Max depth</label>
                <input
                  type="number"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(e.target.value)}
                />
              </div>

              <div className="field">
                <label>Concurrency</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={concurrency}
                  onChange={(e) => setConcurrency(e.target.value)}
                />
                <small>Number of parallel requests (1-10)</small>
              </div>

              <div className="field">
                <label>Request Delay (seconds)</label>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={requestDelay}
                  onChange={(e) => setRequestDelay(e.target.value)}
                />
                <small>Delay between requests to avoid overwhelming server</small>
              </div>

              <div className="field">
                <label>User agent</label>
                <input
                  value={userAgent}
                  onChange={(e) => setUserAgent(e.target.value)}
                />
              </div>

              <div className="field check">
                <label>
                  <input
                    type="checkbox"
                    checked={enabled}
                    onChange={(e) => setEnabled(e.target.checked)}
                  />
                  Enabled (crawler is active)
                </label>
              </div>

              <div className="field check">
                <label>
                  <input
                    type="checkbox"
                    checked={respectRobots}
                    onChange={(e) => setRespectRobots(e.target.checked)}
                  />
                  Respect robots.txt
                </label>
              </div>

              <div className="field check">
                <label>
                  <input
                    type="checkbox"
                    checked={includeSubdomains}
                    onChange={(e) => setIncludeSubdomains(e.target.checked)}
                  />
                  Include subdomains
                </label>
              </div>
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowAdd(false)}>Cancel</button>
              <button className="primary" onClick={createSource}>
                <Save size={16} />
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Options Modal */}
      {showEdit && editing && (
        <div className="modal-backdrop" onMouseDown={() => setShowEdit(false)}>
          <div className="modal wide" onMouseDown={(e) => e.stopPropagation()}>
            <div className="modal-top">
              <h2>Edit options</h2>
              <button className="icon-btn" onClick={() => setShowEdit(false)}>
                <X size={16} />
              </button>
            </div>

            <p className="edit-subtitle">
              {editing.name} options can be edited only when stopped
            </p>

            <div className="form-grid">
              <div className="field">
                <label>Max hits</label>
                <input
                  type="number"
                  value={maxHits}
                  onChange={(e) => setMaxHits(e.target.value)}
                />
              </div>

              <div className="field">
                <label>Max depth</label>
                <input
                  type="number"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(e.target.value)}
                />
              </div>

              <div className="field">
                <label>Concurrency</label>
                <input
                  type="number"
                  value={concurrency}
                  onChange={(e) => setConcurrency(e.target.value)}
                />
              </div>

              <div className="field">
                <label>User agent</label>
                <input
                  value={userAgent}
                  onChange={(e) => setUserAgent(e.target.value)}
                />
              </div>

              <div className="field">
                <label>Keyword Filter</label>
                <select
                  value={keywordFilter}
                  onChange={(e) => setKeywordFilter(e.target.value)}
                >
                  <option value="no_filter">No Filter (Store All Content)</option>
                  <option value="finance">Finance</option>
                  <option value="education">Education</option>
                  <option value="technology">Technology</option>
                  <option value="economy">Economy</option>
                  <option value="politics">Politics</option>
                  <option value="esg">ESG (Sustainability)</option>
                  <option value="health">Health</option>
                  <option value="business">Business</option>
                  <option value="exclude">Exclude (Celebrity, Sports, etc.)</option>
                </select>
                <small>
                  {keywordFilter === "no_filter" 
                    ? "All content will be stored" 
                    : keywordFilter === "exclude"
                    ? "Content matching these keywords will be excluded"
                    : "Only content matching these keywords will be stored"}
                </small>
              </div>

              <div className="field check">
                <label>
                  <input
                    type="checkbox"
                    checked={respectRobots}
                    onChange={(e) => setRespectRobots(e.target.checked)}
                  />
                  Respect robots.txt
                </label>
              </div>

              <div className="field check">
                <label>
                  <input
                    type="checkbox"
                    checked={includeSubdomains}
                    onChange={(e) => setIncludeSubdomains(e.target.checked)}
                  />
                  Include subdomains
                </label>
              </div>
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowEdit(false)}>Cancel</button>
              <button className="primary" onClick={saveEdit}>
                <Save size={16} />
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
