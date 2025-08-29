/**
 * HMAC Verification Utilities - Production-ready S2S authentication
 * Timing-safe HMAC verification for webhook and API authentication
 */

import crypto from 'crypto';

export interface HMACConfig {
  algorithm?: string;
  encoding?: BufferEncoding;
  timestampToleranceMs?: number;
}

const defaultConfig: Required<HMACConfig> = {
  algorithm: 'sha256',
  encoding: 'hex',
  timestampToleranceMs: 300000 // 5 minutes
};

/**
 * Generate HMAC signature for a payload
 */
export function generateHMAC(
  payload: string | Buffer,
  secret: string,
  config: HMACConfig = {}
): string {
  const opts = { ...defaultConfig, ...config };
  
  const hmac = crypto.createHmac(opts.algorithm, secret);
  hmac.update(payload);
  return hmac.digest(opts.encoding);
}

/**
 * Verify HMAC signature using timing-safe comparison
 */
export function verifyHMAC(
  payload: string | Buffer,
  signature: string,
  secret: string,
  config: HMACConfig = {}
): boolean {
  const opts = { ...defaultConfig, ...config };
  
  try {
    const expectedSignature = generateHMAC(payload, secret, config);
    
    // Timing-safe comparison to prevent timing attacks
    return crypto.timingSafeEqual(
      Buffer.from(expectedSignature, opts.encoding),
      Buffer.from(signature, opts.encoding)
    );
  } catch (error) {
    console.error('HMAC verification error:', error);
    return false;
  }
}

/**
 * Generate timestamped HMAC signature (includes timestamp in payload)
 */
export function generateTimestampedHMAC(
  payload: string | Buffer,
  secret: string,
  timestamp?: number,
  config: HMACConfig = {}
): { signature: string; timestamp: number } {
  const ts = timestamp || Math.floor(Date.now() / 1000);
  const timestampedPayload = `${ts}.${payload}`;
  
  return {
    signature: generateHMAC(timestampedPayload, secret, config),
    timestamp: ts
  };
}

/**
 * Verify timestamped HMAC signature with replay protection
 */
export function verifyTimestampedHMAC(
  payload: string | Buffer,
  signature: string,
  timestamp: number,
  secret: string,
  config: HMACConfig = {}
): { valid: boolean; error?: string } {
  const opts = { ...defaultConfig, ...config };
  const currentTime = Math.floor(Date.now() / 1000);
  
  // Check timestamp tolerance
  const timeDiff = Math.abs(currentTime - timestamp) * 1000;
  if (timeDiff > opts.timestampToleranceMs) {
    return {
      valid: false,
      error: `timestamp_outside_tolerance: ${timeDiff}ms > ${opts.timestampToleranceMs}ms`
    };
  }
  
  // Verify signature
  const timestampedPayload = `${timestamp}.${payload}`;
  const isValid = verifyHMAC(timestampedPayload, signature, secret, config);
  
  return {
    valid: isValid,
    error: isValid ? undefined : 'invalid_signature'
  };
}

/**
 * Express middleware for HMAC verification
 */
export function hmacMiddleware(secretKey: string, config: HMACConfig = {}) {
  return (req: any, res: any, next: any) => {
    const signature = req.headers['x-signature'] || req.headers['x-hub-signature-256'];
    const timestamp = req.headers['x-timestamp'];
    
    if (!signature) {
      return res.status(401).json({
        error: 'missing_signature',
        message: 'X-Signature header required'
      });
    }

    // Remove algorithm prefix if present (e.g., "sha256=abc123")
    const cleanSignature = signature.replace(/^sha256=/, '');
    
    let body: string;
    if (typeof req.body === 'string') {
      body = req.body;
    } else {
      body = JSON.stringify(req.body);
    }

    let isValid: boolean;
    let error: string | undefined;

    if (timestamp) {
      const result = verifyTimestampedHMAC(
        body,
        cleanSignature,
        parseInt(timestamp),
        secretKey,
        config
      );
      isValid = result.valid;
      error = result.error;
    } else {
      isValid = verifyHMAC(body, cleanSignature, secretKey, config);
      error = isValid ? undefined : 'invalid_signature';
    }

    if (!isValid) {
      return res.status(401).json({
        error: 'invalid_signature',
        message: error || 'HMAC signature verification failed'
      });
    }

    // Add verification info to request for logging
    req.hmacVerified = {
      algorithm: config.algorithm || 'sha256',
      timestamp: timestamp ? parseInt(timestamp) : null,
      verifiedAt: new Date().toISOString()
    };

    next();
  };
}

/**
 * Attribution webhook HMAC verification specifically for S2S postbacks
 */
export function verifyAttributionHMAC(
  attributionEvent: any,
  signature: string,
  merchantSecret: string
): boolean {
  // Serialize attribution event in deterministic order
  const payload = JSON.stringify(attributionEvent, Object.keys(attributionEvent).sort());
  return verifyHMAC(payload, signature, merchantSecret);
}

/**
 * Usage examples:
 * 
 * // Basic HMAC verification
 * const isValid = verifyHMAC(requestBody, signature, secret);
 * 
 * // Timestamped verification with replay protection
 * const result = verifyTimestampedHMAC(body, sig, timestamp, secret);
 * if (!result.valid) {
 *   console.error('Verification failed:', result.error);
 * }
 * 
 * // Express middleware usage
 * app.use('/webhook/attribution', hmacMiddleware(process.env.WEBHOOK_SECRET!));
 * app.post('/webhook/attribution', (req, res) => {
 *   // Request body is HMAC verified at this point
 *   console.log('Verified attribution:', req.body);
 *   res.json({ status: 'received' });
 * });
 */

export default {
  generateHMAC,
  verifyHMAC,
  generateTimestampedHMAC,
  verifyTimestampedHMAC,
  hmacMiddleware,
  verifyAttributionHMAC
};