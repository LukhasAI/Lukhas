"use client";

export default function EmptyCanvas() {
  return (
    <div style={{
      display: "grid", 
      placeItems: "center", 
      height: 360, 
      border: "1px dashed var(--line2)", 
      borderRadius: 16, 
      background: "rgba(16,20,29,.35)"
    }}>
      <div style={{ textAlign: "center" }}>
        <div className="t-18" style={{ opacity: .95, marginBottom: 6 }}>
          Drop something here or press ⌘K
        </div>
        <div className="t-13" style={{ opacity: .75 }}>
          Validate · Summarize · Generate video · Draft reply
        </div>
      </div>
    </div>
  );
}