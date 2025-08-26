"use client";
import { useEffect, useMemo, useState } from "react";
import { suggestNextHops, executeHop, type Hop } from "@lukhas/orchestrator/handover";
import type { ContextCapsule } from "@lukhas/orchestrator/contextCapsule";
import { getThreadKey } from "@/components/model-context";
import { usePathname } from "next/navigation";

function fmtCost(n?: number) { return n == null ? "~$0.00" : `$${n.toFixed(2)}`; }
function fmtTime(ms?: number) { return ms == null ? "~0s" : `${Math.round(ms/1000)}s`; }

export default function SuggestionChips({ capsule, onResult }: {
  capsule: ContextCapsule;
  onResult?: (r: { model: string; output: string; skill: string }) => void;
}) {
  const pathname = usePathname() || "/studio";
  const threadKey = useMemo(() => getThreadKey(pathname), [pathname]);
  const budgetKey = `lukhas:budget:${threadKey}`;
  const consentKey = `lukhas:consent:${threadKey}`;
  const [hops, setHops] = useState<Hop[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [blocked, setBlocked] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const planned = await suggestNextHops(capsule.userIntents as any, capsule);
      setHops(planned);
    })();
  }, [capsule]);

  async function run(h: Hop) {
    try {
      // enforce consent + budget from localStorage
      const consent = JSON.parse(localStorage.getItem(consentKey) || "null");
      const budget = JSON.parse(localStorage.getItem(budgetKey) || "null");
      if (!consent?.allowCrossProvider && h.to !== "lukhas-core") {
        setBlocked("Cross-provider sharing is disabled for this thread.");
        return;
      }
      const estCost = h.costBudgetUSD ?? 0.0;
      if (budget && estCost > budget.costUSD) {
        setBlocked(`Budget too low (${fmtCost(budget.costUSD)}). Needed ${fmtCost(estCost)}.`);
        return;
      }
      setBusy(h.to); setBlocked(null);
      const r = await executeHop(h, capsule);
      setBusy(null);
      onResult?.({ model: r.model, output: r.output, skill: h.skill });
    } catch (e: any) {
      setBusy(null);
      setBlocked(e?.message || "Error");
    }
  }

  return (
    <div style={{ display: "grid", gap: 6 }}>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {hops.map((h, i) => (
          <button key={i} disabled={!!busy}
            onClick={() => run(h)}
            title={`${fmtTime(h.latencyBudgetMs)} · ${fmtCost(h.costBudgetUSD)}`}
            style={{
              padding: "6px 10px", borderRadius: 10, border: "1px solid #2a2f37",
              background: busy===h.to ? "rgba(59,130,246,0.10)" : "transparent", cursor:"pointer"
            }}>
            {busy===h.to ? "Running…" : `→ ${label(h.skill)} via ${h.to}`}
          </button>
        ))}
      </div>
      {blocked && <div style={{ fontSize: 12, opacity: 0.8 }}>{blocked}</div>}
    </div>
  );
}

function label(skill: string) {
  switch (skill) {
    case "web.research": return "Research";
    case "validate.facts": return "Validate";
    case "write.email": return "Write email";
    case "prompt.optimize": return "Optimize prompts";
    case "video.summarize": return "Summarize to storyboard";
    case "video.generate": return "Generate video";
    default: return skill;
  }
}
