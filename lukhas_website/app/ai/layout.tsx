"use client";

import { useEffect, useState } from "react";
import "./ai.css";
import { ChevronLeftIcon } from "@heroicons/react/24/outline";

interface AILayoutProps {
  children: React.ReactNode;
}

/**
 * AI Domain Layout - LUKHΛS AI Platform
 * 
 * Route-scoped layout that replaces global CSS hacks with proper layout structure.
 * Contains sidebar navigation for AI consciousness technology features.
 * 
 * This layout solves the global CSS issues by providing proper route-scoped styling
 * without relying on data-page attributes or !important overrides.
 */
export default function AILayout({ children }: AILayoutProps) {
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [topbar, setTopbar] = useState(true);

  // Auto-hide topbar on idle
  useEffect(() => {
    let t: any;
    const onMove = () => {
      setTopbar(true);
      clearTimeout(t);
      t = setTimeout(() => setTopbar(false), 2000);
    };
    window.addEventListener("mousemove", onMove);
    onMove();
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  return (
    <div className="ai-layout">
      {/* AI Domain Header */}
      <header
        className="ai-header"
        style={{
          transform: `translateY(${topbar ? 0 : -64}px)`,
        }}
      >
        <div className="ai-header-content">
          <span className="ai-brand">LUKHΛS AI</span>
          <nav className="ai-header-nav">
            <a href="/ai/consciousness">Consciousness</a>
            <a href="/ai/trinity">Trinity Framework</a>
            <a href="/ai/tools">Tools & APIs</a>
            <a href="/experience">Experience</a>
          </nav>
        </div>
      </header>

      <div className="ai-body">
        {/* AI Sidebar */}
        <aside className={`ai-sidebar ${sidebarExpanded ? 'expanded' : 'collapsed'}`}>
          <div className="ai-sidebar-header">
            {sidebarExpanded && (
              <h3 className="ai-sidebar-title">Navigation</h3>
            )}
            <button
              onClick={() => setSidebarExpanded(!sidebarExpanded)}
              className="ai-sidebar-toggle"
            >
              <ChevronLeftIcon className={`chevron-icon ${!sidebarExpanded ? 'rotated' : ''}`} />
            </button>
          </div>
          
          {sidebarExpanded && (
            <nav className="ai-sidebar-nav">
              <div className="ai-nav-section">
                <h4>Consciousness</h4>
                <ul>
                  <li><a href="/ai/consciousness/overview">Overview</a></li>
                  <li><a href="/ai/consciousness/vivox">VIVOX System</a></li>
                  <li><a href="/ai/consciousness/memory">Memory Folds</a></li>
                  <li><a href="/ai/consciousness/dream">Dream States</a></li>
                </ul>
              </div>
              
              <div className="ai-nav-section">
                <h4>Trinity Framework</h4>
                <ul>
                  <li><a href="/ai/trinity/identity">⚛️ Identity</a></li>
                  <li><a href="/ai/trinity/memory">✦ Memory</a></li>
                  <li><a href="/ai/trinity/vision">🔬 Vision</a></li>
                  <li><a href="/ai/trinity/bio">🌱 Bio</a></li>
                  <li><a href="/ai/trinity/dream">🌙 Dream</a></li>
                  <li><a href="/ai/trinity/ethics">⚖️ Ethics</a></li>
                  <li><a href="/ai/trinity/guardian">🛡️ Guardian</a></li>
                  <li><a href="/ai/trinity/quantum">⚛️ Quantum</a></li>
                </ul>
              </div>
              
              <div className="ai-nav-section">
                <h4>Tools & APIs</h4>
                <ul>
                  <li><a href="/ai/api">API Reference</a></li>
                  <li><a href="/ai/integrations">Integrations</a></li>
                  <li><a href="/ai/playground">Playground</a></li>
                  <li><a href="/ai/docs">Documentation</a></li>
                </ul>
              </div>
            </nav>
          )}
        </aside>

        {/* Main Content Area */}
        <main className="ai-main-content">
          {children}
        </main>
      </div>
    </div>
  );
}