// lib/glyphSampler.ts
// Enhanced glyph→points sampler with deterministic seeding and performance guardrails

export type GlyphSampleOpts = {
  N: number;              // total points (must match your fixed pool N)
  fontPx?: number;        // base font size
  canvasW?: number;       // offscreen canvas size
  canvasH?: number;
  bold?: boolean;
  uppercase?: boolean;
  alphaThreshold?: number;
  sampleStride?: number;  // pixel step for sampling (2–4 is fast)
  worldScale?: number;    // map glyph to world units (≈ sphere radius)
  jitter?: number;        // z jitter depth
  centerBias?: number;    // 0..1 stronger bias toward center pixels
  deterministic?: boolean; // use text-based seeding for stable renders
  rng?: () => number;     // custom RNG function
};

// Mulberry32 PRNG for deterministic seeding
function mulberry32(a: number) {
  return function() {
    let t = a += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  }
}

// Simple string hash for seeding
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash);
}

// Performance and sparse glyph tracking
let _lastGlyph = '';
let _lastCandidateCount = 0;

export function glyphToTargets(
  text: string,
  targets: Float32Array,   // length = N*3
  opts: GlyphSampleOpts
) {
  const {
    N,
    fontPx = 180,
    canvasW = 768,
    canvasH = 384,
    bold = true,
    uppercase = true,
    alphaThreshold = 180,
    sampleStride = 2,
    worldScale = 1.6,  // tune: glyph width spans ~1.6 world units
    jitter = 0.02,
    centerBias = 0.35,
    deterministic = true,
    rng,  // Use provided RNG or fallback in logic
  } = opts;

  if (typeof window === 'undefined') return; // SSR guard

  let t = (uppercase ? text.toUpperCase() : text).trim().slice(0, 24);
  if (!t || t.length === 0) {
    // Fall back to tiny dot for empty text
    for (let i = 0; i < N; i++) {
      targets[i*3+0] = 0;
      targets[i*3+1] = 0;
      targets[i*3+2] = (random() - 0.5) * jitter;
    }
    return;
  }

  // Performance guardrail: skip re-sampling if same text
  if (t === _lastGlyph) return;

  // Use provided RNG or create deterministic one if enabled
  const random = rng || (deterministic ? mulberry32(hashString(t)) : mulberry32(Date.now()));

  // OffscreenCanvas if available, else regular canvas
  const cnv = (typeof (window as any).OffscreenCanvas !== 'undefined')
    ? new (window as any).OffscreenCanvas(canvasW, canvasH)
    : document.createElement('canvas');

  (cnv as any).width = canvasW;
  (cnv as any).height = canvasH;
  const ctx = (cnv as HTMLCanvasElement).getContext
    ? (cnv as HTMLCanvasElement).getContext('2d', { willReadFrequently: true })!
    : (cnv as OffscreenCanvas).getContext('2d', { willReadFrequently: true })!;

  // Render text
  ctx.clearRect(0, 0, canvasW, canvasH);
  ctx.fillStyle = '#ffffff';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';
  ctx.font = `${bold ? '700 ' : ''}${fontPx}px Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto`;

  // Fit text: shrink font until it fits
  let f = fontPx;
  while (f > 32 && ctx.measureText(t).width > canvasW * 0.88) {
    f -= 8;
    ctx.font = `${bold ? '700 ' : ''}${f}px Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto`;
  }
  ctx.fillText(t, canvasW / 2, canvasH / 2);

  // Sample opaque pixels with adaptive stride
  let currentStride = sampleStride;
  let candidates: [number, number][] = [];
  let attempts = 0;
  const maxAttempts = 3;

  // Adaptive sampling to ensure sufficient candidate density
  while (attempts < maxAttempts) {
    candidates = [];
    const img = ctx.getImageData(0, 0, canvasW, canvasH);
    const data = img.data;

    for (let y = 0; y < canvasH; y += currentStride) {
      for (let x = 0; x < canvasW; x += currentStride) {
        const idx = (y * canvasW + x) * 4;
        const a = data[idx + 3];
        if (a >= alphaThreshold) candidates.push([x, y]);
      }
    }

    // Performance guardrail: if candidates < N/50, increase density
    if (candidates.length >= N / 50 || attempts === maxAttempts - 1) {
      break;
    }

    // Try denser sampling or adjust scale
    if (attempts === 0 && currentStride > 1) {
      currentStride = Math.max(1, Math.floor(currentStride / 2));
    } else {
      // Last resort: reduce world scale to make glyph denser
      const newScale = worldScale * 0.8;
      if (newScale > 0.5) {
        return glyphToTargets(text, targets, { ...opts, worldScale: newScale });
      }
    }
    attempts++;
  }

  _lastGlyph = t;
  _lastCandidateCount = candidates.length;

  if (candidates.length === 0) {
    // Fallback to tiny dot
    for (let i = 0; i < N; i++) {
      targets[i*3+0] = 0;
      targets[i*3+1] = 0;
      targets[i*3+2] = (random() - 0.5) * jitter;
    }
    return;
  }

  // Optional: bias selection toward the center for denser, cleaner glyphs
  const cx = canvasW / 2, cy = canvasH / 2;
  function pickIndex(i: number): number {
    if (centerBias <= 0) return Math.floor(random() * candidates.length);
    // mix uniform with distance-weighted
    const r = random();
    if (r > centerBias) return Math.floor(random() * candidates.length);
    // weighted by inverse distance to center
    let best = 0, bestScore = -1;
    for (let k = 0; k < 4; k++) { // 4 tries is enough
      const j = Math.floor(random() * candidates.length);
      const dx = candidates[j][0] - cx;
      const dy = candidates[j][1] - cy;
      const score = 1 / (1 + dx*dx + dy*dy);
      if (score > bestScore) { bestScore = score; best = j; }
    }
    return best;
  }

  // Normalize to world space centered at (0,0,0)
  // Map canvas coords to [-1,1] on the longer side, preserve aspect
  const maxDim = Math.max(canvasW, canvasH);
  for (let i = 0; i < N; i++) {
    const j = pickIndex(i);
    const [x, y] = candidates[j];
    const nx = ((x - cx) / maxDim) * 2 * worldScale;
    const ny = (-(y - cy) / maxDim) * 2 * worldScale;
    const nz = (random() - 0.5) * jitter;
    targets[i*3+0] = nx;
    targets[i*3+1] = ny;
    targets[i*3+2] = nz;
  }
}

// Enhanced LRU cache with performance metrics
export function makeGlyphSamplerCache(max = 24) {
  const cache = new Map<string, Float32Array>();
  const stats = { hits: 0, misses: 0, sparse: 0 };

  return {
    get(text: string, N: number, opts: Omit<GlyphSampleOpts, 'N'>) {
      const key = `${text}|${N}|${opts.canvasW}|${opts.canvasH}|${opts.fontPx}|${opts.sampleStride}|${opts.worldScale}`;
      const cached = cache.get(key);
      if (cached) {
        stats.hits++;
        return cached;
      }

      stats.misses++;
      const arr = new Float32Array(N*3);
      glyphToTargets(text, arr, { N, ...opts });

      // Track sparse glyphs for debugging
      if (_lastCandidateCount < N / 50) {
        stats.sparse++;
        console.warn(`[GlyphSampler] Sparse glyph detected: "${text}" (${_lastCandidateCount} candidates for ${N} points)`);
      }

      cache.set(key, arr);
      if (cache.size > max) {
        const first = cache.keys().next().value;
        cache.delete(first);
      }
      return arr;
    },

    getStats() {
      return { ...stats, cacheSize: cache.size };
    },

    clear() {
      cache.clear();
      stats.hits = stats.misses = stats.sparse = 0;
    }
  }
}

// GPU capability detection for render mode fallbacks
export function detectGPUCapability(): 'high' | 'medium' | 'low' {
  if (typeof window === 'undefined') return 'medium';

  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return 'low';

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
      const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
      const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);

      // Check for integrated Intel GPU or low-end mobile
      if (renderer.toLowerCase().includes('intel') &&
          (renderer.toLowerCase().includes('uhd') || renderer.toLowerCase().includes('hd'))) {
        return 'low';
      }

      // Check for mobile indicators
      if (vendor.toLowerCase().includes('qualcomm') ||
          renderer.toLowerCase().includes('adreno') ||
          renderer.toLowerCase().includes('mali')) {
        return /\b(adreno [6-9]|mali.*g[7-9])/i.test(renderer) ? 'medium' : 'low';
      }
    }

    // Check for mobile device
    if (/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent)) {
      return 'medium';
    }

    return 'high';
  } catch (e) {
    return 'low';
  }
}

// Optimal render mode based on GPU capability
export function getOptimalRenderMode(): 'particles' | 'mesh+particles' {
  const capability = detectGPUCapability();
  return capability === 'low' ? 'particles' : 'mesh+particles';
}
