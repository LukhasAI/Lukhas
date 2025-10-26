'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ChevronLeftIcon, 
  ShieldCheckIcon, 
  UserGroupIcon,
  PlusIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  KeyIcon,
  DevicePhoneMobileIcon,
  EnvelopeIcon,
  ExclamationCircleIcon,
  CogIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// Interfaces
interface Guardian {
  id: string
  email: string
  phoneNumber?: string
  relationship: 'FAMILY' | 'FRIEND' | 'COLLEAGUE' | 'PROFESSIONAL'
  status: 'PENDING' | 'ACTIVE' | 'REVOKED' | 'UNRESPONSIVE'
  enrolledAt: string
  lastContactedAt?: string
  responseRate: number
  verificationChallenge: {
    question: string
    // answerHash is not exposed to frontend for security
  }
}

interface RecoveryAttempt {
  id: string
  initiatedAt: string
  status: 'PENDING' | 'APPROVED' | 'DENIED' | 'EXPIRED' | 'COMPLETED'
  justification: string
  requiredApprovals: number
  receivedApprovals: number
  guardianResponses: {
    guardianId: string
    guardianEmail: string
    status: 'PENDING' | 'APPROVED' | 'DENIED'
    respondedAt?: string
  }[]
  completedAt?: string
  cooldownUntil?: string
}

interface GuardianConfig {
  minGuardians: number
  maxGuardians: number
  requiredApprovals: number
  approvalWindow: number // hours
  cooloffPeriod: number // hours
  emergencyOverride: boolean
}

export default function GuardiansPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  // Guardian data
  const [guardians, setGuardians] = useState<Guardian[]>([])
  const [recoveryAttempts, setRecoveryAttempts] = useState<RecoveryAttempt[]>([])
  const [guardianConfig, setGuardianConfig] = useState<GuardianConfig | null>(null)
  
  // UI state
  const [activeTab, setActiveTab] = useState<'guardians' | 'recovery' | 'config'>('guardians')
  const [showAddGuardian, setShowAddGuardian] = useState(false)
  const [newGuardianData, setNewGuardianData] = useState({
    email: '',
    phoneNumber: '',
    relationship: 'FRIEND' as Guardian['relationship'],
    securityQuestion: '',
    securityAnswer: ''
  })
  const [deletingGuardian, setDeletingGuardian] = useState<string | null>(null)

  // Load guardian data (stub)
  useEffect(() => {
    const loadGuardianData = async () => {
      try {
        // Stub data - in real implementation, these would be API calls
        setGuardians([
          {
            id: 'guardian-1',
            email: 'trusted.contact@example.com',
            phoneNumber: '+1234567890',
            relationship: 'FAMILY',
            status: 'ACTIVE',
            enrolledAt: '2025-08-01T10:00:00Z',
            lastContactedAt: '2025-08-20T15:30:00Z',
            responseRate: 100,
            verificationChallenge: {
              question: 'What was the name of our first pet?'
            }
          },
          {
            id: 'guardian-2',
            email: 'backup.guardian@example.com',
            relationship: 'COLLEAGUE',
            status: 'ACTIVE',
            enrolledAt: '2025-08-10T14:20:00Z',
            lastContactedAt: '2025-08-18T09:15:00Z',
            responseRate: 85,
            verificationChallenge: {
              question: 'What company did we work at together?'
            }
          },
          {
            id: 'guardian-3',
            email: 'emergency.contact@example.com',
            relationship: 'PROFESSIONAL',
            status: 'PENDING',
            enrolledAt: '2025-08-22T08:45:00Z',
            responseRate: 0,
            verificationChallenge: {
              question: 'What is our shared professional certification?'
            }
          }
        ])

        setRecoveryAttempts([
          {
            id: 'recovery-1',
            initiatedAt: '2025-08-20T16:00:00Z',
            status: 'COMPLETED',
            justification: 'Lost access to primary device and backup codes',
            requiredApprovals: 2,
            receivedApprovals: 2,
            guardianResponses: [
              {
                guardianId: 'guardian-1',
                guardianEmail: 'trusted.contact@example.com',
                status: 'APPROVED',
                respondedAt: '2025-08-20T16:15:00Z'
              },
              {
                guardianId: 'guardian-2',
                guardianEmail: 'backup.guardian@example.com',
                status: 'APPROVED',
                respondedAt: '2025-08-20T16:45:00Z'
              }
            ],
            completedAt: '2025-08-20T17:00:00Z'
          }
        ])

        setGuardianConfig({
          minGuardians: 2,
          maxGuardians: 5,
          requiredApprovals: 2,
          approvalWindow: 72,
          cooloffPeriod: 24,
          emergencyOverride: false
        })

      } catch (err) {
        setError('Failed to load guardian data')
      } finally {
        setLoading(false)
      }
    }

    loadGuardianData()
  }, [])

  // Add new guardian
  const handleAddGuardian = useCallback(async () => {
    if (!newGuardianData.email.trim()) {
      setError('Guardian email is required')
      return
    }

    if (!newGuardianData.securityQuestion.trim() || !newGuardianData.securityAnswer.trim()) {
      setError('Security question and answer are required')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Stub implementation - would call API
      const newGuardian: Guardian = {
        id: `guardian-${Date.now()}`,
        email: newGuardianData.email.trim(),
        phoneNumber: newGuardianData.phoneNumber.trim() || undefined,
        relationship: newGuardianData.relationship,
        status: 'PENDING',
        enrolledAt: new Date().toISOString(),
        responseRate: 0,
        verificationChallenge: {
          question: newGuardianData.securityQuestion.trim()
        }
      }

      setGuardians(prev => [...prev, newGuardian])
      setNewGuardianData({
        email: '',
        phoneNumber: '',
        relationship: 'FRIEND',
        securityQuestion: '',
        securityAnswer: ''
      })
      setShowAddGuardian(false)
      setSuccess('Guardian invitation sent successfully')
      setTimeout(() => setSuccess(''), 3000)

      console.log('[GUARDIAN STUB]', JSON.stringify({
        event: 'guardian_added',
        guardianId: newGuardian.id,
        email: newGuardian.email,
        relationship: newGuardian.relationship,
        timestamp: new Date().toISOString()
      }))

    } catch (err) {
      setError('Failed to add guardian')
    } finally {
      setLoading(false)
    }
  }, [newGuardianData])

  // Remove guardian
  const handleRemoveGuardian = useCallback(async (guardianId: string) => {
    if (guardians.filter(g => g.status === 'ACTIVE').length <= guardianConfig?.minGuardians!) {
      setError('Cannot remove guardian - minimum guardians required')
      return
    }

    setDeletingGuardian(guardianId)
    setError('')

    try {
      // Stub implementation
      setGuardians(prev => prev.filter(g => g.id !== guardianId))
      setSuccess('Guardian removed successfully')
      setTimeout(() => setSuccess(''), 3000)

      console.log('[GUARDIAN STUB]', JSON.stringify({
        event: 'guardian_removed',
        guardianId,
        timestamp: new Date().toISOString()
      }))

    } catch (err) {
      setError('Failed to remove guardian')
    } finally {
      setDeletingGuardian(null)
    }
  }, [guardians, guardianConfig])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getStatusColor = (status: Guardian['status'] | RecoveryAttempt['status']) => {
    switch (status) {
      case 'ACTIVE':
      case 'APPROVED':
      case 'COMPLETED':
        return 'text-green-400 bg-green-500/20'
      case 'PENDING':
        return 'text-yellow-400 bg-yellow-500/20'
      case 'REVOKED':
      case 'DENIED':
      case 'EXPIRED':
        return 'text-red-400 bg-red-500/20'
      case 'UNRESPONSIVE':
        return 'text-gray-400 bg-gray-500/20'
      default:
        return 'text-white/60 bg-white/10'
    }
  }

  const getRelationshipIcon = (relationship: Guardian['relationship']) => {
    switch (relationship) {
      case 'FAMILY':
        return <UserGroupIcon className="w-5 h-5" />
      case 'PROFESSIONAL':
        return <CogIcon className="w-5 h-5" />
      default:
        return <UserGroupIcon className="w-5 h-5" />
    }
  }

  const toneContent = threeLayerTone(
    "Trust manifests through chosen allies; guardians weave the safety net when digital keys scatter like leaves in autumn wind.",
    "Manage your account recovery guardians - trusted contacts who can help restore access if you lose your authentication methods. Configure guardian policies and monitor recovery attempts through a secure, distributed approval system.",
    "Guardian-based account recovery with 2-of-N approval requirements. Email and phone verification with security challenge validation. Progressive cool-off periods and rate limiting prevent abuse. Emergency override capabilities with audit trails. Real-time status monitoring and response tracking for all guardian interactions."
  )

  // JSON-LD structured data for guardians page
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "LUKHAS AI Account Recovery Guardians",
    "description": "Manage trusted contacts for secure account recovery with distributed guardian approval system",
    "provider": {
      "@type": "Organization",
      "name": "LUKHAS AI",
      "description": "Advanced AI platform with quantum-inspired consciousness and bio-inspired adaptation"
    },
    "potentialAction": [
      {
        "@type": "UpdateAction",
        "name": "Manage Guardians",
        "description": "Add, remove, or configure trusted recovery guardians"
      },
      {
        "@type": "MonitorAction",
        "name": "Recovery Monitoring",
        "description": "Track recovery attempts and guardian responses"
      },
      {
        "@type": "ConfigureAction",
        "name": "Guardian Configuration",
        "description": "Set guardian policies and approval requirements"
      }
    ]
  }

  if (loading && guardians.length === 0) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="animate-pulse text-white/60">Loading guardian settings...</div>
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
            <Link href="/settings/security" className="flex items-center text-white/80 hover:text-white transition-colors">
              <ChevronLeftIcon className="w-5 h-5 mr-2" />
              Back to security
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
              <h1 className="text-2xl font-light text-white mb-2">Account Recovery Guardians</h1>
              <p className="text-white/60">Manage trusted contacts who can help recover your account if you lose access</p>
              
              {/* Feature Flag Notice */}
              <div className="mt-4 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <div className="flex items-start">
                  <ExclamationCircleIcon className="w-5 h-5 text-blue-400 mr-3 mt-0.5" />
                  <div>
                    <p className="text-blue-400 font-medium mb-1">Preview Feature</p>
                    <p className="text-white/60 text-sm">
                      Guardian-based recovery is currently in development. This interface shows planned functionality.
                      Expected availability: Q4 2025. Current recovery options remain available through support.
                    </p>
                  </div>
                </div>
              </div>
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

            {/* Guardian Configuration Summary */}
            {guardianConfig && (
              <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <ShieldCheckIcon className="w-6 h-6 text-trinity-guardian mr-3" />
                  <h2 className="text-xl font-medium text-white">Recovery Policy</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-trinity-guardian">{guardianConfig.requiredApprovals}</div>
                    <div className="text-sm text-white/60">Required Approvals</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-trinity-consciousness">{guardianConfig.approvalWindow}h</div>
                    <div className="text-sm text-white/60">Approval Window</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-trinity-identity">{guardianConfig.cooloffPeriod}h</div>
                    <div className="text-sm text-white/60">Cool-off Period</div>
                  </div>
                </div>
              </div>
            )}

            {/* Tab Navigation */}
            <div className="border-b border-white/10">
              <nav className="-mb-px flex space-x-8">
                {[
                  { id: 'guardians', label: 'Guardians', icon: UserGroupIcon },
                  { id: 'recovery', label: 'Recovery History', icon: ClockIcon },
                  { id: 'config', label: 'Configuration', icon: CogIcon }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-trinity-guardian text-trinity-guardian'
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
              {/* Guardians Tab */}
              {activeTab === 'guardians' && (
                <div className="space-y-6">
                  <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center">
                        <UserGroupIcon className="w-6 h-6 text-trinity-guardian mr-3" />
                        <h2 className="text-xl font-medium text-white">Trusted Guardians</h2>
                      </div>
                      <button
                        onClick={() => setShowAddGuardian(true)}
                        disabled={guardians.length >= (guardianConfig?.maxGuardians || 5)}
                        className="flex items-center px-4 py-2 bg-trinity-guardian hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <PlusIcon className="w-4 h-4 mr-2" />
                        Add Guardian
                      </button>
                    </div>

                    {/* Add Guardian Form */}
                    {showAddGuardian && (
                      <div className="mb-6 p-4 bg-black/20 rounded-lg border border-white/10">
                        <h3 className="text-lg font-medium text-white mb-4">Add New Guardian</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-white/80 mb-2">Email *</label>
                            <input
                              type="email"
                              value={newGuardianData.email}
                              onChange={(e) => setNewGuardianData(prev => ({ ...prev, email: e.target.value }))}
                              className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-guardian focus:border-transparent"
                              placeholder="guardian@example.com"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-white/80 mb-2">Phone (Optional)</label>
                            <input
                              type="tel"
                              value={newGuardianData.phoneNumber}
                              onChange={(e) => setNewGuardianData(prev => ({ ...prev, phoneNumber: e.target.value }))}
                              className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-guardian focus:border-transparent"
                              placeholder="+1234567890"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-white/80 mb-2">Relationship *</label>
                            <select
                              value={newGuardianData.relationship}
                              onChange={(e) => setNewGuardianData(prev => ({ ...prev, relationship: e.target.value as Guardian['relationship'] }))}
                              className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-trinity-guardian focus:border-transparent"
                            >
                              <option value="FAMILY">Family</option>
                              <option value="FRIEND">Friend</option>
                              <option value="COLLEAGUE">Colleague</option>
                              <option value="PROFESSIONAL">Professional</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-white/80 mb-2">Security Question *</label>
                            <input
                              type="text"
                              value={newGuardianData.securityQuestion}
                              onChange={(e) => setNewGuardianData(prev => ({ ...prev, securityQuestion: e.target.value }))}
                              className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-guardian focus:border-transparent"
                              placeholder="What city did we meet in?"
                            />
                          </div>
                          <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-white/80 mb-2">Security Answer *</label>
                            <input
                              type="text"
                              value={newGuardianData.securityAnswer}
                              onChange={(e) => setNewGuardianData(prev => ({ ...prev, securityAnswer: e.target.value }))}
                              className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-guardian focus:border-transparent"
                              placeholder="Enter the answer only you and the guardian would know"
                            />
                          </div>
                        </div>
                        <div className="flex justify-end space-x-3 mt-4">
                          <button
                            onClick={() => setShowAddGuardian(false)}
                            className="px-4 py-2 text-white/80 hover:text-white transition-colors"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={handleAddGuardian}
                            disabled={loading}
                            className="px-4 py-2 bg-trinity-guardian hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium disabled:opacity-50"
                          >
                            Add Guardian
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Guardians List */}
                    <div className="space-y-4">
                      {guardians.length === 0 ? (
                        <div className="text-center py-8 text-white/60">
                          <UserGroupIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                          <p>No guardians configured</p>
                          <p className="text-sm">Add trusted contacts to enable account recovery</p>
                        </div>
                      ) : (
                        guardians.map((guardian) => (
                          <div key={guardian.id} className="flex items-center justify-between p-4 bg-black/20 rounded-lg border border-white/10">
                            <div className="flex items-center space-x-4">
                              <div className="p-2 bg-trinity-guardian/20 rounded-lg">
                                {getRelationshipIcon(guardian.relationship)}
                              </div>
                              <div>
                                <div className="flex items-center space-x-3">
                                  <h3 className="text-white font-medium">{guardian.email}</h3>
                                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(guardian.status)}`}>
                                    {guardian.status}
                                  </span>
                                </div>
                                <div className="text-sm text-white/60 space-y-1">
                                  <p>Relationship: {guardian.relationship.toLowerCase()}</p>
                                  <p>Enrolled: {formatDate(guardian.enrolledAt)}</p>
                                  <p>Response rate: {guardian.responseRate}%</p>
                                  {guardian.phoneNumber && (
                                    <p>Phone: {guardian.phoneNumber}</p>
                                  )}
                                  <p className="text-xs italic">Question: "{guardian.verificationChallenge.question}"</p>
                                </div>
                              </div>
                            </div>
                            <button
                              onClick={() => handleRemoveGuardian(guardian.id)}
                              disabled={deletingGuardian === guardian.id || 
                                       guardians.filter(g => g.status === 'ACTIVE').length <= (guardianConfig?.minGuardians || 2)}
                              className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                              title={guardians.filter(g => g.status === 'ACTIVE').length <= (guardianConfig?.minGuardians || 2) 
                                     ? "Cannot remove - minimum guardians required" 
                                     : "Remove guardian"}
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

              {/* Recovery History Tab */}
              {activeTab === 'recovery' && (
                <div className="space-y-6">
                  <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                    <div className="flex items-center mb-6">
                      <ClockIcon className="w-6 h-6 text-trinity-consciousness mr-3" />
                      <h2 className="text-xl font-medium text-white">Recovery Attempts</h2>
                    </div>

                    <div className="space-y-4">
                      {recoveryAttempts.length === 0 ? (
                        <div className="text-center py-8 text-white/60">
                          <ClockIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                          <p>No recovery attempts</p>
                          <p className="text-sm">Recovery history will appear here</p>
                        </div>
                      ) : (
                        recoveryAttempts.map((attempt) => (
                          <div key={attempt.id} className="p-4 bg-black/20 rounded-lg border border-white/10">
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center space-x-3">
                                <span className={`px-3 py-1 rounded-full text-xs ${getStatusColor(attempt.status)}`}>
                                  {attempt.status}
                                </span>
                                <span className="text-white font-medium">
                                  {attempt.receivedApprovals}/{attempt.requiredApprovals} approvals
                                </span>
                              </div>
                              <span className="text-sm text-white/60">{formatDate(attempt.initiatedAt)}</span>
                            </div>
                            
                            <p className="text-white/80 mb-3">{attempt.justification}</p>
                            
                            <div className="space-y-2">
                              <h4 className="text-sm font-medium text-white/80">Guardian Responses:</h4>
                              {attempt.guardianResponses.map((response) => (
                                <div key={response.guardianId} className="flex items-center justify-between text-sm">
                                  <span className="text-white/60">{response.guardianEmail}</span>
                                  <div className="flex items-center space-x-2">
                                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(response.status)}`}>
                                      {response.status}
                                    </span>
                                    {response.respondedAt && (
                                      <span className="text-white/50 text-xs">{formatDate(response.respondedAt)}</span>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                            
                            {attempt.completedAt && (
                              <div className="mt-3 pt-3 border-t border-white/10 text-sm text-white/60">
                                Completed: {formatDate(attempt.completedAt)}
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Configuration Tab */}
              {activeTab === 'config' && (
                <div className="space-y-6">
                  <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                    <div className="flex items-center mb-6">
                      <CogIcon className="w-6 h-6 text-trinity-identity mr-3" />
                      <h2 className="text-xl font-medium text-white">Guardian Configuration</h2>
                    </div>

                    {guardianConfig && (
                      <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-4">
                            <h3 className="text-lg font-medium text-white">Policy Settings</h3>
                            
                            <div>
                              <label className="block text-sm font-medium text-white/80 mb-2">Required Guardians</label>
                              <div className="text-white/60 text-sm">
                                Minimum: {guardianConfig.minGuardians} • Maximum: {guardianConfig.maxGuardians}
                              </div>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-white/80 mb-2">Required Approvals</label>
                              <div className="text-white/60 text-sm">
                                {guardianConfig.requiredApprovals} out of {guardians.filter(g => g.status === 'ACTIVE').length} active guardians
                              </div>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-white/80 mb-2">Approval Window</label>
                              <div className="text-white/60 text-sm">
                                {guardianConfig.approvalWindow} hours for guardians to respond
                              </div>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-white/80 mb-2">Cool-off Period</label>
                              <div className="text-white/60 text-sm">
                                {guardianConfig.cooloffPeriod} hours between recovery attempts
                              </div>
                            </div>
                          </div>

                          <div className="space-y-4">
                            <h3 className="text-lg font-medium text-white">Security Features</h3>
                            
                            <div className="flex items-center justify-between p-3 bg-black/20 rounded-lg border border-white/10">
                              <div>
                                <div className="text-white font-medium">Emergency Override</div>
                                <div className="text-white/60 text-sm">Allow emergency recovery bypass</div>
                              </div>
                              <div className={`px-3 py-1 rounded-full text-xs ${
                                guardianConfig.emergencyOverride 
                                  ? 'text-green-400 bg-green-500/20' 
                                  : 'text-red-400 bg-red-500/20'
                              }`}>
                                {guardianConfig.emergencyOverride ? 'Enabled' : 'Disabled'}
                              </div>
                            </div>

                            <div className="p-3 bg-black/20 rounded-lg border border-white/10">
                              <div className="text-white font-medium mb-2">Rate Limiting</div>
                              <div className="text-white/60 text-sm space-y-1">
                                <p>• Maximum 3 recovery attempts per 30 days</p>
                                <p>• Progressive delays: 24h, 72h, 7 days</p>
                                <p>• IP and device tracking enabled</p>
                              </div>
                            </div>

                            <div className="p-3 bg-black/20 rounded-lg border border-white/10">
                              <div className="text-white font-medium mb-2">Verification Methods</div>
                              <div className="text-white/60 text-sm space-y-1">
                                <p>• Email link verification required</p>
                                <p>• Security question validation</p>
                                <p>• Multi-factor confirmation</p>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                          <div className="flex items-start">
                            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-400 mr-3 mt-0.5" />
                            <div>
                              <p className="text-yellow-400 font-medium mb-1">Configuration Notice</p>
                              <p className="text-white/60 text-sm">
                                Guardian configuration is currently managed by system policies. 
                                Custom configuration options will be available in the production release.
                                Contact support for specific requirements or enterprise customization.
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
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
              "Guardian enrollment with email and phone verification",
              "Security challenge validation with encrypted answer storage",
              "2-of-N approval system with configurable thresholds", 
              "Real-time recovery attempt monitoring and status tracking",
              "Progressive cool-off periods and rate limiting protection"
            ]}
            limitations={[
              "Currently in development - preview interface only",
              "Minimum guardian requirements cannot be bypassed",
              "Security questions and answers are not recoverable",
              "Guardian responses expire after 72 hours by default",
              "Emergency overrides require manual security team approval"
            ]}
            dependencies={[
              "LUKHAS AI guardian notification service",
              "Email delivery infrastructure for guardian communications",
              "Encrypted storage for security challenge data",
              "Rate limiting and abuse detection systems",
              "Audit logging for all recovery-related activities"
            ]}
            dataHandling={[
              "Guardian contact information encrypted at rest",
              "Security challenge answers cryptographically hashed",
              "Recovery attempts logged with IP and device tracking",
              "All guardian interactions audited for compliance",
              "Personal data minimization in guardian communications"
            ]}
            className="max-w-6xl mx-auto"
          />
        </div>
      </div>
    </>
  )
}