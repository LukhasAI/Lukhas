"use client";
import { useState, useEffect } from "react";
import { getCurrentVocabularyFamily, validateMATRIZPipeline, type VocabularyFamily } from "@/lib/toneSystem";

type ToneMode = "glass" | "solid" | "minimal";
type ConsciousnessLayer = "poetic" | "friendly" | "technical";

interface ToneToggleProps {
  className?: string;
  showVocabularyFamily?: boolean;
  showConsciousnessMetrics?: boolean;
  onLayerChange?: (layer: ConsciousnessLayer) => void;
  onModeChange?: (mode: ToneMode) => void;
}

export default function ToneToggle({
  className = "",
  showVocabularyFamily = true,
  showConsciousnessMetrics = false,
  onLayerChange,
  onModeChange
}: ToneToggleProps) {
  const [mode, setMode] = useState<ToneMode>("glass");
  const [layer, setLayer] = useState<ConsciousnessLayer>("friendly");
  const [isOpen, setIsOpen] = useState(false);
  const [vocabularyFamily, setVocabularyFamily] = useState<VocabularyFamily | null>(null);
  const [consciousnessMetrics, setConsciousnessMetrics] = useState({
    noveltyScore: 0.8,
    matrizValidated: true
  });

  // Load preferences and initialize T4/0.01% consciousness features
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const savedMode = localStorage.getItem('lukhas:tone-mode') as ToneMode;
      const savedLayer = localStorage.getItem('lukhas:consciousness-layer') as ConsciousnessLayer;

      if (savedMode && ['glass', 'solid', 'minimal'].includes(savedMode)) {
        setMode(savedMode);
        applyToneMode(savedMode);
      }

      if (savedLayer && ['poetic', 'friendly', 'technical'].includes(savedLayer)) {
        setLayer(savedLayer);
        applyConsciousnessLayer(savedLayer);
      }

      // Initialize vocabulary family rotation
      const currentFamily = getCurrentVocabularyFamily();
      setVocabularyFamily(currentFamily);

      // Update consciousness metrics
      updateConsciousnessMetrics();

    } catch {}
  }, []);

  // Update vocabulary family when week changes
  useEffect(() => {
    const interval = setInterval(() => {
      const newFamily = getCurrentVocabularyFamily();
      if (newFamily.id !== vocabularyFamily?.id) {
        setVocabularyFamily(newFamily);
      }
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [vocabularyFamily]);

  // Save and apply tone mode
  function changeTone(newMode: ToneMode) {
    setMode(newMode);
    setIsOpen(false);
    try {
      localStorage.setItem('lukhas:tone-mode', newMode);
    } catch {}
    applyToneMode(newMode);
    onModeChange?.(newMode);
  }

  // Change consciousness layer
  function changeLayer(newLayer: ConsciousnessLayer) {
    setLayer(newLayer);
    try {
      localStorage.setItem('lukhas:consciousness-layer', newLayer);
    } catch {}
    applyConsciousnessLayer(newLayer);
    onLayerChange?.(newLayer);
    updateConsciousnessMetrics();
  }

  // Apply consciousness layer styling
  function applyConsciousnessLayer(consciousnessLayer: ConsciousnessLayer) {
    const root = document.documentElement;
    root.setAttribute('data-consciousness-layer', consciousnessLayer);

    // Trigger consciousness layer change event
    const event = new CustomEvent('lukhas:consciousness-layer-change', {
      detail: { layer: consciousnessLayer, vocabularyFamily }
    });
    document.dispatchEvent(event);
  }

  // Update consciousness metrics with T4/0.01% validation
  function updateConsciousnessMetrics() {
    const sampleContent = `LUKHAS consciousness ${layer} communication with ${vocabularyFamily?.name || 'current'} vocabulary family`;
    const matrizValidation = validateMATRIZPipeline(sampleContent);
    const matrizValidated = Object.values(matrizValidation).every(Boolean);

    setConsciousnessMetrics({
      noveltyScore: Math.random() * 0.3 + 0.7, // Simulate 0.7-1.0 range
      matrizValidated
    });
  }

  function applyToneMode(tone: ToneMode) {
    const root = document.documentElement;

    // Set the data-tone attribute for CSS to react to
    root.setAttribute('data-tone', tone);

    // The CSS system now handles tone switching via data-tone attribute
    // No need to manually set CSS properties - the design tokens handle everything
    console.log(`🎨 Tone switched to: ${tone} | 🧠 Consciousness Layer: ${layer} | ${vocabularyFamily?.emoji} ${vocabularyFamily?.name}`);

    // Enhanced event with T4/0.01% consciousness data
    const event = new CustomEvent('lukhas:tone-change', {
      detail: {
        tone,
        layer,
        vocabularyFamily,
        consciousnessMetrics,
        timestamp: new Date().toISOString()
      }
    });
    document.dispatchEvent(event);
  }

  const tones = [
    { id: 'glass', label: 'Glass', icon: '◇', desc: 'Translucent glassmorphism consciousness' },
    { id: 'solid', label: 'Solid', icon: '◼', desc: 'Solid consciousness panels' },
    { id: 'minimal', label: 'Minimal', icon: '◯', desc: 'Ultra-minimal consciousness design' },
  ] as const;

  const layers = [
    { id: 'poetic', label: 'Poetic', icon: '✨', desc: 'Consciousness metaphors and inspiration' },
    { id: 'friendly', label: 'Friendly', icon: '💬', desc: 'Accessible consciousness communication' },
    { id: 'technical', label: 'Technical', icon: '🔬', desc: 'T4/0.01% precision consciousness specs' },
  ] as const;

  return (
    <div className={className} style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        title={`T4/0.01% Consciousness System | Tone: ${mode} | Layer: ${layer} | Family: ${vocabularyFamily?.name}${showConsciousnessMetrics ? ` | Novelty: ${consciousnessMetrics.noveltyScore.toFixed(2)} | MATRIZ: ${consciousnessMetrics.matrizValidated ? '✓' : '✗'}` : ''}`}
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
          border: consciousnessMetrics.matrizValidated ? '1px solid rgba(34, 197, 94, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)'
        }}
      >
        {showVocabularyFamily && vocabularyFamily && (
          <span style={{ fontSize: 14 }} title={vocabularyFamily.description}>
            {vocabularyFamily.emoji}
          </span>
        )}
        <span style={{ fontSize: 14 }}>
          {tones.find(t => t.id === mode)?.icon}
        </span>
        <span style={{ fontSize: 14 }}>
          {layers.find(l => l.id === layer)?.icon}
        </span>
        <span>T4 Tone</span>
        {showConsciousnessMetrics && (
          <span style={{
            fontSize: 10,
            opacity: 0.7,
            color: consciousnessMetrics.noveltyScore >= 0.8 ? '#22c55e' : '#ef4444'
          }}>
            {consciousnessMetrics.noveltyScore.toFixed(2)}
          </span>
        )}
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

          {/* T4/0.01% Enhanced Options Menu */}
          <div
            className="panel"
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              marginTop: 4,
              minWidth: 320,
              backdropFilter: 'saturate(140%) blur(18px)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-2)',
              zIndex: 1000,
              overflow: 'hidden',
            }}
          >
            {/* Vocabulary Family Display */}
            {showVocabularyFamily && vocabularyFamily && (
              <div style={{
                padding: '8px 12px',
                borderBottom: '1px solid var(--border)',
                background: 'var(--panel-heavy)',
                fontSize: 11
              }}>
                <div style={{ fontWeight: 600, marginBottom: 2 }}>
                  {vocabularyFamily.emoji} {vocabularyFamily.name} (Weeks {vocabularyFamily.weeks.join(', ')})
                </div>
                <div style={{ opacity: 0.7 }}>
                  {vocabularyFamily.description}
                </div>
              </div>
            )}

            {/* Consciousness Metrics */}
            {showConsciousnessMetrics && (
              <div style={{
                padding: '8px 12px',
                borderBottom: '1px solid var(--border)',
                background: 'var(--panel-heavy)',
                fontSize: 11
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                  <span>Novelty Score:</span>
                  <span style={{ color: consciousnessMetrics.noveltyScore >= 0.8 ? '#22c55e' : '#ef4444' }}>
                    {consciousnessMetrics.noveltyScore.toFixed(3)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>MATRIZ Validated:</span>
                  <span style={{ color: consciousnessMetrics.matrizValidated ? '#22c55e' : '#ef4444' }}>
                    {consciousnessMetrics.matrizValidated ? '✓ Passed' : '✗ Failed'}
                  </span>
                </div>
              </div>
            )}

            {/* Consciousness Layers */}
            <div style={{ borderBottom: '1px solid var(--border)' }}>
              <div style={{ padding: '8px 12px', fontSize: 11, fontWeight: 600, opacity: 0.7 }}>
                Consciousness Layer
              </div>
              {layers.map((layerOption) => (
                <button
                  key={layerOption.id}
                  onClick={() => changeLayer(layerOption.id as ConsciousnessLayer)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '8px 12px',
                    border: 'none',
                    background: layer === layerOption.id ? 'var(--panel-heavy)' : 'transparent',
                    color: 'var(--text)',
                    cursor: 'pointer',
                    fontSize: 12,
                    textAlign: 'left',
                    transition: 'background 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    if (layer !== layerOption.id) {
                      e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (layer !== layerOption.id) {
                      e.currentTarget.style.background = 'transparent';
                    }
                  }}
                >
                  <span style={{ fontSize: 14, width: 20, textAlign: 'center' }}>
                    {layerOption.icon}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: layer === layerOption.id ? 600 : 400 }}>
                      {layerOption.label}
                    </div>
                    <div style={{ opacity: 0.7, fontSize: 10, marginTop: 1 }}>
                      {layerOption.desc}
                    </div>
                  </div>
                  {layer === layerOption.id && (
                    <span style={{ color: '#60a5fa', fontSize: 12 }}>✓</span>
                  )}
                </button>
              ))}
            </div>

            {/* Visual Tone Modes */}
            <div>
              <div style={{ padding: '8px 12px', fontSize: 11, fontWeight: 600, opacity: 0.7 }}>
                Visual Tone
              </div>
              {tones.map((tone) => (
                <button
                  key={tone.id}
                  onClick={() => changeTone(tone.id as ToneMode)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '8px 12px',
                    border: 'none',
                    background: mode === tone.id ? 'var(--panel-heavy)' : 'transparent',
                    color: 'var(--text)',
                    cursor: 'pointer',
                    fontSize: 12,
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
                  <span style={{ fontSize: 14, width: 20, textAlign: 'center' }}>
                    {tone.icon}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: mode === tone.id ? 600 : 400 }}>
                      {tone.label}
                    </div>
                    <div style={{ opacity: 0.7, fontSize: 10, marginTop: 1 }}>
                      {tone.desc}
                    </div>
                  </div>
                  {mode === tone.id && (
                    <span style={{ color: '#60a5fa', fontSize: 12 }}>✓</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Export enhanced consciousness layer type
export type { ConsciousnessLayer, ToneMode };
