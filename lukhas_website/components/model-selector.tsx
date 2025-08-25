"use client";
import { useModel } from "./model-context";

export default function ModelSelector() {
  const { current, setCurrent, providers, fallback, setFallback } = useModel();

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <h4 style={{ marginBottom: 4 }}>Models</h4>
      <div role="radiogroup" aria-label="Model selection" style={{ display: "grid", gap: 6 }}>
        {providers.map(p => {
          const active = p.id === current.id;
          return (
            <label key={p.id} style={{
              display: "flex", alignItems: "center", gap: 8, padding: "8px 10px",
              border: `1px solid ${active ? "#3b82f6" : "#1f2328"}`, borderRadius: 10,
              background: active ? "rgba(59,130,246,0.10)" : "transparent", cursor: "pointer"
            }}>
              <input
                type="radio" name="model" value={p.id} checked={active}
                onChange={() => setCurrent(p)} style={{ marginRight: 6 }}
                aria-describedby={`${p.id}-hints`}
              />
              <div style={{ display: "grid", lineHeight: 1.1 }}>
                <span>{p.label}</span>
                <small id={`${p.id}-hints`} style={{ opacity: 0.7 }}>
                  {p.latencyHint ?? "—"} latency · {p.qualityHint ?? "—"} quality
                </small>
              </div>
            </label>
          );
        })}
      </div>

      <div style={{ marginTop: 10 }}>
        <label style={{ display: "block", marginBottom: 6, opacity: 0.8 }}>Fallback strategy</label>
        <select
          value={fallback}
          onChange={e => setFallback(e.target.value as any)}
          style={{ width: "100%", padding: "8px 10px", borderRadius: 10, border: "1px solid #1f2328", background: "#0f131a", color: "#e6e6e6" }}
        >
          <option value="latency_then_quality">Latency → Quality (default)</option>
          <option value="quality_then_latency">Quality → Latency</option>
          <option value="off">Disable fallback</option>
        </select>
      </div>
    </div>
  );
}