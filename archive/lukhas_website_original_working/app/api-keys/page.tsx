'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ChevronLeftIcon, 
  KeyIcon, 
  PlusIcon, 
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  ClipboardDocumentIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// Interfaces
interface ApiKey {
  id: string
  name: string
  description?: string
  key: string // Only shown during creation
  keyPrefix: string // Always shown (first 8 chars)
  scopes: string[]
  tier: string
  rateLimits: {
    requestsPerMinute: number
    requestsPerHour: number
    requestsPerDay: number
  }
  createdAt: string
  lastUsedAt: string | null
  isActive: boolean
  expiresAt: string | null
}

interface ApiKeyUsage {
  keyId: string
  requestsToday: number
  requestsThisHour: number
  requestsThisMinute: number
  lastEndpoint: string
  lastUserAgent: string
}

interface ScopeTemplate {
  name: string
  description: string
  scopes: string[]
  minTier: string
}

const SCOPE_TEMPLATES: ScopeTemplate[] = [
  {
    name: 'Read Only',
    description: 'Basic read access to your data',
    scopes: ['user:read', 'matrix:read'],
    minTier: 'T1'
  },
  {
    name: 'Full Access',
    description: 'Complete access to all features',
    scopes: ['user:read', 'user:write', 'matrix:read', 'matrix:write', 'consciousness:read'],
    minTier: 'T2'
  },
  {
    name: 'Organization Admin',
    description: 'Manage organization resources',
    scopes: ['user:read', 'matrix:read', 'matrix:write', 'org:read', 'org:write', 'team:read', 'team:write'],
    minTier: 'T3'
  },
  {
    name: 'Enterprise',
    description: 'Full enterprise access including consciousness',
    scopes: ['*'],
    minTier: 'T4'
  }
]

export default function ApiKeysPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [userTier, setUserTier] = useState<string>('')
  
  // API Keys data
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [usage, setUsage] = useState<Record<string, ApiKeyUsage>>({})
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null)
  
  // Step-up authentication
  const [stepUpRequired, setStepUpRequired] = useState(false)
  const [stepUpCompleted, setStepUpCompleted] = useState(false)
  
  // Form state
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [keyName, setKeyName] = useState('')
  const [keyDescription, setKeyDescription] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [customScopes, setCustomScopes] = useState<string[]>([])
  const [expirationDays, setExpirationDays] = useState<number>(365)
  
  // UI state
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set())
  const [deletingKey, setDeletingKey] = useState<string | null>(null)

  // Load data and check step-up requirement
  useEffect(() => {
    const loadData = async () => {
      try {
        // Check user profile
        const profileRes = await fetch('/api/user/profile', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        })

        if (!profileRes.ok) {
          if (profileRes.status === 401) {
            router.push('/login')
            return
          }
          throw new Error('Failed to load profile')
        }

        const profile = await profileRes.json()
        setUserTier(profile.user.tier)

        // Check if step-up authentication is required
        const stepUpRes = await fetch('/api/auth/step-up/required', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
          },
          body: JSON.stringify({ action: 'api_key_management' })
        })

        if (stepUpRes.ok) {
          const stepUpData = await stepUpRes.json()
          setStepUpRequired(stepUpData.required)
          
          if (!stepUpData.required) {
            setStepUpCompleted(true)
            await loadApiKeys()
          }
        }

      } catch (err) {
        setError('Failed to load API keys data')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [router])

  const loadApiKeys = async () => {
    try {
      const [keysRes, usageRes] = await Promise.all([
        fetch('/api/user/api-keys', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        }),
        fetch('/api/user/api-keys/usage', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        })
      ])

      if (keysRes.ok) {
        const data = await keysRes.json()
        setApiKeys(data.keys || [])
      }

      if (usageRes.ok) {
        const data = await usageRes.json()
        const usageMap: Record<string, ApiKeyUsage> = {}
        data.usage?.forEach((u: ApiKeyUsage) => {
          usageMap[u.keyId] = u
        })
        setUsage(usageMap)
      }

    } catch (err) {
      setError('Failed to load API keys')
    }
  }

  // Handle step-up authentication
  const handleStepUpAuth = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      // Request step-up authentication (this would typically involve biometric auth)
      const response = await fetch('/api/auth/step-up/authenticate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({ action: 'api_key_management' })
      })

      if (response.ok) {
        setStepUpCompleted(true)
        setStepUpRequired(false)
        await loadApiKeys()
        setSuccess('Step-up authentication completed')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Step-up authentication failed')
      }
    } catch (err) {
      setError('Network error during step-up authentication')
    } finally {
      setLoading(false)
    }
  }, [])

  // Create API key
  const handleCreateApiKey = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!keyName.trim()) {
      setError('API key name is required')
      return
    }

    let scopes: string[] = []
    if (selectedTemplate) {
      const template = SCOPE_TEMPLATES.find(t => t.name === selectedTemplate)
      if (template) {
        scopes = template.scopes
      }
    } else {
      scopes = customScopes
    }

    if (scopes.length === 0) {
      setError('At least one scope is required')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/user/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({
          name: keyName.trim(),
          description: keyDescription.trim() || undefined,
          scopes,
          expiresAt: expirationDays > 0 ? new Date(Date.now() + expirationDays * 24 * 60 * 60 * 1000).toISOString() : null
        })
      })

      if (response.ok) {
        const data = await response.json()
        setApiKeys(prev => [...prev, data.key])
        setNewlyCreatedKey(data.key.key) // Store full key for display
        setKeyName('')
        setKeyDescription('')
        setSelectedTemplate('')
        setCustomScopes([])
        setExpirationDays(365)
        setShowCreateForm(false)
        setSuccess('API key created successfully')
        setTimeout(() => setSuccess(''), 5000)
      } else {
        const error = await response.json()
        setError(error.message || 'Failed to create API key')
      }
    } catch (err) {
      setError('Network error creating API key')
    } finally {
      setLoading(false)
    }
  }, [keyName, keyDescription, selectedTemplate, customScopes, expirationDays])

  // Delete API key
  const handleDeleteApiKey = useCallback(async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }

    setDeletingKey(keyId)
    setError('')

    try {
      const response = await fetch(`/api/user/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        }
      })

      if (response.ok) {
        setApiKeys(prev => prev.filter(k => k.id !== keyId))
        setSuccess('API key deleted successfully')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to delete API key')
      }
    } catch (err) {
      setError('Network error deleting API key')
    } finally {
      setDeletingKey(null)
    }
  }, [])

  // Toggle key visibility
  const toggleKeyVisibility = (keyId: string) => {
    setVisibleKeys(prev => {
      const newSet = new Set(prev)
      if (newSet.has(keyId)) {
        newSet.delete(keyId)
      } else {
        newSet.add(keyId)
      }
      return newSet
    })
  }

  // Copy to clipboard
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setSuccess('Copied to clipboard')
      setTimeout(() => setSuccess(''), 2000)
    } catch (err) {
      setError('Failed to copy to clipboard')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getRateLimitColor = (used: number, limit: number) => {
    const ratio = used / limit
    if (ratio >= 0.9) return 'text-red-400'
    if (ratio >= 0.7) return 'text-yellow-400'
    return 'text-green-400'
  }

  const toneContent = threeLayerTone(
    "Keys unlock possibilities; each permission a doorway to consciousness integration.",
    "Create and manage API keys for LUKHAS AI services. Requires step-up authentication for security.",
    "API key management with step-up authentication requirement. Scope-based permissions with tier-based limits. Rate limiting and usage monitoring. Automatic expiration and security controls."
  )

  // Step-up authentication required
  if (stepUpRequired && !stepUpCompleted) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="max-w-md text-center">
          <ShieldCheckIcon className="w-16 h-16 text-trinity-guardian mx-auto mb-6" />
          <h1 className="text-2xl font-light text-white mb-4">Step-up Authentication Required</h1>
          <p className="text-white/60 mb-6">
            API key management requires additional authentication for security. 
            Please verify your identity to continue.
          </p>
          <div className="space-y-3">
            <button 
              onClick={handleStepUpAuth}
              disabled={loading}
              className="w-full px-6 py-3 bg-trinity-guardian hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium disabled:opacity-50"
            >
              {loading ? 'Authenticating...' : 'Authenticate with Passkey'}
            </button>
            <Link 
              href="/experience" 
              className="block w-full px-6 py-3 bg-black/40 hover:bg-black/60 transition-colors rounded-lg text-white font-medium"
            >
              Back to Experience
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="animate-pulse text-white/60">Loading API keys...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <Link href="/experience" className="flex items-center text-white/80 hover:text-white transition-colors">
            <ChevronLeftIcon className="w-5 h-5 mr-2" />
            Back to experience
          </Link>
          <div className="flex items-center space-x-6">
            <span className="text-sm text-white/60">Tier: {userTier}</span>
            <Link href="/settings/security" className="text-sm text-white/60 hover:text-white/80 transition-colors">
              Security Settings
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Page Title */}
          <div>
            <h1 className="text-2xl font-light text-white mb-2">API Keys</h1>
            <p className="text-white/60">Manage your LUKHAS AI API access keys</p>
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

          {/* Newly Created Key Display */}
          {newlyCreatedKey && (
            <div className="p-6 bg-green-500/10 border border-green-500/20 rounded-lg">
              <div className="flex items-center mb-4">
                <CheckCircleIcon className="w-6 h-6 text-green-400 mr-3" />
                <h3 className="text-lg font-medium text-white">API Key Created Successfully</h3>
              </div>
              <div className="bg-black/40 p-4 rounded-lg border border-white/10">
                <div className="flex items-center justify-between">
                  <code className="text-trinity-consciousness font-mono text-sm break-all">
                    {newlyCreatedKey}
                  </code>
                  <button
                    onClick={() => copyToClipboard(newlyCreatedKey)}
                    className="ml-4 p-2 text-trinity-consciousness hover:text-trinity-identity transition-colors"
                    title="Copy to clipboard"
                  >
                    <ClipboardDocumentIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <div className="flex items-start">
                  <ExclamationTriangleIcon className="w-5 h-5 text-yellow-400 mr-3 mt-0.5" />
                  <div>
                    <p className="text-yellow-400 font-medium mb-1">Save this key securely</p>
                    <p className="text-white/60 text-sm">
                      This is the only time you'll see the full key. Store it securely and do not share it.
                    </p>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setNewlyCreatedKey(null)}
                className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 transition-colors rounded-lg text-white text-sm font-medium"
              >
                I've saved the key
              </button>
            </div>
          )}

          {/* API Keys List */}
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <KeyIcon className="w-6 h-6 text-trinity-identity mr-3" />
                <h2 className="text-xl font-medium text-white">Your API Keys</h2>
              </div>
              <button
                onClick={() => setShowCreateForm(true)}
                className="flex items-center px-4 py-2 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Create API Key
              </button>
            </div>

            <div className="space-y-4">
              {apiKeys.length === 0 ? (
                <div className="text-center py-12 text-white/60">
                  <KeyIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                  <p className="text-lg mb-2">No API keys</p>
                  <p className="text-sm">Create your first API key to start using the LUKHAS AI API</p>
                </div>
              ) : (
                apiKeys.map((key) => (
                  <div key={key.id} className="p-4 bg-black/20 rounded-lg border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-white font-medium">{key.name}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            key.isActive ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                          }`}>
                            {key.isActive ? 'Active' : 'Inactive'}
                          </span>
                          <span className="px-2 py-1 bg-trinity-identity/20 text-trinity-identity rounded-full text-xs">
                            {key.tier}
                          </span>
                        </div>
                        {key.description && (
                          <p className="text-white/60 text-sm mb-2">{key.description}</p>
                        )}
                        <div className="text-sm text-white/60 space-y-1">
                          <p>Created: {formatDate(key.createdAt)}</p>
                          <p>Last used: {key.lastUsedAt ? formatDate(key.lastUsedAt) : 'Never'}</p>
                          {key.expiresAt && (
                            <p>Expires: {formatDate(key.expiresAt)}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => toggleKeyVisibility(key.id)}
                          className="p-2 text-white/60 hover:text-white transition-colors"
                          title={visibleKeys.has(key.id) ? "Hide key" : "Show key"}
                        >
                          {visibleKeys.has(key.id) ? (
                            <EyeSlashIcon className="w-4 h-4" />
                          ) : (
                            <EyeIcon className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={() => handleDeleteApiKey(key.id)}
                          disabled={deletingKey === key.id}
                          className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {/* Key Display */}
                    <div className="mb-4">
                      <div className="flex items-center space-x-2">
                        <code className="flex-1 px-3 py-2 bg-black/40 rounded border border-white/10 text-trinity-consciousness font-mono text-sm">
                          {visibleKeys.has(key.id) ? key.key || `${key.keyPrefix}${'*'.repeat(32)}` : `${key.keyPrefix}${'*'.repeat(32)}`}
                        </code>
                        <button
                          onClick={() => copyToClipboard(key.key || `${key.keyPrefix}${'*'.repeat(32)}`)}
                          className="p-2 text-trinity-consciousness hover:text-trinity-identity transition-colors"
                          title="Copy to clipboard"
                        >
                          <ClipboardDocumentIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {/* Scopes */}
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-white/80 mb-2">Scopes</h4>
                      <div className="flex flex-wrap gap-2">
                        {key.scopes.map((scope) => (
                          <span key={scope} className="px-2 py-1 bg-trinity-guardian/20 text-trinity-guardian rounded text-xs">
                            {scope}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Usage Stats */}
                    {usage[key.id] && (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="text-center">
                          <div className={`text-lg font-medium ${getRateLimitColor(usage[key.id].requestsThisMinute, key.rateLimits.requestsPerMinute)}`}>
                            {usage[key.id].requestsThisMinute}/{key.rateLimits.requestsPerMinute}
                          </div>
                          <div className="text-xs text-white/60">Requests/minute</div>
                        </div>
                        <div className="text-center">
                          <div className={`text-lg font-medium ${getRateLimitColor(usage[key.id].requestsThisHour, key.rateLimits.requestsPerHour)}`}>
                            {usage[key.id].requestsThisHour}/{key.rateLimits.requestsPerHour}
                          </div>
                          <div className="text-xs text-white/60">Requests/hour</div>
                        </div>
                        <div className="text-center">
                          <div className={`text-lg font-medium ${getRateLimitColor(usage[key.id].requestsToday, key.rateLimits.requestsPerDay)}`}>
                            {usage[key.id].requestsToday}/{key.rateLimits.requestsPerDay}
                          </div>
                          <div className="text-xs text-white/60">Requests/day</div>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Create API Key Form */}
          {showCreateForm && (
            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
              <h3 className="text-xl font-medium text-white mb-6">Create New API Key</h3>
              
              <form onSubmit={handleCreateApiKey} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="keyName" className="block text-sm font-medium text-white/80 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      id="keyName"
                      value={keyName}
                      onChange={(e) => setKeyName(e.target.value)}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                      placeholder="My API Key"
                      required
                    />
                  </div>
                  <div>
                    <label htmlFor="expirationDays" className="block text-sm font-medium text-white/80 mb-2">
                      Expires in (days)
                    </label>
                    <select
                      id="expirationDays"
                      value={expirationDays}
                      onChange={(e) => setExpirationDays(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                    >
                      <option value={30}>30 days</option>
                      <option value={90}>90 days</option>
                      <option value={365}>1 year</option>
                      <option value={0}>Never</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="keyDescription" className="block text-sm font-medium text-white/80 mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    id="keyDescription"
                    value={keyDescription}
                    onChange={(e) => setKeyDescription(e.target.value)}
                    className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                    placeholder="Description of what this key will be used for"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white/80 mb-4">Permissions</label>
                  <div className="space-y-3">
                    {SCOPE_TEMPLATES.map((template) => (
                      <div
                        key={template.name}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                          selectedTemplate === template.name
                            ? 'border-trinity-identity bg-trinity-identity/10'
                            : 'border-white/10 bg-black/20 hover:border-white/20'
                        }`}
                        onClick={() => setSelectedTemplate(template.name)}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-white font-medium">{template.name}</h4>
                            <p className="text-white/60 text-sm">{template.description}</p>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {template.scopes.map((scope) => (
                                <span key={scope} className="px-2 py-1 bg-trinity-guardian/20 text-trinity-guardian rounded text-xs">
                                  {scope}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="px-2 py-1 bg-trinity-identity/20 text-trinity-identity rounded text-xs">
                              {template.minTier}+
                            </span>
                            <input
                              type="radio"
                              name="template"
                              checked={selectedTemplate === template.name}
                              onChange={() => setSelectedTemplate(template.name)}
                              className="w-4 h-4 text-trinity-identity"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex space-x-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-6 py-3 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create API Key'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="px-6 py-3 bg-gray-600 hover:bg-gray-700 transition-colors rounded-lg text-white font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

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
            "API key creation with scope-based permissions",
            "Step-up authentication for security-sensitive operations",
            "Real-time usage monitoring and rate limit tracking",
            "Automatic key expiration and security controls",
            "Tier-based access control and feature gating"
          ]}
          limitations={[
            "Requires step-up authentication for all operations",
            "API keys shown in full only once during creation",
            "Rate limits enforced based on user tier",
            "Some advanced scopes require higher tier access",
            "Maximum key count limited by tier level"
          ]}
          dependencies={[
            "LUKHAS AI API infrastructure and rate limiting",
            "Step-up authentication system with passkey verification",
            "Usage monitoring and analytics pipeline",
            "Tier-based authorization and billing systems"
          ]}
          dataHandling={[
            "API keys encoded → GLYPH format before storage",
            "Usage data aggregated for monitoring without logging requests",
            "Key operations logged for security auditing",
            "Access patterns analyzed for abuse detection",
            "All sensitive operations require re-authentication"
          ]}
          className="max-w-6xl mx-auto"
        />
      </div>
    </div>
  )
}