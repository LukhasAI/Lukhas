"use client";
import { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
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
import ComposerActions from "@/components/composer-actions";
import ToneToggle from "@/components/tone-toggle";
import ModeChips from "@/components/mode-chips";
import ModeToolbar from "@/components/mode-toolbar";
import { useMode } from "@/components/mode-context";
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
          style={{
            position: "fixed", top: 0, left: 0, right: 0, height: 48,
            transform: `translateY(${topbar ? 0 : -56}px)`,
            transition: "transform 220ms cubic-bezier(0.4,0,0.2,1)",
            background: "rgba(10,12,20,0.7)", borderBottom: "1px solid #1f2328", backdropFilter: "blur(8px)",
            zIndex: 50, display: "flex", alignItems: "center", padding: "0 12px", gap: 8
          }}
        >
          <strong style={{ letterSpacing: 1 }}>LUKHΛS Studio</strong>
          <div style={{ marginLeft: "auto", display: "flex", gap: 8, alignItems: "center" }}>
            <ToneToggle />
            <button>Scenes</button>
            <button>Profile</button>
            <button onClick={() => setShowSettings(true)}>Settings</button>
          </div>
        </header>

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
            <div style={{ borderBottom:"1px solid var(--line)", background:"var(--panel-heavy)" }}>
              <WidgetRail side="top" defaults={["conversations","delivery"]} half={prefs.depth==="half"} />
            </div>
          )}

          <div style={{ display: "flex", flex: 1 }}>
            {/* LEFT rail */}
            {(prefs.placement.startsWith("left") || prefs.placement.endsWith("left")) && (
              <aside style={{ width: 220, background: "var(--panel-heavy)", display:"grid", gridTemplateRows:"auto 1fr auto" }}>
                <div style={{ padding:"10px 10px 0 10px", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                  <strong style={{ fontSize:12, opacity:.8 }}>Models</strong>
                </div>
                <ModelDock />
                <WidgetRail side="left" defaults={["conversations","trading","terminal"]} half={prefs.depth==="half"} />
              </aside>
            )}

            <main style={{ flex: 1, position: "relative", zIndex: 1, padding: "16px 18px 12px 18px" }}>
              <div className="glass" style={{ height:"100%", padding:12 }}>
                {children}
              </div>
            </main>

            {/* RIGHT rail */}
            {(prefs.placement.startsWith("right") || prefs.placement.endsWith("right")) && (
              <aside style={{ width: 240, background:"var(--panel-heavy)", display:"grid", gridTemplateRows:"auto auto 1fr" }}>
                <div style={{ borderBottom:"1px solid var(--line)", padding:"10px 12px" }}>
                  <strong style={{ fontSize:12, opacity:.8 }}>People</strong>
                </div>
                <div style={{ minHeight: 200, borderBottom:"1px solid var(--line)" }}>
                  <div style={{ height:"100%" }}><span id="p2p-root"/></div>
                </div>
                <WidgetRail side="right" defaults={["delivery","trading"]} half={prefs.depth==="half"} />
              </aside>
            )}
          </div>

          {/* BOTTOM rail */}
          {prefs.placement.startsWith("bottom") && (
            <div style={{ borderTop:"1px solid var(--line)", background:"var(--panel-heavy)" }}>
              <WidgetRail side="bottom" defaults={["terminal","trading"]} half={prefs.depth==="half"} />
            </div>
          )}
        </div>

        <FooterBar />

        {showSettings && (
          <SettingsModal onClose={() => setShowSettings(false)}>
            <SettingsTabs />
          </SettingsModal>
        )}
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
    <div style={{
      padding: 14,
      display: "grid",
      gridTemplateColumns: modeChips ? "auto auto 1fr auto" : "auto 1fr auto",
      gap: 12,
      alignItems: "center",
      borderTop:"1px solid var(--line)",
      background:"var(--bg)"
    }}>
      {modeChips}
      {modeToolbar}
      <span style={{ fontSize: 12, opacity: 0.75, padding: "6px 10px", border: "1px solid var(--line2)", borderRadius: 10 }}>
        Model: {current.label}
      </span>
      <div style={{ position: "relative", flex: 1 }}>
        {showActions && (
          <ComposerActions onAction={handleAction} />
        )}
        {/* drag handle to handoff the whole thread to a model icon */}
        <div draggable
             onDragStart={(e)=>{ e.dataTransfer.setData("text/plain","handoff"); }}
             title="Drag onto a model icon to hand off"
             style={{ position:"absolute", left:8, top:8, width:18, height:18, border:"1px solid var(--line)", borderRadius:6, display:"grid", placeItems:"center", opacity:.8, zIndex:10 }}>
          ⋮
        </div>
        {/* actions toggle button */}
        <button
          onClick={() => setShowActions(!showActions)}
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
          placeholder={palette.isIntercepting
            ? "Command Palette — type a command… (Enter to run · Esc to close)"
            : "Type to chat, write an email, /command, or draft… (Enter to send · Shift+Enter for newline · ⌘K commands)"
          }
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            palette.mode === "closed" ? palette.openMini() : palette.close();
          }
          if (e.key === "Escape" && palette.isIntercepting) { palette.close(); }
          if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); dispatch(); }
        }}
          style={{
            width: "100%", minHeight: 60, maxHeight: 220, borderRadius: 18,
            border: "1px solid var(--line)", background: "#0f131a", color: "var(--text)",
            padding: "14px 18px", resize: "none", lineHeight: 1.35,
            boxShadow:"var(--shadow-2)"
          }}
        />
      </div>
      <div style={{ position: "relative" }}>
        <button
          id="send"
          style={{ height: 56, borderRadius: 14, padding: "0 16px" }}
          onMouseEnter={(e) => {
            const r = (e.currentTarget as HTMLButtonElement).getBoundingClientRect();
            setMenu({ open: true, x: r.left, y: r.top - 8 });
          }}
          onMouseLeave={() => {
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
