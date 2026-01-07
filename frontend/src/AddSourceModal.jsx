import { useState } from "react";

export default function AddSourceModal({ onClose, onCreate }) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [type, setType] = useState("html");
  const [maxHits, setMaxHits] = useState(50);
  const [frequency, setFrequency] = useState(24);

  return (
    <div className="modalOverlay" onClick={onClose}>
      <div
        className="modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modalHeader">
          <h2>Add a crawl source</h2>
          <button className="closeButton" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modalBody">
          <label>
            Name
            <input
              placeholder="Example: CNN"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </label>

          <label>
            URL
            <input
              placeholder="https://edition.cnn.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </label>

          <label>
            Source type
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
            >
              <option value="html">html</option>
              <option value="rss">rss</option>
              <option value="api">api</option>
            </select>
            <small>How the crawler should interpret the source.</small>
          </label>

          <label>
            Max hits
            <input
              type="number"
              value={maxHits}
              onChange={(e) => setMaxHits(Number(e.target.value))}
            />
            <small>Maximum number of pages per run.</small>
          </label>

          <label>
            Frequency (hours)
            <input
              type="number"
              value={frequency}
              onChange={(e) => setFrequency(Number(e.target.value))}
            />
            <small>Optional. Used later for scheduling.</small>
          </label>
        </div>

        <div className="modalFooter">
          <button className="secondaryButton" onClick={onClose}>
            Cancel
          </button>
          <button
            className="primaryButton"
            onClick={() =>
              onCreate({
                id: Date.now(),
                name,
                url,
                type,
                maxHits,
                frequency
              })
            }
          >
            Create source
          </button>
        </div>
      </div>
    </div>
  );
}
