// lib/voice-analyzer.ts
// Real-time voice analysis for particle reactivity

export interface VoiceMetrics {
  intensity: number      // 0-1, overall volume/energy
  dominantFreq: number   // Hz, peak frequency
  spectralCentroid: number // Hz, brightness measure
  clarity: number        // 0-1, how clear/noisy
  rhythm: number         // 0-1, detected rhythmic pattern
  timestamp: number      // when measured
}

export interface VoiceAnalyzerConfig {
  fftSize: number
  smoothingTimeConstant: number
  minDecibels: number
  maxDecibels: number
  sampleRate: number
  updateInterval: number // ms
}

export const DEFAULT_VOICE_CONFIG: VoiceAnalyzerConfig = {
  fftSize: 512,
  smoothingTimeConstant: 0.3,
  minDecibels: -90,
  maxDecibels: -10,
  sampleRate: 44100,
  updateInterval: 33 // ~30fps
}

/**
 * Real-time voice analyzer using Web Audio API
 */
export class VoiceAnalyzer {
  private audioContext: AudioContext | null = null
  private analyser: AnalyserNode | null = null
  private microphone: MediaStreamAudioSourceNode | null = null
  private dataArray: Uint8Array | null = null
  private isRunning = false
  private animationFrame: number | null = null

  // Smoothing for stability
  private intensityHistory: number[] = []
  private freqHistory: number[] = []
  private readonly historySize = 5

  constructor(private config: VoiceAnalyzerConfig = DEFAULT_VOICE_CONFIG) {}

  /**
   * Initialize microphone access and analysis
   */
  async initialize(): Promise<boolean> {
    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: this.config.sampleRate
        }
      })

      // Create audio context
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()

      // Create analyser
      this.analyser = this.audioContext.createAnalyser()
      this.analyser.fftSize = this.config.fftSize
      this.analyser.smoothingTimeConstant = this.config.smoothingTimeConstant
      this.analyser.minDecibels = this.config.minDecibels
      this.analyser.maxDecibels = this.config.maxDecibels

      // Connect microphone
      this.microphone = this.audioContext.createMediaStreamSource(stream)
      this.microphone.connect(this.analyser)

      // Initialize data array
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount)

      return true
    } catch (error) {
      console.error('[VoiceAnalyzer] Failed to initialize:', error)
      return false
    }
  }

  /**
   * Start real-time analysis
   */
  start(onUpdate: (metrics: VoiceMetrics) => void): void {
    if (!this.analyser || !this.dataArray || this.isRunning) return

    this.isRunning = true

    const analyze = () => {
      if (!this.isRunning || !this.analyser || !this.dataArray) return

      // Get frequency data
      this.analyser.getByteFrequencyData(this.dataArray)

      // Calculate metrics
      const metrics = this.calculateMetrics(this.dataArray)

      // Smooth the metrics
      const smoothedMetrics = this.smoothMetrics(metrics)

      // Call update callback
      onUpdate(smoothedMetrics)

      // Schedule next analysis
      this.animationFrame = requestAnimationFrame(analyze)
    }

    analyze()
  }

  /**
   * Stop analysis
   */
  stop(): void {
    this.isRunning = false

    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame)
      this.animationFrame = null
    }
  }

  /**
   * Clean up resources
   */
  dispose(): void {
    this.stop()

    if (this.microphone) {
      this.microphone.disconnect()
      this.microphone = null
    }

    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }

    this.analyser = null
    this.dataArray = null
  }

  /**
   * Calculate voice metrics from frequency data
   */
  private calculateMetrics(frequencyData: Uint8Array): VoiceMetrics {
    const timestamp = performance.now()

    // Calculate intensity (RMS of frequency bins)
    let sum = 0
    for (let i = 0; i < frequencyData.length; i++) {
      const normalized = frequencyData[i] / 255
      sum += normalized * normalized
    }
    const intensity = Math.sqrt(sum / frequencyData.length)

    // Find dominant frequency
    let maxAmplitude = 0
    let dominantBin = 0
    for (let i = 0; i < frequencyData.length; i++) {
      if (frequencyData[i] > maxAmplitude) {
        maxAmplitude = frequencyData[i]
        dominantBin = i
      }
    }

    const binWidth = this.config.sampleRate / (2 * frequencyData.length)
    const dominantFreq = dominantBin * binWidth

    // Calculate spectral centroid (brightness)
    let weightedSum = 0
    let amplitudeSum = 0
    for (let i = 0; i < frequencyData.length; i++) {
      const freq = i * binWidth
      const amplitude = frequencyData[i] / 255
      weightedSum += freq * amplitude
      amplitudeSum += amplitude
    }
    const spectralCentroid = amplitudeSum > 0 ? weightedSum / amplitudeSum : 0

    // Calculate clarity (high frequency energy vs low frequency energy)
    const midpoint = Math.floor(frequencyData.length / 2)
    let lowEnergy = 0
    let highEnergy = 0

    for (let i = 0; i < midpoint; i++) {
      lowEnergy += frequencyData[i]
    }
    for (let i = midpoint; i < frequencyData.length; i++) {
      highEnergy += frequencyData[i]
    }

    const totalEnergy = lowEnergy + highEnergy
    const clarity = totalEnergy > 0 ? highEnergy / totalEnergy : 0

    // Simple rhythm detection (energy variation)
    const energyVariation = this.calculateEnergyVariation(frequencyData)
    const rhythm = Math.min(energyVariation * 2, 1) // Scale and clamp

    return {
      intensity: Math.min(intensity, 1),
      dominantFreq,
      spectralCentroid,
      clarity,
      rhythm,
      timestamp
    }
  }

  /**
   * Smooth metrics using history
   */
  private smoothMetrics(current: VoiceMetrics): VoiceMetrics {
    // Add to history
    this.intensityHistory.push(current.intensity)
    this.freqHistory.push(current.dominantFreq)

    // Maintain history size
    if (this.intensityHistory.length > this.historySize) {
      this.intensityHistory.shift()
      this.freqHistory.shift()
    }

    // Calculate smoothed values
    const smoothedIntensity = this.intensityHistory.reduce((a, b) => a + b, 0) / this.intensityHistory.length
    const smoothedFreq = this.freqHistory.reduce((a, b) => a + b, 0) / this.freqHistory.length

    return {
      ...current,
      intensity: smoothedIntensity,
      dominantFreq: smoothedFreq
    }
  }

  /**
   * Calculate energy variation for rhythm detection
   */
  private calculateEnergyVariation(frequencyData: Uint8Array): number {
    const energy = frequencyData.reduce((sum, val) => sum + val, 0)
    const normalizedEnergy = energy / (frequencyData.length * 255)

    // Store energy for variation calculation
    if (!this.energyHistory) {
      this.energyHistory = []
    }

    this.energyHistory.push(normalizedEnergy)
    if (this.energyHistory.length > 10) {
      this.energyHistory.shift()
    }

    if (this.energyHistory.length < 2) return 0

    // Calculate standard deviation
    const mean = this.energyHistory.reduce((a, b) => a + b, 0) / this.energyHistory.length
    const variance = this.energyHistory.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / this.energyHistory.length

    return Math.sqrt(variance)
  }

  private energyHistory: number[] = []
}

/**
 * Create and initialize voice analyzer
 */
export async function createVoiceAnalyzer(config?: Partial<VoiceAnalyzerConfig>): Promise<VoiceAnalyzer | null> {
  const analyzer = new VoiceAnalyzer({ ...DEFAULT_VOICE_CONFIG, ...config })

  const success = await analyzer.initialize()
  if (!success) {
    analyzer.dispose()
    return null
  }

  return analyzer
}

/**
 * Check if voice analysis is supported
 */
export function isVoiceAnalysisSupported(): boolean {
  return !!(
    navigator.mediaDevices &&
    navigator.mediaDevices.getUserMedia &&
    (window.AudioContext || (window as any).webkitAudioContext)
  )
}
