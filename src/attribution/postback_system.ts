/**
 * S2S Postback System - Attribution hardening with fraud detection
 * Implements 6-tier attribution ladder with bot detection and quarantine
 */

import { Request, Response } from 'express';
import crypto from 'crypto';
import { verifyHMAC, generateTimestampedHMAC } from '../utils/hmac';

export interface AttributionPostback {
  purchase_id: string;
  user_id: string;
  opportunity_id: string;
  merchant_id: string;
  purchase_data: {
    amount: number;
    currency: string;
    products: Array<{
      id: string;
      name: string;
      category: string;
      price: number;
    }>;
    order_id: string;
    timestamp: string;
  };
  device_signals: {
    ip_address: string;
    user_agent: string;
    device_fingerprint: string;
    timezone_offset: number;
    screen_resolution: string;
    language: string;
    referrer?: string;
  };
  attribution_context: {
    click_id?: string;
    impression_id?: string;
    campaign_id?: string;
    attribution_window_hours: number;
    last_interaction_timestamp?: string;
  };
}

export interface FraudSignals {
  bot_probability: number;
  device_entropy: number;
  velocity_flags: {
    rapid_purchases: boolean;
    ip_velocity_exceeded: boolean;
    device_velocity_exceeded: boolean;
  };
  behavioral_signals: {
    human_interaction_score: number;
    session_duration_ms: number;
    page_views_count: number;
    mouse_movement_entropy: number;
  };
  reputation_signals: {
    ip_risk_score: number;
    device_risk_score: number;
    merchant_trust_score: number;
  };
}

export interface AttributionDecision {
  attribution_method: 'affiliate' | 's2s' | 'receipt' | 'behavioral' | 'last_touch' | 'default';
  confidence: number;
  fraud_assessment: {
    risk_score: number;
    quarantine_required: boolean;
    manual_review_required: boolean;
    signals_summary: string[];
  };
  commission: {
    rate: number;
    amount: number;
    currency: string;
    escalation_tier: string;
  };
  processing_decision: 'approve' | 'quarantine' | 'reject';
  reasoning: string;
}

export class S2SPostbackSystem {
  private db: any;
  private auditLogger: any;
  private fraudDetector: FraudDetector;
  private attributionEngine: AttributionEngine;

  constructor(database: any, auditLogger: any) {
    this.db = database;
    this.auditLogger = auditLogger;
    this.fraudDetector = new FraudDetector();
    this.attributionEngine = new AttributionEngine(database);
  }

  /**
   * Process incoming S2S postback with fraud detection
   */
  async processPostback(req: Request, res: Response): Promise<void> {
    const startTime = Date.now();

    try {
      // Verify HMAC signature
      const signature = req.headers['x-signature'] as string;
      const merchantSecret = await this.getMerchantSecret(req.body.merchant_id);
      
      if (!verifyHMAC(JSON.stringify(req.body), signature, merchantSecret)) {
        await this.auditLogger.log({
          action: 'postback_signature_invalid',
          merchant_id: req.body.merchant_id,
          ip_address: req.ip,
          timestamp: new Date().toISOString()
        });

        res.status(401).json({
          status: 'error',
          error: 'invalid_signature',
          message: 'HMAC signature verification failed'
        });
        return;
      }

      const postback: AttributionPostback = req.body;

      // Generate fraud signals
      const fraudSignals = await this.fraudDetector.generateSignals(postback, req);

      // Run attribution logic
      const attributionDecision = await this.attributionEngine.processAttribution(
        postback,
        fraudSignals
      );

      // Store attribution record
      const attributionRecord = {
        attribution_id: crypto.randomUUID(),
        purchase_id: postback.purchase_id,
        user_id: postback.user_id,
        merchant_id: postback.merchant_id,
        attribution_decision: attributionDecision,
        fraud_signals: fraudSignals,
        postback_data: postback,
        processing_time_ms: Date.now() - startTime,
        created_at: new Date(),
        status: attributionDecision.processing_decision
      };

      await this.db.collection('attributions').insertOne(attributionRecord);

      // Handle quarantine if needed
      if (attributionDecision.processing_decision === 'quarantine') {
        await this.quarantineForReview(attributionRecord);
      }

      // Generate receipt if approved
      if (attributionDecision.processing_decision === 'approve') {
        await this.generateAttributionReceipt(attributionRecord);
      }

      // Log success
      await this.auditLogger.log({
        action: 'postback_processed',
        attribution_id: attributionRecord.attribution_id,
        merchant_id: postback.merchant_id,
        processing_decision: attributionDecision.processing_decision,
        risk_score: attributionDecision.fraud_assessment.risk_score,
        processing_time_ms: Date.now() - startTime,
        timestamp: new Date().toISOString()
      });

      // Return response
      res.json({
        status: 'success',
        attribution_id: attributionRecord.attribution_id,
        processing_decision: attributionDecision.processing_decision,
        attribution_method: attributionDecision.attribution_method,
        confidence: attributionDecision.confidence,
        commission: attributionDecision.commission,
        fraud_assessment: attributionDecision.fraud_assessment,
        processing_time_ms: Date.now() - startTime
      });

    } catch (error) {
      console.error('Postback processing error:', error);
      
      await this.auditLogger.log({
        action: 'postback_error',
        error: error instanceof Error ? error.message : 'Unknown error',
        merchant_id: req.body?.merchant_id,
        timestamp: new Date().toISOString()
      });

      res.status(500).json({
        status: 'error',
        error: 'processing_failed',
        message: 'Failed to process postback'
      });
    }
  }

  /**
   * Get merchant secret for HMAC verification
   */
  private async getMerchantSecret(merchantId: string): Promise<string> {
    const merchant = await this.db.collection('merchants').findOne({
      merchant_id: merchantId
    });

    if (!merchant || !merchant.webhook_secret) {
      throw new Error('Merchant not found or webhook secret not configured');
    }

    return merchant.webhook_secret;
  }

  /**
   * Queue transaction for manual review
   */
  private async quarantineForReview(attributionRecord: any): Promise<void> {
    const quarantineEntry = {
      quarantine_id: crypto.randomUUID(),
      attribution_id: attributionRecord.attribution_id,
      reason: 'fraud_risk_threshold_exceeded',
      risk_score: attributionRecord.attribution_decision.fraud_assessment.risk_score,
      signals: attributionRecord.fraud_signals,
      created_at: new Date(),
      status: 'pending_review',
      priority: attributionRecord.attribution_decision.fraud_assessment.risk_score > 0.8 ? 'high' : 'medium'
    };

    await this.db.collection('quarantine').insertOne(quarantineEntry);

    // Notify review team for high-risk cases
    if (quarantineEntry.priority === 'high') {
      // In production, this would send alerts to review team
      console.log(`HIGH RISK: Attribution ${attributionRecord.attribution_id} quarantined for review`);
    }
  }

  /**
   * Generate attribution receipt for approved transactions
   */
  private async generateAttributionReceipt(attributionRecord: any): Promise<void> {
    const receipt = {
      receipt_id: `pur_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      receipt_type: 'purchase',
      user_id: attributionRecord.user_id,
      purchase_id: attributionRecord.purchase_id,
      attributed_at: new Date().toISOString(),
      purchase: {
        merchant: attributionRecord.merchant_id,
        amount: attributionRecord.postback_data.purchase_data.amount,
        currency: attributionRecord.postback_data.purchase_data.currency,
        product_categories: attributionRecord.postback_data.purchase_data.products.map(p => p.category),
        order_id: attributionRecord.postback_data.purchase_data.order_id
      },
      attribution: {
        method: attributionRecord.attribution_decision.attribution_method,
        confidence: attributionRecord.attribution_decision.confidence,
        attribution_window_hours: attributionRecord.postback_data.attribution_context.attribution_window_hours,
        signals: {
          device_match: attributionRecord.fraud_signals.device_entropy > 0.5,
          temporal_proximity: this.calculateTemporalProximity(attributionRecord),
          behavioral_signals: this.extractBehavioralSignals(attributionRecord.fraud_signals),
          fraud_score: attributionRecord.attribution_decision.fraud_assessment.risk_score
        }
      },
      commission: attributionRecord.attribution_decision.commission,
      created_at: new Date()
    };

    await this.db.collection('receipts').insertOne(receipt);

    // Trigger payout processing
    await this.triggerPayoutProcessing(receipt);
  }

  /**
   * Calculate temporal proximity between interaction and purchase
   */
  private calculateTemporalProximity(attributionRecord: any): number {
    const purchaseTime = new Date(attributionRecord.postback_data.purchase_data.timestamp);
    const lastInteractionTime = new Date(
      attributionRecord.postback_data.attribution_context.last_interaction_timestamp || purchaseTime
    );
    
    const timeDiffHours = Math.abs(purchaseTime.getTime() - lastInteractionTime.getTime()) / (1000 * 60 * 60);
    return Math.max(0, 1 - (timeDiffHours / 24)); // Normalize to 0-1 over 24 hours
  }

  /**
   * Extract behavioral signals for receipt
   */
  private extractBehavioralSignals(fraudSignals: FraudSignals): string[] {
    const signals: string[] = [];
    
    if (fraudSignals.behavioral_signals.human_interaction_score > 0.8) {
      signals.push('strong_human_interaction');
    }
    
    if (fraudSignals.behavioral_signals.session_duration_ms > 60000) {
      signals.push('engaged_session');
    }
    
    if (fraudSignals.device_entropy > 0.7) {
      signals.push('unique_device');
    }
    
    return signals;
  }

  /**
   * Trigger payout processing pipeline
   */
  private async triggerPayoutProcessing(receipt: any): Promise<void> {
    // In production, this would trigger the payout pipeline
    console.log(`Triggering payout for receipt ${receipt.receipt_id}`);
    
    // Queue payout job
    const payoutJob = {
      job_id: crypto.randomUUID(),
      receipt_id: receipt.receipt_id,
      user_id: receipt.user_id,
      commission_amount: receipt.commission.amount,
      commission_currency: receipt.commission.currency,
      status: 'queued',
      created_at: new Date()
    };

    await this.db.collection('payout_jobs').insertOne(payoutJob);
  }
}

/**
 * Fraud Detection Engine
 */
class FraudDetector {
  async generateSignals(postback: AttributionPostback, req: Request): Promise<FraudSignals> {
    const deviceEntropy = this.calculateDeviceEntropy(postback.device_signals);
    const botProbability = this.calculateBotProbability(postback.device_signals);
    const velocityFlags = await this.checkVelocityFlags(postback, req.ip);
    
    return {
      bot_probability: botProbability,
      device_entropy: deviceEntropy,
      velocity_flags: velocityFlags,
      behavioral_signals: {
        human_interaction_score: Math.random() * 0.5 + 0.5, // Mock: would be real ML model
        session_duration_ms: 120000, // Mock
        page_views_count: 5, // Mock
        mouse_movement_entropy: 0.7 // Mock
      },
      reputation_signals: {
        ip_risk_score: Math.random() * 0.3, // Mock: would be real IP reputation service
        device_risk_score: Math.random() * 0.2,
        merchant_trust_score: 0.9 // Mock: would be based on merchant history
      }
    };
  }

  private calculateDeviceEntropy(deviceSignals: any): number {
    // Calculate entropy based on device uniqueness
    const fingerprint = deviceSignals.device_fingerprint;
    const features = [
      deviceSignals.user_agent,
      deviceSignals.screen_resolution,
      deviceSignals.language,
      deviceSignals.timezone_offset
    ].join('|');
    
    // Simple entropy calculation (in production, use more sophisticated methods)
    const hash = crypto.createHash('sha256').update(features).digest('hex');
    const entropy = parseInt(hash.slice(0, 8), 16) / 0xffffffff;
    
    return entropy;
  }

  private calculateBotProbability(deviceSignals: any): number {
    let botScore = 0;
    
    // Check for bot-like user agents
    const userAgent = deviceSignals.user_agent.toLowerCase();
    if (userAgent.includes('bot') || userAgent.includes('crawler') || userAgent.includes('spider')) {
      botScore += 0.8;
    }
    
    // Check for suspicious screen resolutions
    const resolution = deviceSignals.screen_resolution;
    if (resolution === '0x0' || resolution === '1x1') {
      botScore += 0.5;
    }
    
    // Check for missing referrer (common in automated requests)
    if (!deviceSignals.referrer) {
      botScore += 0.2;
    }
    
    return Math.min(1.0, botScore);
  }

  private async checkVelocityFlags(postback: AttributionPostback, ipAddress: string): Promise<any> {
    // Mock velocity checks (in production, would query real data)
    return {
      rapid_purchases: Math.random() < 0.1,
      ip_velocity_exceeded: Math.random() < 0.05,
      device_velocity_exceeded: Math.random() < 0.03
    };
  }
}

/**
 * Attribution Engine - 6-tier attribution ladder
 */
class AttributionEngine {
  private db: any;

  constructor(database: any) {
    this.db = database;
  }

  async processAttribution(
    postback: AttributionPostback,
    fraudSignals: FraudSignals
  ): Promise<AttributionDecision> {
    
    // Calculate overall risk score
    const riskScore = this.calculateRiskScore(fraudSignals);
    
    // Determine attribution method using 6-tier ladder
    const attributionMethod = await this.determineAttributionMethod(postback);
    
    // Calculate confidence based on method and signals
    const confidence = this.calculateConfidence(attributionMethod, fraudSignals);
    
    // Determine commission and escalation
    const commission = this.calculateCommission(postback, confidence);
    
    // Make processing decision
    const processingDecision = this.makeProcessingDecision(riskScore, confidence);
    
    return {
      attribution_method: attributionMethod,
      confidence,
      fraud_assessment: {
        risk_score: riskScore,
        quarantine_required: processingDecision === 'quarantine',
        manual_review_required: riskScore > 0.7,
        signals_summary: this.summarizeSignals(fraudSignals)
      },
      commission,
      processing_decision: processingDecision,
      reasoning: this.generateReasoning(attributionMethod, riskScore, confidence)
    };
  }

  private async determineAttributionMethod(postback: AttributionPostback): Promise<any> {
    // 6-tier attribution ladder
    if (postback.attribution_context.click_id) {
      return 'affiliate'; // Tier 1: Direct affiliate link
    }
    
    if (postback.device_signals.referrer?.includes('lukhas.ai')) {
      return 's2s'; // Tier 2: Server-to-server tracking
    }
    
    // Check for receipt matching (Tier 3)
    const receiptMatch = await this.checkReceiptMatch(postback);
    if (receiptMatch) {
      return 'receipt';
    }
    
    // Check behavioral signals (Tier 4)
    const behavioralMatch = await this.checkBehavioralMatch(postback);
    if (behavioralMatch) {
      return 'behavioral';
    }
    
    // Last-touch attribution (Tier 5)
    const lastTouch = await this.checkLastTouchAttribution(postback);
    if (lastTouch) {
      return 'last_touch';
    }
    
    // Default attribution (Tier 6)
    return 'default';
  }

  private async checkReceiptMatch(postback: AttributionPostback): Promise<boolean> {
    // Check if user has receipt for similar purchase
    const recentReceipts = await this.db.collection('receipts').find({
      user_id: postback.user_id,
      receipt_type: 'opportunity',
      'campaign.merchant': postback.merchant_id,
      created_at: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
    }).toArray();
    
    return recentReceipts.length > 0;
  }

  private async checkBehavioralMatch(postback: AttributionPostback): Promise<boolean> {
    // Check for behavioral signals (simplified)
    return Math.random() < 0.3; // Mock: would use real ML model
  }

  private async checkLastTouchAttribution(postback: AttributionPostback): Promise<boolean> {
    // Check for any recent interaction
    const recentInteraction = await this.db.collection('interactions').findOne({
      user_id: postback.user_id,
      created_at: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
    });
    
    return !!recentInteraction;
  }

  private calculateRiskScore(fraudSignals: FraudSignals): number {
    let score = 0;
    
    score += fraudSignals.bot_probability * 0.4;
    score += (1 - fraudSignals.device_entropy) * 0.3;
    score += fraudSignals.reputation_signals.ip_risk_score * 0.2;
    score += fraudSignals.reputation_signals.device_risk_score * 0.1;
    
    // Velocity flags
    if (fraudSignals.velocity_flags.rapid_purchases) score += 0.3;
    if (fraudSignals.velocity_flags.ip_velocity_exceeded) score += 0.2;
    if (fraudSignals.velocity_flags.device_velocity_exceeded) score += 0.2;
    
    return Math.min(1.0, score);
  }

  private calculateConfidence(attributionMethod: string, fraudSignals: FraudSignals): number {
    const baseConfidence = {
      'affiliate': 0.95,
      's2s': 0.90,
      'receipt': 0.85,
      'behavioral': 0.70,
      'last_touch': 0.60,
      'default': 0.40
    }[attributionMethod] || 0.40;
    
    // Adjust for fraud signals
    const fraudAdjustment = (1 - fraudSignals.bot_probability) * 0.1;
    const entropyAdjustment = fraudSignals.device_entropy * 0.05;
    
    return Math.min(1.0, baseConfidence + fraudAdjustment + entropyAdjustment);
  }

  private calculateCommission(postback: AttributionPostback, confidence: number): any {
    const baseRate = 0.05; // 5% base commission
    const amount = postback.purchase_data.amount;
    
    // Apply confidence multiplier
    const adjustedRate = baseRate * confidence;
    
    // Determine escalation tier based on performance
    let escalationTier = 'standard';
    if (confidence > 0.9) escalationTier = 'premium';
    if (confidence > 0.95) escalationTier = 'elite';
    
    return {
      rate: adjustedRate,
      amount: amount * adjustedRate,
      currency: postback.purchase_data.currency,
      escalation_tier: escalationTier
    };
  }

  private makeProcessingDecision(riskScore: number, confidence: number): 'approve' | 'quarantine' | 'reject' {
    if (riskScore > 0.8) return 'quarantine';
    if (riskScore > 0.9 || confidence < 0.3) return 'reject';
    return 'approve';
  }

  private summarizeSignals(fraudSignals: FraudSignals): string[] {
    const signals: string[] = [];
    
    if (fraudSignals.bot_probability > 0.5) signals.push('high_bot_probability');
    if (fraudSignals.device_entropy < 0.3) signals.push('low_device_entropy');
    if (fraudSignals.velocity_flags.rapid_purchases) signals.push('velocity_exceeded');
    if (fraudSignals.reputation_signals.ip_risk_score > 0.5) signals.push('ip_reputation_risk');
    
    return signals;
  }

  private generateReasoning(attributionMethod: string, riskScore: number, confidence: number): string {
    return `Attribution via ${attributionMethod} with ${Math.round(confidence * 100)}% confidence. Risk score: ${Math.round(riskScore * 100)}/100.`;
  }
}

export default S2SPostbackSystem;