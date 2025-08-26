"use client";
import { useState, useEffect } from "react";
import { complianceCopy } from "./texts";

export default function PrivacySettings() {
  const [meta, setMeta] = useState(() => {
    if (typeof window === 'undefined') return false;
    try {
      const prefs = localStorage.getItem("lukhas:prefs");
      return prefs ? JSON.parse(prefs).metaAdaptive : false;
    } catch {
      return false;
    }
  });

  const [e2ee, setE2ee] = useState(() => {
    if (typeof window === 'undefined') return false;
    try {
      return localStorage.getItem("lukhas:e2ee") === "on";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const p = JSON.parse(localStorage.getItem("lukhas:prefs") || "{}");
      p.metaAdaptive = !!meta;
      localStorage.setItem("lukhas:prefs", JSON.stringify(p));
    } catch {}
  }, [meta]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem("lukhas:e2ee", e2ee ? "on" : "off");
    } catch {}
  }, [e2ee]);

  return (
    <section>
      <h2 className="t-18">Privacy & Consent</h2>
      <div style={{ marginTop: 8 }}>
        <label className="t-13" style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            type="checkbox"
            checked={meta}
            onChange={e => setMeta(e.target.checked)}
          />
          Meta-adaptive rails (local only)
        </label>
        <p className="t-11" style={{ opacity: .75, marginTop: 4, marginLeft: 20 }}>
          {complianceCopy.metaAdaptive}
        </p>
      </div>
      <div style={{ marginTop: 12 }}>
        <label className="t-13" style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            type="checkbox"
            checked={e2ee}
            onChange={e => setE2ee(e.target.checked)}
          />
          Encrypted messages (QRG)
        </label>
        <p className="t-11" style={{ opacity: .75, marginTop: 4, marginLeft: 20 }}>
          {complianceCopy.qrg}
        </p>
      </div>
    </section>
  );
}
