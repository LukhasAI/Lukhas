# LUKHΛS Website & Experience — Product & Engineering Roadmap
_Last updated: 2024-06-09_

## 0) Executive Summary
We are building a **single-form, glyph-capable morphing field** controlled by text and voice. The MVP must feel premium, deterministic, and truthful:
- **Form/Field only** (no visible “shapes”); quoted `"text"` renders as a glyph cloud.
- **ChatGPT‑style replies by default**; a short **“Insight:”** line appears only when helpful (docs/narrative/voice), never three replies at once.
- **Deterministic visuals** via `mulberry32` (no `Math.random()` in core sampling).
- **Stable GPU pipeline** with a fixed particle pool (no BufferAttribute resizing).
- **Security & trust**: local GLYPH encryption, transparent storage, no leaking errors into chat.

---

## 1) North‑Star Principles
- **Simplicity over spectacle.** One form, infinite meaning. Text→glyph is the expressive channel.
- **Truthful UX.** If unsupported, say so; offer Glyph / Approximate / Queue.
- **Clarity & calm.** Minimal UI, consistent rhythm, premium tone mapping.
- **Performance first.** 60fps target, adaptive complexity, GPU instancing.
- **Safety by design.** Guardian calm mode; sentiment‑gated energy.

---

## 2) Scope Decisions (Locked)
- ✅ **Single Form Engine** (internally sphere sampling), no public shape picker.
- ✅ **Glyph morph** from quoted text (fixed pool N, tiling/subsampling).
- ✅ **Chat**: single concise answer + optional “Insight:” line when the moment calls for it.
- ✅ **Mulberry32** seeded PRNG; `seedFromString(text)` for stable glyphs.
- ✅ **ACES tone mapping** + metallic base body + additive particles.

---

## 3) Phase 1 — Demo‑Ready Pipeline (Do Now)
**Goal:** Stable, compelling, investor‑ready experience.

### 3.1 Deliverables
- ✅ Voice ↔ Particles (intensity → size/color modulation)
- ✅ Chat ↔ Glyph pipeline (quoted text → glyph points → morph)
- ✅ GPU Instancing for >10k particles
- ✅ Signature glyphs (cache per message)
- ✅ Toggle: **AI ↔ Human** blending (particles pulse to current speaker)

### 3.2 Engineering Tasks (checklist)
- [ ] **Relocate files**
  - `enhanced-particle-system.ts` → `lib/visuals/enhanced-particle-system.ts`
  - `advanced-morphing-visualizer.tsx` → `components/experience/advanced-morphing-visualizer.tsx`
- [ ] **Deterministic PRNG**
  - Add `lib/prng.ts` with `mulberry32(seed)` + `seedFromString(s)`.
  - Replace all `Math.random()` in glyph sampler & form sampling.
- [ ] **Fixed Pool + Instancing**
  - Create `InstancedMesh` with configurable `N` (default 12–20k).
  - No BufferAttribute resizing across morphs.
- [ ] **Glyph pipeline**
  - `lib/glyphSampler.ts` produces `Float32Array (N*3)`.
  - Cache (LRU) by message id/text; `setGlyphTargetCached(text)`.
  - Event hook: `lukhas-render-glyph` fired from chat intent helper.
- [ ] **Voice analyzer**
  - `lib/voice-analyzer.ts` outputs `{ intensity: 0–1, dominantFreq: Hz }`.
  - Map to scale & color (calm blue → intense red).
- [ ] **AI↔Human toggle**
  - UI chip toggles audio feed: mic (human) vs TTS/response (AI).
  - Visualizer reads `mode` prop.
- [ ] **Telemetry (basic)**
  - Overlay: FPS, particle count, intensity (top‑right, small).
  - Console log: `{ driftScore, intensity }` once per second.
- [ ] **Error surface discipline**
  - Provider/model errors → sidebar toast; never into chat stream.
- [ ] **Layout polish**
  - Ensure canvas remains centered when right panel opens; footer centered.

### 3.3 Acceptance Criteria
- 60fps at ~10k particles on M1/M2, smooth degradation if <30fps.
- Quoted text (“CAT”) renders as a deterministic glyph cloud with legibility hold.
- Toggle instantly switches pulse source between **Human** mic and **AI**.
- No `WebGLAttributes … does not match` errors.
- Chat feels natural; “Insight:” appears only when appropriate.

### 3.4 Risks & Mitigations
- **GPU overload:** Add adaptive particle count (reduce 20% when FPS <30).
- **Audio permissions:** Graceful fallback; show non-blocking prompt.
- **Sparse glyphs:** Auto‑adjust `sampleStride` / `worldScale` on few candidates.

---

## 4) Phase 2 — Investor/Press Polish (Next)
**Objective:** Raise *perceived sophistication* without destabilizing MVP.

### 4.1 Features
- ✨ Postprocessing: bloom, DOF, subtle trails.
- ✨ Emotion‑mapped palettes (calm→blue, intense→magenta/red).
- ✨ Metrics overlay: FPS, particle count, intensity, optional driftScore.
- ✨ Telemetry hook: send anonymized metrics on opt‑in.

### 4.2 Success
- Visual depth feels “cinematic”; overlay conveys rigor.
- No measurable FPS regression on baseline hardware.

---

## 5) Phase 3 — Scalability & R&D (Later)
- 📦 Config‑driven **ShapeLibrary** stub (kept off by default; research only).
- 🧵 Web Workers for FFT & heavy prep steps.
- 🧪 Unit tests for PRNG determinism & voice analyzer ranges.
- 📚 Storybook for Visualizer variations & QA.
- 🔐 Voice‑auth exploration: blend with other personalization vectors.

---

## 6) Technical Specs (Consolidated)
- **Particle pool:** Fixed `N`; `positions` lerp → `targets`; no attribute resizing.
- **PRNG:** `mulberry32(seed)`; glyph seeds via `seedFromString(text)`.
- **Renderer:** `sRGBColorSpace`, `ACESFilmicToneMapping`, `exposure≈1.05–1.10`.
- **Materials:** `MeshPhysicalMaterial` (metalness 0.9, roughness 0.2, clearcoat 0.6) under `PointsMaterial` (additive).
- **Intent helper:** detect `"quoted"` or `text: foo` → dispatch `lukhas-render-glyph`.
- **Chat UX:** single concise answer; append one `Insight:` line when docs/narrative context is detected.
- **Security:** GLYPH encryption (AES‑GCM), IndexedDB/localStorage; Manage modal clarifies storage.

---

## 7) Manual QA Checklist
- [ ] Paste valid OpenAI key → provider badge lights; model dropdown updates.
- [ ] Chat “write a short blurb” → single reply + optional `Insight:`.
- [ ] Type `"LUKHΛS"` → glyph renders, legibility hold visible.
- [ ] Toggle AI↔Human → pulse source switches immediately.
- [ ] FPS overlay ≥ 55–60 on baseline; adaptive reduction when stressed.
- [ ] Footer & canvas alignment correct at all breakpoints.

---

## 8) Appendix A — **Claude Code Brief (Phase 1 Demo Pack)**

### 🎯 Goal
Implement a **stable, compelling, demo-ready pipeline** for `/app/experience` with:
- Voice ↔ Particles
- Chat ↔ Glyph pipeline
- GPU Instancing (>10k)
- Signature glyphs
- Toggle: **AI ↔ Human** blending

### 📂 File Moves / Setup
1. Move the placeholder files created at project root into proper locations:  
   - `enhanced-particle-system.ts` → `/lib/visuals/`  
   - `advanced-morphing-visualizer.tsx` → `/components/experience/`  
2. Update imports in `/app/experience/page.tsx`.

### ⚙️ Implementation Steps
1) **GPU Instancing**
- Use `THREE.InstancedMesh` for particles. Configurable `N` (default 12–20k).
- Adaptive: if FPS <30 for 2s, reduce `N` by 20% (min clamp).

2) **Voice ↔ Particle Mapping**
- `lib/voice-analyzer.ts` returns `{ intensity, dominantFreq }`.
- Map intensity to particle **scale** and color **hue** (calm blue → intense red).

3) **Signature Glyphs**
- Cache each message id/text → `Float32Array (N*3)` in an LRU.
- Reuse cached clouds for morph transitions.

4) **AI ↔ Human Toggle**
- UI chip toggles pulse source; default **Human**.
- Visualizer takes `mode` prop: `"human" | "ai"`.

5) **Chat ↔ Visualizer Wiring**
```tsx
<MorphingVisualizer quotedText={lastMessage?.content} mode={mode} />
```

### 🔮 Stretch (Optional)
- Small FPS overlay (top‑right).
- Console telemetry: `{ driftScore, intensity }` once/sec.

### ✅ Acceptance
- 60fps @ ~10k particles; smooth degradation.
- Deterministic glyphs; no BufferAttribute resize errors.
- Toggle works; chat feels natural; visuals feel premium.

---

## 9) Appendix B — Glossary & UI Language
- **Form/Field:** The living, morphable particle body (never “sphere” in UI).
- **Glyph:** Quoted text rendered as a particle constellation.
- **Insight:** A short, optional line that adds clarity without verbosity.
- **Guardian:** Instant calm mode; caps energy under negative/violent tone.

---

## 10) Ownership & Milestones
- **Owner:** Gonzalo (@gonzo.dominguez)
- **Phase 1 ETA:** T+7–10 days
- **Review:** Demo script + QA pass + performance capture (FPS, particle count)
