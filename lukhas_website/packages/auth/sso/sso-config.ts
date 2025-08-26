/**
 * SSO Configuration Management
 * Multi-tenant SSO configuration for LUKHAS AI ΛiD System
 *
 * Supports:
 * - Multi-tenant configuration storage
 * - SAML and OIDC provider configuration
 * - Metadata endpoints for integration
 * - Configuration validation and testing
 */

import { SAMLConfig, SAMLProvider, SAMLProviderFactory } from './saml-provider';
import { OIDCConfig, OIDCProvider, OIDCProviderFactory, OIDCEndpoints, discoverOIDCEndpoints } from './oidc-provider';
import { AuditLogger } from '../audit-logger';
import { SecurityFeatures } from '../security-features';

export interface TenantConfig {
  tenantId: string;
  name: string;
  domain: string;
  isActive: boolean;
  ssoRequired: boolean;
  scimRequired: boolean;
  providerType: 'saml' | 'oidc';
  providerConfig: SAMLConfig | OIDCConfig;
  groupMapping?: GroupMappingRule[];
  createdAt: Date;
  updatedAt: Date;
}

export interface GroupMappingRule {
  id: string;
  groupPattern: string; // Regex pattern to match group names
  roleName: string;
  priority: number; // Higher priority = checked first
  isActive: boolean;
}

export interface SSOMetadata {
  entityId?: string;
  ssoUrl?: string;
  sloUrl?: string;
  certificate?: string;
  metadataXml?: string;

  // OIDC metadata
  issuer?: string;
  authorizationEndpoint?: string;
  tokenEndpoint?: string;
  userinfoEndpoint?: string;
  jwksUri?: string;
  endSessionEndpoint?: string;
}

export interface ProviderTestResult {
  success: boolean;
  message: string;
  details?: any;
  timestamp: Date;
}

export class SSOConfigManager {
  private tenantConfigs = new Map<string, TenantConfig>();
  private auditLogger: AuditLogger;
  private security: SecurityFeatures;

  constructor(auditLogger: AuditLogger) {
    this.auditLogger = auditLogger;
    this.security = new SecurityFeatures();
  }

  /**
   * Create or update tenant SSO configuration
   */
  async setTenantConfig(config: Omit<TenantConfig, 'createdAt' | 'updatedAt'>): Promise<void> {
    try {
      // Validate configuration
      await this.validateTenantConfig(config);

      const now = new Date();
      const existingConfig = this.tenantConfigs.get(config.tenantId);

      const tenantConfig: TenantConfig = {
        ...config,
        createdAt: existingConfig?.createdAt || now,
        updatedAt: now
      };

      this.tenantConfigs.set(config.tenantId, tenantConfig);

      await this.auditLogger.logSecurityEvent('sso_tenant_config_updated', {
        tenantId: config.tenantId,
        name: config.name,
        domain: config.domain,
        providerType: config.providerType,
        ssoRequired: config.ssoRequired,
        scimRequired: config.scimRequired,
        isActive: config.isActive,
        groupMappingCount: config.groupMapping?.length || 0
      });

    } catch (error) {
      await this.auditLogger.logSecurityEvent('sso_tenant_config_failed', {
        tenantId: config.tenantId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Get tenant configuration by ID
   */
  getTenantConfig(tenantId: string): TenantConfig | null {
    return this.tenantConfigs.get(tenantId) || null;
  }

  /**
   * Get tenant configuration by domain
   */
  getTenantConfigByDomain(domain: string): TenantConfig | null {
    for (const config of this.tenantConfigs.values()) {
      if (config.domain === domain || config.domain === `*.${domain}`) {
        return config;
      }
    }
    return null;
  }

  /**
   * Get all tenant configurations
   */
  getAllTenantConfigs(): TenantConfig[] {
    return Array.from(this.tenantConfigs.values());
  }

  /**
   * Delete tenant configuration
   */
  async deleteTenantConfig(tenantId: string): Promise<boolean> {
    const config = this.tenantConfigs.get(tenantId);
    if (!config) {
      return false;
    }

    this.tenantConfigs.delete(tenantId);

    await this.auditLogger.logSecurityEvent('sso_tenant_config_deleted', {
      tenantId,
      name: config.name,
      domain: config.domain
    });

    return true;
  }

  /**
   * Create SSO provider instance for tenant
   */
  async createProvider(tenantId: string): Promise<SAMLProvider | OIDCProvider> {
    const config = this.getTenantConfig(tenantId);
    if (!config) {
      throw new Error(`Tenant configuration not found: ${tenantId}`);
    }

    if (!config.isActive) {
      throw new Error(`Tenant is not active: ${tenantId}`);
    }

    if (config.providerType === 'saml') {
      const samlConfig = config.providerConfig as SAMLConfig;
      return new SAMLProvider(samlConfig, this.auditLogger);
    } else {
      const oidcConfig = config.providerConfig as OIDCConfig;

      // Discover endpoints if not provided
      let endpoints: OIDCEndpoints;
      if ('endpoints' in oidcConfig) {
        endpoints = (oidcConfig as any).endpoints;
      } else {
        endpoints = await discoverOIDCEndpoints(oidcConfig.issuer);
      }

      return new OIDCProvider(oidcConfig, endpoints, this.auditLogger);
    }
  }

  /**
   * Generate SAML metadata for tenant
   */
  async generateSAMLMetadata(tenantId: string): Promise<string> {
    const config = this.getTenantConfig(tenantId);
    if (!config) {
      throw new Error(`Tenant configuration not found: ${tenantId}`);
    }

    if (config.providerType !== 'saml') {
      throw new Error(`Tenant is not configured for SAML: ${tenantId}`);
    }

    const provider = await this.createProvider(tenantId) as SAMLProvider;
    return provider.generateMetadata();
  }

  /**
   * Get SSO metadata for tenant
   */
  async getSSOMetadata(tenantId: string): Promise<SSOMetadata> {
    const config = this.getTenantConfig(tenantId);
    if (!config) {
      throw new Error(`Tenant configuration not found: ${tenantId}`);
    }

    if (config.providerType === 'saml') {
      const samlConfig = config.providerConfig as SAMLConfig;
      return {
        entityId: samlConfig.entityId,
        ssoUrl: samlConfig.ssoUrl,
        sloUrl: samlConfig.sloUrl,
        certificate: samlConfig.certificate,
        metadataXml: await this.generateSAMLMetadata(tenantId)
      };
    } else {
      const oidcConfig = config.providerConfig as OIDCConfig;
      const endpoints = await discoverOIDCEndpoints(oidcConfig.issuer);

      return {
        issuer: oidcConfig.issuer,
        authorizationEndpoint: endpoints.authorization,
        tokenEndpoint: endpoints.token,
        userinfoEndpoint: endpoints.userinfo,
        jwksUri: endpoints.jwks,
        endSessionEndpoint: endpoints.endSession
      };
    }
  }

  /**
   * Test SSO provider configuration
   */
  async testProviderConfig(tenantId: string): Promise<ProviderTestResult> {
    try {
      const config = this.getTenantConfig(tenantId);
      if (!config) {
        return {
          success: false,
          message: 'Tenant configuration not found',
          timestamp: new Date()
        };
      }

      if (config.providerType === 'saml') {
        return await this.testSAMLConfig(config.providerConfig as SAMLConfig);
      } else {
        return await this.testOIDCConfig(config.providerConfig as OIDCConfig);
      }

    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date()
      };
    }
  }

  /**
   * Import tenant configuration from metadata
   */
  async importFromMetadata(
    tenantId: string,
    name: string,
    domain: string,
    metadataUrl: string,
    providerType: 'saml' | 'oidc'
  ): Promise<TenantConfig> {
    try {
      const response = await fetch(metadataUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch metadata: ${response.status}`);
      }

      let providerConfig: SAMLConfig | OIDCConfig;

      if (providerType === 'saml') {
        const metadataXml = await response.text();
        providerConfig = await this.parseSAMLMetadata(metadataXml);
      } else {
        const discoveryDoc = await response.json();
        providerConfig = await this.parseOIDCDiscovery(discoveryDoc);
      }

      const tenantConfig: Omit<TenantConfig, 'createdAt' | 'updatedAt'> = {
        tenantId,
        name,
        domain,
        isActive: true,
        ssoRequired: false,
        scimRequired: false,
        providerType,
        providerConfig
      };

      await this.setTenantConfig(tenantConfig);

      await this.auditLogger.logSecurityEvent('sso_config_imported', {
        tenantId,
        metadataUrl,
        providerType
      });

      return this.getTenantConfig(tenantId)!;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('sso_config_import_failed', {
        tenantId,
        metadataUrl,
        providerType,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Add or update group mapping rule
   */
  async setGroupMappingRule(tenantId: string, rule: GroupMappingRule): Promise<void> {
    const config = this.getTenantConfig(tenantId);
    if (!config) {
      throw new Error(`Tenant configuration not found: ${tenantId}`);
    }

    const groupMapping = config.groupMapping || [];
    const existingIndex = groupMapping.findIndex(r => r.id === rule.id);

    if (existingIndex >= 0) {
      groupMapping[existingIndex] = rule;
    } else {
      groupMapping.push(rule);
    }

    // Sort by priority (higher first)
    groupMapping.sort((a, b) => b.priority - a.priority);

    await this.setTenantConfig({
      ...config,
      groupMapping
    });
  }

  /**
   * Delete group mapping rule
   */
  async deleteGroupMappingRule(tenantId: string, ruleId: string): Promise<boolean> {
    const config = this.getTenantConfig(tenantId);
    if (!config || !config.groupMapping) {
      return false;
    }

    const initialLength = config.groupMapping.length;
    config.groupMapping = config.groupMapping.filter(r => r.id !== ruleId);

    if (config.groupMapping.length < initialLength) {
      await this.setTenantConfig(config);
      return true;
    }

    return false;
  }

  private async validateTenantConfig(config: Omit<TenantConfig, 'createdAt' | 'updatedAt'>): Promise<void> {
    if (!config.tenantId) {
      throw new Error('Tenant ID is required');
    }

    if (!config.name) {
      throw new Error('Tenant name is required');
    }

    if (!config.domain) {
      throw new Error('Tenant domain is required');
    }

    if (!config.providerConfig) {
      throw new Error('Provider configuration is required');
    }

    // Validate provider-specific configuration
    if (config.providerType === 'saml') {
      await this.validateSAMLConfig(config.providerConfig as SAMLConfig);
    } else {
      await this.validateOIDCConfig(config.providerConfig as OIDCConfig);
    }

    // Validate group mapping rules
    if (config.groupMapping) {
      for (const rule of config.groupMapping) {
        try {
          new RegExp(rule.groupPattern);
        } catch (error) {
          throw new Error(`Invalid group pattern in rule ${rule.id}: ${rule.groupPattern}`);
        }
      }
    }
  }

  private async validateSAMLConfig(config: SAMLConfig): Promise<void> {
    if (!config.entityId) {
      throw new Error('SAML Entity ID is required');
    }

    if (!config.ssoUrl) {
      throw new Error('SAML SSO URL is required');
    }

    if (!config.assertionConsumerServiceUrl) {
      throw new Error('SAML Assertion Consumer Service URL is required');
    }

    if (!config.certificate) {
      throw new Error('SAML Certificate is required');
    }

    // Validate URLs
    try {
      new URL(config.ssoUrl);
      new URL(config.assertionConsumerServiceUrl);
      if (config.sloUrl) {
        new URL(config.sloUrl);
      }
    } catch (error) {
      throw new Error('Invalid URL in SAML configuration');
    }
  }

  private async validateOIDCConfig(config: OIDCConfig): Promise<void> {
    if (!config.issuer) {
      throw new Error('OIDC Issuer is required');
    }

    if (!config.clientId) {
      throw new Error('OIDC Client ID is required');
    }

    if (!config.redirectUri) {
      throw new Error('OIDC Redirect URI is required');
    }

    if (!config.scopes || config.scopes.length === 0) {
      throw new Error('OIDC Scopes are required');
    }

    // Validate URLs
    try {
      new URL(config.issuer);
      new URL(config.redirectUri);
    } catch (error) {
      throw new Error('Invalid URL in OIDC configuration');
    }

    // Validate required scopes
    if (!config.scopes.includes('openid')) {
      throw new Error('OIDC configuration must include "openid" scope');
    }
  }

  private async testSAMLConfig(config: SAMLConfig): Promise<ProviderTestResult> {
    try {
      // Test SSO URL accessibility
      const response = await fetch(config.ssoUrl, { method: 'HEAD' });

      return {
        success: response.ok,
        message: response.ok ? 'SAML provider accessible' : `SAML provider returned ${response.status}`,
        details: {
          ssoUrl: config.ssoUrl,
          status: response.status
        },
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        message: `SAML provider test failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
    }
  }

  private async testOIDCConfig(config: OIDCConfig): Promise<ProviderTestResult> {
    try {
      // Test discovery endpoint
      const discoveryUrl = `${config.issuer}/.well-known/openid_configuration`;
      const response = await fetch(discoveryUrl);

      if (!response.ok) {
        return {
          success: false,
          message: `OIDC discovery failed: ${response.status}`,
          details: { discoveryUrl, status: response.status },
          timestamp: new Date()
        };
      }

      const discoveryDoc = await response.json();

      return {
        success: true,
        message: 'OIDC provider accessible and valid',
        details: {
          discoveryUrl,
          authorizationEndpoint: discoveryDoc.authorization_endpoint,
          tokenEndpoint: discoveryDoc.token_endpoint,
          userinfoEndpoint: discoveryDoc.userinfo_endpoint
        },
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        message: `OIDC provider test failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
    }
  }

  private async parseSAMLMetadata(metadataXml: string): Promise<SAMLConfig> {
    // Basic SAML metadata parsing - in production, use a proper SAML library
    throw new Error('SAML metadata parsing not implemented - use manual configuration');
  }

  private async parseOIDCDiscovery(discoveryDoc: any): Promise<OIDCConfig> {
    return {
      issuer: discoveryDoc.issuer,
      clientId: '', // Must be provided manually
      redirectUri: '', // Must be provided manually
      scopes: ['openid', 'profile', 'email']
    };
  }
}

/**
 * Global SSO configuration manager instance
 */
export const ssoConfigManager = new SSOConfigManager(new AuditLogger());

/**
 * Middleware to detect tenant from request
 */
export function detectTenant(request: Request): string | null {
  // Try to extract tenant from subdomain
  const host = request.headers.get('host');
  if (host) {
    const subdomain = host.split('.')[0];
    if (subdomain && subdomain !== 'www') {
      return subdomain;
    }
  }

  // Try to extract from custom header
  const tenantHeader = request.headers.get('x-tenant-id');
  if (tenantHeader) {
    return tenantHeader;
  }

  // Try to extract from query parameter
  const url = new URL(request.url);
  const tenantParam = url.searchParams.get('tenant');
  if (tenantParam) {
    return tenantParam;
  }

  return null;
}
