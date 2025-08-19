'use client'

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import {
  LukhasUser,
  AuthSession,
  LoginCredentials,
  RegisterCredentials,
  login as authLogin,
  register as authRegister,
  logout as authLogout,
  getStoredSession,
  refreshSession,
  updateProfile,
  verifyEmail,
  hasAccessToModule,
  isSubscriptionActive,
  getSubscriptionStatus
} from '@/lib/auth/lukhas-id'

interface AuthContextType {
  // State
  user: LukhasUser | null
  session: AuthSession | null
  isLoading: boolean
  isAuthenticated: boolean
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
  updateUserProfile: (updates: Partial<Pick<LukhasUser, 'displayName' | 'avatar'>>) => Promise<void>
  verifyUserEmail: (token: string) => Promise<boolean>
  
  // Utilities
  hasModuleAccess: (module: keyof LukhasUser['trinityAccess']) => boolean
  isSubscriptionValid: boolean
  subscriptionStatus: 'active' | 'expired' | 'none'
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<LukhasUser | null>(null)
  const [session, setSession] = useState<AuthSession | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize auth state from storage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedSession = getStoredSession()
        if (storedSession) {
          setSession(storedSession)
          setUser(storedSession.user)
          
          // Try to refresh the session
          try {
            const refreshedSession = await refreshSession()
            if (refreshedSession) {
              setSession(refreshedSession)
              setUser(refreshedSession.user)
            }
          } catch (error) {
            console.warn('Failed to refresh session:', error)
            // Keep the stored session if refresh fails
          }
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        setSession(null)
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()
  }, [])

  // Auto-refresh session periodically
  useEffect(() => {
    if (!session) return

    const refreshInterval = setInterval(async () => {
      try {
        const refreshedSession = await refreshSession()
        if (refreshedSession) {
          setSession(refreshedSession)
          setUser(refreshedSession.user)
        } else {
          // Session expired or invalid
          setSession(null)
          setUser(null)
        }
      } catch (error) {
        console.warn('Auto-refresh failed:', error)
      }
    }, 15 * 60 * 1000) // Refresh every 15 minutes

    return () => clearInterval(refreshInterval)
  }, [session])

  const login = useCallback(async (credentials: LoginCredentials) => {
    setIsLoading(true)
    try {
      const newSession = await authLogin(credentials)
      setSession(newSession)
      setUser(newSession.user)
    } catch (error) {
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  const register = useCallback(async (credentials: RegisterCredentials) => {
    setIsLoading(true)
    try {
      const newSession = await authRegister(credentials)
      setSession(newSession)
      setUser(newSession.user)
    } catch (error) {
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    setIsLoading(true)
    try {
      await authLogout()
      setSession(null)
      setUser(null)
    } catch (error) {
      console.error('Logout failed:', error)
      // Force local logout even if server request fails
      setSession(null)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const refresh = useCallback(async () => {
    try {
      const refreshedSession = await refreshSession()
      if (refreshedSession) {
        setSession(refreshedSession)
        setUser(refreshedSession.user)
      } else {
        setSession(null)
        setUser(null)
      }
    } catch (error) {
      console.error('Refresh failed:', error)
      setSession(null)
      setUser(null)
    }
  }, [])

  const updateUserProfile = useCallback(async (updates: Partial<Pick<LukhasUser, 'displayName' | 'avatar'>>) => {
    if (!user) throw new Error('No user logged in')
    
    try {
      const updatedUser = await updateProfile(updates)
      setUser(updatedUser)
      
      // Update session as well
      if (session) {
        const updatedSession: AuthSession = {
          ...session,
          user: updatedUser
        }
        setSession(updatedSession)
      }
    } catch (error) {
      throw error
    }
  }, [user, session])

  const verifyUserEmail = useCallback(async (token: string): Promise<boolean> => {
    try {
      const result = await verifyEmail(token)
      if (result && session) {
        // Refresh session to get updated user data
        await refresh()
      }
      return result
    } catch (error) {
      console.error('Email verification failed:', error)
      return false
    }
  }, [session, refresh])

  const hasModuleAccess = useCallback((module: keyof LukhasUser['trinityAccess']): boolean => {
    return hasAccessToModule(user, module)
  }, [user])

  const isSubscriptionValid = isSubscriptionActive(user)
  const subscriptionStatus = getSubscriptionStatus(user)
  const isAuthenticated = !!user && !!session

  const value: AuthContextType = {
    // State
    user,
    session,
    isLoading,
    isAuthenticated,
    
    // Actions
    login,
    register,
    logout,
    refresh,
    updateUserProfile,
    verifyUserEmail,
    
    // Utilities
    hasModuleAccess,
    isSubscriptionValid,
    subscriptionStatus
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Higher-order component for protected routes
interface ProtectedRouteProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  requireVerification?: boolean
  requiredModule?: keyof LukhasUser['trinityAccess']
  requiredSubscription?: boolean
}

export function ProtectedRoute({ 
  children, 
  fallback = null, 
  requireVerification = false,
  requiredModule,
  requiredSubscription = false
}: ProtectedRouteProps) {
  const { isAuthenticated, user, hasModuleAccess, isSubscriptionValid, isLoading } = useAuth()

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="glass-panel p-8 rounded-2xl">
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 border-2 border-trinity-consciousness/20 border-t-trinity-consciousness rounded-full animate-spin" />
            <span className="font-thin text-lg">Authenticating...</span>
          </div>
        </div>
      </div>
    )
  }

  // Check authentication
  if (!isAuthenticated) {
    return fallback
  }

  // Check email verification
  if (requireVerification && !user?.isVerified) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="glass-panel p-8 rounded-2xl text-center max-w-md">
          <div className="w-16 h-16 bg-trinity-consciousness/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">📧</span>
          </div>
          <h3 className="font-regular text-xl tracking-[0.1em] uppercase mb-4">Email Verification Required</h3>
          <p className="font-thin text-neutral-gray">
            Please verify your email address to access this feature.
          </p>
        </div>
      </div>
    )
  }

  // Check module access
  if (requiredModule && !hasModuleAccess(requiredModule)) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="glass-panel p-8 rounded-2xl text-center max-w-md">
          <div className="w-16 h-16 bg-trinity-guardian/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">🛡️</span>
          </div>
          <h3 className="font-regular text-xl tracking-[0.1em] uppercase mb-4">Access Restricted</h3>
          <p className="font-thin text-neutral-gray">
            You don't have access to the {requiredModule} module. Please contact support to upgrade your access.
          </p>
        </div>
      </div>
    )
  }

  // Check subscription
  if (requiredSubscription && !isSubscriptionValid) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="glass-panel p-8 rounded-2xl text-center max-w-md">
          <div className="w-16 h-16 bg-accent-gold/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">⭐</span>
          </div>
          <h3 className="font-regular text-xl tracking-[0.1em] uppercase mb-4">Subscription Required</h3>
          <p className="font-thin text-neutral-gray">
            This feature requires an active subscription. Please upgrade your plan to continue.
          </p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

// Hook for conditional rendering based on auth state
export function useAuthGuard() {
  const { isAuthenticated, user, hasModuleAccess, isSubscriptionValid } = useAuth()

  return {
    isAuthenticated,
    isVerified: user?.isVerified ?? false,
    hasModuleAccess,
    isSubscriptionValid,
    canAccess: (options: {
      requireAuth?: boolean
      requireVerification?: boolean
      requiredModule?: keyof LukhasUser['trinityAccess']
      requiredSubscription?: boolean
    }) => {
      if (options.requireAuth && !isAuthenticated) return false
      if (options.requireVerification && !user?.isVerified) return false
      if (options.requiredModule && !hasModuleAccess(options.requiredModule)) return false
      if (options.requiredSubscription && !isSubscriptionValid) return false
      return true
    }
  }
}