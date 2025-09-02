"use client";
import { useState, useEffect } from "react";

type ToneMode = "glass" | "solid" | "minimal";

interface ToneToggleProps {
  className?: string;
}

export default function ToneToggle({ className = "" }: ToneToggleProps) {
  const [mode, setMode] = useState<ToneMode>("glass");
  const [isOpen, setIsOpen] = useState(false);

  // Load tone preference from localStorage
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const saved = localStorage.getItem('lukhas:tone-mode') as ToneMode;
      if (saved && ['glass', 'solid', 'minimal'].includes(saved)) {
        setMode(saved);
        applyToneMode(saved);
      }
    } catch {}
  }, []);

  // Save and apply tone mode
  function changeTone(newMode: ToneMode) {
    setMode(newMode);
    setIsOpen(false);
    try {
      localStorage.setItem('lukhas:tone-mode', newMode);
    } catch {}
    applyToneMode(newMode);
  }

  function applyToneMode(tone: ToneMode) {
    const root = document.documentElement;
    
    // Set the data-tone attribute for CSS to react to
    root.setAttribute('data-tone', tone);

    // The CSS system now handles tone switching via data-tone attribute
    // No need to manually set CSS properties - the design tokens handle everything
    console.log(`🎨 Tone switched to: ${tone}`);
    
    // Optional: Trigger a custom event for other components to listen to
    const event = new CustomEvent('lukhas:tone-change', { detail: { tone } });
    document.dispatchEvent(event);
  }

  const tones = [
    { id: 'glass', label: 'Glass', icon: '◇', desc: 'Translucent glassmorphism' },
    { id: 'solid', label: 'Solid', icon: '◼', desc: 'Solid dark panels' },
    { id: 'minimal', label: 'Minimal', icon: '◯', desc: 'Ultra-minimal design' },
  ] as const;

  return (
    <div className={className} style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        title={`Current tone: ${mode}`}
        className="panel"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '6px 10px',
          borderRadius: 10,
          color: 'var(--text)',
          cursor: 'pointer',
          fontSize: 12,
          transition: 'background 0.15s ease',
        }}
      >
        <span style={{ fontSize: 14 }}>
          {tones.find(t => t.id === mode)?.icon}
        </span>
        <span>Tone</span>
        <span style={{ opacity: 0.6, transform: isOpen ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s ease' }}>
          ▾
        </span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop to close on outside click */}
          <div
            onClick={() => setIsOpen(false)}
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 999,
            }}
          />

          {/* Tone options menu */}
          <div
            className="panel"
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              marginTop: 4,
              minWidth: 180,
              backdropFilter: 'saturate(140%) blur(18px)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-2)',
              zIndex: 1000,
              overflow: 'hidden',
            }}
          >
            {tones.map((tone) => (
              <button
                key={tone.id}
                onClick={() => changeTone(tone.id as ToneMode)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '10px 12px',
                  border: 'none',
                  background: mode === tone.id ? 'var(--panel-heavy)' : 'transparent',
                  color: 'var(--text)',
                  cursor: 'pointer',
                  fontSize: 13,
                  textAlign: 'left',
                  transition: 'background 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  if (mode !== tone.id) {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (mode !== tone.id) {
                    e.currentTarget.style.background = 'transparent';
                  }
                }}
              >
                <span style={{ fontSize: 16, width: 20, textAlign: 'center' }}>
                  {tone.icon}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: mode === tone.id ? 600 : 400 }}>
                    {tone.label}
                  </div>
                  <div style={{ opacity: 0.7, fontSize: 11, marginTop: 1 }}>
                    {tone.desc}
                  </div>
                </div>
                {mode === tone.id && (
                  <span style={{ color: '#60a5fa', fontSize: 12 }}>✓</span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
