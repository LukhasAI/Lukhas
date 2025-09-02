"use client";
import { useEffect, useState, use } from "react";
import SuggestionChips from "@/components/suggestion-chips";
import ConsentBanner from "@/components/consent-banner";
import CanvasCarousel from "@/components/canvas-carousel";
import P2PChat from "@/components/p2p-chat";
import EmptyCanvas from "@/components/empty-canvas";
import { ModeProvider } from "@/components/mode-context";
import type { ContextCapsule } from "@lukhas/orchestrator/contextCapsule";
import type { ResultCardData } from "@/components/result-card";

export const dynamic = "force-dynamic";
export default function StudioThreadPage({ params }: { params: Promise<{ threadId: string }> }) {
  // Unwrap params Promise for Next.js 15 compatibility
  const { threadId } = use(params);
  const [cards, setCards] = useState<ResultCardData[]>([]);
  const [composerFocused, setComposerFocused] = useState(false);

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
    threadId: threadId,
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
    let root: any = null;
    
    import('react-dom/client').then((ReactDOM) => {
      const mountPoint = document.getElementById('p2p-root');
      if (mountPoint) {
        // Clear existing content and create new root
        mountPoint.innerHTML = '';
        root = ReactDOM.createRoot(mountPoint);
        root.render(<P2PChat threadId={threadId} />);
      }
    });

    return () => {
      if (root) {
        root.unmount();
      }
    };
  }, [threadId]);

  // Listen for composer focus/blur events
  useEffect(() => {
    const onFocus = () => setComposerFocused(true);
    const onBlur = () => setComposerFocused(false);
    
    document.addEventListener('lukhas:composer:focus', onFocus);
    document.addEventListener('lukhas:composer:blur', onBlur);
    
    return () => {
      document.removeEventListener('lukhas:composer:focus', onFocus);
      document.removeEventListener('lukhas:composer:blur', onBlur);
    };
  }, []);
  
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
    <ModeProvider threadId={threadId}>
      {/* Canvas - Main Content Area with floating design */}
      <div style={{ 
        flex: 1, 
        display: "flex", 
        flexDirection: "column",
        position: "relative",
        background: "linear-gradient(135deg, rgba(107,70,193,0.05), rgba(168,85,247,0.03))"
      }}>
        {/* Canvas Content */}
        <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
          {/* Background gradient for depth */}
          <div style={{
            position: "absolute",
            inset: 0,
            background: "radial-gradient(circle at 50% 50%, rgba(168,85,247,0.08) 0%, transparent 70%)"
          }} />
          
          {/* Canvas State Content */}
          <div style={{ 
            position: "relative", 
            height: "100%", 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center",
            padding: "2rem"
          }}>
            {/* Hero - Non-blocking decorative background */}
            <div
              className="studio-hero"
              aria-hidden="true"
              style={{
                opacity: (cards.length === 0 && !composerFocused) ? 1 : 0
              }}
            >
              <div className="studio-hero-content">
                <div className="lukhas-canvas-logo">
                  LUKHΛS
                </div>
                <p style={{ 
                  color: "var(--text-secondary)", 
                  fontSize: "var(--text-lg)",
                  margin: "var(--pad-md) 0 0 0",
                  fontWeight: 300
                }}>
                  Ready when you are.
                </p>
              </div>
            </div>
            
            {cards.length > 0 && (
              <div style={{ width: "100%", maxWidth: "56rem" }}>
                <CanvasCarousel cards={cards} />
              </div>
            )}
          </div>
        </div>
        
        {/* Consent Banner - floating at top */}
        <div style={{ 
          position: "absolute", 
          top: "1rem", 
          left: "1rem", 
          right: "1rem", 
          zIndex: 10 
        }}>
          <ConsentBanner />
        </div>
        
        {/* Suggestion Chips - floating above input */}
        <div style={{
          position: "absolute",
          bottom: "5rem",
          left: "1rem",
          right: "1rem",
          display: "flex",
          justifyContent: "center",
          zIndex: 10
        }}>
          <SuggestionChips capsule={capsule} onResult={onResult} />
        </div>
      </div>
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