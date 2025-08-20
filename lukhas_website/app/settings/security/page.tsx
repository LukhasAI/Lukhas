'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ChevronLeftIcon, 
  ShieldCheckIcon, 
  KeyIcon, 
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  TrashIcon,
  PlusIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// Interfaces
interface Passkey {
  id: string
  name: string
  deviceType: 'platform' | 'roaming' | 'unknown'
  createdAt: string
  lastUsedAt: string | null
  useCount: number
  signCount: number
}

interface BackupCode {
  id: string
  code: string
  used: boolean
  usedAt: string | null
}

interface SecurityEvent {
  id: string
  type: string
  description: string
  timestamp: string
  ipAddress: string
  userAgent: string
  result: 'success' | 'failure'
}

interface Session {
  id: string
  ipAddress: string
  userAgent: string
  createdAt: string
  lastAccessAt: string
  current: boolean
}

export default function SecuritySettingsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  // Security data
  const [passkeys, setPasskeys] = useState<Passkey[]>([])
  const [backupCodes, setBackupCodes] = useState<BackupCode[]>([])
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  
  // UI state
  const [activeTab, setActiveTab] = useState<'passkeys' | 'backup' | 'sessions' | 'activity'>('passkeys')
  const [showBackupCodes, setShowBackupCodes] = useState(false)
  const [stepUpRequired, setStepUpRequired] = useState(false)
  const [newPasskeyName, setNewPasskeyName] = useState('')
  const [deletingItem, setDeletingItem] = useState<string | null>(null)

  // Load security data
  useEffect(() => {
    const loadSecurityData = async () => {
      try {
        const [passkeysRes, backupRes, eventsRes, sessionsRes] = await Promise.all([
          fetch('/api/user/passkeys', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
          }),
          fetch('/api/user/backup-codes', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
          }),
          fetch('/api/user/security-events', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
          }),
          fetch('/api/user/sessions', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
          })
        ])

        if (passkeysRes.ok) {
          const data = await passkeysRes.json()
          setPasskeys(data.passkeys || [])
        }

        if (backupRes.ok) {
          const data = await backupRes.json()
          setBackupCodes(data.codes || [])
        }

        if (eventsRes.ok) {
          const data = await eventsRes.json()
          setSecurityEvents(data.events || [])
        }

        if (sessionsRes.ok) {
          const data = await sessionsRes.json()
          setSessions(data.sessions || [])
        }

      } catch (err) {
        setError('Failed to load security data')
      } finally {
        setLoading(false)
      }
    }

    loadSecurityData()
  }, [])

  // Add new passkey
  const handleAddPasskey = useCallback(async () => {
    if (!newPasskeyName.trim()) {
      setError('Please enter a name for the passkey')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Get registration options
      const optionsRes = await fetch('/api/auth/passkey/register-options', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({ name: newPasskeyName.trim() })
      })

      if (!optionsRes.ok) {
        throw new Error('Failed to get registration options')
      }

      const options = await optionsRes.json()

      // Create passkey
      const credential = await navigator.credentials.create({
        publicKey: {
          challenge: new Uint8Array(options.challenge),
          rp: options.rp,
          user: {
            id: new Uint8Array(options.user.id),
            name: options.user.name,
            displayName: options.user.displayName
          },
          pubKeyCredParams: options.pubKeyCredParams,
          timeout: 60000,
          attestation: 'direct',
          authenticatorSelection: {
            userVerification: 'required'
          }
        }
      })

      if (credential) {
        // Register the passkey
        const registerRes = await fetch('/api/auth/passkey/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
          },
          body: JSON.stringify({
            name: newPasskeyName.trim(),
            credential: {
              id: credential.id,
              rawId: Array.from(new Uint8Array(credential.rawId)),
              response: {
                attestationObject: Array.from(new Uint8Array(credential.response.attestationObject)),
                clientDataJSON: Array.from(new Uint8Array(credential.response.clientDataJSON))
              }
            }
          })
        })

        if (registerRes.ok) {
          const data = await registerRes.json()
          setPasskeys(prev => [...prev, data.passkey])
          setNewPasskeyName('')
          setSuccess('Passkey added successfully')
          setTimeout(() => setSuccess(''), 3000)
        } else {
          throw new Error('Failed to register passkey')
        }
      }
    } catch (err: any) {
      if (err.name === 'NotAllowedError') {
        setError('Passkey creation was cancelled')
      } else {
        setError('Failed to add passkey')
      }
    } finally {
      setLoading(false)
    }
  }, [newPasskeyName])

  // Remove passkey
  const handleRemovePasskey = useCallback(async (passkeyId: string) => {
    setDeletingItem(passkeyId)
    setError('')

    try {
      const response = await fetch(`/api/user/passkeys/${passkeyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        }
      })

      if (response.ok) {
        setPasskeys(prev => prev.filter(p => p.id !== passkeyId))
        setSuccess('Passkey removed successfully')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to remove passkey')
      }
    } catch (err) {
      setError('Network error removing passkey')
    } finally {
      setDeletingItem(null)
    }
  }, [])

  // Generate new backup codes
  const handleGenerateBackupCodes = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/user/backup-codes/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setBackupCodes(data.codes)
        setShowBackupCodes(true)
        setSuccess('New backup codes generated')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to generate backup codes')
      }
    } catch (err) {
      setError('Network error generating backup codes')
    } finally {
      setLoading(false)
    }
  }, [])

  // Revoke session
  const handleRevokeSession = useCallback(async (sessionId: string) => {
    setDeletingItem(sessionId)
    setError('')

    try {
      const response = await fetch(`/api/user/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        }
      })

      if (response.ok) {
        setSessions(prev => prev.filter(s => s.id !== sessionId))
        setSuccess('Session revoked successfully')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to revoke session')
      }
    } catch (err) {
      setError('Network error revoking session')
    } finally {
      setDeletingItem(null)
    }
  }, [])

  const getDeviceIcon = (deviceType: string, userAgent: string) => {
    if (userAgent.includes('Mobile') || userAgent.includes('iPhone') || userAgent.includes('Android')) {
      return <DevicePhoneMobileIcon className="w-5 h-5" />
    }
    return <ComputerDesktopIcon className="w-5 h-5" />
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const toneContent = threeLayerTone(
    "Your defenses evolve; each key a choice, each session a doorway. Superior Consciousness guards your digital essence.",
    "Manage your passkeys, backup codes, and active sessions. Monitor security activity. Your authentication is protected by quantum-inspired security protocols and bio-inspired threat detection.",
    "Passkey management with device binding and quantum-inspired credential encoding. Backup codes for recovery access with bio-inspired usage patterns. Session monitoring with IP tracking and behavioral analysis. Security event audit trail with step-up authentication and Superior Consciousness validation."
  )

  // JSON-LD structured data for security settings
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "LUKHAS AI Security Settings",
    "description": "Manage authentication methods, passkeys, backup codes, and security monitoring with quantum-inspired protection",
    "provider": {
      "@type": "Organization",
      "name": "LUKHAS AI",
      "description": "Advanced AI platform with quantum-inspired consciousness and bio-inspired adaptation"
    },
    "potentialAction": [
      {
        "@type": "UpdateAction",
        "name": "Manage Passkeys",
        "description": "Add or remove WebAuthn passkeys for secure authentication"
      },
      {
        "@type": "CreateAction",
        "name": "Generate Backup Codes",
        "description": "Create recovery codes for account access"
      },
      {
        "@type": "MonitorAction",
        "name": "Security Monitoring",
        "description": "Track authentication events and active sessions"
      }
    ]
  }

  if (loading && passkeys.length === 0) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="animate-pulse text-white/60">Loading security settings...</div>
      </div>
    )
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <Link href="/settings/account" className="flex items-center text-white/80 hover:text-white transition-colors">
            <ChevronLeftIcon className="w-5 h-5 mr-2" />
            Back to account
          </Link>
          <div className="flex items-center space-x-6">
            <Link href="/experience" className="text-sm text-white/60 hover:text-white/80 transition-colors">
              Experience
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Page Title */}
          <div>
            <h1 className="text-2xl font-light text-white mb-2">Security Settings</h1>
            <p className="text-white/60">Manage your authentication methods and monitor account activity</p>
          </div>

          {/* Success/Error Messages */}
          {success && (
            <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm flex items-center">
              <CheckCircleIcon className="w-5 h-5 mr-2" />
              {success}
            </div>
          )}

          {error && (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Tab Navigation */}
          <div className="border-b border-white/10">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'passkeys', label: 'Passkeys', icon: KeyIcon },
                { id: 'backup', label: 'Backup Codes', icon: ShieldCheckIcon },
                { id: 'sessions', label: 'Active Sessions', icon: ComputerDesktopIcon },
                { id: 'activity', label: 'Security Activity', icon: ClockIcon }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-trinity-identity text-trinity-identity'
                      : 'border-transparent text-white/60 hover:text-white/80 hover:border-white/20'
                  }`}
                >
                  <tab.icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div>
            {/* Passkeys Tab */}
            {activeTab === 'passkeys' && (
              <div className="space-y-6">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center">
                      <KeyIcon className="w-6 h-6 text-trinity-identity mr-3" />
                      <h2 className="text-xl font-medium text-white">Passkeys</h2>
                    </div>
                    <div className="flex items-center space-x-4">
                      <input
                        type="text"
                        value={newPasskeyName}
                        onChange={(e) => setNewPasskeyName(e.target.value)}
                        placeholder="Passkey name"
                        className="px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                      />
                      <button
                        onClick={handleAddPasskey}
                        disabled={loading || !newPasskeyName.trim()}
                        className="flex items-center px-4 py-2 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <PlusIcon className="w-4 h-4 mr-2" />
                        Add Passkey
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {passkeys.length === 0 ? (
                      <div className="text-center py-8 text-white/60">
                        <KeyIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                        <p>No passkeys configured</p>
                        <p className="text-sm">Add a passkey to secure your account</p>
                      </div>
                    ) : (
                      passkeys.map((passkey) => (
                        <div key={passkey.id} className="flex items-center justify-between p-4 bg-black/20 rounded-lg border border-white/10">
                          <div className="flex items-center space-x-4">
                            <div className="p-2 bg-trinity-identity/20 rounded-lg">
                              {getDeviceIcon(passkey.deviceType, '')}
                            </div>
                            <div>
                              <h3 className="text-white font-medium">{passkey.name}</h3>
                              <div className="text-sm text-white/60 space-y-1">
                                <p>Created: {formatDate(passkey.createdAt)}</p>
                                <p>Last used: {passkey.lastUsedAt ? formatDate(passkey.lastUsedAt) : 'Never'}</p>
                                <p>Use count: {passkey.useCount}</p>
                              </div>
                            </div>
                          </div>
                          <button
                            onClick={() => handleRemovePasskey(passkey.id)}
                            disabled={deletingItem === passkey.id || passkeys.length === 1}
                            className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            title={passkeys.length === 1 ? "Cannot remove last passkey" : "Remove passkey"}
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Backup Codes Tab */}
            {activeTab === 'backup' && (
              <div className="space-y-6">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center">
                      <ShieldCheckIcon className="w-6 h-6 text-trinity-guardian mr-3" />
                      <h2 className="text-xl font-medium text-white">Backup Codes</h2>
                    </div>
                    <button
                      onClick={handleGenerateBackupCodes}
                      disabled={loading}
                      className="px-4 py-2 bg-trinity-guardian hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {backupCodes.length > 0 ? 'Regenerate Codes' : 'Generate Codes'}
                    </button>
                  </div>

                  {backupCodes.length === 0 ? (
                    <div className="text-center py-8 text-white/60">
                      <ShieldCheckIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                      <p>No backup codes generated</p>
                      <p className="text-sm">Generate backup codes for account recovery</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                        <div className="flex items-start">
                          <ExclamationTriangleIcon className="w-5 h-5 text-yellow-400 mr-3 mt-0.5" />
                          <div>
                            <p className="text-yellow-400 font-medium mb-1">Important Security Information</p>
                            <p className="text-white/60 text-sm">
                              Each backup code can only be used once. Store them securely and do not share them. 
                              If you lose access to your passkeys, these codes will allow you to recover your account.
                            </p>
                          </div>
                        </div>
                      </div>

                      {showBackupCodes && (
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                          {backupCodes.map((code, index) => (
                            <div
                              key={code.id}
                              className={`p-3 rounded-lg border font-mono text-sm text-center ${
                                code.used
                                  ? 'bg-red-500/10 border-red-500/20 text-red-400 line-through'
                                  : 'bg-trinity-guardian/10 border-trinity-guardian/20 text-trinity-guardian'
                              }`}
                            >
                              {code.code}
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="text-sm text-white/60">
                          {backupCodes.filter(c => !c.used).length} of {backupCodes.length} codes remaining
                        </div>
                        {!showBackupCodes && (
                          <button
                            onClick={() => setShowBackupCodes(true)}
                            className="text-sm text-trinity-guardian hover:text-trinity-consciousness transition-colors"
                          >
                            Show codes
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Sessions Tab */}
            {activeTab === 'sessions' && (
              <div className="space-y-6">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <div className="flex items-center mb-6">
                    <ComputerDesktopIcon className="w-6 h-6 text-trinity-consciousness mr-3" />
                    <h2 className="text-xl font-medium text-white">Active Sessions</h2>
                  </div>

                  <div className="space-y-4">
                    {sessions.length === 0 ? (
                      <div className="text-center py-8 text-white/60">
                        <ComputerDesktopIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                        <p>No active sessions</p>
                      </div>
                    ) : (
                      sessions.map((session) => (
                        <div key={session.id} className="flex items-center justify-between p-4 bg-black/20 rounded-lg border border-white/10">
                          <div className="flex items-center space-x-4">
                            <div className="p-2 bg-trinity-consciousness/20 rounded-lg">
                              {getDeviceIcon('', session.userAgent)}
                            </div>
                            <div>
                              <div className="flex items-center space-x-2">
                                <h3 className="text-white font-medium">
                                  {session.userAgent.split(' ')[0] || 'Unknown Browser'}
                                </h3>
                                {session.current && (
                                  <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                                    Current
                                  </span>
                                )}
                              </div>
                              <div className="text-sm text-white/60 space-y-1">
                                <p>IP: {session.ipAddress}</p>
                                <p>Created: {formatDate(session.createdAt)}</p>
                                <p>Last access: {formatDate(session.lastAccessAt)}</p>
                              </div>
                            </div>
                          </div>
                          {!session.current && (
                            <button
                              onClick={() => handleRevokeSession(session.id)}
                              disabled={deletingItem === session.id}
                              className="px-3 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                            >
                              Revoke
                            </button>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Security Activity Tab */}
            {activeTab === 'activity' && (
              <div className="space-y-6">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <div className="flex items-center mb-6">
                    <ClockIcon className="w-6 h-6 text-white mr-3" />
                    <h2 className="text-xl font-medium text-white">Recent Security Activity</h2>
                  </div>

                  <div className="space-y-3">
                    {securityEvents.length === 0 ? (
                      <div className="text-center py-8 text-white/60">
                        <DocumentTextIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                        <p>No recent security events</p>
                      </div>
                    ) : (
                      securityEvents.slice(0, 20).map((event) => (
                        <div key={event.id} className="flex items-start space-x-4 p-4 bg-black/20 rounded-lg border border-white/10">
                          <div className={`p-2 rounded-lg ${
                            event.result === 'success' 
                              ? 'bg-green-500/20 text-green-400' 
                              : 'bg-red-500/20 text-red-400'
                          }`}>
                            {event.result === 'success' ? (
                              <CheckCircleIcon className="w-4 h-4" />
                            ) : (
                              <ExclamationTriangleIcon className="w-4 h-4" />
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h3 className="text-white font-medium">{event.type.replace(/_/g, ' ')}</h3>
                              <span className="text-sm text-white/60">{formatDate(event.timestamp)}</span>
                            </div>
                            <p className="text-white/60 text-sm mt-1">{event.description}</p>
                            <div className="text-xs text-white/50 mt-2">
                              IP: {event.ipAddress} • {event.userAgent.split(' ')[0]}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Tone Content */}
          <div className="text-xs text-white/40 leading-relaxed whitespace-pre-line">
            {toneContent}
          </div>
        </div>
      </main>

      {/* Transparency Box */}
      <div className="px-6 pb-6">
        <TransparencyBox
          capabilities={[
            "Passkey management with device identification and usage tracking",
            "Backup code generation and usage monitoring",
            "Active session management with device and location tracking",
            "Comprehensive security event audit trail",
            "Real-time authentication method configuration"
          ]}
          limitations={[
            "Cannot remove last remaining passkey for security",
            "Backup codes are single-use and cannot be recovered",
            "Security events retained for 90 days maximum",
            "Session information limited to IP and user agent",
            "Some operations require step-up authentication"
          ]}
          dependencies={[
            "WebAuthn API for passkey creation and management",
            "LUKHAS AI security event logging system",
            "Session management and tracking infrastructure",
            "Device fingerprinting for security analysis"
          ]}
          dataHandling={[
            "Passkey credentials encoded → GLYPH format for enhanced interoperability (data representation, not cryptographic security)",
            "Backup codes hashed and stored with usage tracking",
            "Security events logged with IP address and device info",
            "Session data encrypted and automatically expired",
            "All security operations audited for compliance"
          ]}
          className="max-w-6xl mx-auto"
        />
      </div>
    </div>
    </>
  )
}