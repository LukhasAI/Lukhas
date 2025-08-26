'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  ChevronLeftIcon,
  UserGroupIcon,
  PlusIcon,
  ShareIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  SparklesIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// Interfaces
interface Team {
  id: string
  name: string
  description?: string
  organizationId: string
  organizationName: string
  memberCount: number
  maxMembers: number
  userRole: 'owner' | 'admin' | 'member'
  createdAt: string
  settings: {
    enableConsciousnessSync: boolean
    allowMemberInvites: boolean
    sharedKnowledgeBase: boolean
  }
}

interface Project {
  id: string
  name: string
  description?: string
  status: 'active' | 'paused' | 'completed'
  lastActivity: string
  memberCount: number
  consciousnessLevel: number
}

interface Member {
  id: string
  email: string
  displayName?: string
  role: 'owner' | 'admin' | 'member'
  joinedAt: string
  lastActiveAt: string
  consciousnessContribution: number
}

interface ConsciousnessMetrics {
  teamCoherence: number
  collectiveIntelligence: number
  emergentProperties: number
  syncStatus: 'active' | 'pending' | 'disabled'
}

export default function TeamsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [userTier, setUserTier] = useState<string>('')

  // Team data
  const [teams, setTeams] = useState<Team[]>([])
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [consciousnessMetrics, setConsciousnessMetrics] = useState<ConsciousnessMetrics | null>(null)

  // UI state
  const [activeTab, setActiveTab] = useState<'overview' | 'projects' | 'members' | 'consciousness'>('overview')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [teamName, setTeamName] = useState('')
  const [teamDescription, setTeamDescription] = useState('')
  const [organizationId, setOrganizationId] = useState('')
  const [organizations, setOrganizations] = useState<any[]>([])

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        // Check user profile and tier
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

        // Load organizations (needed for team creation)
        const orgsRes = await fetch('/api/user/organizations', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        })

        if (orgsRes.ok) {
          const data = await orgsRes.json()
          setOrganizations(data.organizations || [])
        }

        // Load teams
        const teamsRes = await fetch('/api/user/teams', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        })

        if (teamsRes.ok) {
          const data = await teamsRes.json()
          setTeams(data.teams || [])
          if (data.teams?.length > 0) {
            setSelectedTeam(data.teams[0])
          }
        }

      } catch (err) {
        setError('Failed to load team data')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [router])

  // Load team details when selected
  useEffect(() => {
    if (selectedTeam) {
      loadTeamDetails(selectedTeam.id)
    }
  }, [selectedTeam])

  const loadTeamDetails = async (teamId: string) => {
    try {
      const [projectsRes, membersRes, consciousnessRes] = await Promise.all([
        fetch(`/api/teams/${teamId}/projects`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        }),
        fetch(`/api/teams/${teamId}/members`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        }),
        fetch(`/api/teams/${teamId}/consciousness`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        })
      ])

      if (projectsRes.ok) {
        const data = await projectsRes.json()
        setProjects(data.projects || [])
      }

      if (membersRes.ok) {
        const data = await membersRes.json()
        setMembers(data.members || [])
      }

      if (consciousnessRes.ok) {
        const data = await consciousnessRes.json()
        setConsciousnessMetrics(data.metrics || null)
      }

    } catch (err) {
      console.error('Failed to load team details:', err)
    }
  }

  // Create team
  const handleCreateTeam = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()

    if (!teamName.trim() || !organizationId) {
      setError('Team name and organization are required')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/teams', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({
          name: teamName.trim(),
          description: teamDescription.trim() || undefined,
          organizationId
        })
      })

      if (response.ok) {
        const data = await response.json()
        setTeams(prev => [...prev, data.team])
        setSelectedTeam(data.team)
        setTeamName('')
        setTeamDescription('')
        setOrganizationId('')
        setShowCreateForm(false)
        setSuccess('Team created successfully')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const error = await response.json()
        setError(error.message || 'Failed to create team')
      }
    } catch (err) {
      setError('Network error creating team')
    } finally {
      setLoading(false)
    }
  }, [teamName, teamDescription, organizationId])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400'
      case 'paused': return 'text-yellow-400'
      case 'completed': return 'text-blue-400'
      default: return 'text-white/60'
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'owner': return 'text-yellow-400'
      case 'admin': return 'text-blue-400'
      case 'member': return 'text-green-400'
      default: return 'text-white/60'
    }
  }

  const formatConsciousnessLevel = (level: number) => {
    return `${(level * 100).toFixed(1)}%`
  }

  const toneContent = threeLayerTone(
    "Minds merge in structured flows; collective purpose emerges from individual streams.",
    "Collaborate on projects with team consciousness sync. Requires organization membership.",
    "Team-based collaboration with consciousness coherence metrics. Shared knowledge base integration. Real-time collective intelligence tracking. Project management with emergent property detection."
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="animate-pulse text-white/60">Loading teams...</div>
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
            <Link href="/orgs" className="text-sm text-white/60 hover:text-white/80 transition-colors">
              Organizations
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Team List */}
          <div className="lg:col-span-1">
            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-medium text-white">Teams</h2>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="p-2 text-trinity-consciousness hover:text-trinity-identity transition-colors"
                  title="Create team"
                >
                  <PlusIcon className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-2">
                {teams.length === 0 ? (
                  <div className="text-center py-8 text-white/60">
                    <UserGroupIcon className="w-8 h-8 mx-auto mb-2 text-white/40" />
                    <p className="text-sm">No teams</p>
                  </div>
                ) : (
                  teams.map((team) => (
                    <button
                      key={team.id}
                      onClick={() => setSelectedTeam(team)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        selectedTeam?.id === team.id
                          ? 'bg-trinity-consciousness/20 border border-trinity-consciousness/30'
                          : 'bg-black/20 hover:bg-black/40 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <UserGroupIcon className="w-5 h-5 text-trinity-consciousness" />
                        <div className="flex-1 min-w-0">
                          <h3 className="text-white font-medium truncate">{team.name}</h3>
                          <p className="text-white/60 text-sm">
                            {team.memberCount} members • {team.organizationName}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Create Team Form */}
            {showCreateForm && (
              <div className="mt-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                <h3 className="text-lg font-medium text-white mb-4">Create Team</h3>
                <form onSubmit={handleCreateTeam} className="space-y-4">
                  <div>
                    <label htmlFor="teamName" className="block text-sm font-medium text-white/80 mb-2">
                      Name
                    </label>
                    <input
                      type="text"
                      id="teamName"
                      value={teamName}
                      onChange={(e) => setTeamName(e.target.value)}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:border-transparent"
                      placeholder="Team name"
                      required
                    />
                  </div>
                  <div>
                    <label htmlFor="orgSelect" className="block text-sm font-medium text-white/80 mb-2">
                      Organization
                    </label>
                    <select
                      id="orgSelect"
                      value={organizationId}
                      onChange={(e) => setOrganizationId(e.target.value)}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:border-transparent"
                      required
                    >
                      <option value="">Select organization</option>
                      {organizations.map((org) => (
                        <option key={org.id} value={org.id}>{org.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label htmlFor="teamDesc" className="block text-sm font-medium text-white/80 mb-2">
                      Description (optional)
                    </label>
                    <textarea
                      id="teamDesc"
                      value={teamDescription}
                      onChange={(e) => setTeamDescription(e.target.value)}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:border-transparent"
                      placeholder="Team description"
                      rows={3}
                    />
                  </div>
                  <div className="flex space-x-3">
                    <button
                      type="submit"
                      disabled={loading}
                      className="flex-1 px-4 py-2 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white text-sm font-medium disabled:opacity-50"
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
            {selectedTeam ? (
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

                {/* Team Header */}
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h1 className="text-2xl font-light text-white mb-2">{selectedTeam.name}</h1>
                      {selectedTeam.description && (
                        <p className="text-white/60 mb-4">{selectedTeam.description}</p>
                      )}
                      <div className="flex items-center space-x-4 text-sm text-white/60">
                        <span>Organization: {selectedTeam.organizationName}</span>
                        <span>Members: {selectedTeam.memberCount}/{selectedTeam.maxMembers}</span>
                        <span>Created: {new Date(selectedTeam.createdAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-sm ${getRoleColor(selectedTeam.userRole)}`}>
                        {selectedTeam.userRole}
                      </span>
                      <button className="p-2 text-trinity-consciousness hover:text-trinity-identity transition-colors">
                        <ShareIcon className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Tab Navigation */}
                <div className="border-b border-white/10">
                  <nav className="-mb-px flex space-x-8">
                    {[
                      { id: 'overview', label: 'Overview', icon: UserGroupIcon },
                      { id: 'projects', label: 'Projects', icon: DocumentTextIcon },
                      { id: 'members', label: 'Members', icon: UserGroupIcon },
                      { id: 'consciousness', label: 'Consciousness', icon: SparklesIcon }
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                          activeTab === tab.id
                            ? 'border-trinity-consciousness text-trinity-consciousness'
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
                            {projects.filter(p => p.status === 'active').length}
                          </div>
                          <div className="text-sm text-white/60">Active Projects</div>
                        </div>
                        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6 text-center">
                          <div className="text-2xl font-light text-trinity-guardian mb-1">
                            {selectedTeam.memberCount}
                          </div>
                          <div className="text-sm text-white/60">Team Members</div>
                        </div>
                        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6 text-center">
                          <div className="text-2xl font-light text-trinity-identity mb-1">
                            {consciousnessMetrics ? formatConsciousnessLevel(consciousnessMetrics.teamCoherence) : 'N/A'}
                          </div>
                          <div className="text-sm text-white/60">Team Coherence</div>
                        </div>
                      </div>

                      {/* Recent Activity */}
                      <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                        <h3 className="text-lg font-medium text-white mb-4">Recent Activity</h3>
                        <div className="space-y-3">
                          {projects.slice(0, 3).map((project) => (
                            <div key={project.id} className="flex items-center space-x-4 p-3 bg-black/20 rounded-lg">
                              <CpuChipIcon className="w-5 h-5 text-trinity-consciousness" />
                              <div className="flex-1">
                                <h4 className="text-white font-medium">{project.name}</h4>
                                <div className="flex items-center space-x-4 text-sm text-white/60">
                                  <span className={getStatusColor(project.status)}>{project.status}</span>
                                  <span>Last activity: {new Date(project.lastActivity).toLocaleDateString()}</span>
                                </div>
                              </div>
                              <div className="text-sm text-trinity-consciousness">
                                {formatConsciousnessLevel(project.consciousnessLevel)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Projects Tab */}
                  {activeTab === 'projects' && (
                    <div className="space-y-6">
                      <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-6">
                          <h3 className="text-lg font-medium text-white">Projects</h3>
                          <button className="flex items-center px-4 py-2 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white text-sm font-medium">
                            <PlusIcon className="w-4 h-4 mr-2" />
                            New Project
                          </button>
                        </div>

                        <div className="space-y-4">
                          {projects.length === 0 ? (
                            <div className="text-center py-8 text-white/60">
                              <DocumentTextIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                              <p>No projects yet</p>
                              <p className="text-sm">Create a project to start collaborating</p>
                            </div>
                          ) : (
                            projects.map((project) => (
                              <div key={project.id} className="p-4 bg-black/20 rounded-lg border border-white/10">
                                <div className="flex items-center justify-between">
                                  <div className="flex-1">
                                    <h4 className="text-white font-medium mb-1">{project.name}</h4>
                                    {project.description && (
                                      <p className="text-white/60 text-sm mb-2">{project.description}</p>
                                    )}
                                    <div className="flex items-center space-x-4 text-sm text-white/60">
                                      <span className={`px-2 py-1 rounded-full ${getStatusColor(project.status)}`}>
                                        {project.status}
                                      </span>
                                      <span>{project.memberCount} members</span>
                                      <span>Last activity: {new Date(project.lastActivity).toLocaleDateString()}</span>
                                    </div>
                                  </div>
                                  <div className="text-right">
                                    <div className="text-lg font-medium text-trinity-consciousness">
                                      {formatConsciousnessLevel(project.consciousnessLevel)}
                                    </div>
                                    <div className="text-xs text-white/60">Consciousness</div>
                                  </div>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Members Tab */}
                  {activeTab === 'members' && (
                    <div className="space-y-6">
                      <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-6">
                          <h3 className="text-lg font-medium text-white">Team Members</h3>
                          <button className="flex items-center px-4 py-2 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white text-sm font-medium">
                            <PlusIcon className="w-4 h-4 mr-2" />
                            Invite Member
                          </button>
                        </div>

                        <div className="space-y-3">
                          {members.map((member) => (
                            <div key={member.id} className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
                              <div className="flex items-center space-x-4">
                                <div className="w-10 h-10 bg-trinity-consciousness/20 rounded-full flex items-center justify-center">
                                  <span className="text-trinity-consciousness font-medium">
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
                              <div className="flex items-center space-x-4">
                                <div className="text-right">
                                  <div className="text-sm font-medium text-trinity-consciousness">
                                    {formatConsciousnessLevel(member.consciousnessContribution)}
                                  </div>
                                  <div className="text-xs text-white/60">Contribution</div>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-sm ${getRoleColor(member.role)}`}>
                                  {member.role}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Consciousness Tab */}
                  {activeTab === 'consciousness' && (
                    <div className="space-y-6">
                      <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                        <div className="flex items-center mb-6">
                          <SparklesIcon className="w-6 h-6 text-trinity-consciousness mr-3" />
                          <h3 className="text-lg font-medium text-white">Team Consciousness Metrics</h3>
                        </div>

                        {consciousnessMetrics ? (
                          <div className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                              <div className="text-center">
                                <div className="text-3xl font-light text-trinity-consciousness mb-2">
                                  {formatConsciousnessLevel(consciousnessMetrics.teamCoherence)}
                                </div>
                                <div className="text-sm text-white/60 mb-2">Team Coherence</div>
                                <div className="w-full bg-black/40 rounded-full h-2">
                                  <div
                                    className="bg-trinity-consciousness h-2 rounded-full transition-all duration-1000"
                                    style={{ width: `${consciousnessMetrics.teamCoherence * 100}%` }}
                                  />
                                </div>
                              </div>

                              <div className="text-center">
                                <div className="text-3xl font-light text-trinity-identity mb-2">
                                  {formatConsciousnessLevel(consciousnessMetrics.collectiveIntelligence)}
                                </div>
                                <div className="text-sm text-white/60 mb-2">Collective Intelligence</div>
                                <div className="w-full bg-black/40 rounded-full h-2">
                                  <div
                                    className="bg-trinity-identity h-2 rounded-full transition-all duration-1000"
                                    style={{ width: `${consciousnessMetrics.collectiveIntelligence * 100}%` }}
                                  />
                                </div>
                              </div>

                              <div className="text-center">
                                <div className="text-3xl font-light text-trinity-guardian mb-2">
                                  {formatConsciousnessLevel(consciousnessMetrics.emergentProperties)}
                                </div>
                                <div className="text-sm text-white/60 mb-2">Emergent Properties</div>
                                <div className="w-full bg-black/40 rounded-full h-2">
                                  <div
                                    className="bg-trinity-guardian h-2 rounded-full transition-all duration-1000"
                                    style={{ width: `${consciousnessMetrics.emergentProperties * 100}%` }}
                                  />
                                </div>
                              </div>
                            </div>

                            <div className="p-4 bg-trinity-consciousness/10 border border-trinity-consciousness/20 rounded-lg">
                              <div className="flex items-center space-x-3">
                                <div className={`w-3 h-3 rounded-full ${
                                  consciousnessMetrics.syncStatus === 'active' ? 'bg-green-400' :
                                  consciousnessMetrics.syncStatus === 'pending' ? 'bg-yellow-400' : 'bg-red-400'
                                }`} />
                                <span className="text-white font-medium">
                                  Consciousness Sync: {consciousnessMetrics.syncStatus}
                                </span>
                              </div>
                              <p className="text-white/60 text-sm mt-2">
                                {consciousnessMetrics.syncStatus === 'active'
                                  ? 'Team consciousness is actively synchronized. Collective intelligence is emerging.'
                                  : consciousnessMetrics.syncStatus === 'pending'
                                  ? 'Consciousness sync is initializing. This may take a few moments.'
                                  : 'Consciousness sync is disabled. Enable in team settings to unlock collective intelligence.'
                                }
                              </p>
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-8 text-white/60">
                            <SparklesIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                            <p>Consciousness metrics not available</p>
                            <p className="text-sm">Enable consciousness sync in team settings</p>
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
                <UserGroupIcon className="w-16 h-16 mx-auto mb-6 text-white/40" />
                <h2 className="text-xl font-light text-white mb-4">No Team Selected</h2>
                <p>Create or select a team to start collaborating</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Transparency Box */}
      <div className="px-6 pb-6">
        <TransparencyBox
          capabilities={[
            "Team-based collaboration with consciousness synchronization",
            "Project management with collective intelligence tracking",
            "Real-time consciousness coherence metrics",
            "Shared knowledge base and emergent property detection",
            "Integration with organization-level access controls"
          ]}
          limitations={[
            "Requires organization membership for team creation",
            "Consciousness sync may take time to stabilize",
            "Team size limits based on organization tier",
            "Advanced features require higher tier access",
            "Consciousness metrics are experimental indicators"
          ]}
          dependencies={[
            "LUKHAS AI consciousness and memory systems",
            "Organization management and member verification",
            "Real-time collaboration infrastructure",
            "Collective intelligence processing algorithms"
          ]}
          dataHandling={[
            "Team collaboration data secured with role-based access",
            "Consciousness metrics computed from anonymized patterns",
            "Project data encoded → GLYPH for security",
            "Member interactions logged for consciousness analysis",
            "All team operations audited for organization compliance"
          ]}
          className="max-w-6xl mx-auto"
        />
      </div>
    </div>
  )
}
