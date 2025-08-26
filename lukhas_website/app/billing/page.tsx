'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  ChevronLeftIcon,
  CreditCardIcon,
  BanknotesIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  CalendarIcon,
  ArrowPathIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// Interfaces
interface BillingInfo {
  tier: 'T0' | 'T1' | 'T2' | 'T3' | 'T4'
  tierName: string
  monthlyAmount: number
  currency: string
  billingCycle: 'monthly' | 'yearly'
  nextBillingDate: string
  prorationAmount?: number
  status: 'active' | 'past_due' | 'cancelled' | 'trial'
}

interface PaymentMethod {
  id: string
  type: 'card' | 'bank' | 'digital_wallet'
  brand: string
  last4: string
  expiryMonth?: number
  expiryYear?: number
  isDefault: boolean
  name: string
}

interface Invoice {
  id: string
  number: string
  amount: number
  currency: string
  status: 'paid' | 'pending' | 'failed' | 'draft'
  issueDate: string
  dueDate: string
  paidDate?: string
  downloadUrl: string
  items: InvoiceItem[]
}

interface InvoiceItem {
  description: string
  quantity: number
  unitAmount: number
  amount: number
}

interface UsageMetrics {
  apiRequests: { used: number; limit: number; period: string }
  storageGB: { used: number; limit: number }
  teamMembers: { used: number; limit: number }
  consciousnessSync: { used: number; limit: number; period: string }
}

const TIER_PRICING = {
  T0: { name: 'Explorer', price: 0, features: ['Basic consciousness access', '1,000 API requests/month'] },
  T1: { name: 'Builder', price: 29, features: ['Enhanced features', '50,000 API requests/month', 'Email support'] },
  T2: { name: 'Creator', price: 99, features: ['Professional tools', '500,000 API requests/month', 'Priority support'] },
  T3: { name: 'Innovator', price: 299, features: ['Team collaboration', 'Unlimited API requests', 'Organization management'] },
  T4: { name: 'Visionary', price: 999, features: ['Enterprise features', 'Custom integrations', 'Dedicated support'] }
}

export default function BillingPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [userTier, setUserTier] = useState<string>('')

  // Step-up authentication
  const [stepUpRequired, setStepUpRequired] = useState(false)
  const [stepUpCompleted, setStepUpCompleted] = useState(false)

  // Billing data
  const [billingInfo, setBillingInfo] = useState<BillingInfo | null>(null)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [usageMetrics, setUsageMetrics] = useState<UsageMetrics | null>(null)

  // UI state
  const [activeTab, setActiveTab] = useState<'overview' | 'methods' | 'invoices' | 'usage'>('overview')
  const [showAddPayment, setShowAddPayment] = useState(false)
  const [showTierUpgrade, setShowTierUpgrade] = useState(false)
  const [selectedTier, setSelectedTier] = useState<string>('')
  const [processingPayment, setProcessingPayment] = useState(false)

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

        // Check if user has access to billing (T4+ for payment management)
        if (!['T1', 'T2', 'T3', 'T4'].includes(profile.user.tier)) {
          setError('Billing management requires a paid tier')
          setLoading(false)
          return
        }

        // Check if step-up authentication is required
        const stepUpRes = await fetch('/api/auth/step-up/required', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
          },
          body: JSON.stringify({ action: 'billing_management' })
        })

        if (stepUpRes.ok) {
          const stepUpData = await stepUpRes.json()
          setStepUpRequired(stepUpData.required)

          if (!stepUpData.required) {
            setStepUpCompleted(true)
            await loadBillingData()
          }
        }

      } catch (err) {
        setError('Failed to load billing data')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [router])

  const loadBillingData = async () => {
    try {
      const [billingRes, methodsRes, invoicesRes, usageRes] = await Promise.all([
        fetch('/api/user/billing', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        }),
        fetch('/api/user/payment-methods', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        }),
        fetch('/api/user/invoices', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        }),
        fetch('/api/user/usage', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
        })
      ])

      if (billingRes.ok) {
        const data = await billingRes.json()
        setBillingInfo(data.billing)
      }

      if (methodsRes.ok) {
        const data = await methodsRes.json()
        setPaymentMethods(data.methods || [])
      }

      if (invoicesRes.ok) {
        const data = await invoicesRes.json()
        setInvoices(data.invoices || [])
      }

      if (usageRes.ok) {
        const data = await usageRes.json()
        setUsageMetrics(data.usage)
      }

    } catch (err) {
      setError('Failed to load billing information')
    }
  }

  // Handle step-up authentication
  const handleStepUpAuth = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/auth/step-up/authenticate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({ action: 'billing_management' })
      })

      if (response.ok) {
        setStepUpCompleted(true)
        setStepUpRequired(false)
        await loadBillingData()
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

  // Handle tier upgrade
  const handleTierUpgrade = useCallback(async (newTier: string) => {
    setProcessingPayment(true)
    setError('')

    try {
      const response = await fetch('/api/user/billing/upgrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}`
        },
        body: JSON.stringify({ tier: newTier })
      })

      if (response.ok) {
        const data = await response.json()
        setBillingInfo(data.billing)
        setSuccess(`Successfully upgraded to ${TIER_PRICING[newTier as keyof typeof TIER_PRICING].name}`)
        setShowTierUpgrade(false)
        setTimeout(() => setSuccess(''), 5000)
      } else {
        const error = await response.json()
        setError(error.message || 'Failed to upgrade tier')
      }
    } catch (err) {
      setError('Network error during upgrade')
    } finally {
      setProcessingPayment(false)
    }
  }, [])

  // Set default payment method
  const handleSetDefaultPayment = useCallback(async (methodId: string) => {
    try {
      const response = await fetch(`/api/user/payment-methods/${methodId}/default`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('lukhas_access_token')}` }
      })

      if (response.ok) {
        setPaymentMethods(prev => prev.map(method => ({
          ...method,
          isDefault: method.id === methodId
        })))
        setSuccess('Default payment method updated')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to update default payment method')
      }
    } catch (err) {
      setError('Network error updating payment method')
    }
  }, [])

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount / 100) // Assuming amounts are in cents
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'paid': return 'text-green-400'
      case 'pending': return 'text-yellow-400'
      case 'past_due':
      case 'failed': return 'text-red-400'
      case 'cancelled': return 'text-gray-400'
      default: return 'text-white/60'
    }
  }

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === 0) return 0
    return Math.min((used / limit) * 100, 100)
  }

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-400'
    if (percentage >= 70) return 'text-yellow-400'
    return 'text-green-400'
  }

  const toneContent = threeLayerTone(
    "Value flows through chosen channels; consciousness expansion follows commitment.",
    "Manage your subscription, payment methods, and usage. Requires step-up authentication.",
    "Billing management with step-up authentication. Tier-based pricing with usage monitoring. Payment method management and invoice history. Enterprise features for T4+ users."
  )

  // Access check for T0 users
  if (!loading && userTier === 'T0') {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="max-w-md text-center">
          <BanknotesIcon className="w-16 h-16 text-yellow-400 mx-auto mb-6" />
          <h1 className="text-2xl font-light text-white mb-4">Upgrade Required</h1>
          <p className="text-white/60 mb-6">
            Billing management requires a paid tier. Upgrade to access payment methods and invoices.
          </p>
          <div className="space-y-3">
            <Link
              href="/pricing"
              className="block w-full px-6 py-3 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium"
            >
              View Pricing
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

  // Step-up authentication required
  if (stepUpRequired && !stepUpCompleted) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="max-w-md text-center">
          <ShieldCheckIcon className="w-16 h-16 text-trinity-guardian mx-auto mb-6" />
          <h1 className="text-2xl font-light text-white mb-4">Step-up Authentication Required</h1>
          <p className="text-white/60 mb-6">
            Billing management requires additional authentication for security.
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
        <div className="animate-pulse text-white/60">Loading billing information...</div>
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
            <Link href="/pricing" className="text-sm text-white/60 hover:text-white/80 transition-colors">
              Pricing
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Page Title */}
          <div>
            <h1 className="text-2xl font-light text-white mb-2">Billing & Payments</h1>
            <p className="text-white/60">Manage your LUKHAS AI subscription and payment methods</p>
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

          {/* Billing Overview */}
          {billingInfo && (
            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <BanknotesIcon className="w-6 h-6 text-trinity-identity mr-3" />
                  <h2 className="text-xl font-medium text-white">Current Subscription</h2>
                </div>
                <button
                  onClick={() => setShowTierUpgrade(true)}
                  className="px-4 py-2 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white text-sm font-medium"
                >
                  Upgrade Tier
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-light text-trinity-identity mb-1">
                    {billingInfo.tierName}
                  </div>
                  <div className="text-sm text-white/60">Current Tier</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-light text-trinity-consciousness mb-1">
                    {formatCurrency(billingInfo.monthlyAmount, billingInfo.currency)}
                  </div>
                  <div className="text-sm text-white/60">{billingInfo.billingCycle}</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-light text-trinity-guardian mb-1">
                    {formatDate(billingInfo.nextBillingDate)}
                  </div>
                  <div className="text-sm text-white/60">Next billing</div>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between p-4 bg-black/20 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    billingInfo.status === 'active' ? 'bg-green-400' :
                    billingInfo.status === 'past_due' ? 'bg-red-400' :
                    billingInfo.status === 'trial' ? 'bg-yellow-400' : 'bg-gray-400'
                  }`} />
                  <span className="text-white font-medium">
                    Status: <span className={getStatusColor(billingInfo.status)}>{billingInfo.status}</span>
                  </span>
                </div>
                {billingInfo.prorationAmount && (
                  <div className="text-sm text-white/60">
                    Proration: {formatCurrency(billingInfo.prorationAmount, billingInfo.currency)}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab Navigation */}
          <div className="border-b border-white/10">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', label: 'Overview', icon: BanknotesIcon },
                { id: 'methods', label: 'Payment Methods', icon: CreditCardIcon },
                { id: 'invoices', label: 'Invoices', icon: DocumentTextIcon },
                { id: 'usage', label: 'Usage', icon: CalendarIcon }
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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-white mb-4">Quick Actions</h3>
                  <div className="space-y-3">
                    <button
                      onClick={() => setShowTierUpgrade(true)}
                      className="w-full p-3 bg-trinity-identity/20 border border-trinity-identity/30 rounded-lg text-left hover:bg-trinity-identity/30 transition-colors"
                    >
                      <div className="text-white font-medium">Upgrade Tier</div>
                      <div className="text-white/60 text-sm">Access more features and higher limits</div>
                    </button>
                    <button
                      onClick={() => setShowAddPayment(true)}
                      className="w-full p-3 bg-trinity-consciousness/20 border border-trinity-consciousness/30 rounded-lg text-left hover:bg-trinity-consciousness/30 transition-colors"
                    >
                      <div className="text-white font-medium">Add Payment Method</div>
                      <div className="text-white/60 text-sm">Add a new card or payment method</div>
                    </button>
                  </div>
                </div>

                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-white mb-4">Recent Invoices</h3>
                  <div className="space-y-3">
                    {invoices.slice(0, 3).map((invoice) => (
                      <div key={invoice.id} className="flex items-center justify-between p-3 bg-black/20 rounded-lg">
                        <div>
                          <div className="text-white font-medium">{invoice.number}</div>
                          <div className="text-white/60 text-sm">{formatDate(invoice.issueDate)}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-white">{formatCurrency(invoice.amount, invoice.currency)}</div>
                          <div className={`text-sm ${getStatusColor(invoice.status)}`}>{invoice.status}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Payment Methods Tab */}
            {activeTab === 'methods' && (
              <div className="space-y-6">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-medium text-white">Payment Methods</h3>
                    <button
                      onClick={() => setShowAddPayment(true)}
                      className="px-4 py-2 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white text-sm font-medium"
                    >
                      Add Payment Method
                    </button>
                  </div>

                  <div className="space-y-4">
                    {paymentMethods.length === 0 ? (
                      <div className="text-center py-8 text-white/60">
                        <CreditCardIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                        <p>No payment methods</p>
                        <p className="text-sm">Add a payment method to manage billing</p>
                      </div>
                    ) : (
                      paymentMethods.map((method) => (
                        <div key={method.id} className="flex items-center justify-between p-4 bg-black/20 rounded-lg border border-white/10">
                          <div className="flex items-center space-x-4">
                            <CreditCardIcon className="w-8 h-8 text-trinity-consciousness" />
                            <div>
                              <div className="flex items-center space-x-2">
                                <h4 className="text-white font-medium">{method.brand} ••••{method.last4}</h4>
                                {method.isDefault && (
                                  <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                                    Default
                                  </span>
                                )}
                              </div>
                              <div className="text-white/60 text-sm">
                                {method.name}
                                {method.expiryMonth && method.expiryYear &&
                                  ` • Expires ${method.expiryMonth}/${method.expiryYear}`
                                }
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            {!method.isDefault && (
                              <button
                                onClick={() => handleSetDefaultPayment(method.id)}
                                className="px-3 py-1 text-trinity-consciousness hover:text-trinity-identity transition-colors text-sm"
                              >
                                Set Default
                              </button>
                            )}
                            <button className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors">
                              <XCircleIcon className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Invoices Tab */}
            {activeTab === 'invoices' && (
              <div className="space-y-6">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-white mb-6">Invoice History</h3>

                  <div className="space-y-4">
                    {invoices.length === 0 ? (
                      <div className="text-center py-8 text-white/60">
                        <DocumentTextIcon className="w-12 h-12 mx-auto mb-4 text-white/40" />
                        <p>No invoices</p>
                      </div>
                    ) : (
                      invoices.map((invoice) => (
                        <div key={invoice.id} className="p-4 bg-black/20 rounded-lg border border-white/10">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <h4 className="text-white font-medium">{invoice.number}</h4>
                              <div className="text-white/60 text-sm space-y-1">
                                <p>Issued: {formatDate(invoice.issueDate)}</p>
                                <p>Due: {formatDate(invoice.dueDate)}</p>
                                {invoice.paidDate && <p>Paid: {formatDate(invoice.paidDate)}</p>}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-xl font-medium text-white">
                                {formatCurrency(invoice.amount, invoice.currency)}
                              </div>
                              <div className={`text-sm ${getStatusColor(invoice.status)}`}>
                                {invoice.status}
                              </div>
                              <button className="mt-2 px-3 py-1 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded text-white text-sm">
                                Download
                              </button>
                            </div>
                          </div>

                          <div className="space-y-2">
                            {invoice.items.map((item, index) => (
                              <div key={index} className="flex items-center justify-between text-sm">
                                <span className="text-white/60">{item.description}</span>
                                <span className="text-white">
                                  {item.quantity} × {formatCurrency(item.unitAmount, invoice.currency)} = {formatCurrency(item.amount, invoice.currency)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Usage Tab */}
            {activeTab === 'usage' && usageMetrics && (
              <div className="space-y-6">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-white mb-6">Usage Metrics</h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="p-4 bg-black/20 rounded-lg">
                      <h4 className="text-white font-medium mb-3">API Requests</h4>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white/60 text-sm">{usageMetrics.apiRequests.period}</span>
                        <span className={`text-sm font-medium ${getUsageColor(getUsagePercentage(usageMetrics.apiRequests.used, usageMetrics.apiRequests.limit))}`}>
                          {usageMetrics.apiRequests.used.toLocaleString()} / {usageMetrics.apiRequests.limit.toLocaleString()}
                        </span>
                      </div>
                      <div className="w-full bg-black/40 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-1000 ${
                            getUsagePercentage(usageMetrics.apiRequests.used, usageMetrics.apiRequests.limit) >= 90 ? 'bg-red-400' :
                            getUsagePercentage(usageMetrics.apiRequests.used, usageMetrics.apiRequests.limit) >= 70 ? 'bg-yellow-400' : 'bg-green-400'
                          }`}
                          style={{ width: `${getUsagePercentage(usageMetrics.apiRequests.used, usageMetrics.apiRequests.limit)}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-4 bg-black/20 rounded-lg">
                      <h4 className="text-white font-medium mb-3">Storage</h4>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white/60 text-sm">Used storage</span>
                        <span className={`text-sm font-medium ${getUsageColor(getUsagePercentage(usageMetrics.storageGB.used, usageMetrics.storageGB.limit))}`}>
                          {usageMetrics.storageGB.used.toFixed(1)} GB / {usageMetrics.storageGB.limit} GB
                        </span>
                      </div>
                      <div className="w-full bg-black/40 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-1000 ${
                            getUsagePercentage(usageMetrics.storageGB.used, usageMetrics.storageGB.limit) >= 90 ? 'bg-red-400' :
                            getUsagePercentage(usageMetrics.storageGB.used, usageMetrics.storageGB.limit) >= 70 ? 'bg-yellow-400' : 'bg-green-400'
                          }`}
                          style={{ width: `${getUsagePercentage(usageMetrics.storageGB.used, usageMetrics.storageGB.limit)}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-4 bg-black/20 rounded-lg">
                      <h4 className="text-white font-medium mb-3">Team Members</h4>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white/60 text-sm">Active members</span>
                        <span className={`text-sm font-medium ${getUsageColor(getUsagePercentage(usageMetrics.teamMembers.used, usageMetrics.teamMembers.limit))}`}>
                          {usageMetrics.teamMembers.used} / {usageMetrics.teamMembers.limit}
                        </span>
                      </div>
                      <div className="w-full bg-black/40 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-1000 ${
                            getUsagePercentage(usageMetrics.teamMembers.used, usageMetrics.teamMembers.limit) >= 90 ? 'bg-red-400' :
                            getUsagePercentage(usageMetrics.teamMembers.used, usageMetrics.teamMembers.limit) >= 70 ? 'bg-yellow-400' : 'bg-green-400'
                          }`}
                          style={{ width: `${getUsagePercentage(usageMetrics.teamMembers.used, usageMetrics.teamMembers.limit)}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-4 bg-black/20 rounded-lg">
                      <h4 className="text-white font-medium mb-3">Consciousness Sync</h4>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white/60 text-sm">{usageMetrics.consciousnessSync.period}</span>
                        <span className={`text-sm font-medium ${getUsageColor(getUsagePercentage(usageMetrics.consciousnessSync.used, usageMetrics.consciousnessSync.limit))}`}>
                          {usageMetrics.consciousnessSync.used} / {usageMetrics.consciousnessSync.limit}
                        </span>
                      </div>
                      <div className="w-full bg-black/40 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-1000 ${
                            getUsagePercentage(usageMetrics.consciousnessSync.used, usageMetrics.consciousnessSync.limit) >= 90 ? 'bg-red-400' :
                            getUsagePercentage(usageMetrics.consciousnessSync.used, usageMetrics.consciousnessSync.limit) >= 70 ? 'bg-yellow-400' : 'bg-green-400'
                          }`}
                          style={{ width: `${getUsagePercentage(usageMetrics.consciousnessSync.used, usageMetrics.consciousnessSync.limit)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Tier Upgrade Modal */}
          {showTierUpgrade && (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
              <div className="bg-black/90 backdrop-blur-xl border border-white/10 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-medium text-white">Upgrade Your Tier</h3>
                  <button
                    onClick={() => setShowTierUpgrade(false)}
                    className="p-2 text-white/60 hover:text-white transition-colors"
                  >
                    <XCircleIcon className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  {Object.entries(TIER_PRICING).map(([tier, info]) => (
                    <div
                      key={tier}
                      className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                        selectedTier === tier
                          ? 'border-trinity-identity bg-trinity-identity/10'
                          : 'border-white/10 bg-black/20 hover:border-white/20'
                      } ${tier <= userTier ? 'opacity-50 cursor-not-allowed' : ''}`}
                      onClick={() => tier > userTier && setSelectedTier(tier)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-3">
                            <h4 className="text-white font-medium">{info.name}</h4>
                            <span className="px-2 py-1 bg-trinity-identity/20 text-trinity-identity rounded text-sm">
                              {tier}
                            </span>
                            {tier <= userTier && (
                              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-sm">
                                Current
                              </span>
                            )}
                          </div>
                          <div className="text-white/60 text-sm mt-1">
                            {info.features.join(' • ')}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-xl font-medium text-white">
                            ${info.price}
                          </div>
                          <div className="text-sm text-white/60">per month</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex space-x-3 mt-6">
                  <button
                    onClick={() => selectedTier && handleTierUpgrade(selectedTier)}
                    disabled={!selectedTier || processingPayment}
                    className="flex-1 px-6 py-3 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium disabled:opacity-50"
                  >
                    {processingPayment ? 'Processing...' : 'Upgrade Now'}
                  </button>
                  <button
                    onClick={() => setShowTierUpgrade(false)}
                    className="px-6 py-3 bg-gray-600 hover:bg-gray-700 transition-colors rounded-lg text-white font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </div>
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
            "Subscription and tier management with real-time billing",
            "Payment method management with secure storage",
            "Invoice history with downloadable receipts",
            "Usage monitoring and limit tracking",
            "Step-up authentication for all billing operations"
          ]}
          limitations={[
            "Requires step-up authentication for all operations",
            "Billing management available for paid tiers only",
            "Payment processing handled by third-party providers",
            "Usage metrics updated with 24-hour delay",
            "Tier downgrades may require billing cycle completion"
          ]}
          dependencies={[
            "Stripe payment processing and billing infrastructure",
            "LUKHAS AI usage tracking and metering systems",
            "Step-up authentication with passkey verification",
            "Invoice generation and PDF creation services"
          ]}
          dataHandling={[
            "Payment information processed securely by Stripe",
            "Billing data encoded → GLYPH before internal storage",
            "Usage metrics aggregated without storing individual requests",
            "Invoice downloads secured with temporary access tokens",
            "All billing operations logged for audit and compliance"
          ]}
          className="max-w-6xl mx-auto"
        />
      </div>
    </div>
  )
}
