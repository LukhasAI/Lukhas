# LUKHΛS Text-to-Shape Morph Integration

This drop-in adds **text ➜ particle morph** and AI-controlled shape intent to your existing WebGL particle system.
Files included:

- `text-shape-morph-target.js` — rasterizes text to a 2D point cloud (offscreen canvas), assigns points to vertices.
- `morphing-engine.js` — easing + per-vertex interpolation with named or point-cloud targets.
- `ai-shape-controller.js` — interprets prompts (via AI if available) and triggers morphs; injects a minimal prompt UI.
- `shader-modifications.js` — harmless stub (satisfies `<script src="shader-modifications.js">` in `main.html`).
- `morphing-system.patch.js` — adds safe setters and defaults to your existing `MorphingSystem` instance.

## How to wire it

1. Include the new scripts **after** your existing ones (order matters):
   ```html
   <script src="jl_matrix_min.js"></script>
   <script src="build.js"></script>
   <script src="morphing-system.js"></script>

   <!-- New modules -->
   <script src="morphing-system.patch.js"></script>
   <script src="morphing-engine.js"></script>
   <script src="text-shape-morph-target.js"></script>
   <script src="ai-shape-controller.js"></script>
   ```

2. Optional: keep `shader-modifications.js` in the page to avoid 404 and future GPU color work.

3. Run the page. You will see a small prompt bar near the top. Try:
   - `morph into a torus`
   - `text: LUKHΛS`
   - `morph into a cube / helix / heart`

## Notes

- The engine keeps **60fps** by preparing the point cloud once per prompt and only interpolating per-frame.
- Voice reactivity (intensity ➜ morph acceleration) is auto-wired if your `ai-voice-integration.js` exposes `voiceData`.
- Works **offline** (no keys) using heuristics; if your AI is configured, structured `shapeParameters` from your provider
  are used automatically (see `API_SPECIFICATION.md`).

## Extending

- Add new shapes by registering `vertexModifier` functions in `AIShapeController._augmentShapes`.
- Swap easing in `MorphingEngine` or bind UI sliders to `morphSpeed` for artistic control.
