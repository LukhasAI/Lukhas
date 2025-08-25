"use client";
import { useEffect, useMemo, useState } from "react";
import { getThreadKey } from "@/components/model-context";
import { usePathname } from "next/navigation";

type Consent = { allowCrossProvider: boolean; allowExternalWebFetch: boolean; containPII: boolean; piiRedacted: boolean };
type Budget = { costUSD: number; timeMs: number };

export default function ConsentBanner() {
  const pathname = usePathname() || "/studio";
  const threadKey = useMemo(() => getThreadKey(pathname), [pathname]);
  const consentKey = `lukhas:consent:${threadKey}`;
  const budgetKey = `lukhas:budget:${threadKey}`;
  const [consent, setConsent] = useState<Consent | null>(null);
  const [budget, setBudget] = useState<Budget | null>(null);
  const [open, setOpen] = useState<boolean>(true);

  useEffect(() => {
    try {
      const c = JSON.parse(localStorage.getItem(consentKey) || "null");
      const b = JSON.parse(localStorage.getItem(budgetKey) || "null");
      setConsent(c ?? { allowCrossProvider: false, allowExternalWebFetch: true, containPII: false, piiRedacted: true });
      const defCost = Number(process.env.NEXT_PUBLIC_ORCH_DEFAULT_COST_BUDGET ?? "0.50");
      const defTime = Number(process.env.NEXT_PUBLIC_ORCH_DEFAULT_TIME_BUDGET_MS ?? "30000");
      setBudget(b ?? { costUSD: isNaN(defCost) ? 0.5 : defCost, timeMs: isNaN(defTime) ? 30000 : defTime });
    } catch {}
  }, [consentKey, budgetKey]);
  
  useEffect(() => {
    const onReq = () => {
      setConsent((c) => {
        if (!c) return c;
        const next = { ...c, allowCrossProvider: !c.allowCrossProvider };
        localStorage.setItem(consentKey, JSON.stringify(next));
        return next;
      });
    };
    document.addEventListener("lukhas:consent-toggle-request", onReq as any);
    return () => document.removeEventListener("lukhas:consent-toggle-request", onReq as any);
  }, [consentKey]);

  if (!consent || !budget || !open) return null;
  return (
    <div style={{
      marginBottom: 12, padding: 10, border: "1px solid #2a2f37", borderRadius: 10,
      background: "rgba(59,130,246,0.10)", display:"flex", gap: 12, alignItems:"center"
    }}>
      <strong style={{ fontSize: 12 }}>Cross-model handoff</strong>
      <label style={{ display:"flex", alignItems:"center", gap:6, fontSize:12 }}>
        <input type="checkbox"
          checked={consent.allowCrossProvider}
          onChange={(e) => {
            const next = { ...consent, allowCrossProvider: e.target.checked };
            setConsent(next); localStorage.setItem(consentKey, JSON.stringify(next));
          }} />
        Enable cross-provider sharing
      </label>
      <label style={{ display:"flex", alignItems:"center", gap:6, fontSize:12 }}>
        Budget $:
        <input type="number" step="0.1" min="0" value={budget.costUSD}
          onChange={(e) => { const nb = { ...budget, costUSD: Number(e.target.value) }; setBudget(nb); localStorage.setItem(budgetKey, JSON.stringify(nb)); }}
          style={{ width: 72, background:"#0f131a", border:"1px solid #2a2f37", color:"#e6e6e6", borderRadius:8, padding:"4px 6px" }}
        />
      </label>
      <label style={{ display:"flex", alignItems:"center", gap:6, fontSize:12 }}>
        Time ms:
        <input type="number" step="500" min="0" value={budget.timeMs}
          onChange={(e) => { const nb = { ...budget, timeMs: Number(e.target.value) }; setBudget(nb); localStorage.setItem(budgetKey, JSON.stringify(nb)); }}
          style={{ width: 90, background:"#0f131a", border:"1px solid #2a2f37", color:"#e6e6e6", borderRadius:8, padding:"4px 6px" }}
        />
      </label>
      <button onClick={() => setOpen(false)} style={{ marginLeft:"auto", fontSize:12, border:"1px solid #2a2f37", borderRadius:8, padding:"4px 8px" }}>
        Hide
      </button>
    </div>
  );
}