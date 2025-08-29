/**
 * Idempotency Middleware - Drop-in production-ready implementation
 * Prevents duplicate operations on POST requests using Redis caching
 */

import { Request, Response, NextFunction } from 'express';
import { createClient } from 'redis';
import crypto from 'crypto';

interface IdempotencyOptions {
  redisClient?: any;
  ttlSeconds?: number;
  keyPrefix?: string;
  headerName?: string;
  generateKey?: (req: Request) => string;
}

const defaultOptions: Required<IdempotencyOptions> = {
  redisClient: createClient({ url: process.env.REDIS_URL || 'redis://localhost:6379' }),
  ttlSeconds: 3600, // 1 hour
  keyPrefix: 'idem:',
  headerName: 'Idempotency-Key',
  generateKey: (req: Request) => crypto.randomUUID()
};

export function idempotencyMiddleware(options: IdempotencyOptions = {}) {
  const opts = { ...defaultOptions, ...options };
  
  return async (req: Request, res: Response, next: NextFunction) => {
    // Only apply to POST requests
    if (req.method !== 'POST') {
      return next();
    }

    // Get or generate idempotency key
    let key = req.header(opts.headerName);
    if (!key) {
      key = opts.generateKey(req);
      req.headers[opts.headerName.toLowerCase()] = key;
    }

    // Validate key format (should be UUID-like)
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(key)) {
      return res.status(400).json({
        error: 'invalid_idempotency_key',
        message: 'Idempotency key must be a valid UUID'
      });
    }

    const cacheKey = `${opts.keyPrefix}${key}`;

    try {
      // Check for existing response
      const cached = await opts.redisClient.get(cacheKey);
      if (cached) {
        const response = JSON.parse(cached);
        return res.status(response.status).json(response.body);
      }

      // Capture response for caching
      const originalSend = res.send;
      const originalJson = res.json;
      const originalStatus = res.status;
      
      let statusCode = 200;
      let responseBody: any;

      // Override status method to capture status
      res.status = function(code: number) {
        statusCode = code;
        return originalStatus.call(this, code);
      };

      // Override json method to capture body
      res.json = function(body: any) {
        responseBody = body;
        return originalJson.call(this, body);
      };

      // Override send method to capture body
      res.send = function(body: any) {
        if (typeof body === 'object') {
          responseBody = body;
        } else {
          responseBody = { data: body };
        }
        return originalSend.call(this, body);
      };

      // Cache successful responses after they're sent
      res.on('finish', async () => {
        if (statusCode >= 200 && statusCode < 500) {
          const cacheData = {
            status: statusCode,
            body: responseBody,
            timestamp: new Date().toISOString(),
            headers: {
              'x-idempotency-replayed': 'false',
              'x-idempotency-key': key
            }
          };

          try {
            await opts.redisClient.setEx(
              cacheKey,
              opts.ttlSeconds,
              JSON.stringify(cacheData)
            );
          } catch (error) {
            console.error('Failed to cache idempotent response:', error);
          }
        }
      });

      // Add idempotency headers to response
      res.set('X-Idempotency-Key', key);
      res.set('X-Idempotency-Replayed', 'false');

      next();
    } catch (error) {
      console.error('Idempotency middleware error:', error);
      // Don't fail the request if Redis is down
      next();
    }
  };
}

/**
 * Express app integration example:
 * 
 * import express from 'express';
 * import { idempotencyMiddleware } from './middleware/idempotency';
 * 
 * const app = express();
 * app.use(express.json());
 * app.use(idempotencyMiddleware({
 *   ttlSeconds: 3600,
 *   keyPrefix: 'lukhas:idem:'
 * }));
 * 
 * app.post('/merchant/campaigns', async (req, res) => {
 *   // This endpoint is now idempotent
 *   const campaign = await createCampaign(req.body);
 *   res.json(campaign);
 * });
 */

export default idempotencyMiddleware;