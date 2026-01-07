import { useState } from "react";
import { updateSource } from "./services/api";

function SourceOptions({ source, onUpdated }) {
  const [frequency, setFrequency] = useState(source.frequency || 60);
  const [maxPages, setMaxPages] = useState(source.max_pages || 100);
  const [depth, setDepth] = useState(source.depth || 2);
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    const updated = await updateSource(source.id, {
      frequency,
      max_pages: maxPages,
      depth,
    });
    onUpdated(updated);
    setSaving(false);
  }

  return (
    <div style={{ marginTop: "14px" }}>
      <div>
        <label>Frequency (seconds)</label>
        <input
          type="number"
          value={frequency}
          onChange={(e) => setFrequency(Number(e.target.value))}
        />
      </div>

      <div>
        <label>Max pages</label>
        <input
          type="number"
          value={maxPages}
          onChange={(e) => setMaxPages(Number(e.target.value))}
        />
      </div>

      <div>
        <label>Depth</label>
        <input
          type="number"
          value={depth}
          onChange={(e) => setDepth(Number(e.target.value))}
        />
      </div>

      <button onClick={save} disabled={saving} style={{ marginTop: "8px" }}>
        Save options
      </button>
    </div>
  );
}

export default SourceOptions;
