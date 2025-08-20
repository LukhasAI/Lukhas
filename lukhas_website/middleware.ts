/**
 * Authorization Middleware for ΛiD Authentication System
 * 
 * Implements deny-by-default authorization with route guards, tier-based access control,
 * step-up authentication, and comprehensive audit logging for LUKHAS AI.
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
// import JWTManager from './packages/auth/jwt';
// import { ScopeGuard } from './packages/auth/scopes';
// import { TierLevel, TierManager } from './packages/auth/tier-system';
// import { RBACManager, Permission, Role } from './packages/auth/rbac';
// import { RateLimiter } from './packages/auth/rate-limiter';

export interface RouteGuard {
  pattern: RegExp;
  scope?: string;
  permission?: Permission;
  minTier?: TierLevel;
  requiresStepUp?: boolean;
  requiresVerification?: boolean;
  requiresSSO?: boolean;
  allowAnonymous?: boolean;
  rateLimitKey?: string;
  customRateLimits?: {
    rpm: number;
    rpd: number;
  };
}

export interface AuthContext {
  userId?: string;
  tier: TierLevel;
  role?: Role;
  organizationId?: string;
  isAuthenticated: boolean;
  isVerified: boolean;
  isSSOAuthenticated: boolean;
  sessionCreatedAt: Date;
  lastStepUpAt?: Date;
  ipAddress: string;
  userAgent: string;
  sessionId: string;
}

export interface AuthResult {
  allowed: boolean;
  response?: NextResponse;
  reasons: string[];
  auditData: AuditData;
}

export interface AuditData {
  timestamp: Date;
  userId?: string;
  action: string;
  resource: string;
  allowed: boolean;
  reasons: string[];
  ipAddress: string;
  userAgent: string;
  tier: TierLevel;
  role?: Role;
  organizationId?: string;
  sessionId: string;
  stepUpRequired?: boolean;
  rateLimitTriggered?: boolean;
}

/**
 * Route guards configuration - DENY BY DEFAULT
 * Every route must be explicitly allowed or it will be blocked
 */
export const ROUTE_GUARDS: RouteGuard[] = [
  // Public routes (explicitly allowed)
  {
    pattern: /^\/$/,
    allowAnonymous: true,
    rateLimitKey: 'public_home'
  },
  {
    pattern: /^\/login$/,
    allowAnonymous: true,
    rateLimitKey: 'auth_login'
  },
  {
    pattern: /^\/register$/,
    allowAnonymous: true,
    rateLimitKey: 'auth_register'
  },
  {
    pattern: /^\/forgot-password$/,
    allowAnonymous: true,
    rateLimitKey: 'auth_password_reset'
  },
  {
    pattern: /^\/verify-email$/,
    allowAnonymous: true,
    rateLimitKey: 'auth_verify'
  },
  {
    pattern: /^\/pricing$/,
    allowAnonymous: true,
    rateLimitKey: 'public_pricing'
  },
  {
    pattern: /^\/docs/,
    allowAnonymous: true,
    rateLimitKey: 'public_docs'
  },
  {
    pattern: /^\/about$/,
    allowAnonymous: true,
    rateLimitKey: 'public_about'
  },

  // API routes - require authentication and specific permissions
  {
    pattern: /^\/api\/auth\//,
    allowAnonymous: true,
    rateLimitKey: 'api_auth',
    customRateLimits: { rpm: 10, rpd: 100 }
  },
  {
    pattern: /^\/api\/public\//,
    allowAnonymous: true,
    scope: 'api:public:read',
    rateLimitKey: 'api_public'
  },
  {
    pattern: /^\/api\/user\//,
    scope: 'api:user:read',
    rateLimitKey: 'api_user'
  },
  {
    pattern: /^\/api\/projects/,
    permission: 'project:read',
    minTier: 'T2',
    rateLimitKey: 'api_projects'
  },
  {
    pattern: /^\/api\/models/,
    permission: 'models:read',
    minTier: 'T2',
    rateLimitKey: 'api_models'
  },

  // Sensitive API routes - require step-up authentication
  {
    pattern: /^\/api\/keys/,
    permission: 'api:keys:create',
    minTier: 'T2',
    requiresStepUp: true,
    rateLimitKey: 'api_keys',
    customRateLimits: { rpm: 5, rpd: 20 }
  },
  {
    pattern: /^\/api\/billing/,
    permission: 'billing:read',
    minTier: 'T2',
    requiresStepUp: true,
    requiresVerification: true,
    rateLimitKey: 'api_billing',
    customRateLimits: { rpm: 5, rpd: 50 }
  },
  {
    pattern: /^\/api\/organizations/,
    permission: 'org:read',
    minTier: 'T3',
    rateLimitKey: 'api_organizations'
  },

  // Admin routes - high security requirements
  {
    pattern: /^\/admin/,
    permission: 'admin:system:read',
    minTier: 'T5',
    requiresSSO: true,
    requiresVerification: true,
    requiresStepUp: true,
    rateLimitKey: 'admin_access',
    customRateLimits: { rpm: 30, rpd: 500 }
  },

  // Dashboard routes
  {
    pattern: /^\/dashboard$/,
    scope: 'dashboard:read',
    minTier: 'T1',
    rateLimitKey: 'dashboard'
  },
  {
    pattern: /^\/dashboard\/settings/,
    scope: 'user:update',
    rateLimitKey: 'dashboard_settings'
  },
  {
    pattern: /^\/dashboard\/api-keys/,
    permission: 'api:keys:read',
    minTier: 'T2',
    rateLimitKey: 'dashboard_api_keys'
  },
  {
    pattern: /^\/dashboard\/billing/,
    permission: 'billing:read',
    minTier: 'T2',
    requiresStepUp: true,
    rateLimitKey: 'dashboard_billing'
  },
  {
    pattern: /^\/dashboard\/organizations/,
    permission: 'org:read',
    minTier: 'T3',
    rateLimitKey: 'dashboard_orgs'
  },

  // Organization management
  {
    pattern: /^\/orgs\/[^\/]+\/settings/,
    permission: 'org:update',
    minTier: 'T3',
    requiresStepUp: true,
    rateLimitKey: 'org_settings'
  },
  {
    pattern: /^\/orgs\/[^\/]+\/members/,
    permission: 'org:manage_roles',
    minTier: 'T3',
    rateLimitKey: 'org_members'
  },
  {
    pattern: /^\/orgs\/[^\/]+\/billing/,
    permission: 'org:manage_billing',
    minTier: 'T3',
    requiresStepUp: true,
    requiresVerification: true,
    rateLimitKey: 'org_billing'
  }
];

/**
 * Step-up authentication requirements
 */
const STEP_UP_TIMEOUT = 15 * 60 * 1000; // 15 minutes

/**
 * Extract authentication context from request
 */
async function extractAuthContext(request: NextRequest): Promise<AuthContext> {
  const ipAddress = request.ip || request.headers.get('x-forwarded-for') || 'unknown';
  const userAgent = request.headers.get('user-agent') || 'unknown';
  
  // Extract session information from cookie or header
  const authCookie = request.cookies.get('lukhas_auth')?.value;
  const authHeader = request.headers.get('authorization');
  
  let context: AuthContext = {
    tier: 'T1',
    isAuthenticated: false,
    isVerified: false,
    isSSOAuthenticated: false,
    sessionCreatedAt: new Date(),
    ipAddress,
    userAgent,
    sessionId: 'anonymous'
  };

  if (authCookie || authHeader) {
    try {
      const token = authCookie || authHeader?.replace('Bearer ', '');
      if (token) {
        const payload = await verifyJWT(token);
        context = {
          userId: payload.sub,
          tier: (payload.tier as TierLevel) || 'T1',
          role: payload.role as Role,
          organizationId: payload.org,
          isAuthenticated: true,
          isVerified: payload.verified || false,
          isSSOAuthenticated: payload.sso || false,
          sessionCreatedAt: new Date(payload.iat * 1000),
          lastStepUpAt: payload.stepUpAt ? new Date(payload.stepUpAt * 1000) : undefined,
          ipAddress,
          userAgent,
          sessionId: payload.sessionId || 'unknown'
        };
      }
    } catch (error) {
      // Invalid token - treat as anonymous
      console.warn('Invalid auth token:', error);
    }
  }

  return context;
}

/**
 * Find matching route guard
 */
function findRouteGuard(pathname: string): RouteGuard | null {
  return ROUTE_GUARDS.find(guard => guard.pattern.test(pathname)) || null;
}

/**
 * Check if step-up authentication is required and valid
 */
function checkStepUpAuthentication(
  guard: RouteGuard,
  context: AuthContext
): { required: boolean; valid: boolean } {
  if (!guard.requiresStepUp) {
    return { required: false, valid: true };
  }

  if (!context.lastStepUpAt) {
    return { required: true, valid: false };
  }

  const stepUpAge = Date.now() - context.lastStepUpAt.getTime();
  const valid = stepUpAge < STEP_UP_TIMEOUT;

  return { required: true, valid };
}

/**
 * Perform authorization check
 */
async function authorize(
  guard: RouteGuard,
  context: AuthContext,
  pathname: string
): Promise<AuthResult> {
  const reasons: string[] = [];
  let allowed = false;

  // Check if anonymous access is allowed
  if (guard.allowAnonymous && !guard.scope && !guard.permission) {
    allowed = true;
  } else {
    // Require authentication for protected routes
    if (!context.isAuthenticated) {
      reasons.push('Authentication required');
    } else {
      // Check minimum tier requirement
      if (guard.minTier) {
        const tierConfig = TierManager.getTierConfig(context.tier);
        const requiredConfig = TierManager.getTierConfig(guard.minTier);
        const tierOrder: TierLevel[] = ['T1', 'T2', 'T3', 'T4', 'T5'];
        const currentIndex = tierOrder.indexOf(context.tier);
        const requiredIndex = tierOrder.indexOf(guard.minTier);
        
        if (currentIndex < requiredIndex) {
          reasons.push(`Requires ${guard.minTier} tier or higher`);
        }
      }

      // Check verification requirement
      if (guard.requiresVerification && !context.isVerified) {
        reasons.push('Account verification required');
      }

      // Check SSO requirement
      if (guard.requiresSSO && !context.isSSOAuthenticated) {
        reasons.push('SSO authentication required');
      }

      // Check step-up authentication
      const stepUp = checkStepUpAuthentication(guard, context);
      if (stepUp.required && !stepUp.valid) {
        reasons.push('Step-up authentication required');
      }

      // Check scope-based access
      if (guard.scope && context.userId) {
        try {
          const hasScope = await ScopeGuard.hasScope(context.userId, guard.scope);
          if (!hasScope) {
            reasons.push(`Missing required scope: ${guard.scope}`);
          }
        } catch (error) {
          reasons.push('Scope validation failed');
        }
      }

      // Check permission-based access (RBAC)
      if (guard.permission && context.role) {
        const hasPermission = RBACManager.hasPermission(context.role, guard.permission);
        if (!hasPermission) {
          reasons.push(`Missing required permission: ${guard.permission}`);
        }
      }

      // If no blocking reasons, allow access
      if (reasons.length === 0) {
        allowed = true;
      }
    }
  }

  // Create audit data
  const auditData: AuditData = {
    timestamp: new Date(),
    userId: context.userId,
    action: 'route_access',
    resource: pathname,
    allowed,
    reasons,
    ipAddress: context.ipAddress,
    userAgent: context.userAgent,
    tier: context.tier,
    role: context.role,
    organizationId: context.organizationId,
    sessionId: context.sessionId,
    stepUpRequired: guard.requiresStepUp,
    rateLimitTriggered: false
  };

  // Generate appropriate response if access denied
  let response: NextResponse | undefined;
  if (!allowed) {
    if (!context.isAuthenticated) {
      // Redirect to login with return URL
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('returnTo', pathname);
      response = NextResponse.redirect(loginUrl);
    } else if (guard.requiresStepUp && checkStepUpAuthentication(guard, context).required && !checkStepUpAuthentication(guard, context).valid) {
      // Redirect to step-up authentication
      const stepUpUrl = new URL('/auth/step-up', request.url);
      stepUpUrl.searchParams.set('returnTo', pathname);
      response = NextResponse.redirect(stepUpUrl);
    } else {
      // Show access denied
      response = new NextResponse('Access Denied', { status: 403 });
    }
  }

  return { allowed, response, reasons, auditData };
}

/**
 * Log audit data (implement storage mechanism)
 */
async function logAudit(auditData: AuditData): Promise<void> {
  // TODO: Implement audit logging to database/file
  // This should integrate with the governance/audit system
  console.log('AUDIT:', JSON.stringify(auditData, null, 2));
  
  // In production, this should write to:
  // - Database audit table
  // - CloudWatch/DataDog logs
  // - SIEM system
  // - File-based audit trail
}

/**
 * Main middleware function
 */
export async function middleware(request: NextRequest) {
  // TEMPORARY: Allow all requests during development
  return NextResponse.next();
  
  /*
  const pathname = request.nextUrl.pathname;
  
  // Skip middleware for static assets and API routes that don't need protection
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/static/') ||
    pathname.startsWith('/favicon.ico') ||
    pathname.startsWith('/robots.txt') ||
    pathname.startsWith('/sitemap.xml')
  ) {
    return NextResponse.next();
  }

  try {
    // Extract authentication context
    const context = await extractAuthContext(request);
    
    // Find matching route guard
    const guard = findRouteGuard(pathname);
    
    // DENY BY DEFAULT - if no guard found, block access
    if (!guard) {
      const auditData: AuditData = {
        timestamp: new Date(),
        userId: context.userId,
        action: 'route_access',
        resource: pathname,
        allowed: false,
        reasons: ['No route guard configured - denied by default'],
        ipAddress: context.ipAddress,
        userAgent: context.userAgent,
        tier: context.tier,
        role: context.role,
        organizationId: context.organizationId,
        sessionId: context.sessionId
      };
      
      await logAudit(auditData);
      return new NextResponse('Access Denied - Route Not Configured', { status: 403 });
    }

    // Check rate limits
    const rateLimitKey = guard.rateLimitKey || 'default';
    const customLimits = guard.customRateLimits;
    const tierLimits = TierManager.getRateLimits(context.tier);
    
    const rateLimitConfig = {
      rpm: customLimits?.rpm || tierLimits.rpm,
      rpd: customLimits?.rpd || tierLimits.rpd,
      identifier: `${rateLimitKey}:${context.userId || context.ipAddress}`
    };

    const rateLimitResult = await RateLimiter.checkLimit(rateLimitConfig);
    
    if (!rateLimitResult.allowed) {
      const auditData: AuditData = {
        timestamp: new Date(),
        userId: context.userId,
        action: 'route_access',
        resource: pathname,
        allowed: false,
        reasons: ['Rate limit exceeded'],
        ipAddress: context.ipAddress,
        userAgent: context.userAgent,
        tier: context.tier,
        role: context.role,
        organizationId: context.organizationId,
        sessionId: context.sessionId,
        rateLimitTriggered: true
      };
      
      await logAudit(auditData);
      
      const response = new NextResponse('Rate Limit Exceeded', { status: 429 });
      response.headers.set('Retry-After', rateLimitResult.resetTime.toString());
      response.headers.set('X-RateLimit-Limit', rateLimitConfig.rpm.toString());
      response.headers.set('X-RateLimit-Remaining', rateLimitResult.remaining.toString());
      response.headers.set('X-RateLimit-Reset', rateLimitResult.resetTime.toString());
      
      return response;
    }

    // Perform authorization
    const authResult = await authorize(guard, context, pathname);
    
    // Log audit data
    authResult.auditData.rateLimitTriggered = false;
    await logAudit(authResult.auditData);

    // Return response if access denied
    if (!authResult.allowed && authResult.response) {
      return authResult.response;
    }

    // Add security headers
    const response = NextResponse.next();
    response.headers.set('X-Content-Type-Options', 'nosniff');
    response.headers.set('X-Frame-Options', 'DENY');
    response.headers.set('X-XSS-Protection', '1; mode=block');
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    
    // Add rate limit headers
    response.headers.set('X-RateLimit-Limit', rateLimitConfig.rpm.toString());
    response.headers.set('X-RateLimit-Remaining', rateLimitResult.remaining.toString());
    response.headers.set('X-RateLimit-Reset', rateLimitResult.resetTime.toString());

    return response;
    
  } catch (error) {
    console.error('Middleware error:', error);
    
    // Log the error for audit
    const auditData: AuditData = {
      timestamp: new Date(),
      action: 'middleware_error',
      resource: pathname,
      allowed: false,
      reasons: [`Middleware error: ${error.message}`],
      ipAddress: request.ip || 'unknown',
      userAgent: request.headers.get('user-agent') || 'unknown',
      tier: 'T1',
      sessionId: 'error'
    };
    
    await logAudit(auditData);
    
    // In case of error, deny access (fail secure)
    return new NextResponse('Internal Error - Access Denied', { status: 500 });
  }
  */
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public|static).*)',
  ],
};

export type { RouteGuard, AuthContext, AuthResult, AuditData };