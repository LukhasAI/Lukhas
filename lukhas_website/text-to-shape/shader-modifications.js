(function (global) {
  /**
   * Minimal shader hook to avoid 404s and to enable future GPU color control.
   * If your build system exposes a way to tweak uniforms, plug it here.
   */
  const ShaderMods = {
    apply(uniforms) {
      // Example: uniforms.uColor = [r,g,b,a];
      // Left intentionally lightweight. Extend as needed.
      console.debug('[ShaderMods] apply called with uniforms:', uniforms ? Object.keys(uniforms) : 'n/a');
    }
  };
  global.ShaderMods = ShaderMods;
})(typeof window !== 'undefined' ? window : globalThis);
