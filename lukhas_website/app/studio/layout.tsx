"use client";
import { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import "./studio.css";
import { ModelProvider } from "@/components/model-context";
import ModelDock from "@/components/model-dock";
import WidgetRail from "@/components/widget-rail";
import { loadPrefs } from "@/components/layout-prefs";
import SettingsModal from "@/components/settings-modal";
import SettingsTabs from "@/components/settings-tabs";
import { useModel, getThreadKey } from "@/components/model-context";
import { usePathname } from "next/navigation";
import SendTargetMenu, { type SendTarget } from "@/components/send-target-menu";
import UnifiedInbox from "@/components/unified-inbox";
import { PaletteProvider, usePalette } from "@/components/palette-context";
import TopHotspot from "@/components/top-hotspot";
import AgentPalette from "@/components/agent-palette";
import ComposerActionsPortal from "@/components/composer-actions-portal";
import ToneToggle from "@/components/tone-toggle";
import ModeChips from "@/components/mode-chips";
import ModeToolbar from "@/components/mode-toolbar";
import { useMode } from "@/components/mode-context";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import type { Metadata } from 'next'

const NeuralBackground = dynamic(() => import("@/components/neural-background"), { ssr: false });

interface StudioLayoutProps {
  children: React.ReactNode
}

export default function StudioLayout({ children }: StudioLayoutProps) {
  const bgEnabled = process.env.NEXT_PUBLIC_BG_IN_STUDIO === "true";
  const [topbar, setTopbar] = useState(true);
  const [prefs, setPrefs] = useState(loadPrefs());
  const [showSettings, setShowSettings] = useState(false);
  const [leftBarExpanded, setLeftBarExpanded] = useState(true);
  const [rightBarExpanded, setRightBarExpanded] = useState(true);

  // Refresh prefs when localStorage changes
  useEffect(() => {
    const handleStorage = () => setPrefs(loadPrefs());
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);
  useEffect(() => {
    let t: any;
    const onMove = () => {
      setTopbar(true);
      clearTimeout(t);
      t = setTimeout(() => setTopbar(false), 1500); // auto-hide after idle
    };
    window.addEventListener("mousemove", onMove);
    onMove();
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  return (
    <PaletteProvider>
      <ModelProvider>
        <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", position: "relative", background:"var(--bg)" }}>
          {bgEnabled && <NeuralBackground mode="studio" />}
          <TopHotspot />
          <AgentPalette />
        <header
          className="studio-header"
          style={{
            transform: `translateY(${topbar ? 0 : -64}px)`,
          }}
        >
          <span className="lukhas-brand" style={{ fontSize: "18px" }}>
            LUKHΛS
          </span>
          <div style={{ marginLeft: "auto", display: "flex", gap: 8, alignItems: "center" }}>
            <ToneToggle />
            <button>Scenes</button>
            <button>Profile</button>
            <button onClick={() => setShowSettings(true)}>Settings</button>
          </div>
        </header>
        <div style={{ height: 56 }} />
        <div
          style={{
            display: prefs.placement.includes("top") || prefs.placement.includes("bottom") ? "grid" : "flex",
            gridTemplateRows: prefs.placement.includes("top") || prefs.placement.includes("bottom")
              ? (prefs.depth==="half" ? "50vh 1fr auto" : "auto 1fr auto")
              : undefined,
            flex: 1
          }}
        >
          {/* TOP rail */}
          {prefs.placement.startsWith("top") && (
            <div className="panel" style={{ borderBottom:"1px solid var(--line)", background:"var(--panel-heavy)" }}>
              <WidgetRail side="top" defaults={["conversations","delivery"]} half={prefs.depth==="half"} />
            </div>
          )}

          <div style={{
            display: 'grid',
            gridTemplateColumns: `${(prefs.placement.startsWith("left") || prefs.placement.endsWith("left")) 
              ? (leftBarExpanded ? 'var(--rail-w-left)' : '48px') 
              : '0px'} 1fr ${(prefs.placement.startsWith("right") || prefs.placement.endsWith("right")) 
              ? (rightBarExpanded ? 'var(--rail-w-right)' : '48px') 
              : '0px'}`,
            gridTemplateRows: '1fr auto',
            flex: 1
          }}>
            {/* LEFT rail */}
            {(prefs.placement.startsWith("left") || prefs.placement.endsWith("left")) && (
              <aside 
                className="studio-sidebar-left panel-heavy"
                style={{ gridColumn: 1, gridRow: '1 / 3' }}
              >
                <div style={{ 
                  padding: "var(--pad)", 
                  display: "flex", 
                  justifyContent: leftBarExpanded ? "space-between" : "center", 
                  alignItems: "center",
                  borderBottom: "1px solid var(--glass-border)"
                }}>
                  {leftBarExpanded && (
                    <strong style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)", fontWeight: 300 }}>Models</strong>
                  )}
                  <button
                    onClick={() => setLeftBarExpanded(!leftBarExpanded)}
                    className="studio-collapse-button"
                  >
                    <ChevronLeftIcon className={`chevron-icon ${!leftBarExpanded ? 'chevron-rotated' : ''}`} />
                  </button>
                </div>
                {leftBarExpanded && <ModelDock />}
                {leftBarExpanded && <WidgetRail side="left" defaults={["conversations","trading","terminal"]} half={prefs.depth==="half"} />}
              </aside>
            )}

            {/* CENTER column - Main content */}
            <main style={{ 
              gridColumn: 2, 
              gridRow: 1,
              position: "relative", 
              padding: "72px var(--spacing-4) var(--spacing-3) var(--spacing-4)",
              minHeight: 0 // Allow grid to size it
            }}>
              <div style={{ height: "100%", maxWidth: 'var(--max-content-width)', margin: "0 auto" }}>
                {children}
              </div>
            </main>

            {/* Footer Bar spans center column only */}
            <div style={{ gridColumn: 2, gridRow: 2 }}>
              <FooterBar />
            </div>

            {/* RIGHT rail */}
            {(prefs.placement.startsWith("right") || prefs.placement.endsWith("right")) && (
              <aside 
                className="studio-sidebar-right panel-heavy"
                style={{ gridColumn: 3, gridRow: '1 / 3' }}
              >
                <div style={{ 
                  borderBottom: "1px solid var(--glass-border)", 
                  padding: "var(--pad)", 
                  display: "flex", 
                  justifyContent: rightBarExpanded ? "space-between" : "center", 
                  alignItems: "center" 
                }}>
                  {rightBarExpanded && (
                    <strong style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)", fontWeight: 300 }}>People</strong>
                  )}
                  <button
                    onClick={() => setRightBarExpanded(!rightBarExpanded)}
                    className="studio-collapse-button"
                  >
                    <ChevronRightIcon className={`chevron-icon ${!rightBarExpanded ? 'chevron-rotated' : ''}`} />
                  </button>
                </div>
                {rightBarExpanded && (
                  <div style={{ minHeight: 200, borderBottom: "1px solid var(--line)" }}>
                    <div style={{ height: "100%" }}><span id="p2p-root"/></div>
                  </div>
                )}
                {rightBarExpanded && <WidgetRail side="right" defaults={["delivery","trading"]} half={prefs.depth==="half"} />}
              </aside>
            )}
          </div>

          {/* BOTTOM rail */}
          {prefs.placement.startsWith("bottom") && (
            <div className="panel" style={{ borderTop:"1px solid var(--line)", background:"var(--panel-heavy)" }}>
              <WidgetRail side="bottom" defaults={["terminal","trading"]} half={prefs.depth==="half"} />
            </div>
          )}
        </div>

        {showSettings && (
          <SettingsModal onClose={() => setShowSettings(false)}>
            <SettingsTabs />
          </SettingsModal>
        )}
        <style jsx global>{`
          /* Global layout guards (Studio scope) */
          *, *::before, *::after { box-sizing: border-box; }
          html, body { height: 100%; }

          /* Typography clamps for large screens so hero headings don't explode */
          h1{ font-size: clamp(24px, 3.6vw + 8px, 56px); line-height: 1.1; }
          h2{ font-size: clamp(18px, 2.4vw + 6px, 32px); line-height: 1.2; }

          /* Media should never overflow */
          img, svg, canvas, video { max-width: 100%; height: auto; }

          /* Any decorative background SVGs sit behind content and ignore clicks */
          .hero-bg, [data-hero-bg] { position: absolute; inset: 0; z-index: 0; pointer-events: none; }

          /* Primary content sits above decorative layers */
          .content-layer { position: relative; z-index: 1; }

          /* Cookie banner should not overlap hero/header */
          .cookie-banner, [data-cookie-banner] {
            position: fixed; left: 12px; right: 12px; bottom: 12px; z-index: 40;
            max-width: min(720px, 92vw);
          }

          /* Constrain panels to a comfortable reading width */
          .container { max-width: 1200px; margin: 0 auto; padding-left: clamp(12px, 2vw, 24px); padding-right: clamp(12px, 2vw, 24px); }

          /* Prevent absolute-positioned badges/icons from covering text */
          [data-badge], .hero-badge { max-width: 60vmin; max-height: 60vmin; z-index: 0; }
        `}</style>
        </div>
      </ModelProvider>
    </PaletteProvider>
  );
}

function FooterBar() {
  const { current } = useModel();
  const pathname = usePathname() || "/studio";
  const threadKey = getThreadKey(pathname);
  const storageKey = `lukhas:sendTarget:${threadKey}`;
  const defaultTarget: SendTarget = "agent";
  const [target, setTarget] = useState<SendTarget>(() => {
    try { return (localStorage.getItem(storageKey) as SendTarget) || defaultTarget; } catch { return defaultTarget; }
  });
  const [menu, setMenu] = useState<{ open: boolean; x: number; y: number }>({ open: false, x: 0, y: 0 });
  useEffect(() => { try { localStorage.setItem(storageKey, target); } catch {} }, [target, storageKey]);
  const taRef = useRef<HTMLTextAreaElement | null>(null);
  const [showActions, setShowActions] = useState(false);
  const [actionsPosition, setActionsPosition] = useState({ x: 0, y: 0 });
  const palette = usePalette();

  // Check if we're in a mode context
  let modeChips = null;
  let modeToolbar = null;
  try {
    const modeContext = useMode();
    modeChips = <ModeChips />;
    modeToolbar = <ModeToolbar />;
  } catch {
    // Not in a mode context, skip mode components
  }

  function dispatch() {
    if (palette.isIntercepting) {
      const value = taRef.current?.value || "";
      palette.executeFromQuery(value);
      if (taRef.current) taRef.current.value = "";
      return;
    }
    alert(`Dispatch to ${target.toUpperCase()} (stub)`);
  }

  function handleAction(action: string) {
    setShowActions(false);
    const prompts = {
      email: "Draft a professional email about: ",
      research: "Research this topic thoroughly: ",
      code: "Help me with this code: ",
      creative: "Creative writing on: ",
      analysis: "Analyze this data/information: ",
      summary: "Summarize this content: ",
    };
    if (taRef.current) {
      taRef.current.value = prompts[action as keyof typeof prompts] || "";
      taRef.current.focus();
    }
  }

  // listen for "composer-email" requests (from command palette)
  useEffect(() => {
    const onCompose = (e: any) => {
      const draft = String(e.detail?.body || "Subject: …\n\nHi …,\n\n");
      if (taRef.current) {
        taRef.current.value = draft;
        taRef.current.focus();
        taRef.current.setSelectionRange(draft.length, draft.length);
      }
    };
    document.addEventListener("lukhas:composer-email", onCompose as any);
    return () => document.removeEventListener("lukhas:composer-email", onCompose as any);
  }, []);

  return (
    <div className="studio-footer-bar" style={{
      display: "grid",
      gridTemplateColumns: modeChips ? "auto auto 1fr auto" : "auto 1fr auto",
      gap: 12,
      alignItems: "center"
    }}>
      {modeChips}
      {modeToolbar}
      <span style={{ fontSize: 12, opacity: 0.75, padding: "6px 10px", border: "1px solid var(--line2)", borderRadius: 10 }}>
        Model: {current.label}
      </span>
      <div style={{ position: "relative", flex: 1 }}>
        <ComposerActionsPortal
          show={showActions}
          position={actionsPosition}
          onAction={handleAction}
        />
        {/* drag handle to handoff the whole thread to a model icon */}
        <div draggable
             onDragStart={(e)=>{ e.dataTransfer.setData("text/plain","handoff"); }}
             title="Drag onto a model icon to hand off"
             style={{ position:"absolute", left:8, top:8, width:18, height:18, border:"1px solid var(--line)", borderRadius:6, display:"grid", placeItems:"center", opacity:.8, zIndex:10 }}>
          ⋮
        </div>
        {/* actions toggle button */}
        <button
          onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            setActionsPosition({
              x: rect.left,
              y: rect.top - 8
            });
            setShowActions(!showActions);
          }}
          title="Quick actions"
          style={{
            position: "absolute", right: 8, top: 8, width: 28, height: 28,
            border: "1px solid var(--line)", borderRadius: 8, background: showActions ? "var(--panel-heavy)" : "transparent",
            display: "grid", placeItems: "center", opacity: 0.8, zIndex: 10, cursor: "pointer"
          }}
        >
          ⚡
        </button>
        <textarea
          ref={taRef}
          aria-label="Unified input"
          className="studio-textarea"
          placeholder={palette.isIntercepting
            ? "Command Palette — type a command… (Enter to run · Esc to close)"
            : "Type, /command, or ⌘K for actions."
          }
          onFocus={() => {
            document.dispatchEvent(new CustomEvent('lukhas:composer:focus'));
          }}
          onBlur={() => {
            document.dispatchEvent(new CustomEvent('lukhas:composer:blur'));
          }}
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
              e.preventDefault();
              palette.mode === "closed" ? palette.openMini() : palette.close();
            }
            if (e.key === "Escape" && palette.isIntercepting) { palette.close(); }
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); dispatch(); }
          }}
        />
      </div>
      <div style={{ position: "relative" }}>
        <button
          id="send"
          style={{ 
            height: 56, 
            borderRadius: 12, 
            padding: "0 20px",
            background: "linear-gradient(135deg, rgba(107, 70, 193, 0.8), rgba(168, 85, 247, 0.8))",
            border: "1px solid rgba(168, 85, 247, 0.3)",
            color: "white",
            fontSize: "14px",
            fontWeight: 500,
            cursor: "pointer",
            transition: "all 0.2s ease",
            boxShadow: "0 4px 16px rgba(168, 85, 247, 0.2)"
          }}
          onMouseEnter={(e) => {
            const btn = e.target as HTMLButtonElement;
            btn.style.background = "linear-gradient(135deg, rgba(107, 70, 193, 1), rgba(168, 85, 247, 1))";
            btn.style.boxShadow = "0 6px 24px rgba(168, 85, 247, 0.3)";
            btn.style.transform = "translateY(-1px)";
            
            const r = (e.currentTarget as HTMLButtonElement).getBoundingClientRect();
            setMenu({ open: true, x: r.left, y: r.top - 8 });
          }}
          onMouseLeave={(e) => {
            const btn = e.target as HTMLButtonElement;
            btn.style.background = "linear-gradient(135deg, rgba(107, 70, 193, 0.8), rgba(168, 85, 247, 0.8))";
            btn.style.boxShadow = "0 4px 16px rgba(168, 85, 247, 0.2)";
            btn.style.transform = "translateY(0)";
            // keep menu if pointer is over it; on outside click menu will close
          }}
          onClick={() => dispatch()}
          aria-haspopup="menu"
          aria-expanded={menu.open}
        >
          Send → {target}
        </button>
        <SendTargetMenu
          open={menu.open}
          x={menu.x}
          y={menu.y - 180}
          onClose={() => setMenu((m) => ({ ...m, open: false }))}
          onSelect={(t) => setTarget(t)}
        />
      </div>
    </div>
  );
}
