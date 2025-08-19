(function (global) {
  /**
   * TextShapeMorphTarget
   * Renders text to an offscreen canvas and samples bright pixels into a point cloud.
   * Provides deterministic assignment of target points to vertex indices for stable morphs.
   */
  class TextShapeMorphTarget {
    constructor(options = {}) {
      this.options = Object.assign({
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        fontWeight: 600,
        resolution: 384,      // Canvas width/height in px
        threshold: 0.5,       // Pixel alpha threshold [0..1]
        sampleStep: 3,        // Pixel step when sampling
        depth: 0.0,           // Z depth for 2D forms
        padding: 16,          // Canvas padding
        center: true          // Center the text glyphs
      }, options);
      this._cache = new Map();
      this._pointCache = new Map();
      this._canvas = null;
      this._ctx = null;
      this._rng = this._mulberry32(0xC0FFEE);
    }

    _ensureCanvas() {
      if (this._canvas) return;
      const res = this.options.resolution;
      try {
        // Use OffscreenCanvas when available
        this._canvas = (typeof OffscreenCanvas !== 'undefined')
          ? new OffscreenCanvas(res, res)
          : Object.assign(document.createElement('canvas'), { width: res, height: res });
      } catch (e) {
        this._canvas = Object.assign(document.createElement('canvas'), { width: res, height: res });
      }
      this._ctx = this._canvas.getContext('2d');
    }

    _mulberry32(a) {
      return function() {
        let t = a += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
      }
    }

    _hash(str) {
      let h = 2166136261 >>> 0;
      for (let i = 0; i < str.length; i++) {
        h ^= str.charCodeAt(i);
        h = Math.imul(h, 16777619);
      }
      return h >>> 0;
    }

    /**
     * Rasterize text into a binary bitmap and sample points.
     * Returns a list of {x,y,z} in [-1..1] range (z controlled via options.depth).
     */
    textToPointCloud(text, opts = {}) {
      const options = Object.assign({}, this.options, opts);
      const key = JSON.stringify({ text, options });
      if (this._pointCache.has(key)) return this._pointCache.get(key);

      this._ensureCanvas();
      const ctx = this._ctx;
      const res = options.resolution;
      ctx.clearRect(0, 0, res, res);

      // Compute font size to fit
      const maxWidth = res - options.padding * 2;
      let fontSize = Math.floor(res * 0.5);
      ctx.font = `${options.fontWeight} ${fontSize}px ${options.fontFamily}`;
      let metrics = ctx.measureText(text);
      // Shrink until text fits
      while ((metrics.width > maxWidth) && fontSize > 12) {
        fontSize -= 4;
        ctx.font = `${options.fontWeight} ${fontSize}px ${options.fontFamily}`;
        metrics = ctx.measureText(text);
      }

      // Centering coordinates
      const actualHeight = fontSize;
      const x = options.center ? (res - metrics.width) * 0.5 : options.padding;
      const y = options.center ? (res + actualHeight * 0.4) * 0.5 : res * 0.7;

      // Draw text
      ctx.save();
      ctx.fillStyle = "#fff";
      ctx.textBaseline = "alphabetic";
      ctx.textAlign = "left";
      ctx.fillText(text, x, y);
      ctx.restore();

      // Read pixels
      const img = ctx.getImageData(0, 0, res, res).data;
      const pts = [];
      const step = Math.max(1, options.sampleStep|0);
      const thresh = Math.floor(options.threshold * 255);

      // Deterministic shuffle seed based on text
      const rng = this._mulberry32(this._hash(text));

      for (let j = 0; j < res; j += step) {
        for (let i = 0; i < res; i += step) {
          const idx = (j * res + i) * 4;
          const alpha = img[idx + 3]; // Use alpha channel
          if (alpha >= thresh) {
            // Map pixel (i,j) to [-1..1] range
            const nx = (i / (res - 1)) * 2 - 1;
            const ny = (j / (res - 1)) * 2 - 1;
            // Flip Y to match canvas to GL coords
            const px = nx;
            const py = -ny;
            const pz = options.depth;
            // Jitter to avoid perfect grid
            const jx = (rng() - 0.5) * (2 / res) * step;
            const jy = (rng() - 0.5) * (2 / res) * step;
            pts.push({ x: px + jx, y: py + jy, z: pz });
          }
        }
      }

      // Cache and return
      this._pointCache.set(key, pts);
      return pts;
    }

    /**
     * Assign a point from the cloud to each vertex index (wrap when needed).
     */
    assignToVertexCount(points, vertexCount) {
      const assigned = new Array(vertexCount);
      if (!points || points.length === 0) {
        // Fallback to a dot at origin if no points
        for (let i = 0; i < vertexCount; i++) assigned[i] = { x: 0, y: 0, z: 0 };
        return assigned;
      }
      // Deterministic shuffle for better coverage
      const indices = points.map((_, i) => i);
      // Fisher-Yates shuffle
      for (let i = indices.length - 1; i > 0; i--) {
        const j = Math.floor(this._rng() * (i + 1));
        [indices[i], indices[j]] = [indices[j], indices[i]];
      }
      for (let v = 0; v < vertexCount; v++) {
        const p = points[indices[v % points.length]];
        assigned[v] = { x: p.x, y: p.y, z: p.z };
      }
      return assigned;
    }
  }

  // UMD-style export
  global.TextShapeMorphTarget = TextShapeMorphTarget;
})(typeof window !== 'undefined' ? window : globalThis);
