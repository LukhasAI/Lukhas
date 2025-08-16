# Dream Weaver — Engineering Brief for Claude Code
**Cut-through goal:** ship a mystical-but-clear experience with a **stable 2D baseline**, progressive 3D, and explicit safety/comms. Keep cinematic ambitions behind flags.

## Scope (Ship v0.2)
- **Status line + tooltips**: phase-aware, `aria-live="polite"`.
- **Resilient SSE**: debounce + backoff + jitter (no UI thrash).
- **VignetteOverlay**: CSS fallback; shaders optional.
- **Version pins**: react 18.2.0, r3f 8.16.8, drei 9.105.6.
- **Copy import**: `dw_copy.json` drives text + FX levels.
- **OpenAI usage**: narration (text) and stills (images) only in v0.2. No live video generation.

## Non-goals (defer)
- Live video (Sora) and full cinematic pipeline.
- Spatial audio / complex mixing.
- Biometric feedback loops.

## Tasks
1) **Hook** — drop `useSSE.ts` into `src/hooks/` and wire DreamWeaver to it.
2) **Overlay** — add `VignetteOverlay.tsx` + `dw_effects.css`; mount once at app root.
3) **Status/Tooltips** — read from `dw_copy.json`; ensure `phase` updates drive both.
4) **OpenAI calls** — implement `POST /api/dream/seed` → server uses Chat Completions (stream) for narration; Images for still snapshots. Phrase: “**Built using OpenAI APIs**.”
5) **A11y** — `aria-live="polite"`, reduce-motion lowers vignette and disables pulses.

## Acceptance criteria
- SSE reconnects under network flap; no UI spam (coalesced ≥300ms).
- 2D baseline renders on any device; R3F can be off without breaking flow.
- Exit comprehension ≥4/5; artifact export ≥20% in pilot.
- No language implying partnership; only “built using OpenAI APIs.”

## Do / Don’t
- **Do** centralize copy + FX in `dw_copy.json`.
- **Do** ship with React/R3F pins; upgrade only as a pair.
- **Don’t** block on shaders/Sora; ship CSS fallback + stills.
- **Don’t** add theatrical lore to UI; keep it in docs.

## Pseudocode (integration)
```tsx
// DreamWeaver.tsx
import { useSSE, DreamEvent } from '@/hooks/useSSE'
import VignetteOverlay from '@/components/VignetteOverlay'
import dwCopy from './dw_copy.json'

const { data } = useSSE<DreamEvent>('/api/dream/stream', { debounceMs: 300 })
useEffect(() => {
  if (!data) return
  setPhase(data.phase ?? phase)
  setAwareness(data.awareness ?? awareness)
  setCoherence(data.coherence ?? coherence)
  setStatusLine((dwCopy.phases.find(p => p.id===phase)?.status||'')
    .replace('{awareness}', String(awareness))
    .replace('{coherence}', String(coherence)))
}, [data])
```

## Notes on the “Cinematic Plan” (on hold)
- Keep **Acts** in docs, not UI. Expose as “Layers” in a dev flag:
  - Base 2D → Enhanced Stills → Cinematic Video (future).
- Shader intensity **only at decision points**. No global bloom/glare by default.
- Narration copy style: mystic clarity 6/10, short sentences, explainable.

— End of brief.
