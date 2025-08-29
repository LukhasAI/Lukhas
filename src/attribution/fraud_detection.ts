/**
 * Advanced Fraud Detection - ML-powered bot detection and device fingerprinting
 * Implements sophisticated fraud scoring with quarantine workflows
 */

import crypto from 'crypto';

export interface DeviceFingerprint {
  canvas_hash: string;
  webgl_hash: string;
  audio_hash: string;
  font_list: string[];
  plugin_list: string[];
  timezone: string;
  language: string;
  platform: string;
  hardware_concurrency: number;
  device_memory: number;
  screen_resolution: string;
  color_depth: number;
  pixel_ratio: number;
  touch_support: boolean;
  webrtc_ips: string[];
  battery_info?: {
    charging: boolean;
    level: number;
    charging_time: number;
  };
}

export interface BehavioralSignals {
  mouse_movements: Array<{
    x: number;
    y: number;
    timestamp: number;
  }>;
  keypress_timings: number[];
  scroll_patterns: Array<{
    position: number;
    velocity: number;
    timestamp: number;
  }>;
  focus_events: Array<{
    element_type: string;
    duration_ms: number;
    timestamp: number;
  }>;
  page_visibility_changes: Array<{
    hidden: boolean;
    timestamp: number;
  }>;
  session_metadata: {
    start_time: number;
    page_loads: number;
    user_agent: string;
    referrer: string;
    viewport_size: string;
  };
}

export interface NetworkSignals {
  ip_address: string;
  connection_type: string;
  rtt: number;
  downlink: number;
  effective_type: string;
  proxy_detected: boolean;
  tor_detected: boolean;
  vpn_detected: boolean;
  geolocation: {
    country: string;
    region: string;
    city: string;
    latitude?: number;
    longitude?: number;
    accuracy: number;
  };
  asn: {
    number: number;
    organization: string;
    type: 'residential' | 'datacenter' | 'mobile' | 'unknown';
  };
}

export interface FraudScore {
  overall_score: number; // 0-1, higher = more fraudulent
  component_scores: {
    bot_likelihood: number;
    device_spoofing: number;
    behavioral_anomalies: number;
    network_risk: number;
    velocity_risk: number;
    reputation_risk: number;
  };
  risk_factors: string[];
  confidence: number;
  reasoning: string;
  quarantine_recommended: boolean;
  manual_review_required: boolean;
}

export class AdvancedFraudDetector {
  private db: any;
  private mlModel: any; // In production, this would be a real ML model
  private ipReputationService: any;
  private deviceFingerprintCache: Map<string, DeviceFingerprint> = new Map();

  constructor(database: any, mlModel?: any, ipService?: any) {
    this.db = database;
    this.mlModel = mlModel;
    this.ipReputationService = ipService;
  }

  /**
   * Generate comprehensive fraud score
   */
  async generateFraudScore(
    deviceFingerprint: DeviceFingerprint,
    behavioralSignals: BehavioralSignals,
    networkSignals: NetworkSignals,
    transactionContext: any
  ): Promise<FraudScore> {
    
    // Calculate individual component scores
    const botLikelihood = await this.calculateBotLikelihood(
      deviceFingerprint,
      behavioralSignals,
      networkSignals
    );

    const deviceSpoofing = this.detectDeviceSpoofing(deviceFingerprint);
    
    const behavioralAnomalies = this.analyzeBehavioralAnomalies(
      behavioralSignals,
      transactionContext.user_id
    );
    
    const networkRisk = await this.assessNetworkRisk(networkSignals);
    
    const velocityRisk = await this.calculateVelocityRisk(
      transactionContext,
      networkSignals.ip_address,
      deviceFingerprint
    );
    
    const reputationRisk = await this.assessReputationRisk(
      networkSignals,
      transactionContext.user_id
    );

    // Weighted overall score
    const weights = {
      bot_likelihood: 0.25,
      device_spoofing: 0.20,
      behavioral_anomalies: 0.20,
      network_risk: 0.15,
      velocity_risk: 0.15,
      reputation_risk: 0.05
    };

    const componentScores = {
      bot_likelihood: botLikelihood,
      device_spoofing: deviceSpoofing,
      behavioral_anomalies: behavioralAnomalies,
      network_risk: networkRisk,
      velocity_risk: velocityRisk,
      reputation_risk: reputationRisk
    };

    const overallScore = Object.entries(componentScores).reduce(
      (sum, [key, score]) => sum + (score * weights[key as keyof typeof weights]),
      0
    );

    // Generate risk factors and reasoning
    const riskFactors = this.identifyRiskFactors(componentScores);
    const reasoning = this.generateReasoning(componentScores, riskFactors);
    
    // Determine if quarantine or manual review needed
    const quarantineRecommended = overallScore > 0.7 || riskFactors.length > 3;
    const manualReviewRequired = overallScore > 0.8 || riskFactors.includes('high_bot_likelihood');

    const confidence = this.calculateConfidence(componentScores, behavioralSignals);

    return {
      overall_score: overallScore,
      component_scores: componentScores,
      risk_factors: riskFactors,
      confidence,
      reasoning,
      quarantine_recommended: quarantineRecommended,
      manual_review_required: manualReviewRequired
    };
  }

  /**
   * Calculate bot likelihood using ML model and heuristics
   */
  private async calculateBotLikelihood(
    deviceFingerprint: DeviceFingerprint,
    behavioralSignals: BehavioralSignals,
    networkSignals: NetworkSignals
  ): Promise<number> {
    
    let botScore = 0;

    // Heuristic checks
    
    // 1. User agent analysis
    const userAgent = behavioralSignals.session_metadata.user_agent.toLowerCase();
    if (this.isSuspiciousUserAgent(userAgent)) {
      botScore += 0.4;
    }

    // 2. Behavioral pattern analysis
    const behaviorScore = this.analyzeBehaviorForBotPatterns(behavioralSignals);
    botScore += behaviorScore * 0.3;

    // 3. Device consistency check
    const consistencyScore = this.checkDeviceConsistency(deviceFingerprint);
    botScore += (1 - consistencyScore) * 0.2;

    // 4. Network characteristics
    if (networkSignals.proxy_detected || networkSignals.tor_detected) {
      botScore += 0.3;
    }

    // 5. Automation detection
    const automationScore = this.detectAutomationSignals(deviceFingerprint, behavioralSignals);
    botScore += automationScore * 0.4;

    // 6. ML model prediction (if available)
    if (this.mlModel) {
      const features = this.extractMLFeatures(deviceFingerprint, behavioralSignals, networkSignals);
      const mlScore = await this.mlModel.predict(features);
      botScore = (botScore * 0.6) + (mlScore * 0.4); // Combine heuristics with ML
    }

    return Math.min(1.0, botScore);
  }

  /**
   * Detect device spoofing attempts
   */
  private detectDeviceSpoofing(fingerprint: DeviceFingerprint): number {
    let spoofingScore = 0;

    // Check for inconsistent fingerprint elements
    if (fingerprint.canvas_hash === '' || fingerprint.webgl_hash === '') {
      spoofingScore += 0.3;
    }

    // Detect common spoofing patterns
    if (fingerprint.font_list.length < 10) {
      spoofingScore += 0.2;
    }

    // Check for impossible hardware combinations
    if (fingerprint.hardware_concurrency > 32 || fingerprint.device_memory > 32) {
      spoofingScore += 0.4;
    }

    // Detect fingerprint randomization
    const entropy = this.calculateFingerprintEntropy(fingerprint);
    if (entropy < 0.3) {
      spoofingScore += 0.5;
    }

    return Math.min(1.0, spoofingScore);
  }

  /**
   * Analyze behavioral patterns for anomalies
   */
  private analyzeBehavioralAnomalies(
    behavioralSignals: BehavioralSignals,
    userId: string
  ): Promise<number> {
    // This would compare against historical behavior for the user
    // For now, using heuristics
    
    let anomalyScore = 0;

    // Mouse movement analysis
    const mouseEntropy = this.calculateMouseEntropy(behavioralSignals.mouse_movements);
    if (mouseEntropy < 0.2) {
      anomalyScore += 0.3; // Too linear/robotic
    }

    // Keypress timing analysis
    const keystrokeRhythm = this.analyzeKeystrokeRhythm(behavioralSignals.keypress_timings);
    if (keystrokeRhythm < 0.3) {
      anomalyScore += 0.2; // Too uniform
    }

    // Session duration analysis
    const sessionDuration = Date.now() - behavioralSignals.session_metadata.start_time;
    if (sessionDuration < 5000) {
      anomalyScore += 0.4; // Suspiciously short session
    }

    // Page interaction patterns
    if (behavioralSignals.focus_events.length === 0) {
      anomalyScore += 0.3; // No focus events suggest automation
    }

    return Promise.resolve(Math.min(1.0, anomalyScore));
  }

  /**
   * Assess network-based risk factors
   */
  private async assessNetworkRisk(networkSignals: NetworkSignals): Promise<number> {
    let networkRisk = 0;

    // Proxy/VPN/Tor detection
    if (networkSignals.tor_detected) networkRisk += 0.6;
    if (networkSignals.proxy_detected) networkRisk += 0.4;
    if (networkSignals.vpn_detected) networkRisk += 0.2;

    // Datacenter IP detection
    if (networkSignals.asn.type === 'datacenter') {
      networkRisk += 0.5;
    }

    // Geographic risk assessment
    const geoRisk = await this.assessGeographicRisk(networkSignals.geolocation);
    networkRisk += geoRisk * 0.3;

    // Connection quality analysis
    if (networkSignals.rtt > 1000 || networkSignals.downlink < 0.5) {
      networkRisk += 0.2; // Poor connection might indicate proxy chains
    }

    return Math.min(1.0, networkRisk);
  }

  /**
   * Calculate velocity-based risk
   */
  private async calculateVelocityRisk(
    transactionContext: any,
    ipAddress: string,
    deviceFingerprint: DeviceFingerprint
  ): Promise<number> {
    
    const now = new Date();
    const hourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    // Check velocity by IP
    const ipTransactions = await this.db.collection('attributions').countDocuments({
      'postback_data.device_signals.ip_address': ipAddress,
      created_at: { $gte: hourAgo }
    });

    // Check velocity by device
    const deviceHash = this.hashDeviceFingerprint(deviceFingerprint);
    const deviceTransactions = await this.db.collection('attributions').countDocuments({
      device_hash: deviceHash,
      created_at: { $gte: hourAgo }
    });

    // Check user velocity
    const userTransactions = await this.db.collection('attributions').countDocuments({
      user_id: transactionContext.user_id,
      created_at: { $gte: dayAgo }
    });

    let velocityRisk = 0;
    
    if (ipTransactions > 10) velocityRisk += 0.6;
    if (deviceTransactions > 5) velocityRisk += 0.5;
    if (userTransactions > 20) velocityRisk += 0.4;

    return Math.min(1.0, velocityRisk);
  }

  /**
   * Assess reputation-based risk
   */
  private async assessReputationRisk(
    networkSignals: NetworkSignals,
    userId: string
  ): Promise<number> {
    
    let reputationRisk = 0;

    // IP reputation check
    if (this.ipReputationService) {
      const ipRep = await this.ipReputationService.checkReputation(networkSignals.ip_address);
      reputationRisk += ipRep.risk_score * 0.6;
    }

    // User historical behavior
    const userHistory = await this.db.collection('user_reputation').findOne({
      user_id: userId
    });

    if (userHistory) {
      if (userHistory.fraud_score > 0.5) {
        reputationRisk += 0.4;
      }
      if (userHistory.chargeback_rate > 0.1) {
        reputationRisk += 0.3;
      }
    }

    return Math.min(1.0, reputationRisk);
  }

  /**
   * Utility methods
   */
  
  private isSuspiciousUserAgent(userAgent: string): boolean {
    const botPatterns = [
      'headlesschrome', 'phantomjs', 'selenium', 'webdriver',
      'bot', 'crawler', 'spider', 'scraper', 'automation'
    ];
    
    return botPatterns.some(pattern => userAgent.includes(pattern));
  }

  private analyzeBehaviorForBotPatterns(behavioralSignals: BehavioralSignals): number {
    let botScore = 0;

    // Perfect timing patterns (common in bots)
    const timingVariance = this.calculateTimingVariance(behavioralSignals.keypress_timings);
    if (timingVariance < 0.1) {
      botScore += 0.4;
    }

    // Linear mouse movements
    const mouseLinearity = this.calculateMouseLinearity(behavioralSignals.mouse_movements);
    if (mouseLinearity > 0.9) {
      botScore += 0.5;
    }

    // No idle time
    if (behavioralSignals.page_visibility_changes.length === 0) {
      botScore += 0.3;
    }

    return Math.min(1.0, botScore);
  }

  private checkDeviceConsistency(fingerprint: DeviceFingerprint): number {
    // Check if device properties are consistent with each other
    let consistencyScore = 1.0;

    // Mobile device checks
    if (fingerprint.touch_support && fingerprint.screen_resolution.includes('1920x1080')) {
      consistencyScore -= 0.3; // Unlikely combination
    }

    // Hardware concurrency vs device memory consistency
    if (fingerprint.hardware_concurrency > 16 && fingerprint.device_memory < 4) {
      consistencyScore -= 0.4;
    }

    return Math.max(0, consistencyScore);
  }

  private detectAutomationSignals(
    fingerprint: DeviceFingerprint,
    behavioralSignals: BehavioralSignals
  ): number {
    let automationScore = 0;

    // WebDriver detection
    if (!fingerprint.webgl_hash) {
      automationScore += 0.3;
    }

    // Missing plugins (common in automation)
    if (fingerprint.plugin_list.length === 0) {
      automationScore += 0.2;
    }

    // Perfect scroll patterns
    const scrollVariance = this.calculateScrollVariance(behavioralSignals.scroll_patterns);
    if (scrollVariance < 0.1) {
      automationScore += 0.4;
    }

    return Math.min(1.0, automationScore);
  }

  private calculateFingerprintEntropy(fingerprint: DeviceFingerprint): number {
    // Calculate entropy of fingerprint components
    const components = [
      fingerprint.canvas_hash,
      fingerprint.webgl_hash,
      fingerprint.audio_hash,
      fingerprint.font_list.join(','),
      fingerprint.plugin_list.join(',')
    ];

    let entropy = 0;
    components.forEach(component => {
      if (component && component.length > 0) {
        entropy += this.shannonEntropy(component);
      }
    });

    return entropy / components.length;
  }

  private calculateMouseEntropy(movements: any[]): number {
    if (movements.length < 10) return 0;
    
    // Calculate entropy based on direction changes and velocity variations
    const velocities = movements.slice(1).map((move, i) => {
      const prev = movements[i];
      const distance = Math.sqrt(
        Math.pow(move.x - prev.x, 2) + Math.pow(move.y - prev.y, 2)
      );
      const time = move.timestamp - prev.timestamp;
      return time > 0 ? distance / time : 0;
    });

    return this.shannonEntropy(velocities.map(v => Math.floor(v * 100).toString()).join(''));
  }

  private shannonEntropy(str: string): number {
    const freq: { [key: string]: number } = {};
    for (const char of str) {
      freq[char] = (freq[char] || 0) + 1;
    }

    let entropy = 0;
    const length = str.length;
    Object.values(freq).forEach(count => {
      const p = count / length;
      entropy -= p * Math.log2(p);
    });

    return entropy;
  }

  private analyzeKeystrokeRhythm(timings: number[]): number {
    if (timings.length < 5) return 0.5;
    
    const intervals = timings.slice(1).map((time, i) => time - timings[i]);
    const mean = intervals.reduce((a, b) => a + b) / intervals.length;
    const variance = intervals.reduce((sum, interval) => sum + Math.pow(interval - mean, 2), 0) / intervals.length;
    
    return Math.min(1.0, variance / 10000); // Normalize variance
  }

  private calculateTimingVariance(timings: number[]): number {
    if (timings.length < 2) return 1;
    
    const intervals = timings.slice(1).map((time, i) => time - timings[i]);
    const mean = intervals.reduce((a, b) => a + b) / intervals.length;
    const variance = intervals.reduce((sum, interval) => sum + Math.pow(interval - mean, 2), 0) / intervals.length;
    
    return variance / (mean * mean); // Coefficient of variation
  }

  private calculateMouseLinearity(movements: any[]): number {
    if (movements.length < 3) return 0;
    
    // Calculate how close mouse movements are to straight lines
    let totalDeviation = 0;
    for (let i = 2; i < movements.length; i++) {
      const p1 = movements[i - 2];
      const p2 = movements[i - 1];
      const p3 = movements[i];
      
      // Calculate deviation from straight line between p1 and p3
      const deviation = this.pointToLineDistance(p1, p3, p2);
      totalDeviation += deviation;
    }
    
    const averageDeviation = totalDeviation / (movements.length - 2);
    return Math.max(0, 1 - (averageDeviation / 100)); // Normalize
  }

  private pointToLineDistance(p1: any, p2: any, point: any): number {
    const A = point.x - p1.x;
    const B = point.y - p1.y;
    const C = p2.x - p1.x;
    const D = p2.y - p1.y;

    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    
    if (lenSq === 0) return Math.sqrt(A * A + B * B);
    
    const param = dot / lenSq;
    let xx, yy;

    if (param < 0) {
      xx = p1.x;
      yy = p1.y;
    } else if (param > 1) {
      xx = p2.x;
      yy = p2.y;
    } else {
      xx = p1.x + param * C;
      yy = p1.y + param * D;
    }

    const dx = point.x - xx;
    const dy = point.y - yy;
    return Math.sqrt(dx * dx + dy * dy);
  }

  private calculateScrollVariance(scrollPatterns: any[]): number {
    if (scrollPatterns.length < 2) return 1;
    
    const velocities = scrollPatterns.map(scroll => scroll.velocity);
    const mean = velocities.reduce((a, b) => a + b) / velocities.length;
    const variance = velocities.reduce((sum, vel) => sum + Math.pow(vel - mean, 2), 0) / velocities.length;
    
    return variance / (mean * mean + 1); // Coefficient of variation with offset
  }

  private async assessGeographicRisk(geolocation: any): Promise<number> {
    // High-risk countries/regions (simplified)
    const highRiskCountries = ['XX', 'YY', 'ZZ']; // Placeholder
    if (highRiskCountries.includes(geolocation.country)) {
      return 0.6;
    }
    
    // Check for impossible travel (would require user history)
    return 0.1; // Default low risk
  }

  private hashDeviceFingerprint(fingerprint: DeviceFingerprint): string {
    const fingerprintString = JSON.stringify(fingerprint, Object.keys(fingerprint).sort());
    return crypto.createHash('sha256').update(fingerprintString).digest('hex');
  }

  private extractMLFeatures(
    deviceFingerprint: DeviceFingerprint,
    behavioralSignals: BehavioralSignals,
    networkSignals: NetworkSignals
  ): number[] {
    // Extract numerical features for ML model
    return [
      deviceFingerprint.hardware_concurrency,
      deviceFingerprint.device_memory,
      deviceFingerprint.font_list.length,
      deviceFingerprint.plugin_list.length,
      behavioralSignals.mouse_movements.length,
      behavioralSignals.keypress_timings.length,
      behavioralSignals.session_metadata.page_loads,
      networkSignals.rtt,
      networkSignals.downlink,
      networkSignals.proxy_detected ? 1 : 0,
      networkSignals.tor_detected ? 1 : 0,
      networkSignals.vpn_detected ? 1 : 0,
      // Add more features as needed
    ];
  }

  private identifyRiskFactors(componentScores: any): string[] {
    const factors: string[] = [];
    
    if (componentScores.bot_likelihood > 0.7) factors.push('high_bot_likelihood');
    if (componentScores.device_spoofing > 0.6) factors.push('device_spoofing_detected');
    if (componentScores.behavioral_anomalies > 0.5) factors.push('behavioral_anomalies');
    if (componentScores.network_risk > 0.6) factors.push('network_risk');
    if (componentScores.velocity_risk > 0.5) factors.push('velocity_exceeded');
    if (componentScores.reputation_risk > 0.4) factors.push('reputation_risk');
    
    return factors;
  }

  private generateReasoning(componentScores: any, riskFactors: string[]): string {
    const scores = Object.entries(componentScores)
      .map(([key, score]) => `${key}: ${Math.round((score as number) * 100)}%`)
      .join(', ');
    
    return `Risk assessment based on: ${scores}. Primary concerns: ${riskFactors.join(', ')}`;
  }

  private calculateConfidence(componentScores: any, behavioralSignals: BehavioralSignals): number {
    // Confidence based on amount of behavioral data available
    let confidence = 0.5; // Base confidence
    
    if (behavioralSignals.mouse_movements.length > 50) confidence += 0.2;
    if (behavioralSignals.keypress_timings.length > 10) confidence += 0.1;
    if (behavioralSignals.session_metadata.page_loads > 3) confidence += 0.1;
    
    // Reduce confidence if scores are conflicting
    const scoreVariance = this.calculateScoreVariance(Object.values(componentScores) as number[]);
    confidence -= scoreVariance * 0.3;
    
    return Math.max(0.1, Math.min(1.0, confidence));
  }

  private calculateScoreVariance(scores: number[]): number {
    const mean = scores.reduce((a, b) => a + b) / scores.length;
    const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
    return variance;
  }
}

export default AdvancedFraudDetector;