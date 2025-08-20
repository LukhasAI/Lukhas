// enhanced-particle-system.ts

// Mulberry32 seeded RNG
export function mulberry32(seed: number) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Fixed particle pool generator
export function createParticlePool(size: number) {
  const pool = new Array(size);
  for (let i = 0; i < size; i++) {
    pool[i] = {
      position: [0, 0, 0] as [number, number, number],
      velocity: [0, 0, 0] as [number, number, number],
      life: 0,
      active: false,
    };
  }
  return pool;
}

// Glyph target cache with LRU
class GlyphTargetCache {
  private maxSize: number;
  private cache: Map<string, any>;

  constructor(maxSize: number = 50) {
    this.maxSize = maxSize;
    this.cache = new Map();
  }

  get(key: string) {
    if (!this.cache.has(key)) return undefined;
    const value = this.cache.get(key);
    // move to end to show that it was recently used
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  set(key: string, value: any) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size === this.maxSize) {
      // remove least recently used
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
}

const glyphTargetCache = new GlyphTargetCache();

// API

// Generates a base form particle configuration
export function generateBaseForm(seed: number, particleCount: number) {
  const rng = mulberry32(seed);
  const pool = createParticlePool(particleCount);
  for (let i = 0; i < particleCount; i++) {
    pool[i].position = [
      (rng() - 0.5) * 2,
      (rng() - 0.5) * 2,
      (rng() - 0.5) * 2,
    ];
    pool[i].velocity = [0, 0, 0];
    pool[i].life = 1;
    pool[i].active = true;
  }
  return pool;
}

// Sets a glyph target cached by key
export function setGlyphTargetCached(key: string, glyphTarget: any) {
  glyphTargetCache.set(key, glyphTarget);
}

export function getGlyphTargetCached(key: string) {
  return glyphTargetCache.get(key);
}
