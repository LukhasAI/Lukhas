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

    switch (tone) {
      case 'glass':
        root.style.setProperty('--panel', 'rgba(16,20,29,0.55)');
        root.style.setProperty('--panel-heavy', 'rgba(16,20,29,0.75)');
        root.style.setProperty('--bg', '#0c1018');
        break;
      case 'solid':
        root.style.setProperty('--panel', 'rgb(16,20,29)');
        root.style.setProperty('--panel-heavy', 'rgb(12,16,24)');
        root.style.setProperty('--bg', '#000000');
        break;
      case 'minimal':
        root.style.setProperty('--panel', 'rgba(255,255,255,0.03)');
        root.style.setProperty('--panel-heavy', 'rgba(255,255,255,0.05)');
        root.style.setProperty('--bg', '#050505');
        break;
    }
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
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '6px 10px',
          border: '1px solid var(--line)',
          borderRadius: 10,
          background: 'var(--panel)',
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
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              marginTop: 4,
              minWidth: 180,
              background: 'var(--panel)',
              backdropFilter: 'saturate(140%) blur(18px)',
              border: '1px solid var(--line)',
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
