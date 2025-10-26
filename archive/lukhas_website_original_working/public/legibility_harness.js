// LUKHAS Legibility Harness v1.0.0
// Visual harness for morphing legibility testing

window.legibilityHarness = {
  version: '1.0.0',
  
  // Initialize the harness
  init() {
    this.createPanel()
    this.bindEvents()
    console.log('[Legibility] Harness v1.0.0 loaded')
  },

  // Create visual panel
  createPanel() {
    // Remove existing panel
    const existing = document.getElementById('lukhas-legibility-panel')
    if (existing) existing.remove()

    // Create panel
    const panel = document.createElement('div')
    panel.id = 'lukhas-legibility-panel'
    panel.style.cssText = `
      position: fixed;
      top: 80px;
      left: 8px;
      width: 200px;
      background: rgba(0, 0, 0, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 8px;
      font-family: monospace;
      font-size: 10px;
      color: rgba(255, 255, 255, 0.8);
      z-index: 1000;
      backdrop-filter: blur(10px);
      display: none;
    `

    panel.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 4px;">Legibility Harness</div>
      <div>Target: <span id="leg-target">—</span></div>
      <div>Chamfer: <span id="leg-chamfer">—</span></div>
      <div>OCR Conf: <span id="leg-ocr">—</span></div>
      <div>Hold: <span id="leg-hold">—</span>ms</div>
      <div style="margin-top: 4px;">
        <input type="checkbox" id="leg-log-metrics"> Log Metrics
      </div>
    `

    document.body.appendChild(panel)
    this.panel = panel
  },

  // Bind events
  bindEvents() {
    // Listen for morphScript events
    window.addEventListener('lukhas-morph-start', (e) => {
      this.onMorphStart(e.detail)
    })

    window.addEventListener('lukhas-morph-complete', (e) => {
      this.onMorphComplete(e.detail)
    })

    // Show panel on Alt+L
    document.addEventListener('keydown', (e) => {
      if (e.altKey && e.key === 'l') {
        e.preventDefault()
        this.togglePanel()
      }
    })
  },

  // Toggle panel visibility
  togglePanel() {
    if (this.panel) {
      this.panel.style.display = this.panel.style.display === 'none' ? 'block' : 'none'
    }
  },

  // Morph start handler
  onMorphStart(detail) {
    if (!this.panel || this.panel.style.display === 'none') return

    const target = detail?.text || detail?.shape || 'unknown'
    document.getElementById('leg-target').textContent = target
    document.getElementById('leg-chamfer').textContent = (detail?.chamferMax || 0).toFixed(3)
    document.getElementById('leg-hold').textContent = detail?.holdMs || 0
    
    this.startTime = performance.now()
  },

  // Morph complete handler
  onMorphComplete(detail) {
    if (!this.panel || this.panel.style.display === 'none') return

    const elapsed = performance.now() - (this.startTime || 0)
    const confidence = this.calculateOCRConfidence(detail)
    
    document.getElementById('leg-ocr').textContent = confidence.toFixed(3)

    // Log metrics if enabled
    const logMetrics = document.getElementById('leg-log-metrics')?.checked
    if (logMetrics) {
      this.logMetrics({
        target: document.getElementById('leg-target').textContent,
        chamfer: parseFloat(document.getElementById('leg-chamfer').textContent),
        ocrConfidence: confidence,
        timeToReadable: Math.round(elapsed),
        timestamp: new Date().toISOString()
      })
    }
  },

  // Calculate OCR confidence (simulated for demo)
  calculateOCRConfidence(detail) {
    // In real implementation, this would use actual OCR
    // For demo, simulate based on morphing parameters
    const baseConfidence = 0.85
    const morphSpeed = detail?.morphSpeed || 0.02
    const particleCount = detail?.particleCount || 1000
    
    let confidence = baseConfidence
    confidence += (particleCount / 5000) * 0.1  // More particles = better
    confidence -= (morphSpeed * 5)  // Faster morph = less stable
    confidence += (Date.now() % 100 / 1000) * 0.1 - 0.05  // Some deterministic noise
    
    return Math.max(0, Math.min(1, confidence))
  },

  // Log metrics to localStorage
  logMetrics(metrics) {
    try {
      const key = 'lukhas:legibility-metrics'
      const existing = JSON.parse(localStorage.getItem(key) || '[]')
      existing.push(metrics)
      
      // Keep only last 100 entries
      if (existing.length > 100) {
        existing.splice(0, existing.length - 100)
      }
      
      localStorage.setItem(key, JSON.stringify(existing))
      console.log('[Legibility] Metrics logged:', metrics)
    } catch (e) {
      console.warn('[Legibility] Failed to log metrics:', e)
    }
  },

  // Get stored metrics
  getMetrics() {
    try {
      return JSON.parse(localStorage.getItem('lukhas:legibility-metrics') || '[]')
    } catch {
      return []
    }
  },

  // Check if text is readable (main API)
  check(text, options = {}) {
    const confidence = (Date.now() % 300 / 1000) + 0.7  // 0.7-1.0 range for demo (deterministic)
    const readable = confidence >= (options.threshold || 0.92)
    
    return {
      confidence,
      readable,
      text,
      timestamp: Date.now()
    }
  },

  // Monitor mode (placeholder)
  monitor() {
    console.log('[Legibility] Monitoring active')
    return true
  }
}

// Auto-initialize when script loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.legibilityHarness.init()
  })
} else {
  window.legibilityHarness.init()
}