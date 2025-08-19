(function (global) {
  /**
   * AI Shape Controller
   * Orchestrates prompt -> shape intent -> morphing engine target.
   * Works even without network keys using rule-based fallback.
   */
  class AIShapeController {
    constructor() {
      this.engine = new (global.MorphingEngine || function(){})();
      this.textTarget = new (global.TextShapeMorphTarget || function(){})({ resolution: 448, sampleStep: 3 });
      this._wireToMorphSystem();
      this._installUI();
      this._tryWireToVoice();
    }

    _wireToMorphSystem() {
      const wait = () => {
        if (global.morphSystem && global.morphSystem.shapeDefinitions) {
          // Register extra shapes and patch processVertices with index support
          this._augmentShapes(global.morphSystem);
          this._patchProcessVertices(global.morphSystem);
          return;
        }
        setTimeout(wait, 100);
      };
      wait();
    }

    _augmentShapes(ms) {
      // Utilities
      const normalize = (v) => {
        const len = Math.hypot(v.x, v.y, v.z) || 1e-6;
        return { x: v.x/len, y: v.y/len, z: v.z/len };
      };
      const radiusOf = (voice) => 10.0 + (voice.intensity||0) * 0.15;

      // Register additional shapes
      ms.shapeDefinitions.cube = {
        name: 'Cube',
        vertexModifier: (vertex, time, voice, idx) => {
          const n = normalize(vertex);
          const r = radiusOf(voice);
          // Project onto cube by normalizing to max component
          const ax = Math.abs(n.x), ay = Math.abs(n.y), az = Math.abs(n.z);
          const m = Math.max(ax, ay, az) || 1e-6;
          return { x: (n.x/m)*r, y: (n.y/m)*r, z: (n.z/m)*r };
        }
      };

      ms.shapeDefinitions.torus = {
        name: 'Torus',
        vertexModifier: (vertex, time, voice, idx) => {
          const n = normalize(vertex);
          // Convert to angles
          const theta = Math.atan2(n.z, n.x);  // around Y
          const phi = Math.asin(n.y);          // elevation
          const R = 8.0, r = 2.4 + (voice.intensity||0)*0.2;
          const x = (R + r*Math.cos(phi)) * Math.cos(theta);
          const z = (R + r*Math.cos(phi)) * Math.sin(theta);
          const y = r * Math.sin(phi);
          return { x, y, z };
        }
      };

      ms.shapeDefinitions.helix = {
        name: 'Helix',
        vertexModifier: (vertex, time, voice, idx) => {
          const n = normalize(vertex);
          const t = Math.atan2(n.z, n.x) + idx*0.0005; // add slight per-vertex offset
          const h = (n.y + 1) * Math.PI; // [-1..1] -> [0..2π]
          const R = 8.0, r = 1.5;
          const x = (R + r*Math.cos(h*2)) * Math.cos(t*2);
          const z = (R + r*Math.cos(h*2)) * Math.sin(t*2);
          const y = r * Math.sin(h*2) * 1.5;
          return { x, y, z };
        }
      };

      ms.shapeDefinitions.heart2d = {
        name: 'Heart 2D',
        vertexModifier: (vertex, time, voice, idx) => {
          const n = normalize(vertex);
          // Map spherical coords to 2D param u in [-π..π]
          const u = Math.atan2(n.z, n.x);
          const v = Math.asin(n.y);
          // Classic heart curve (2D) then expand slightly in depth
          const a = 1.0;
          const x = 16*Math.pow(Math.sin(u),3);
          const y = 13*Math.cos(u) - 5*Math.cos(2*u) - 2*Math.cos(3*u) - Math.cos(4*u);
          const scale = 0.6; // scale to fit
          return { x: x*scale, y: (y*scale)*0.8, z: (v*0.5) };
        }
      };

      // Placeholder that will be driven by text point cloud
      ms.shapeDefinitions.text2d = {
        name: 'Text 2D',
        vertexModifier: (vertex, time, voice, idx) => {
          // The actual position is provided by MorphingEngine when targetKind === 'points'.
          // Here we just return current vertex to let engine blend to explicit points.
          return { x: vertex.x, y: vertex.y, z: vertex.z };
        }
      };
    }

    _patchProcessVertices(ms) {
      // Install our MorphingEngine-driven vertex processing with index awareness.
      const original = ms.processVerticesWithMorphing ? ms.processVerticesWithMorphing.bind(ms) : null;

      const patched = (vertices, time) => {
        // Determine vertex count
        const count = (vertices.length / 3)|0;
        this.engine.setVertexCount(count);
        this.engine.setMorphSpeed(ms.morphSpeed || 0.02);
        this.engine.setVoiceData(ms.voiceData || { intensity: 0, frequency: 0 });
        this.engine.setCurrentShape(ms.currentShape || 'default');
        this.engine.step(1/60);

        const out = new Float32Array(vertices.length);

        for (let i = 0, v = 0; i < vertices.length; i += 3, v++) {
          const vert = { x: vertices[i], y: vertices[i+1], z: vertices[i+2] };
          const morphed = this.engine.computeVertex(ms, vert, v, time);
          out[i]   = morphed.x;
          out[i+1] = morphed.y;
          out[i+2] = morphed.z;
        }
        return Array.from(out);
      };

      // Replace global processVertices to ensure our patch is used by the render loop.
      global.processVertices = patched;
    }

    _tryWireToVoice() {
      const poll = () => {
        const ai = global.aiVoiceIntegration || global.AIVoiceIntegrationInstance;
        const ms = global.morphSystem;
        if (ai && ms && ai.voiceData) {
          // Push voice metrics to MorphingEngine via morphSystem
          if (!ms.setVoiceData) {
            ms.setVoiceData = (data) => { ms.voiceData = Object.assign(ms.voiceData||{}, data || {}); };
          }
          ms.setVoiceData(ai.voiceData);
        }
        setTimeout(poll, 200);
      };
      poll();
    }

    // --- Public API ---

    /**
     * Interpret a free-form prompt and set the appropriate morph target.
     * Uses AI provider if available, else falls back to rules.
     */
    async morphFromPrompt(prompt, opts = {}) {
      const ai = global.aiVoiceIntegration; // optional
      let intent = null;

      // 1) If the AI layer is available and configured, ask it for structured shape parameters
      if (ai && typeof ai.getAIResponse === 'function') {
        try {
          const res = await ai.getAIResponse(prompt, { expect: 'shapeParameters' });
          const params = res && (res.shapeParameters || res.data || res.parameters);
          if (params && (params.shapeType || params.type)) {
            intent = {
              type: (params.shapeType || params.type),
              text: params.text || null,
              color: params.color || null,
              scale: params.scale || 1.0,
              animation: params.animation || null
            };
          }
        } catch (e) {
          console.warn('[AIShapeController] AI provider failed, using rule-based fallback.', e);
        }
      }

      // 2) Rule-based fallback
      if (!intent) {
        intent = this._heuristicIntent(prompt);
      }

      // 3) Apply intent
      await this._applyIntent(intent);
    }

    _heuristicIntent(prompt) {
      const p = (prompt || '').toLowerCase();

      // Extract quoted text for text shapes
      const quoted = /"(.*?)"/.exec(prompt);
      const textCandidate = quoted ? quoted[1] : null;
      const textKeywords = /(text|word|write|spell|letters?|logo|lukh[aɅ]s|lúkhas)/i.test(prompt);

      const shapes = ['sphere','cube','torus','helix','heart','heart2d','cat','car','person','butterfly','star'];
      for (const s of shapes) {
        if (p.includes(s)) return { type: s };
      }

      if (textCandidate || textKeywords) {
        return { type: 'text2d', text: textCandidate || prompt.replace(/^(text|write|spell):?/i,'').trim() };
      }

      // Default
      return { type: 'sphere' };
    }

    async _applyIntent(intent) {
      const ms = global.morphSystem;
      if (!ms) return;

      // Map synonyms
      const alias = { sphere: 'default', text: 'text2d', heart: 'heart2d' };
      const type = alias[intent.type] || intent.type;

      if (type === 'text2d' && intent.text) {
        // Build 2D point cloud target for the provided text
        // 1) Create point cloud in [-1..1]
        const pts = this.textTarget.textToPointCloud(intent.text, { threshold: 0.45, sampleStep: 2 });
        // 2) Assign to the current vertex count (we'll update on next frame as well)
        const count = (ms.icosahedronData && ms.icosahedronData.vertices && ms.icosahedronData.vertices.length/3) || 10000;
        const assigned = this.textTarget.assignToVertexCount(pts, count);
        // 3) Tell morph engine to use explicit points and set target shape placeholder
        this.engine.setPointTarget(assigned);
        ms.targetShape = 'text2d';
        ms.currentShape = ms.currentShape || 'default';
        return;
      }

      // Named shapes
      if (ms.shapeDefinitions[type]) {
        this.engine.setNamedTarget(type);
        ms.targetShape = type;
        return;
      }

      // Fallback
      this.engine.setNamedTarget('default');
      ms.targetShape = 'default';
    }

    // --- UI wiring ---
    _installUI() {
      if (document && !document.getElementById('lukhas-morph-ui')) {
        const wrap = document.createElement('div');
        wrap.id = 'lukhas-morph-ui';
        wrap.style.position = 'fixed';
        wrap.style.left = '50%';
        wrap.style.top = '72px';
        wrap.style.transform = 'translateX(-50%)';
        wrap.style.zIndex = '1100';
        wrap.style.pointerEvents = 'auto';
        wrap.style.display = 'flex';
        wrap.style.gap = '8px';

        const input = document.createElement('input');
        input.id = 'morphPrompt';
        input.placeholder = 'Type: “morph into a torus” or “text: LUKHΛS”';
        input.autocomplete = 'off';
        input.style.width = '420px';
        input.style.height = '36px';
        input.style.padding = '0 12px';
        input.style.borderRadius = '8px';
        input.style.border = '1px solid #2a2e39';
        input.style.background = 'rgba(0,0,0,0.32)';
        input.style.color = '#e8eef5';
        input.style.fontFamily = 'Inter, sans-serif';
        input.style.fontSize = '14px';
        input.style.backdropFilter = 'blur(6px)';

        const btn = document.createElement('button');
        btn.textContent = 'Morph';
        btn.style.height = '36px';
        btn.style.padding = '0 14px';
        btn.style.borderRadius = '8px';
        btn.style.border = '1px solid #2a2e39';
        btn.style.background = 'linear-gradient(135deg,#2962ff,#00d4ff)';
        btn.style.color = '#fff';
        btn.style.fontFamily = 'Inter, sans-serif';
        btn.style.fontWeight = '600';
        btn.style.cursor = 'pointer';

        const onSubmit = async () => {
          const value = input.value.trim();
          if (!value) return;
          await this.morphFromPrompt(value);
        };
        btn.addEventListener('click', onSubmit);
        input.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') onSubmit();
        });

        wrap.appendChild(input);
        wrap.appendChild(btn);
        document.body.appendChild(wrap);
      }
    }
  }

  // Bootstrap once DOM is ready
  function ready(fn){ if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }
  ready(() => { global.aiShapeController = new AIShapeController(); });

  global.AIShapeController = AIShapeController;
})(typeof window !== 'undefined' ? window : globalThis);
