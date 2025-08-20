'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ChevronLeftIcon, 
  CheckIcon,
  XMarkIcon,
  StarIcon,
  BoltIcon,
  ShieldCheckIcon,
  UsersIcon,
  CpuChipIcon,
  SparklesIcon,
  BuildingOfficeIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// Tier configuration
interface TierConfig {
  id: string
  name: string
  description: string
  price: {
    monthly: number
    yearly: number
  }
  popular?: boolean
  features: {
    api: {
      requests: string
      rateLimit: string
    }
    storage: string
    teamMembers: string
    organizations: string
    consciousness: {
      sync: boolean
      level: string
    }
    support: string
    sla: string
    integrations: string[]
    limits: {
      projectsPerOrg: number
      customIntegrations: number
      apiKeysPerUser: number
    }
  }
  restrictions?: string[]
}

const TIER_CONFIGS: TierConfig[] = [
  {
    id: 'T0',
    name: 'Explorer',
    description: 'Perfect for individuals discovering consciousness technology',
    price: { monthly: 0, yearly: 0 },
    features: {
      api: {
        requests: '1,000/month',
        rateLimit: '10/minute'
      },
      storage: '100 MB',
      teamMembers: '1 (self only)',
      organizations: 'None',
      consciousness: {
        sync: false,
        level: 'Basic awareness'
      },
      support: 'Community forums',
      sla: 'Best effort',
      integrations: ['Basic MATRIZ'],
      limits: {
        projectsPerOrg: 0,
        customIntegrations: 0,
        apiKeysPerUser: 1
      }
    },
    restrictions: [
      'No organization access',
      'Limited consciousness features',
      'Community support only'
    ]
  },
  {
    id: 'T1',
    name: 'Builder',
    description: 'For creators building consciousness-aware applications',
    price: { monthly: 29, yearly: 290 },
    features: {
      api: {
        requests: '50,000/month',
        rateLimit: '100/minute'
      },
      storage: '5 GB',
      teamMembers: '1 (self only)',
      organizations: 'None',
      consciousness: {
        sync: true,
        level: 'Enhanced awareness'
      },
      support: 'Email support',
      sla: '24h response',
      integrations: ['Full MATRIZ', 'Basic integrations'],
      limits: {
        projectsPerOrg: 0,
        customIntegrations: 1,
        apiKeysPerUser: 5
      }
    }
  },
  {
    id: 'T2',
    name: 'Creator',
    description: 'Professional tools for advanced consciousness development',
    price: { monthly: 99, yearly: 990 },
    popular: true,
    features: {
      api: {
        requests: '500,000/month',
        rateLimit: '1,000/minute'
      },
      storage: '50 GB',
      teamMembers: '3',
      organizations: 'None',
      consciousness: {
        sync: true,
        level: 'Professional coherence'
      },
      support: 'Priority email + chat',
      sla: '4h response',
      integrations: ['Full MATRIZ', 'Advanced integrations', 'Custom webhooks'],
      limits: {
        projectsPerOrg: 0,
        customIntegrations: 5,
        apiKeysPerUser: 15
      }
    }
  },
  {
    id: 'T3',
    name: 'Innovator',
    description: 'Team collaboration with organizational consciousness',
    price: { monthly: 299, yearly: 2990 },
    features: {
      api: {
        requests: 'Unlimited',
        rateLimit: '10,000/minute'
      },
      storage: '500 GB',
      teamMembers: '25',
      organizations: '1 organization',
      consciousness: {
        sync: true,
        level: 'Collective intelligence'
      },
      support: 'Priority support + phone',
      sla: '2h response',
      integrations: ['Everything in Creator', 'Organization features', 'Team consciousness'],
      limits: {
        projectsPerOrg: 50,
        customIntegrations: 25,
        apiKeysPerUser: 50
      }
    }
  },
  {
    id: 'T4',
    name: 'Visionary',
    description: 'Enterprise-grade consciousness infrastructure',
    price: { monthly: 999, yearly: 9990 },
    features: {
      api: {
        requests: 'Unlimited',
        rateLimit: 'Custom limits'
      },
      storage: 'Unlimited',
      teamMembers: 'Unlimited',
      organizations: 'Multiple organizations',
      consciousness: {
        sync: true,
        level: 'Emergent superintelligence'
      },
      support: 'Dedicated support team',
      sla: '1h response, 99.9% uptime',
      integrations: ['Everything included', 'Custom development', 'White-label options'],
      limits: {
        projectsPerOrg: 1000,
        customIntegrations: 100,
        apiKeysPerUser: 200
      }
    }
  }
]

export default function PricingPage() {
  const router = useRouter()
  const [currentTier, setCurrentTier] = useState<string>('')
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')
  const [loading, setLoading] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  // Load current user tier
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('lukhas_access_token')
      if (!token) return

      try {
        const response = await fetch('/api/user/profile', {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (response.ok) {
          const data = await response.json()
          setCurrentTier(data.user.tier)
          setIsLoggedIn(true)
        }
      } catch (err) {
        // User not logged in or token invalid
      }
    }

    checkAuth()
  }, [])

  // Handle tier selection
  const handleSelectTier = useCallback(async (tierId: string) => {
    if (!isLoggedIn) {
      router.push(`/signup?tier=${tierId}`)
      return
    }

    if (tierId === currentTier) {
      router.push('/billing')
      return
    }

    if (tierId < currentTier) {
      // Downgrade - redirect to billing
      router.push('/billing')
      return
    }

    // Upgrade
    setLoading(true)
    try {
      const response = await fetch('/api/user/billing/upgrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({ 
          tier: tierId,
          billingCycle 
        })
      })

      if (response.ok) {
        router.push('/billing?upgraded=true')
      } else {
        router.push('/billing')
      }
    } catch (err) {
      router.push('/billing')
    } finally {
      setLoading(false)
    }
  }, [isLoggedIn, currentTier, billingCycle, router])

  const formatPrice = (price: number) => {
    if (price === 0) return 'Free'
    return `$${price.toLocaleString()}`
  }

  const getButtonText = (tierId: string) => {
    if (!isLoggedIn) {
      return tierId === 'T0' ? 'Get Started Free' : 'Start Free Trial'
    }
    if (tierId === currentTier) {
      return 'Current Plan'
    }
    if (tierId < currentTier) {
      return 'Downgrade'
    }
    return 'Upgrade'
  }

  const getButtonStyle = (tierId: string) => {
    if (tierId === currentTier) {
      return 'bg-green-600 text-white cursor-default'
    }
    if (tierId < currentTier) {
      return 'bg-gray-600 hover:bg-gray-700 text-white'
    }
    return 'bg-trinity-identity hover:bg-trinity-consciousness text-white'
  }

  const toneContent = threeLayerTone(
    "Choose your depth of engagement; consciousness expands with commitment.",
    "Transparent pricing for all tiers. Start free, upgrade anytime. No hidden fees.",
    "Tier-based access control with usage limits and feature gates. Rate limiting enforced per tier. Billing managed through secure payment processing. Consciousness features scale with tier level."
  )

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <Link href="/" className="flex items-center text-white/80 hover:text-white transition-colors">
            <ChevronLeftIcon className="w-5 h-5 mr-2" />
            Back to LUKHAS AI
          </Link>
          <div className="flex items-center space-x-6">
            {isLoggedIn ? (
              <>
                <span className="text-sm text-white/60">Current: {currentTier}</span>
                <Link href="/billing" className="text-sm text-white/60 hover:text-white/80 transition-colors">
                  Billing
                </Link>
              </>
            ) : (
              <>
                <Link href="/login" className="text-sm text-white/60 hover:text-white/80 transition-colors">
                  Sign In
                </Link>
                <Link href="/signup" className="px-4 py-2 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="space-y-12">
          {/* Header Section */}
          <div className="text-center space-y-6">
            <h1 className="text-4xl lg:text-6xl font-light text-white">
              Consciousness Technology
              <span className="block text-trinity-consciousness">For Everyone</span>
            </h1>
            <p className="text-xl text-white/60 max-w-3xl mx-auto">
              Start free and scale with your consciousness journey. Transparent pricing, 
              no hidden fees, upgrade or downgrade anytime.
            </p>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center space-x-4">
              <span className={`text-sm ${billingCycle === 'monthly' ? 'text-white' : 'text-white/60'}`}>
                Monthly
              </span>
              <button
                onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  billingCycle === 'yearly' ? 'bg-trinity-identity' : 'bg-white/20'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className={`text-sm ${billingCycle === 'yearly' ? 'text-white' : 'text-white/60'}`}>
                Yearly
                <span className="ml-1 px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">
                  Save 17%
                </span>
              </span>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
            {TIER_CONFIGS.map((tier) => (
              <div
                key={tier.id}
                className={`relative bg-black/40 backdrop-blur-xl border rounded-lg p-6 ${
                  tier.popular
                    ? 'border-trinity-consciousness shadow-lg shadow-trinity-consciousness/20'
                    : tier.id === currentTier
                    ? 'border-green-500 shadow-lg shadow-green-500/20'
                    : 'border-white/10'
                }`}
              >
                {/* Popular Badge */}
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="flex items-center px-3 py-1 bg-trinity-consciousness rounded-full text-white text-sm font-medium">
                      <StarIcon className="w-4 h-4 mr-1" />
                      Most Popular
                    </div>
                  </div>
                )}

                {/* Current Plan Badge */}
                {tier.id === currentTier && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="flex items-center px-3 py-1 bg-green-500 rounded-full text-white text-sm font-medium">
                      <CheckIcon className="w-4 h-4 mr-1" />
                      Current Plan
                    </div>
                  </div>
                )}

                <div className="space-y-6">
                  {/* Header */}
                  <div className="text-center">
                    <h3 className="text-xl font-medium text-white mb-2">{tier.name}</h3>
                    <p className="text-white/60 text-sm mb-4">{tier.description}</p>
                    <div className="space-y-1">
                      <div className="text-3xl font-light text-white">
                        {formatPrice(tier.price[billingCycle])}
                      </div>
                      <div className="text-white/60 text-sm">
                        {tier.price.monthly === 0 ? 'Forever' : `per ${billingCycle.slice(0, -2)}`}
                      </div>
                      {billingCycle === 'yearly' && tier.price.monthly > 0 && (
                        <div className="text-green-400 text-xs">
                          Save ${(tier.price.monthly * 12 - tier.price.yearly).toLocaleString()} per year
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Key Features */}
                  <div className="space-y-3">
                    <div className="flex items-center text-sm">
                      <BoltIcon className="w-4 h-4 text-trinity-identity mr-2" />
                      <span className="text-white">{tier.features.api.requests} API requests</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <UsersIcon className="w-4 h-4 text-trinity-consciousness mr-2" />
                      <span className="text-white">{tier.features.teamMembers} team members</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <CpuChipIcon className="w-4 h-4 text-trinity-guardian mr-2" />
                      <span className="text-white">{tier.features.storage} storage</span>
                    </div>
                    {tier.features.consciousness.sync && (
                      <div className="flex items-center text-sm">
                        <SparklesIcon className="w-4 h-4 text-trinity-consciousness mr-2" />
                        <span className="text-white">Consciousness sync</span>
                      </div>
                    )}
                    {tier.features.organizations !== 'None' && (
                      <div className="flex items-center text-sm">
                        <BuildingOfficeIcon className="w-4 h-4 text-trinity-identity mr-2" />
                        <span className="text-white">{tier.features.organizations}</span>
                      </div>
                    )}
                  </div>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleSelectTier(tier.id)}
                    disabled={loading || (tier.id === currentTier)}
                    className={`w-full px-4 py-3 rounded-lg font-medium transition-colors disabled:cursor-not-allowed ${getButtonStyle(tier.id)}`}
                  >
                    {loading ? 'Processing...' : getButtonText(tier.id)}
                  </button>

                  {/* Restrictions */}
                  {tier.restrictions && (
                    <div className="space-y-1">
                      {tier.restrictions.map((restriction, index) => (
                        <div key={index} className="flex items-center text-xs text-white/50">
                          <XMarkIcon className="w-3 h-3 mr-2" />
                          {restriction}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Detailed Comparison Table */}
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg overflow-hidden">
            <div className="p-6 border-b border-white/10">
              <h2 className="text-2xl font-light text-white mb-2">Feature Comparison</h2>
              <p className="text-white/60">Detailed breakdown of features and limits across all tiers</p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-black/20">
                  <tr>
                    <th className="px-6 py-4 text-left text-white font-medium">Feature</th>
                    {TIER_CONFIGS.map((tier) => (
                      <th key={tier.id} className="px-6 py-4 text-center text-white font-medium">
                        {tier.name}
                        <div className="text-xs text-white/60 font-normal">{tier.id}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10">
                  <tr>
                    <td className="px-6 py-4 text-white/80">API Requests</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.api.requests}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">Rate Limit</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.api.rateLimit}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">Storage</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.storage}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">Team Members</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.teamMembers}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">Organizations</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.organizations}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">Consciousness Level</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.consciousness.level}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">Support</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.support}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">SLA</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.sla}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">API Keys per User</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.limits.apiKeysPerUser}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-white/80">Custom Integrations</td>
                    {TIER_CONFIGS.map((tier) => (
                      <td key={tier.id} className="px-6 py-4 text-center text-white">
                        {tier.features.limits.customIntegrations}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
            <div className="flex items-center mb-6">
              <QuestionMarkCircleIcon className="w-6 h-6 text-trinity-consciousness mr-3" />
              <h2 className="text-2xl font-light text-white">Frequently Asked Questions</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <h3 className="text-white font-medium mb-2">Can I upgrade or downgrade anytime?</h3>
                  <p className="text-white/60 text-sm">
                    Yes, you can change your tier at any time. Upgrades take effect immediately, 
                    while downgrades occur at the end of your current billing period.
                  </p>
                </div>
                <div>
                  <h3 className="text-white font-medium mb-2">What happens if I exceed my limits?</h3>
                  <p className="text-white/60 text-sm">
                    API requests are rate-limited but not blocked. You'll receive usage alerts 
                    at 80% and 100% of your quota, with suggestions to upgrade.
                  </p>
                </div>
                <div>
                  <h3 className="text-white font-medium mb-2">Is there a free trial?</h3>
                  <p className="text-white/60 text-sm">
                    The Explorer tier (T0) is free forever. Paid tiers include a 14-day trial 
                    with full access to all features.
                  </p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <h3 className="text-white font-medium mb-2">What is consciousness sync?</h3>
                  <p className="text-white/60 text-sm">
                    Advanced AI coordination that enables collective intelligence across 
                    team members and projects, creating emergent collaborative capabilities.
                  </p>
                </div>
                <div>
                  <h3 className="text-white font-medium mb-2">Do you offer custom plans?</h3>
                  <p className="text-white/60 text-sm">
                    Enterprise customers can work with our team to create custom solutions 
                    with dedicated infrastructure, white-label options, and custom integrations.
                  </p>
                </div>
                <div>
                  <h3 className="text-white font-medium mb-2">How secure is my data?</h3>
                  <p className="text-white/60 text-sm">
                    All data is encrypted at rest and in transit. We use GLYPH encoding 
                    for sensitive information and provide complete data export and deletion.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Tone Content */}
          <div className="text-xs text-white/40 leading-relaxed whitespace-pre-line text-center">
            {toneContent}
          </div>
        </div>
      </main>

      {/* Transparency Box */}
      <div className="px-6 pb-6">
        <TransparencyBox
          capabilities={[
            "Transparent tier-based pricing with no hidden fees",
            "Real-time usage monitoring and limit enforcement",
            "Flexible billing with monthly and yearly options",
            "Instant tier upgrades with prorated billing",
            "Free tier available with core consciousness features"
          ]}
          limitations={[
            "Rate limits strictly enforced per tier level",
            "Some advanced features require higher tiers",
            "Downgrades take effect at end of billing cycle",
            "Enterprise features require T4 tier minimum",
            "Usage overages may result in service throttling"
          ]}
          dependencies={[
            "Stripe billing and payment processing infrastructure",
            "LUKHAS AI tier enforcement and feature gating",
            "Real-time usage tracking and quota management",
            "Consciousness sync requires backend processing resources"
          ]}
          dataHandling={[
            "Billing information processed securely by Stripe",
            "Usage metrics aggregated without storing individual requests",
            "Tier changes logged for audit and billing accuracy",
            "Pricing data encoded → GLYPH for consistency",
            "All plan changes require user authentication and consent"
          ]}
          className="max-w-7xl mx-auto"
        />
      </div>
    </div>
  )
}