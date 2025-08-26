/**
 * JWKS (JSON Web Key Set) Management for ΛiD Authentication System
 *
 * Provides secure RSA key rotation and JWKS endpoint for JWT verification.
 * Implements quarterly key rotation with 30-day overlap for seamless transitions.
 */

import { createHash, randomBytes } from 'crypto';
import { JWK, importPKCS8, importSPKI, exportJWK } from 'jose';

export interface JWKSKey {
  kid: string;
  kty: 'RSA';
  use: 'sig';
  alg: 'RS256';
  n: string;
  e: string;
  created_at: string;
  expires_at: string;
  status: 'active' | 'rotating' | 'deprecated';
}

export interface JWKSConfig {
  privateKey: string;
  publicKey: string;
  keyId: string;
  rotationDays: number;
}

export class JWKSManager {
  private config: JWKSConfig;
  private keys: Map<string, JWKSKey> = new Map();

  constructor(config: JWKSConfig) {
    this.config = config;
  }

  /**
   * Initialize JWKS with current key pair
   */
  async initialize(): Promise<void> {
    try {
      const publicKey = await this.importPublicKey(this.config.publicKey);
      const jwk = await exportJWK(publicKey);

      const key: JWKSKey = {
        kid: this.config.keyId,
        kty: 'RSA',
        use: 'sig',
        alg: 'RS256',
        n: jwk.n!,
        e: jwk.e!,
        created_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + this.config.rotationDays * 24 * 60 * 60 * 1000).toISOString(),
        status: 'active'
      };

      this.keys.set(key.kid, key);
    } catch (error) {
      throw new Error(`Failed to initialize JWKS: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate JWKS response for /.well-known/jwks.json endpoint
   */
  getJWKS(): { keys: Omit<JWKSKey, 'created_at' | 'expires_at' | 'status'>[] } {
    const activeKeys = Array.from(this.keys.values())
      .filter(key => key.status === 'active' || key.status === 'rotating')
      .map(key => ({
        kid: key.kid,
        kty: key.kty,
        use: key.use,
        alg: key.alg,
        n: key.n,
        e: key.e
      }));

    return { keys: activeKeys };
  }

  /**
   * Get key by ID for JWT verification
   */
  getKey(kid: string): JWKSKey | undefined {
    return this.keys.get(kid);
  }

  /**
   * Check if key rotation is needed
   */
  needsRotation(): boolean {
    const activeKey = Array.from(this.keys.values()).find(key => key.status === 'active');
    if (!activeKey) return true;

    const expiryDate = new Date(activeKey.expires_at);
    const now = new Date();
    const daysUntilExpiry = (expiryDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000);

    // Start rotation 30 days before expiry
    return daysUntilExpiry <= 30;
  }

  /**
   * Rotate keys (mark current as rotating, add new active key)
   */
  async rotateKeys(newPrivateKey: string, newPublicKey: string): Promise<string> {
    try {
      // Mark current active key as rotating
      Array.from(this.keys.values())
        .filter(key => key.status === 'active')
        .forEach(key => {
          key.status = 'rotating';
        });

      // Generate new key ID
      const newKeyId = this.generateKeyId();

      // Import and add new key
      const publicKey = await this.importPublicKey(newPublicKey);
      const jwk = await exportJWK(publicKey);

      const newKey: JWKSKey = {
        kid: newKeyId,
        kty: 'RSA',
        use: 'sig',
        alg: 'RS256',
        n: jwk.n!,
        e: jwk.e!,
        created_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + this.config.rotationDays * 24 * 60 * 60 * 1000).toISOString(),
        status: 'active'
      };

      this.keys.set(newKey.kid, newKey);

      // Schedule cleanup of deprecated keys after 30 days
      setTimeout(() => {
        this.cleanupDeprecatedKeys();
      }, 30 * 24 * 60 * 60 * 1000);

      return newKeyId;
    } catch (error) {
      throw new Error(`Failed to rotate keys: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Remove deprecated keys that are older than 30 days
   */
  private cleanupDeprecatedKeys(): void {
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

    Array.from(this.keys.entries()).forEach(([kid, key]) => {
      if (key.status === 'rotating' && new Date(key.created_at) < thirtyDaysAgo) {
        key.status = 'deprecated';
        // In production, you might want to move these to a backup storage
        // this.keys.delete(kid);
      }
    });
  }

  /**
   * Generate a unique key ID
   */
  private generateKeyId(): string {
    const timestamp = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    const random = randomBytes(4).toString('hex');
    return `lukhas-auth-${timestamp}-${random}`;
  }

  /**
   * Import a base64-encoded public key
   */
  private async importPublicKey(base64Key: string): Promise<CryptoKey> {
    try {
      const pemKey = Buffer.from(base64Key, 'base64').toString('utf8');
      return await importSPKI(pemKey, 'RS256');
    } catch (error) {
      throw new Error(`Invalid public key format: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Import a base64-encoded private key
   */
  private async importPrivateKey(base64Key: string): Promise<CryptoKey> {
    try {
      const pemKey = Buffer.from(base64Key, 'base64').toString('utf8');
      return await importPKCS8(pemKey, 'RS256');
    } catch (error) {
      throw new Error(`Invalid private key format: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Validate JWKS configuration
   */
  static validateConfig(config: JWKSConfig): void {
    if (!config.privateKey || !config.publicKey) {
      throw new Error('Private and public keys are required');
    }

    if (!config.keyId || config.keyId.length < 8) {
      throw new Error('Key ID must be at least 8 characters long');
    }

    if (config.rotationDays < 30 || config.rotationDays > 365) {
      throw new Error('Rotation period must be between 30 and 365 days');
    }
  }

  /**
   * Generate a new RSA key pair for rotation
   */
  static async generateKeyPair(): Promise<{ privateKey: string; publicKey: string }> {
    try {
      // This would typically be done server-side with OpenSSL or Node.js crypto
      // For security, key generation should not happen in the browser
      throw new Error('Key generation must be performed server-side');
    } catch (error) {
      throw new Error(`Key generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

/**
 * Key rotation utility for server-side use
 */
export class KeyRotationManager {
  private jwksManager: JWKSManager;
  private rotationInterval?: NodeJS.Timer;

  constructor(jwksManager: JWKSManager) {
    this.jwksManager = jwksManager;
  }

  /**
   * Start automatic key rotation monitoring
   */
  startRotationMonitoring(checkIntervalHours: number = 24): void {
    this.rotationInterval = setInterval(async () => {
      try {
        if (this.jwksManager.needsRotation()) {
          console.log('🔄 Key rotation needed, triggering rotation...');
          await this.performRotation();
        }
      } catch (error) {
        console.error('❌ Key rotation check failed:', error);
      }
    }, checkIntervalHours * 60 * 60 * 1000);

    console.log(`🔐 Key rotation monitoring started (checking every ${checkIntervalHours} hours)`);
  }

  /**
   * Stop automatic key rotation monitoring
   */
  stopRotationMonitoring(): void {
    if (this.rotationInterval) {
      clearInterval(this.rotationInterval);
      this.rotationInterval = undefined;
      console.log('🛑 Key rotation monitoring stopped');
    }
  }

  /**
   * Perform key rotation (should be implemented with your key generation service)
   */
  private async performRotation(): Promise<void> {
    throw new Error('Key rotation must be implemented with your key generation service');
  }
}

export default JWKSManager;
