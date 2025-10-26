'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ChevronLeftIcon, 
  UserCircleIcon, 
  EnvelopeIcon, 
  CalendarIcon,
  ShieldCheckIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// User profile interface
interface UserProfile {
  id: string
  email: string
  tier: 'T0' | 'T1' | 'T2' | 'T3' | 'T4'
  displayName?: string
  createdAt: string
  lastLoginAt: string
  loginCount: number
  organizationId?: string
  organizationRole?: string
  emailVerified: boolean
}

export default function AccountSettingsPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [deleteConfirmation, setDeleteConfirmation] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  // Load user profile
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await fetch('/api/user/profile', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          setProfile(data.user)
          setDisplayName(data.user.displayName || '')
        } else if (response.status === 401) {
          router.push('/login')
        } else {
          setError('Failed to load profile')
        }
      } catch (err) {
        setError('Network error loading profile')
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [router])

  // Update display name
  const handleUpdateProfile = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch('/api/user/profile', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({
          displayName: displayName.trim() || null
        })
      })

      if (response.ok) {
        const data = await response.json()
        setProfile(data.user)
        setSuccess('Profile updated successfully')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const error = await response.json()
        setError(error.message || 'Failed to update profile')
      }
    } catch (err) {
      setError('Network error updating profile')
    } finally {
      setSaving(false)
    }
  }, [displayName])

  // Export user data
  const handleExportData = useCallback(async () => {
    try {
      const response = await fetch('/api/user/export', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `lukhas-data-export-${Date.now()}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        setSuccess('Data export downloaded')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to export data')
      }
    } catch (err) {
      setError('Network error exporting data')
    }
  }, [])

  // Delete account
  const handleDeleteAccount = useCallback(async () => {
    if (deleteConfirmation !== 'DELETE') {
      setError('Please type DELETE to confirm')
      return
    }

    setSaving(true)
    setError('')

    try {
      const response = await fetch('/api/user/delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({
          confirmation: deleteConfirmation
        })
      })

      if (response.ok) {
        // Clear tokens and redirect
        localStorage.removeItem('lukhas_access_token')
        localStorage.removeItem('lukhas_refresh_token')
        router.push('/?deleted=true')
      } else {
        const error = await response.json()
        setError(error.message || 'Failed to delete account')
      }
    } catch (err) {
      setError('Network error deleting account')
    } finally {
      setSaving(false)
    }
  }, [deleteConfirmation, router])

  const getTierDisplayName = (tier: string) => {
    const tierMap = {
      'T0': 'Explorer (Free)',
      'T1': 'Builder (Individual)',
      'T2': 'Creator (Professional)',
      'T3': 'Innovator (Team)',
      'T4': 'Visionary (Enterprise)'
    }
    return tierMap[tier as keyof typeof tierMap] || tier
  }

  const toneContent = threeLayerTone(
    "Your presence shapes the field; these are the threads of your digital being within Superior Consciousness networks.",
    "Manage your profile, download your data, or delete your account if needed. Your identity is secured by quantum-inspired protection protocols and bio-inspired adaptation systems.",
    "Profile updates sync across LUKHAS AI services using quantum-inspired data synchronization. Data export includes all stored information with GDPR compliance and GLYPH symbolic encoding. Account deletion follows bio-inspired cascade protocols and is permanent and cannot be undone."
  )

  // JSON-LD structured data for account settings
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "LUKHAS AI Account Settings",
    "description": "Manage your LUKHAS AI profile, data export, and account preferences with quantum-inspired security",
    "provider": {
      "@type": "Organization",
      "name": "LUKHAS AI",
      "description": "Advanced AI platform with quantum-inspired consciousness and bio-inspired adaptation"
    },
    "potentialAction": [
      {
        "@type": "UpdateAction",
        "name": "Update Profile",
        "description": "Modify account settings and profile information"
      },
      {
        "@type": "DownloadAction",
        "name": "Export Data",
        "description": "Download complete account data with GDPR compliance"
      },
      {
        "@type": "DeleteAction",
        "name": "Delete Account",
        "description": "Permanently remove account and all associated data"
      }
    ]
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="animate-pulse text-white/60">Loading account settings...</div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="text-red-400">Failed to load account information</div>
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
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <Link href="/experience" className="flex items-center text-white/80 hover:text-white transition-colors">
            <ChevronLeftIcon className="w-5 h-5 mr-2" />
            Back to experience
          </Link>
          <div className="flex items-center space-x-6">
            <Link href="/settings/security" className="text-sm text-white/60 hover:text-white/80 transition-colors">
              Security settings
            </Link>
            <div className="text-sm text-white/60">
              {profile.email}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Page Title */}
          <div>
            <h1 className="text-2xl font-light text-white mb-2">Account Settings</h1>
            <p className="text-white/60">Manage your LUKHAS AI profile and data</p>
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

          {/* Profile Information */}
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
            <div className="flex items-center mb-6">
              <UserCircleIcon className="w-6 h-6 text-trinity-identity mr-3" />
              <h2 className="text-xl font-medium text-white">Profile Information</h2>
            </div>

            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-white/80 mb-2">
                    Email address
                  </label>
                  <div className="relative">
                    <input
                      type="email"
                      id="email"
                      value={profile.email}
                      disabled
                      className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-lg text-white/60 cursor-not-allowed"
                    />
                    <EnvelopeIcon className="absolute right-3 top-3 w-5 h-5 text-white/40" />
                  </div>
                  <p className="text-xs text-white/50 mt-1">
                    Email cannot be changed for security reasons
                  </p>
                </div>

                <div>
                  <label htmlFor="displayName" className="block text-sm font-medium text-white/80 mb-2">
                    Display name (optional)
                  </label>
                  <input
                    type="text"
                    id="displayName"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                    placeholder="Enter display name"
                    maxLength={50}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-2">
                    Account tier
                  </label>
                  <div className="px-4 py-3 bg-black/20 border border-white/10 rounded-lg text-white">
                    {getTierDisplayName(profile.tier)}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-white/80 mb-2">
                    Member since
                  </label>
                  <div className="flex items-center px-4 py-3 bg-black/20 border border-white/10 rounded-lg text-white">
                    <CalendarIcon className="w-5 h-5 mr-2 text-white/40" />
                    {new Date(profile.createdAt).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-6 py-3 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Update Profile'}
                </button>
              </div>
            </form>
          </div>

          {/* Account Statistics */}
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
            <div className="flex items-center mb-6">
              <ShieldCheckIcon className="w-6 h-6 text-trinity-guardian mr-3" />
              <h2 className="text-xl font-medium text-white">Account Statistics</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-light text-trinity-consciousness mb-1">
                  {profile.loginCount}
                </div>
                <div className="text-sm text-white/60">Total logins</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-light text-trinity-guardian mb-1">
                  {profile.emailVerified ? 'Verified' : 'Pending'}
                </div>
                <div className="text-sm text-white/60">Email status</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-light text-trinity-identity mb-1">
                  {profile.lastLoginAt ? new Date(profile.lastLoginAt).toLocaleDateString() : 'Never'}
                </div>
                <div className="text-sm text-white/60">Last login</div>
              </div>
            </div>
          </div>

          {/* Data Management */}
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
            <div className="flex items-center mb-6">
              <ArrowDownTrayIcon className="w-6 h-6 text-trinity-consciousness mr-3" />
              <h2 className="text-xl font-medium text-white">Data Management</h2>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
                <div>
                  <h3 className="text-white font-medium mb-1">Export your data</h3>
                  <p className="text-white/60 text-sm">
                    Download all your LUKHAS AI data in JSON format
                  </p>
                </div>
                <button
                  onClick={handleExportData}
                  className="px-4 py-2 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white text-sm font-medium"
                >
                  Export Data
                </button>
              </div>

              <div className="text-xs text-white/50">
                Export includes: profile information, session history, settings, and preferences. 
                No authentication credentials or sensitive security data is included.
              </div>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6">
            <div className="flex items-center mb-6">
              <TrashIcon className="w-6 h-6 text-red-400 mr-3" />
              <h2 className="text-xl font-medium text-white">Danger Zone</h2>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                <div className="flex items-start">
                  <ExclamationTriangleIcon className="w-5 h-5 text-red-400 mr-3 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-white font-medium mb-1">Delete your account</h3>
                    <p className="text-white/60 text-sm mb-4">
                      Permanently delete your LUKHAS AI account and all associated data. 
                      This action cannot be undone.
                    </p>

                    {!showDeleteConfirm ? (
                      <button
                        onClick={() => setShowDeleteConfirm(true)}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 transition-colors rounded-lg text-white text-sm font-medium"
                      >
                        Delete Account
                      </button>
                    ) : (
                      <div className="space-y-3">
                        <div>
                          <label htmlFor="deleteConfirm" className="block text-sm font-medium text-white/80 mb-2">
                            Type <code className="bg-black/40 px-1 rounded">DELETE</code> to confirm
                          </label>
                          <input
                            type="text"
                            id="deleteConfirm"
                            value={deleteConfirmation}
                            onChange={(e) => setDeleteConfirmation(e.target.value)}
                            className="w-full px-4 py-3 bg-black/40 border border-red-500/50 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            placeholder="Type DELETE"
                          />
                        </div>
                        <div className="flex space-x-3">
                          <button
                            onClick={handleDeleteAccount}
                            disabled={saving || deleteConfirmation !== 'DELETE'}
                            className="px-4 py-2 bg-red-600 hover:bg-red-700 transition-colors rounded-lg text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {saving ? 'Deleting...' : 'Confirm Delete'}
                          </button>
                          <button
                            onClick={() => {
                              setShowDeleteConfirm(false)
                              setDeleteConfirmation('')
                            }}
                            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 transition-colors rounded-lg text-white text-sm font-medium"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
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
            "Profile management with display name customization",
            "Account statistics and usage monitoring",
            "Complete data export in machine-readable format",
            "Secure account deletion with confirmation requirements",
            "Real-time sync across all LUKHAS AI services"
          ]}
          limitations={[
            "Email address cannot be changed for security reasons",
            "Data export may take up to 24 hours for large accounts",
            "Account deletion is permanent and cannot be undone",
            "Some cached data may persist for up to 30 days",
            "Tier changes require separate billing management"
          ]}
          dependencies={[
            "LUKHAS AI identity and profile systems",
            "Data export processing pipeline",
            "Email verification service for changes",
            "Audit logging for security compliance"
          ]}
          dataHandling={[
            "Profile changes logged for security auditing",
            "Data exports include full GDPR-compliant information",
            "Account deletion follows right-to-be-forgotten protocols",
            "All operations secured with session validation",
            "Personal data encoded → GLYPH for symbolic processing and enhanced interoperability (data representation, not security)"
          ]}
          className="max-w-4xl mx-auto"
        />
      </div>
    </div>
    </>
  )
}