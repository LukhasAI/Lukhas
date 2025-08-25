"use client";
import { useEffect, useState } from "react";
import SuggestionChips from "@/components/suggestion-chips";
import ConsentBanner from "@/components/consent-banner";
import CanvasCarousel from "@/components/canvas-carousel";
import P2PChat from "@/components/p2p-chat";
import EmptyCanvas from "@/components/empty-canvas";
import { ModeProvider } from "@/components/mode-context";
import type { ContextCapsule } from "@lukhas/orchestrator/contextCapsule";
import type { ResultCardData } from "@/components/result-card";

export const dynamic = "force-dynamic";
export default function StudioThreadPage({ params }: { params: { threadId: string } }) {
  const [cards, setCards] = useState<ResultCardData[]>([]);
  
  // Demo seed for testing UI changes
  useEffect(() => {
    if (process.env.NEXT_PUBLIC_DEMO_SEED === "true") {
      setCards([
        {id:"demo1", kind:"text", title:"Demo Result", body:"This is a demo card to showcase the new glass design.", ts:Date.now(), model:"LUKHΛS Core"},
        {id:"demo2", kind:"validation", title:"Facts Validated", body:"All information checked and verified with high confidence.", ts:Date.now()-1000, model:"GPT-5"},
      ]);
    }
  }, []);
  const capsule: ContextCapsule = {
    threadId: params.threadId,
    summary: "Research → validate → produce short video explainer",
    excerpts: ["Perplexity answer pasted here (sample excerpt)."],
    evidence: [],
    userIntents: ["validate.facts", "video.summarize", "video.generate"],
    consent: { allowCrossProvider: false, allowExternalWebFetch: true, containPII: false, piiRedacted: true },
    hash: "dev"
  };
  
  // Bridge capsule to palette layer
  useEffect(() => {
    const ev = new CustomEvent("lukhas:capsule", { detail: capsule });
    window.dispatchEvent(ev);
  }, [capsule]);
  
  // Listen for palette results to add cards
  useEffect(() => {
    const onAdd = (e: any) => {
      const r = e.detail as { title: string; body: string; kind?: string; model?: string };
      setCards((prev) => [
        ...prev,
        {
          id: Math.random().toString(36).slice(2, 10),
          kind: (r.kind as any) || "text",
          title: r.title, body: r.body, model: r.model, ts: Date.now(), meta: {}
        }
      ]);
    };
    document.addEventListener("lukhas:canvas-add-card", onAdd as any);
    return () => document.removeEventListener("lukhas:canvas-add-card", onAdd as any);
  }, []);
  
  // Mount P2P chat in the right sidebar
  useEffect(() => {
    import('react-dom/client').then((ReactDOM) => {
      const mountPoint = document.getElementById('p2p-root');
      if (mountPoint && !mountPoint.hasChildNodes()) {
        const root = ReactDOM.createRoot(mountPoint);
        root.render(<P2PChat threadId={params.threadId} />);
      }
    });
  }, [params.threadId]);
  function onResult(r: { model: string; output: string; skill: string }) {
    const kind = r.skill === "validate.facts" ? "validation"
      : r.skill === "video.summarize" ? "storyboard"
      : r.skill === "write.email" ? "draft"
      : "text";
    setCards((prev) => [
      ...prev,
      {
        id: Math.random().toString(36).slice(2, 10),
        kind: kind as ResultCardData["kind"],
        title: label(kind as any),
        body: r.output,
        model: r.model,
        ts: Date.now(),
        meta: kind === "storyboard" ? { scenes: (r.output.match(/(?:Scene|•|\d+\.)\s.+/g) || []).slice(0, 8) } : {},
      },
    ]);
  }
  return (
    <ModeProvider threadId={params.threadId}>
      <section style={{ border: "1px solid var(--line)", borderRadius: "var(--radius-lg)", padding: 16, minHeight: 480, background:"var(--panel)", boxShadow:"var(--shadow-inset)" }}>
        <div style={{ display:"grid", gap: 10 }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
            <h2>Canvas · Thread {params.threadId}</h2>
            <div />
          </div>
          <ConsentBanner />
          <SuggestionChips capsule={capsule} onResult={onResult} />
          {cards.length ? <CanvasCarousel cards={cards} /> : <EmptyCanvas />}
        </div>
      </section>
    </ModeProvider>
  );
}

function label(kind: "validation"|"storyboard"|"draft"|"text") {
  switch (kind) {
    case "validation": return "Validation · Facts checked";
    case "storyboard": return "Storyboard · Video plan";
    case "draft": return "Draft · Proposed reply";
    default: return "Result";
  }
}