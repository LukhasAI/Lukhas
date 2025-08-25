(function (global) {
  /**
   * Patch helpers for the existing MorphingSystem (adds setTargetShape, setVoiceData, and safe defaults).
   * Must be loaded AFTER morphing-system.js.
   */
  function installPatch() {
    const ms = global.morphSystem;
    if (!ms) { setTimeout(installPatch, 200); return; }

    // Safe setters
    if (!ms.setTargetShape) {
      ms.setTargetShape = function(name) { this.targetShape = name; };
    }
    if (!ms.setVoiceData) {
      ms.setVoiceData = function(voice) { this.voiceData = Object.assign(this.voiceData || {}, voice || {}); };
    }

    // Ensure required fields exist
    ms.currentShape = ms.currentShape || 'default';
    ms.targetShape  = ms.targetShape  || 'default';
    ms.voiceData    = ms.voiceData    || { intensity: 0, frequency: 0 };
    ms.shapeDefinitions = ms.shapeDefinitions || { default: {
      name: 'Default',
      vertexModifier: (v,t,voice) => v
    }};

    console.log('[Morphing Patch] Installed.');
  }

  installPatch();
})(typeof window !== 'undefined' ? window : globalThis);
