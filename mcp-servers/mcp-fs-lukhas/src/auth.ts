import { createRemoteJWKSet, jwtVerify } from 'jose';
import { z } from 'zod';

// OAuth Configuration Schema
export const OAuthConfigSchema = z.object({
  provider: z.enum(['auth0', 'keycloak', 'cloudflare']),
  jwksUrl: z.string().url(),
  issuer: z.string(),
  audience: z.string(),
  clientId: z.string().optional(),
  requiredScopes: z.array(z.string()).default(['read:files']),
  cacheTtl: z.number().default(300000) // 5 minutes
});

export type OAuthConfig = z.infer<typeof OAuthConfigSchema>;

// JWT Cache for performance
const jwksCache = new Map<string, any>();
const jwksSets = new Map<string, any>();

export class OAuthValidator {
  private config: OAuthConfig;
  private jwks: any;

  constructor(config: OAuthConfig) {
    this.config = OAuthConfigSchema.parse(config);
    this.jwks = this.getOrCreateJWKS();
  }

  private getOrCreateJWKS() {
    if (!jwksSets.has(this.config.jwksUrl)) {
      const jwks = createRemoteJWKSet(new URL(this.config.jwksUrl));
      jwksSets.set(this.config.jwksUrl, jwks);
    }
    return jwksSets.get(this.config.jwksUrl);
  }

  async validateToken(authHeader: string): Promise<{ valid: boolean; payload?: any; error?: string }> {
    try {
      // Extract Bearer token
      if (!authHeader?.startsWith('Bearer ')) {
        return { valid: false, error: 'Missing or invalid Authorization header' };
      }

      const token = authHeader.slice(7);
      if (!token) {
        return { valid: false, error: 'Empty access token' };
      }

      // Verify JWT with JWKS
      const { payload } = await jwtVerify(token, this.jwks, {
        issuer: this.config.issuer,
        audience: this.config.audience,
      });

      // Validate required scopes
      const tokenScopes = this.extractScopes(payload);
      const hasRequiredScopes = this.config.requiredScopes.every(scope => 
        tokenScopes.includes(scope)
      );

      if (!hasRequiredScopes) {
        return { 
          valid: false, 
          error: `Missing required scopes. Required: ${this.config.requiredScopes.join(', ')}, Found: ${tokenScopes.join(', ')}` 
        };
      }

      return { valid: true, payload };

    } catch (error) {
      return { 
        valid: false, 
        error: `JWT validation failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  private extractScopes(payload: any): string[] {
    // Different providers store scopes differently
    const scopeField = payload.scope || payload.scopes || payload.scp || '';
    
    if (Array.isArray(scopeField)) {
      return scopeField;
    }
    
    if (typeof scopeField === 'string') {
      return scopeField.split(' ').filter(Boolean);
    }
    
    return [];
  }

  static createFromEnv(): OAuthValidator | null {
    const provider = process.env.OAUTH_PROVIDER as 'auth0' | 'keycloak' | 'cloudflare';
    const jwksUrl = process.env.OAUTH_JWKS_URL;
    const issuer = process.env.OAUTH_ISSUER;
    const audience = process.env.OAUTH_AUDIENCE;

    if (!provider || !jwksUrl || !issuer || !audience) {
      console.log('OAuth not configured - running without authentication');
      return null;
    }

    const config: OAuthConfig = {
      provider,
      jwksUrl,
      issuer,
      audience,
      clientId: process.env.OAUTH_CLIENT_ID,
      requiredScopes: process.env.OAUTH_REQUIRED_SCOPES?.split(',') || ['read:files'],
      cacheTtl: parseInt(process.env.OAUTH_CACHE_TTL || '300000'),
    };

    return new OAuthValidator(config);
  }
}

// Provider-specific configuration helpers
export const ProviderConfigs = {
  auth0: (domain: string, audience: string) => ({
    provider: 'auth0' as const,
    jwksUrl: `https://${domain}/.well-known/jwks.json`,
    issuer: `https://${domain}/`,
    audience,
  }),

  keycloak: (realm: string, baseUrl: string, clientId: string) => ({
    provider: 'keycloak' as const,
    jwksUrl: `${baseUrl}/realms/${realm}/protocol/openid-connect/certs`,
    issuer: `${baseUrl}/realms/${realm}`,
    audience: clientId,
  }),

  cloudflare: (accountId: string, applicationAud: string) => ({
    provider: 'cloudflare' as const,
    jwksUrl: `https://${accountId}.cloudflareaccess.com/cdn-cgi/access/certs`,
    issuer: `https://${accountId}.cloudflareaccess.com`,
    audience: applicationAud,
  }),
};

// Middleware for MCP request authentication
export async function authenticateRequest(
  authValidator: OAuthValidator | null,
  authHeader: string | undefined
): Promise<{ authorized: boolean; error?: string; payload?: any }> {
  
  // If no OAuth configured, allow all requests
  if (!authValidator) {
    return { authorized: true };
  }

  if (!authHeader) {
    return { 
      authorized: false, 
      error: 'Authentication required. Please provide a valid Bearer token.' 
    };
  }

  const result = await authValidator.validateToken(authHeader);
  
  return {
    authorized: result.valid,
    error: result.error,
    payload: result.payload,
  };
}
