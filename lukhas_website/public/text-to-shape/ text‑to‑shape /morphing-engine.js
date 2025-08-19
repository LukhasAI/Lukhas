(function (global) {
  /**
   * MorphingEngine
   * - Holds current/target states and performs eased interpolation per-vertex.
   * - Supports two kinds of targets:
   *    1) Named shape (resolved through MorphingSystem.shapeDefinitions)
   *    2) Explicit point cloud assignment (array of {x,y,z} indexed by vertex id)
   */
  class MorphingEngine {
    constructor() {
      this.morphProgress = 0;
      this.morphSpeed = 0.02;
      this.easing = this.easeInOutCubic;
      this.targetKind = 'named'; // 'named' | 'points'
      this.namedTarget = 'default';
      this.pointTarget = null;    // Array<{x,y,z}>
      this.currentShape = 'default';
      this.voiceData = { intensity: 0, frequency: 0 };
      this._vertexCount = 0;
    }

    setVertexCount(count) { this._vertexCount = count|0; }
    setMorphSpeed(speed) { this.morphSpeed = Math.max(0.001, speed || 0.02); }
    setVoiceData(voice) { this.voiceData = Object.assign({}, this.voiceData, voice || {}); }
    setCurrentShape(name) { this.currentShape = name; }
    setNamedTarget(name) { this.targetKind = 'named'; this.namedTarget = name; this.morphProgress = 0; }
    setPointTarget(points) { this.targetKind = 'points'; this.pointTarget = points; this.morphProgress = 0; }
    isPointTargetActive() { return this.targetKind === 'points' && Array.isArray(this.pointTarget); }

    step(deltaTime) {
      const dt = (typeof deltaTime === 'number' ? deltaTime : 1/60);
      // Accelerate morph slightly with voice intensity
      const boost = 1.0 + (this.voiceData.intensity || 0) * 0.5;
      this.morphProgress = Math.min(1.0, this.morphProgress + this.morphSpeed * dt * boost);
    }

    easeInOutCubic(t) {
      return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    /**
     * Compute morphed vertex position.
     * @param {object} systems - references to the host MorphingSystem and definitions
     * @param {object} vertex - {x,y,z}
     * @param {number} index  - vertex index
     * @param {number} time   - time
     */
    computeVertex(systems, vertex, index, time) {
      const t = this.easing(this.morphProgress);
      const defs = systems.shapeDefinitions || {};
      const cur = defs[this.currentShape] || defs['default'];
      let curPos = cur.vertexModifier(vertex, time, this.voiceData, index);

      let tgtPos;
      if (this.isPointTargetActive()) {
        // Map to 2D/3D explicit target
        const p = this.pointTarget[index % this.pointTarget.length];
        // Map from [-1..1] to system radius ~ 10 (match default sphere radius in MorphingSystem)
        const R = 10.0;
        tgtPos = { x: p.x * R, y: p.y * R, z: p.z * R };
      } else {
        const tgt = defs[this.namedTarget] || defs['default'];
        tgtPos = tgt.vertexModifier(vertex, time, this.voiceData, index);
      }

      return {
        x: curPos.x + (tgtPos.x - curPos.x) * t,
        y: curPos.y + (tgtPos.y - curPos.y) * t,
        z: curPos.z + (tgtPos.z - curPos.z) * t
      };
    }
  }

  global.MorphingEngine = MorphingEngine;
})(typeof window !== 'undefined' ? window : globalThis);
