'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ChevronLeftIcon, 
  BuildingOfficeIcon, 
  UserGroupIcon, 
  PlusIcon, 
  TrashIcon, 
  PencilIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  KeyIcon,
  CogIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// Interfaces
interface Organization {
  id: string
  name: string
  description?: string
  tier: 'T3' | 'T4'
  createdAt: string
  memberCount: number
  maxMembers: number
  userRole: 'owner' | 'admin' | 'member'
  settings: {
    requireStepUp: boolean
    allowMemberInvites: boolean
    enforcePasskeys: boolean
  }
}

interface Member {
  id: string
  email: string
  displayName?: string
  role: 'owner' | 'admin' | 'member'
  joinedAt: string
  lastActiveAt: string
  tier: string
}

interface Invitation {
  id: string
  email: string
  role: 'admin' | 'member'
  createdAt: string
  expiresAt: string
  invitedBy: string
}

export default function OrganizationsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [userTier, setUserTier] = useState<string>('')
  
  // Organization data
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null)
  const [members, setMembers] = useState<Member[]>([])
  const [invitations, setInvitations] = useState<Invitation[]>([])
  
  // UI state
  const [activeTab, setActiveTab] = useState<'overview' | 'members' | 'settings'>('overview')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showInviteForm, setShowInviteForm] = useState(false)
  const [orgName, setOrgName] = useState('')
  const [orgDescription, setOrgDescription] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<'admin' | 'member'>('member')

  // Check tier access and load data
  useEffect(() => {
    const loadData = async () => {
      try {
        // Check user tier
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

        // Check if user has access to organizations (T3+)
        if (!['T3', 'T4'].includes(profile.user.tier)) {
          setError('Organization management requires Innovator (T3) tier or higher')
          setLoading(false)
          return
        }

        // Load organizations
        const orgsRes = await fetch('/api/user/organizations', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        })

        if (orgsRes.ok) {
          const data = await orgsRes.json()
          setOrganizations(data.organizations || [])
          if (data.organizations?.length > 0) {
            setSelectedOrg(data.organizations[0])
          }
        }

      } catch (err) {
        setError('Failed to load organization data')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [router])

  // Load organization details when selected
  useEffect(() => {
    if (selectedOrg) {
      loadOrganizationDetails(selectedOrg.id)
    }
  }, [selectedOrg])

  const loadOrganizationDetails = async (orgId: string) => {
    try {
      const [membersRes, invitesRes] = await Promise.all([
        fetch(`/api/organizations/${orgId}/members`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        }),
        fetch(`/api/organizations/${orgId}/invitations`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        })
      ])

      if (membersRes.ok) {
        const data = await membersRes.json()
        setMembers(data.members || [])
      }

      if (invitesRes.ok) {
        const data = await invitesRes.json()
        setInvitations(data.invitations || [])
      }

    } catch (err) {
      console.error('Failed to load organization details:', err)
    }
  }

  // Create organization
  const handleCreateOrganization = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!orgName.trim()) {
      setError('Organization name is required')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/organizations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({
          name: orgName.trim(),
          description: orgDescription.trim() || undefined
        })
      })

      if (response.ok) {
        const data = await response.json()
        setOrganizations(prev => [...prev, data.organization])
        setSelectedOrg(data.organization)
        setOrgName('')
        setOrgDescription('')
        setShowCreateForm(false)
        setSuccess('Organization created successfully')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const error = await response.json()
        setError(error.message || 'Failed to create organization')
      }
    } catch (err) {
      setError('Network error creating organization')
    } finally {
      setLoading(false)
    }
  }, [orgName, orgDescription])

  // Invite member
  const handleInviteMember = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedOrg || !inviteEmail.trim()) {
      setError('Email is required')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`/api/organizations/${selectedOrg.id}/invitations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({
          email: inviteEmail.trim(),
          role: inviteRole
        })
      })

      if (response.ok) {
        const data = await response.json()
        setInvitations(prev => [...prev, data.invitation])
        setInviteEmail('')
        setShowInviteForm(false)
        setSuccess('Invitation sent successfully')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const error = await response.json()
        setError(error.message || 'Failed to send invitation')
      }
    } catch (err) {
      setError('Network error sending invitation')
    } finally {
      setLoading(false)
    }
  }, [selectedOrg, inviteEmail, inviteRole])

  // Remove member
  const handleRemoveMember = useCallback(async (memberId: string) => {
    if (!selectedOrg) return

    if (!confirm('Are you sure you want to remove this member?')) return

    try {
      const response = await fetch(`/api/organizations/${selectedOrg.id}/members/${memberId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
      })

      if (response.ok) {
        setMembers(prev => prev.filter(m => m.id !== memberId))
        setSuccess('Member removed successfully')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to remove member')
      }
    } catch (err) {
      setError('Network error removing member')
    }
  }, [selectedOrg])

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'owner': return 'text-yellow-400'
      case 'admin': return 'text-blue-400'
      case 'member': return 'text-green-400'
      default: return 'text-white/60'
    }
  }

  const toneContent = threeLayerTone(
    "Collective intelligence emerges; boundaries dissolve into collaborative flows.",
    "Create organizations, invite team members, and manage permissions. Requires T3+ tier access.",
    "Organization management with role-based access control. Member invitation system with email verification. Settings enforcement across team members. Tier-based feature gates."
  )

  // Tier access check
  if (!loading && !['T3', 'T4'].includes(userTier)) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="max-w-md text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-yellow-400 mx-auto mb-6" />
          <h1 className="text-2xl font-light text-white mb-4">Access Restricted</h1>
          <p className="text-white/60 mb-6">
            Organization management requires Innovator (T3) tier or higher. 
            Your current tier is {userTier}.
          </p>
          <div className="space-y-3">
            <Link 
              href="/pricing" 
              className="block w-full px-6 py-3 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium"
            >
              Upgrade to T3+
            </Link>
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
        <div className="animate-pulse text-white/60">Loading organizations...</div>
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
            <Link href="/teams" className="text-sm text-white/60 hover:text-white/80 transition-colors">
              Teams
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Organization List */}
          <div className="lg:col-span-1">
            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-medium text-white">Organizations</h2>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="p-2 text-trinity-identity hover:text-trinity-consciousness transition-colors"
                  title="Create organization"
                >
                  <PlusIcon className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-2">
                {organizations.length === 0 ? (
                  <div className="text-center py-8 text-white/60">
                    <BuildingOfficeIcon className="w-8 h-8 mx-auto mb-2 text-white/40" />
                    <p className="text-sm">No organizations</p>
                  </div>
                ) : (
                  organizations.map((org) => (
                    <button
                      key={org.id}
                      onClick={() => setSelectedOrg(org)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        selectedOrg?.id === org.id
                          ? 'bg-trinity-identity/20 border border-trinity-identity/30'
                          : 'bg-black/20 hover:bg-black/40 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <BuildingOfficeIcon className="w-5 h-5 text-trinity-identity" />
                        <div className="flex-1 min-w-0">
                          <h3 className="text-white font-medium truncate">{org.name}</h3>
                          <p className="text-white/60 text-sm">
                            {org.memberCount} members • {org.userRole}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Create Organization Form */}
            {showCreateForm && (
              <div className="mt-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                <h3 className="text-lg font-medium text-white mb-4">Create Organization</h3>
                <form onSubmit={handleCreateOrganization} className="space-y-4">
                  <div>
                    <label htmlFor="orgName" className="block text-sm font-medium text-white/80 mb-2">
                      Name
                    </label>
                    <input
                      type="text"
                      id="orgName"
                      value={orgName}
                      onChange={(e) => setOrgName(e.target.value)}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                      placeholder="Organization name"
                      required
                    />
                  </div>
                  <div>
                    <label htmlFor="orgDesc" className="block text-sm font-medium text-white/80 mb-2">
                      Description (optional)
                    </label>
                    <textarea
                      id="orgDesc"
                      value={orgDescription}
                      onChange={(e) => setOrgDescription(e.target.value)}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                      placeholder="Organization description"
                      rows={3}
                    />
                  </div>
                  <div className="flex space-x-3">
                    <button
                      type="submit"
                      disabled={loading}
                      className="flex-1 px-4 py-2 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium disabled:opacity-50"
                    >
                      Create
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateForm(false)}
                      className="px-4 py-2 bg-gray-600 hover:bg-gray-700 transition-colors rounded-lg text-white text-sm font-medium"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
            {selectedOrg ? (
              <div className="space-y-6">
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

                {/* Organization Header */}
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h1 className="text-2xl font-light text-white mb-2">{selectedOrg.name}</h1>
                      {selectedOrg.description && (
                        <p className="text-white/60">{selectedOrg.description}</p>
                      )}
                      <div className="flex items-center space-x-4 mt-4 text-sm text-white/60">
                        <span>Created: {new Date(selectedOrg.createdAt).toLocaleDateString()}</span>
                        <span>Tier: {selectedOrg.tier}</span>
                        <span>Members: {selectedOrg.memberCount}/{selectedOrg.maxMembers}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-3 py-1 rounded-full text-sm ${getRoleColor(selectedOrg.userRole)}`}>
                        {selectedOrg.userRole}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Tab Navigation */}
                <div className="border-b border-white/10">
                  <nav className="-mb-px flex space-x-8">
                    {[
                      { id: 'overview', label: 'Overview', icon: BuildingOfficeIcon },
                      { id: 'members', label: 'Members', icon: UserGroupIcon },
                      { id: 'settings', label: 'Settings', icon: CogIcon }
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
                  {/* Overview Tab */}
                  {activeTab === 'overview' && (
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6 text-center">
                          <div className="text-2xl font-light text-trinity-consciousness mb-1">
                            {selectedOrg.memberCount}
                          </div>
                          <div className="text-sm text-white/60">Active Members</div>
                        </div>
                        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6 text-center">
                          <div className="text-2xl font-light text-trinity-guardian mb-1">
                            {invitations.length}
                          </div>
                          <div className="text-sm text-white/60">Pending Invites</div>
                        </div>
                        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6 text-center">
                          <div className="text-2xl font-light text-trinity-identity mb-1">
                            {selectedOrg.tier}
                          </div>
                          <div className="text-sm text-white/60">Organization Tier</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Members Tab */}
                  {activeTab === 'members' && (
                    <div className="space-y-6">
                      <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-6">
                          <h3 className="text-lg font-medium text-white">Members</h3>
                          {['owner', 'admin'].includes(selectedOrg.userRole) && (
                            <button
                              onClick={() => setShowInviteForm(true)}
                              className="flex items-center px-4 py-2 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium"
                            >
                              <PlusIcon className="w-4 h-4 mr-2" />
                              Invite Member
                            </button>
                          )}
                        </div>

                        <div className="space-y-3">
                          {members.map((member) => (
                            <div key={member.id} className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
                              <div className="flex items-center space-x-4">
                                <div className="w-10 h-10 bg-trinity-identity/20 rounded-full flex items-center justify-center">
                                  <span className="text-trinity-identity font-medium">
                                    {(member.displayName || member.email).charAt(0).toUpperCase()}
                                  </span>
                                </div>
                                <div>
                                  <h4 className="text-white font-medium">
                                    {member.displayName || member.email}
                                  </h4>
                                  <div className="text-sm text-white/60">
                                    {member.email} • Joined {new Date(member.joinedAt).toLocaleDateString()}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-3">
                                <span className={`px-3 py-1 rounded-full text-sm ${getRoleColor(member.role)}`}>
                                  {member.role}
                                </span>
                                {selectedOrg.userRole === 'owner' && member.role !== 'owner' && (
                                  <button
                                    onClick={() => handleRemoveMember(member.id)}
                                    className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                                  >
                                    <TrashIcon className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Pending Invitations */}
                        {invitations.length > 0 && (
                          <div className="mt-8">
                            <h4 className="text-white font-medium mb-4">Pending Invitations</h4>
                            <div className="space-y-3">
                              {invitations.map((invite) => (
                                <div key={invite.id} className="flex items-center justify-between p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                                  <div>
                                    <h5 className="text-white font-medium">{invite.email}</h5>
                                    <div className="text-sm text-white/60">
                                      Invited as {invite.role} • Expires {new Date(invite.expiresAt).toLocaleDateString()}
                                    </div>
                                  </div>
                                  <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm">
                                    Pending
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Invite Form */}
                      {showInviteForm && (
                        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                          <h3 className="text-lg font-medium text-white mb-4">Invite Member</h3>
                          <form onSubmit={handleInviteMember} className="space-y-4">
                            <div>
                              <label htmlFor="inviteEmail" className="block text-sm font-medium text-white/80 mb-2">
                                Email address
                              </label>
                              <input
                                type="email"
                                id="inviteEmail"
                                value={inviteEmail}
                                onChange={(e) => setInviteEmail(e.target.value)}
                                className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                                placeholder="member@example.com"
                                required
                              />
                            </div>
                            <div>
                              <label htmlFor="inviteRole" className="block text-sm font-medium text-white/80 mb-2">
                                Role
                              </label>
                              <select
                                id="inviteRole"
                                value={inviteRole}
                                onChange={(e) => setInviteRole(e.target.value as 'admin' | 'member')}
                                className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                              >
                                <option value="member">Member</option>
                                <option value="admin">Admin</option>
                              </select>
                            </div>
                            <div className="flex space-x-3">
                              <button
                                type="submit"
                                disabled={loading}
                                className="flex-1 px-4 py-2 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium disabled:opacity-50"
                              >
                                Send Invitation
                              </button>
                              <button
                                type="button"
                                onClick={() => setShowInviteForm(false)}
                                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 transition-colors rounded-lg text-white text-sm font-medium"
                              >
                                Cancel
                              </button>
                            </div>
                          </form>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Settings Tab */}
                  {activeTab === 'settings' && (
                    <div className="space-y-6">
                      <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                        <h3 className="text-lg font-medium text-white mb-6">Organization Settings</h3>
                        
                        {['owner', 'admin'].includes(selectedOrg.userRole) ? (
                          <div className="space-y-6">
                            <div className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
                              <div>
                                <h4 className="text-white font-medium">Require step-up authentication</h4>
                                <p className="text-white/60 text-sm">Require additional authentication for sensitive operations</p>
                              </div>
                              <input
                                type="checkbox"
                                checked={selectedOrg.settings.requireStepUp}
                                className="w-5 h-5 text-trinity-identity bg-black/40 border-white/10 rounded focus:ring-trinity-identity"
                                disabled // Would implement settings update
                              />
                            </div>
                            
                            <div className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
                              <div>
                                <h4 className="text-white font-medium">Allow member invites</h4>
                                <p className="text-white/60 text-sm">Let members invite other members to the organization</p>
                              </div>
                              <input
                                type="checkbox"
                                checked={selectedOrg.settings.allowMemberInvites}
                                className="w-5 h-5 text-trinity-identity bg-black/40 border-white/10 rounded focus:ring-trinity-identity"
                                disabled // Would implement settings update
                              />
                            </div>
                            
                            <div className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
                              <div>
                                <h4 className="text-white font-medium">Enforce passkeys</h4>
                                <p className="text-white/60 text-sm">Require all members to use passkey authentication</p>
                              </div>
                              <input
                                type="checkbox"
                                checked={selectedOrg.settings.enforcePasskeys}
                                className="w-5 h-5 text-trinity-identity bg-black/40 border-white/10 rounded focus:ring-trinity-identity"
                                disabled // Would implement settings update
                              />
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-8 text-white/60">
                            <ExclamationTriangleIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                            <p>Only owners and admins can modify organization settings</p>
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
            ) : (
              <div className="text-center py-16 text-white/60">
                <BuildingOfficeIcon className="w-16 h-16 mx-auto mb-6 text-white/40" />
                <h2 className="text-xl font-light text-white mb-4">No Organization Selected</h2>
                <p>Create or select an organization to manage members and settings</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Transparency Box */}
      <div className="px-6 pb-6">
        <TransparencyBox
          capabilities={[
            "Organization creation and management for T3+ users",
            "Role-based access control (owner, admin, member)",
            "Member invitation system with email verification",
            "Organization settings and policy enforcement",
            "Real-time collaboration and team management"
          ]}
          limitations={[
            "Requires Innovator (T3) tier or higher for access",
            "Member limits based on organization tier",
            "Invitation links expire after 7 days",
            "Settings changes require owner or admin role",
            "Organization deletion not available through UI"
          ]}
          dependencies={[
            "LUKHAS AI tier system and billing integration",
            "Email service for member invitations",
            "Role-based authorization system",
            "Organization database and management APIs"
          ]}
          dataHandling={[
            "Organization data secured with member access controls",
            "Invitation emails sent through secure channels",
            "Member activity logged for audit purposes",
            "Organization settings encoded → GLYPH for security",
            "All operations require valid session and authorization"
          ]}
          className="max-w-6xl mx-auto"
        />
      </div>
    </div>
  )
}