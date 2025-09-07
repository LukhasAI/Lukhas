/**
 * LUKHAS ΛiD Authentication Service
 * 
 * Integration with LUKHAS Trinity Framework (⚛️🧠🛡️) Authentication System
 * Supports JWT tokens, magic links, passkeys, and tier-based access control
 */

import { User, AuthResponse, LoginRequest, RegistrationRequest, UserTier } from '@/types/auth';

// API Configuration
const LUKHAS_API_BASE = process.env.NEXT_PUBLIC_LUKHAS_API_URL || 'http://localhost:8080';
const API_VERSION = 'v1';

/**
 * Authentication API client
 */
class LukhасAuthService {
  private baseURL: string;
  
  constructor() {
    this.baseURL = `${LUKHAS_API_BASE}/api/${API_VERSION}/auth`;
  }

  /**
   * Login with email/password or magic link
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseURL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Authentication failed');
      }

      const authResponse: AuthResponse = await response.json();
      
      // Store tokens securely
      if (authResponse.tokens) {
        localStorage.setItem('lukhas_access_token', authResponse.tokens.accessToken);
        localStorage.setItem('lukhas_refresh_token', authResponse.tokens.refreshToken);
      }

      return authResponse;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Register new user with email
   */
  async register(data: RegistrationRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseURL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Registration failed');
      }

      const authResponse: AuthResponse = await response.json();
      
      // Store tokens securely
      if (authResponse.tokens) {
        localStorage.setItem('lukhas_access_token', authResponse.tokens.accessToken);
        localStorage.setItem('lukhas_refresh_token', authResponse.tokens.refreshToken);
      }

      return authResponse;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  /**
   * Send magic link for passwordless authentication
   */
  async sendMagicLink(email: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseURL}/magic-link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email,
          ipAddress: await this.getClientIP(),
          userAgent: navigator.userAgent 
        }),
      });

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Magic link error:', error);
      return { success: false, message: 'Failed to send magic link' };
    }
  }

  /**
   * Logout user and cleanup tokens
   */
  async logout(): Promise<void> {
    try {
      const token = localStorage.getItem('lukhas_access_token');
      
      if (token) {
        await fetch(`${this.baseURL}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always cleanup local storage
      localStorage.removeItem('lukhas_access_token');
      localStorage.removeItem('lukhas_refresh_token');
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const token = localStorage.getItem('lukhas_access_token');
      
      if (!token) {
        return null;
      }

      const response = await fetch(`${this.baseURL}/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, try to refresh
          const refreshed = await this.refreshToken();
          if (refreshed) {
            return this.getCurrentUser();
          }
        }
        return null;
      }

      const userData: User = await response.json();
      return userData;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = localStorage.getItem('lukhas_refresh_token');
      
      if (!refreshToken) {
        return false;
      }

      const response = await fetch(`${this.baseURL}/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken }),
      });

      if (!response.ok) {
        return false;
      }

      const { tokens } = await response.json();
      
      localStorage.setItem('lukhas_access_token', tokens.accessToken);
      localStorage.setItem('lukhas_refresh_token', tokens.refreshToken);
      
      return true;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('lukhas_access_token');
  }

  /**
   * Get client IP address for security logging
   */
  private async getClientIP(): Promise<string> {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch (error) {
      return 'unknown';
    }
  }
}

// Demo mode fallback for development
class DemoAuthService {
  async login(data: LoginRequest): Promise<AuthResponse> {
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    if (data.email === 'demo@lukhas.ai' && data.password === 'consciousness') {
      const mockUser: User = {
        id: 'demo-user-id',
        email: 'demo@lukhas.ai',
        emailVerified: true,
        tier: 'T3' as UserTier,
        role: 'developer',
        status: 'active',
        failedLoginAttempts: 0,
        displayName: 'Demo User',
        timezone: 'UTC',
        locale: 'en',
        metadata: {},
        preferences: {},
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString(),
      };

      const mockTokens = {
        accessToken: 'demo-access-token',
        refreshToken: 'demo-refresh-token',
        tokenType: 'Bearer' as const,
        expiresIn: 3600,
        scope: 'matriz:read identity:read',
      };

      const mockSession = {
        id: 'demo-session-id',
        userId: 'demo-user-id',
        deviceHandle: 'demo-device',
        accessTokenJti: 'demo-jti',
        scopes: ['matriz:read' as any, 'identity:read' as any],
        tier: 'T3' as UserTier,
        role: 'developer' as any,
        createdAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 3600000).toISOString(),
        lastUsedAt: new Date().toISOString(),
        metadata: {},
      };

      // Store demo tokens
      localStorage.setItem('lukhas_access_token', mockTokens.accessToken);
      localStorage.setItem('lukhas_refresh_token', mockTokens.refreshToken);

      return {
        user: mockUser,
        tokens: mockTokens,
        session: mockSession,
      };
    } else {
      throw new Error('Invalid credentials. Try demo@lukhas.ai / consciousness');
    }
  }

  async register(data: RegistrationRequest): Promise<AuthResponse> {
    throw new Error('Registration not available in demo mode. Please use demo@lukhas.ai');
  }

  async sendMagicLink(email: string): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return { 
      success: true, 
      message: 'Demo magic link would be sent to ' + email 
    };
  }

  async logout(): Promise<void> {
    localStorage.removeItem('lukhas_access_token');
    localStorage.removeItem('lukhas_refresh_token');
  }

  async getCurrentUser(): Promise<User | null> {
    const token = localStorage.getItem('lukhas_access_token');
    if (token === 'demo-access-token') {
      return {
        id: 'demo-user-id',
        email: 'demo@lukhas.ai',
        emailVerified: true,
        tier: 'T3' as UserTier,
        role: 'developer',
        status: 'active',
        failedLoginAttempts: 0,
        displayName: 'Demo User',
        timezone: 'UTC',
        locale: 'en',
        metadata: {},
        preferences: {},
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString(),
      };
    }
    return null;
  }

  async refreshToken(): Promise<boolean> {
    return this.isAuthenticated();
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('lukhas_access_token');
  }
}

// Choose implementation based on environment
const isDevelopment = process.env.NODE_ENV === 'development';
const useDemoMode = process.env.NEXT_PUBLIC_USE_DEMO_AUTH === 'true';

export const authService = isDevelopment && useDemoMode 
  ? new DemoAuthService() 
  : new LukhасAuthService();

export default authService;