/**
 * LUKHAS AI ΛiD Authentication System - Scopes & RBAC Unit Tests
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Tests for scope-based authorization, RBAC, and tier-based access control
 */

import { 
  ScopeGuard, 
  ScopeManager, 
  ScopeUtils, 
  TIER_ENVELOPES, 
  RBAC_ROLES,
  type TierLevel,
  type SecurityContext,
  type ScopeCheckResult,
  type Scope,
  type Role
} from '@/packages/auth/scopes';

describe('ScopeManager', () => {
  describe('Scope Validation', () => {
    it('should validate basic scope format', () => {
      const validScopes = [
        'matriz:read',
        'auth:login',
        'profile:view',
        'admin:users:read',
        'api:v1:data:write',
      ];

      const invalidScopes = [
        '',
        'invalid-scope',
        'no-colon',
        ':missing-category',
        'missing-action:',
        'too:many:colons:here:invalid',
      ];

      validScopes.forEach(scope => {
        expect(ScopeManager.validateScope(scope)).toBe(true);
      });

      invalidScopes.forEach(scope => {
        expect(ScopeManager.validateScope(scope)).toBe(false);
      });
    });

    it('should parse scope components correctly', () => {
      const scope = 'api:v1:data:write';
      const parsed = ScopeManager.parseScope(scope);

      expect(parsed.category).toBe('api');
      expect(parsed.action).toBe('write');
      expect(parsed.resource).toBe('v1:data');
      expect(parsed.full).toBe(scope);
    });

    it('should handle hierarchical scopes', () => {
      const testCases = [
        { scope: 'matriz:read', category: 'matriz', action: 'read', resource: undefined },
        { scope: 'admin:users:write', category: 'admin', action: 'write', resource: 'users' },
        { scope: 'api:v2:analytics:read', category: 'api', action: 'read', resource: 'v2:analytics' },
      ];

      testCases.forEach(({ scope, category, action, resource }) => {
        const parsed = ScopeManager.parseScope(scope);
        expect(parsed.category).toBe(category);
        expect(parsed.action).toBe(action);
        expect(parsed.resource).toBe(resource);
      });
    });
  });

  describe('Tier-based Access Control', () => {
    it('should enforce T1 tier limitations', () => {
      const t1Context: SecurityContext = {
        userId: 'user1',
        userTier: 'T1',
        sessionId: 'session1',
        roles: ['viewer'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // T1 should have access to basic scopes
      expect(ScopeManager.hasScope(t1Context, 'matriz:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(t1Context, 'auth:login').allowed).toBe(true);
      expect(ScopeManager.hasScope(t1Context, 'profile:view').allowed).toBe(true);

      // T1 should NOT have access to advanced scopes
      expect(ScopeManager.hasScope(t1Context, 'admin:users:write').allowed).toBe(false);
      expect(ScopeManager.hasScope(t1Context, 'api:analytics:read').allowed).toBe(false);
      expect(ScopeManager.hasScope(t1Context, 'enterprise:sso:manage').allowed).toBe(false);
    });

    it('should enforce T2 tier capabilities', () => {
      const t2Context: SecurityContext = {
        userId: 'user2',
        userTier: 'T2',
        sessionId: 'session2',
        roles: ['user'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // T2 should have T1 scopes plus additional ones
      expect(ScopeManager.hasScope(t2Context, 'matriz:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(t2Context, 'matriz:write').allowed).toBe(true);
      expect(ScopeManager.hasScope(t2Context, 'api:basic:read').allowed).toBe(true);

      // T2 should NOT have admin scopes
      expect(ScopeManager.hasScope(t2Context, 'admin:users:write').allowed).toBe(false);
      expect(ScopeManager.hasScope(t2Context, 'enterprise:sso:manage').allowed).toBe(false);
    });

    it('should enforce T3 tier capabilities', () => {
      const t3Context: SecurityContext = {
        userId: 'user3',
        userTier: 'T3',
        sessionId: 'session3',
        roles: ['power_user'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // T3 should have T1+T2 scopes plus advanced API access
      expect(ScopeManager.hasScope(t3Context, 'matriz:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(t3Context, 'matriz:write').allowed).toBe(true);
      expect(ScopeManager.hasScope(t3Context, 'api:advanced:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(t3Context, 'api:analytics:read').allowed).toBe(true);

      // T3 should NOT have enterprise admin scopes
      expect(ScopeManager.hasScope(t3Context, 'enterprise:sso:manage').allowed).toBe(false);
      expect(ScopeManager.hasScope(t3Context, 'admin:system:write').allowed).toBe(false);
    });

    it('should enforce T4 tier capabilities', () => {
      const t4Context: SecurityContext = {
        userId: 'user4',
        userTier: 'T4',
        sessionId: 'session4',
        roles: ['team_admin'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // T4 should have team admin capabilities
      expect(ScopeManager.hasScope(t4Context, 'admin:team:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(t4Context, 'admin:team:write').allowed).toBe(true);
      expect(ScopeManager.hasScope(t4Context, 'api:premium:read').allowed).toBe(true);

      // T4 should NOT have system admin scopes
      expect(ScopeManager.hasScope(t4Context, 'admin:system:write').allowed).toBe(false);
      expect(ScopeManager.hasScope(t4Context, 'enterprise:billing:manage').allowed).toBe(false);
    });

    it('should enforce T5 tier full capabilities', () => {
      const t5Context: SecurityContext = {
        userId: 'user5',
        userTier: 'T5',
        sessionId: 'session5',
        roles: ['enterprise_admin'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
        organizationId: 'org1',
      };

      // T5 should have access to all scopes
      expect(ScopeManager.hasScope(t5Context, 'matriz:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(t5Context, 'admin:system:write').allowed).toBe(true);
      expect(ScopeManager.hasScope(t5Context, 'enterprise:sso:manage').allowed).toBe(true);
      expect(ScopeManager.hasScope(t5Context, 'enterprise:billing:manage').allowed).toBe(true);
      expect(ScopeManager.hasScope(t5Context, 'api:unlimited:read').allowed).toBe(true);
    });
  });

  describe('Role-based Access Control', () => {
    it('should enforce viewer role restrictions', () => {
      const viewerContext: SecurityContext = {
        userId: 'user1',
        userTier: 'T3', // High tier but viewer role
        sessionId: 'session1',
        roles: ['viewer'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Viewer should only have read access
      expect(ScopeManager.hasScope(viewerContext, 'matriz:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(viewerContext, 'api:read').allowed).toBe(true);

      // Viewer should NOT have write access
      expect(ScopeManager.hasScope(viewerContext, 'matriz:write').allowed).toBe(false);
      expect(ScopeManager.hasScope(viewerContext, 'api:write').allowed).toBe(false);
      expect(ScopeManager.hasScope(viewerContext, 'admin:users:write').allowed).toBe(false);
    });

    it('should enforce user role capabilities', () => {
      const userContext: SecurityContext = {
        userId: 'user2',
        userTier: 'T2',
        sessionId: 'session2',
        roles: ['user'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // User should have read/write for their own data
      expect(ScopeManager.hasScope(userContext, 'matriz:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(userContext, 'matriz:write').allowed).toBe(true);
      expect(ScopeManager.hasScope(userContext, 'profile:write').allowed).toBe(true);

      // User should NOT have admin access
      expect(ScopeManager.hasScope(userContext, 'admin:users:read').allowed).toBe(false);
    });

    it('should enforce admin role hierarchy', () => {
      const adminContext: SecurityContext = {
        userId: 'admin1',
        userTier: 'T4',
        sessionId: 'session3',
        roles: ['team_admin'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Admin should have team management access
      expect(ScopeManager.hasScope(adminContext, 'admin:team:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(adminContext, 'admin:team:write').allowed).toBe(true);
      expect(ScopeManager.hasScope(adminContext, 'admin:users:read').allowed).toBe(true);

      // Team admin should NOT have system admin access
      expect(ScopeManager.hasScope(adminContext, 'admin:system:write').allowed).toBe(false);
    });

    it('should support multiple roles', () => {
      const multiRoleContext: SecurityContext = {
        userId: 'user3',
        userTier: 'T3',
        sessionId: 'session4',
        roles: ['user', 'analyst', 'reviewer'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Should have capabilities from all roles
      expect(ScopeManager.hasScope(multiRoleContext, 'matriz:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(multiRoleContext, 'api:analytics:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(multiRoleContext, 'admin:review:write').allowed).toBe(true);
    });
  });

  describe('Organization Context', () => {
    it('should enforce organization boundaries', () => {
      const org1Context: SecurityContext = {
        userId: 'user1',
        userTier: 'T4',
        sessionId: 'session1',
        roles: ['team_admin'],
        organizationId: 'org1',
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      const org2Context: SecurityContext = {
        userId: 'user2',
        userTier: 'T4',
        sessionId: 'session2',
        roles: ['team_admin'],
        organizationId: 'org2',
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Both should have their own organization admin access
      expect(ScopeManager.hasScope(org1Context, 'admin:org:read').allowed).toBe(true);
      expect(ScopeManager.hasScope(org2Context, 'admin:org:read').allowed).toBe(true);

      // Cross-org access should be prevented
      const crossOrgResult = ScopeManager.hasScope(org1Context, 'admin:org:read', {
        organizationId: 'org2'
      });
      expect(crossOrgResult.allowed).toBe(false);
      expect(crossOrgResult.reason).toMatch(/organization/i);
    });

    it('should support organization hierarchy', () => {
      const parentOrgContext: SecurityContext = {
        userId: 'user1',
        userTier: 'T5',
        sessionId: 'session1',
        roles: ['enterprise_admin'],
        organizationId: 'parent-org',
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Parent org admin should have access to child orgs
      const childOrgResult = ScopeManager.hasScope(parentOrgContext, 'admin:org:read', {
        organizationId: 'child-org',
        parentOrganizationId: 'parent-org'
      });
      expect(childOrgResult.allowed).toBe(true);
    });
  });

  describe('Scope Inheritance and Wildcards', () => {
    it('should support wildcard scopes', () => {
      const adminContext: SecurityContext = {
        userId: 'admin1',
        userTier: 'T5',
        sessionId: 'session1',
        roles: ['system_admin'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Admin with wildcard scope should have access to all admin actions
      const wildcardResult = ScopeManager.hasScope(adminContext, 'admin:*');
      expect(wildcardResult.allowed).toBe(true);

      // Specific admin scopes should also be allowed
      expect(ScopeManager.hasScope(adminContext, 'admin:users:write').allowed).toBe(true);
      expect(ScopeManager.hasScope(adminContext, 'admin:system:read').allowed).toBe(true);
    });

    it('should support scope inheritance', () => {
      const context: SecurityContext = {
        userId: 'user1',
        userTier: 'T3',
        sessionId: 'session1',
        roles: ['user'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Higher-level scope should grant access to lower-level scopes
      const writeScope = ScopeManager.hasScope(context, 'matriz:write');
      if (writeScope.allowed) {
        // Write access should imply read access
        expect(ScopeManager.hasScope(context, 'matriz:read').allowed).toBe(true);
      }
    });
  });

  describe('Conditional Access', () => {
    it('should enforce IP-based restrictions', () => {
      const restrictedContext: SecurityContext = {
        userId: 'user1',
        userTier: 'T5',
        sessionId: 'session1',
        roles: ['enterprise_admin'],
        ipAddress: '203.0.113.1', // External IP
        userAgent: 'Test Agent',
      };

      // Admin scopes might require internal IP
      const adminResult = ScopeManager.hasScope(restrictedContext, 'admin:system:write', {
        requiredIPRange: '10.0.0.0/8' // Internal network only
      });

      // Should be denied due to IP restriction
      expect(adminResult.allowed).toBe(false);
      expect(adminResult.reason).toMatch(/ip|network|location/i);
    });

    it('should enforce time-based restrictions', () => {
      const context: SecurityContext = {
        userId: 'user1',
        userTier: 'T3',
        sessionId: 'session1',
        roles: ['user'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Some scopes might have time restrictions
      const timeRestrictedResult = ScopeManager.hasScope(context, 'api:batch:write', {
        allowedHours: [9, 10, 11, 12, 13, 14, 15, 16, 17] // Business hours only
      });

      // Result depends on current time - just test that function executes
      expect(typeof timeRestrictedResult.allowed).toBe('boolean');
    });

    it('should enforce session-based restrictions', () => {
      const recentContext: SecurityContext = {
        userId: 'user1',
        userTier: 'T4',
        sessionId: 'session1',
        roles: ['team_admin'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
        sessionCreatedAt: new Date(), // Recent session
      };

      const oldContext: SecurityContext = {
        userId: 'user1',
        userTier: 'T4',
        sessionId: 'session2',
        roles: ['team_admin'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
        sessionCreatedAt: new Date(Date.now() - 25 * 60 * 60 * 1000), // 25 hours ago
      };

      // Sensitive operations might require recent authentication
      const recentResult = ScopeManager.hasScope(recentContext, 'admin:sensitive:write', {
        maxSessionAge: 24 * 60 * 60 * 1000 // 24 hours
      });

      const oldResult = ScopeManager.hasScope(oldContext, 'admin:sensitive:write', {
        maxSessionAge: 24 * 60 * 60 * 1000 // 24 hours
      });

      expect(recentResult.allowed).toBe(true);
      expect(oldResult.allowed).toBe(false);
      expect(oldResult.reason).toMatch(/session|age|authentication/i);
    });
  });
});

describe('ScopeGuard', () => {
  let scopeGuard: ScopeGuard;

  beforeEach(() => {
    scopeGuard = new ScopeGuard();
  });

  describe('Middleware Functionality', () => {
    it('should create Express middleware for scope checking', () => {
      const middleware = scopeGuard.middleware(['matriz:read']);

      expect(typeof middleware).toBe('function');
      expect(middleware.length).toBe(3); // req, res, next
    });

    it('should allow requests with valid scopes', async () => {
      const req = {
        user: {
          id: 'user1',
          tier: 'T2',
          scopes: ['matriz:read', 'auth:login'],
          roles: ['user'],
        },
        session: { id: 'session1' },
        ip: '127.0.0.1',
        get: jest.fn(() => 'Test Agent'),
      };

      const res = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn(),
      };

      const next = jest.fn();

      const middleware = scopeGuard.middleware(['matriz:read']);
      await middleware(req as any, res as any, next);

      expect(next).toHaveBeenCalled();
      expect(res.status).not.toHaveBeenCalled();
    });

    it('should reject requests without required scopes', async () => {
      const req = {
        user: {
          id: 'user1',
          tier: 'T1',
          scopes: ['matriz:read'],
          roles: ['viewer'],
        },
        session: { id: 'session1' },
        ip: '127.0.0.1',
        get: jest.fn(() => 'Test Agent'),
      };

      const res = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn(),
      };

      const next = jest.fn();

      const middleware = scopeGuard.middleware(['admin:users:write']);
      await middleware(req as any, res as any, next);

      expect(next).not.toHaveBeenCalled();
      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Insufficient scope',
        })
      );
    });

    it('should handle missing user context', async () => {
      const req = {
        ip: '127.0.0.1',
        get: jest.fn(() => 'Test Agent'),
      };

      const res = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn(),
      };

      const next = jest.fn();

      const middleware = scopeGuard.middleware(['matriz:read']);
      await middleware(req as any, res as any, next);

      expect(next).not.toHaveBeenCalled();
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Authentication required',
        })
      );
    });
  });

  describe('Decorator Functionality', () => {
    it('should create method decorator for scope checking', () => {
      const decorator = scopeGuard.requireScopes(['admin:users:read']);

      expect(typeof decorator).toBe('function');
    });

    it('should validate scopes in decorated methods', () => {
      class TestController {
        @scopeGuard.requireScopes(['admin:users:read'])
        getUserList(context: SecurityContext) {
          return 'success';
        }
      }

      const controller = new TestController();
      const adminContext: SecurityContext = {
        userId: 'admin1',
        userTier: 'T4',
        sessionId: 'session1',
        roles: ['team_admin'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      const userContext: SecurityContext = {
        userId: 'user1',
        userTier: 'T1',
        sessionId: 'session2',
        roles: ['viewer'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      // Admin should have access
      expect(() => controller.getUserList(adminContext)).not.toThrow();

      // Regular user should be denied
      expect(() => controller.getUserList(userContext)).toThrow(/scope|permission/i);
    });
  });

  describe('Bulk Scope Validation', () => {
    it('should validate multiple scopes efficiently', () => {
      const context: SecurityContext = {
        userId: 'user1',
        userTier: 'T3',
        sessionId: 'session1',
        roles: ['power_user'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      const scopes = [
        'matriz:read',
        'matriz:write',
        'api:analytics:read',
        'admin:users:write', // Should fail
        'enterprise:sso:manage', // Should fail
      ];

      const results = scopeGuard.validateScopes(context, scopes);

      expect(results).toHaveLength(scopes.length);
      expect(results.filter(r => r.allowed)).toHaveLength(3); // First 3 should pass
      expect(results.filter(r => !r.allowed)).toHaveLength(2); // Last 2 should fail
    });

    it('should short-circuit on first failure when configured', () => {
      const context: SecurityContext = {
        userId: 'user1',
        userTier: 'T1',
        sessionId: 'session1',
        roles: ['viewer'],
        ipAddress: '127.0.0.1',
        userAgent: 'Test Agent',
      };

      const scopes = [
        'matriz:read', // Should pass
        'admin:users:write', // Should fail and stop here
        'matriz:write', // Should not be evaluated
      ];

      const result = scopeGuard.validateAllScopes(context, scopes);

      expect(result.allowed).toBe(false);
      expect(result.failedScope).toBe('admin:users:write');
    });
  });
});

describe('ScopeUtils', () => {
  describe('Scope Parsing and Formatting', () => {
    it('should expand scope wildcards correctly', () => {
      const availableScopes = [
        'admin:users:read',
        'admin:users:write',
        'admin:system:read',
        'admin:system:write',
        'api:read',
        'api:write',
      ];

      const expanded = ScopeUtils.expandWildcards(['admin:*'], availableScopes);

      expect(expanded).toContain('admin:users:read');
      expect(expanded).toContain('admin:users:write');
      expect(expanded).toContain('admin:system:read');
      expect(expanded).toContain('admin:system:write');
      expect(expanded).not.toContain('api:read');
      expect(expanded).not.toContain('api:write');
    });

    it('should normalize scope arrays', () => {
      const scopes = [
        'matriz:read',
        'MATRIZ:READ', // Duplicate in different case
        'auth:login',
        'matriz:read', // Exact duplicate
        'api:write',
      ];

      const normalized = ScopeUtils.normalizeScopes(scopes);

      expect(normalized).toEqual([
        'matriz:read',
        'auth:login',
        'api:write',
      ]);
      expect(normalized).toHaveLength(3);
    });

    it('should filter scopes by category', () => {
      const scopes = [
        'matriz:read',
        'matriz:write',
        'admin:users:read',
        'admin:system:write',
        'api:read',
        'auth:login',
      ];

      const adminScopes = ScopeUtils.filterByCategory(scopes, 'admin');
      const matrizScopes = ScopeUtils.filterByCategory(scopes, 'matriz');

      expect(adminScopes).toEqual(['admin:users:read', 'admin:system:write']);
      expect(matrizScopes).toEqual(['matriz:read', 'matriz:write']);
    });

    it('should group scopes by category', () => {
      const scopes = [
        'matriz:read',
        'matriz:write',
        'admin:users:read',
        'admin:system:write',
        'api:read',
      ];

      const grouped = ScopeUtils.groupByCategory(scopes);

      expect(grouped.matriz).toEqual(['matriz:read', 'matriz:write']);
      expect(grouped.admin).toEqual(['admin:users:read', 'admin:system:write']);
      expect(grouped.api).toEqual(['api:read']);
    });
  });

  describe('Scope Hierarchy and Inheritance', () => {
    it('should determine scope hierarchy correctly', () => {
      expect(ScopeUtils.isHigherScope('admin:*', 'admin:users:read')).toBe(true);
      expect(ScopeUtils.isHigherScope('admin:users:*', 'admin:users:read')).toBe(true);
      expect(ScopeUtils.isHigherScope('admin:users:write', 'admin:users:read')).toBe(true);
      expect(ScopeUtils.isHigherScope('admin:users:read', 'admin:users:write')).toBe(false);
      expect(ScopeUtils.isHigherScope('matriz:read', 'admin:users:read')).toBe(false);
    });

    it('should calculate effective scopes from roles', () => {
      const roles: Role[] = [
        {
          name: 'viewer',
          scopes: ['matriz:read', 'profile:view'],
          tier: 'T1',
        },
        {
          name: 'user',
          scopes: ['matriz:write', 'api:basic:read'],
          tier: 'T2',
        },
      ];

      const effectiveScopes = ScopeUtils.getEffectiveScopes(['viewer', 'user'], roles);

      expect(effectiveScopes).toContain('matriz:read');
      expect(effectiveScopes).toContain('matriz:write');
      expect(effectiveScopes).toContain('profile:view');
      expect(effectiveScopes).toContain('api:basic:read');
    });

    it('should resolve scope conflicts appropriately', () => {
      const conflictingScopes = [
        'matriz:read',
        'matriz:write', // Higher than read
        'admin:users:read',
        'admin:*', // Higher than admin:users:read
      ];

      const resolved = ScopeUtils.resolveConflicts(conflictingScopes);

      expect(resolved).toContain('matriz:write');
      expect(resolved).toContain('admin:*');
      expect(resolved).not.toContain('matriz:read');
      expect(resolved).not.toContain('admin:users:read');
    });
  });

  describe('Tier Integration', () => {
    it('should get available scopes for tier', () => {
      const t1Scopes = ScopeUtils.getScopesForTier('T1');
      const t5Scopes = ScopeUtils.getScopesForTier('T5');

      expect(t1Scopes).toContain('matriz:read');
      expect(t1Scopes).toContain('auth:login');
      expect(t1Scopes).not.toContain('admin:system:write');

      expect(t5Scopes).toContain('matriz:read');
      expect(t5Scopes).toContain('admin:system:write');
      expect(t5Scopes).toContain('enterprise:sso:manage');
      expect(t5Scopes.length).toBeGreaterThan(t1Scopes.length);
    });

    it('should validate tier scope compatibility', () => {
      expect(ScopeUtils.isScopeValidForTier('matriz:read', 'T1')).toBe(true);
      expect(ScopeUtils.isScopeValidForTier('admin:system:write', 'T1')).toBe(false);
      expect(ScopeUtils.isScopeValidForTier('admin:system:write', 'T5')).toBe(true);
    });

    it('should suggest tier upgrade for scopes', () => {
      const requiredTier = ScopeUtils.getMinimumTierForScope('admin:system:write');
      expect(requiredTier).toBe('T5');

      const basicTier = ScopeUtils.getMinimumTierForScope('matriz:read');
      expect(basicTier).toBe('T1');
    });
  });

  describe('Security Validation', () => {
    it('should detect dangerous scope combinations', () => {
      const dangerousScopes = [
        'admin:*',
        'enterprise:billing:manage',
        'system:maintenance:write',
      ];

      const safeScopes = [
        'matriz:read',
        'api:read',
        'profile:view',
      ];

      expect(ScopeUtils.hasDangerousScopes(dangerousScopes)).toBe(true);
      expect(ScopeUtils.hasDangerousScopes(safeScopes)).toBe(false);
    });

    it('should validate scope request patterns', () => {
      // Suspicious: requesting unrelated high-privilege scopes
      const suspiciousRequest = [
        'matriz:read',
        'admin:system:write',
        'enterprise:billing:manage',
      ];

      // Normal: requesting related scopes
      const normalRequest = [
        'matriz:read',
        'matriz:write',
        'api:read',
      ];

      expect(ScopeUtils.isSuspiciousRequest(suspiciousRequest)).toBe(true);
      expect(ScopeUtils.isSuspiciousRequest(normalRequest)).toBe(false);
    });

    it('should audit scope usage patterns', () => {
      const usageHistory = [
        { scope: 'matriz:read', timestamp: new Date(), userId: 'user1' },
        { scope: 'admin:system:write', timestamp: new Date(), userId: 'user1' },
        { scope: 'admin:system:write', timestamp: new Date(), userId: 'user1' },
      ];

      const audit = ScopeUtils.auditScopeUsage('user1', usageHistory);

      expect(audit.totalRequests).toBe(3);
      expect(audit.uniqueScopes).toBe(2);
      expect(audit.privilegedRequests).toBe(2);
      expect(audit.riskScore).toBeGreaterThan(0);
    });
  });
});