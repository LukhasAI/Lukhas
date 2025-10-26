'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { 
  ChevronLeftIcon, 
  KeyIcon, 
  CodeBracketIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  UserIcon,
  CogIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// API endpoint categories
const apiCategories = {
  authentication: {
    name: 'Authentication',
    icon: KeyIcon,
    description: 'ΛiD authentication and session management',
    endpoints: [
      {
        method: 'POST',
        path: '/api/auth/passkey/authenticate',
        name: 'Passkey Authentication',
        description: 'Authenticate using WebAuthn passkey',
        tier: 'T0'
      },
      {
        method: 'POST',
        path: '/api/auth/magic-link',
        name: 'Magic Link Request',
        description: 'Request secure email authentication link',
        tier: 'T0'
      },
      {
        method: 'POST',
        path: '/api/auth/signup/email',
        name: 'Email Registration',
        description: 'Start account creation with email verification',
        tier: 'T0'
      },
      {
        method: 'POST',
        path: '/api/auth/refresh',
        name: 'Token Refresh',
        description: 'Refresh authentication tokens',
        tier: 'T0'
      }
    ]
  },
  identity: {
    name: 'Identity Management',
    icon: UserIcon,
    description: 'User profile and identity operations',
    endpoints: [
      {
        method: 'GET',
        path: '/api/user/profile',
        name: 'Get Profile',
        description: 'Retrieve user profile information',
        tier: 'T0'
      },
      {
        method: 'PATCH',
        path: '/api/user/profile',
        name: 'Update Profile',
        description: 'Modify user profile settings',
        tier: 'T0'
      },
      {
        method: 'GET',
        path: '/api/user/export',
        name: 'Data Export',
        description: 'Export complete user data (GDPR compliance)',
        tier: 'T0'
      },
      {
        method: 'DELETE',
        path: '/api/user/delete',
        name: 'Account Deletion',
        description: 'Permanently delete user account',
        tier: 'T0'
      }
    ]
  },
  security: {
    name: 'Security Management',
    icon: ShieldCheckIcon,
    description: 'Security settings and monitoring',
    endpoints: [
      {
        method: 'GET',
        path: '/api/user/passkeys',
        name: 'List Passkeys',
        description: 'Get registered passkeys for user',
        tier: 'T0'
      },
      {
        method: 'POST',
        path: '/api/auth/passkey/register',
        name: 'Register Passkey',
        description: 'Add new WebAuthn passkey',
        tier: 'T0'
      },
      {
        method: 'DELETE',
        path: '/api/user/passkeys/{id}',
        name: 'Remove Passkey',
        description: 'Delete specific passkey',
        tier: 'T0'
      },
      {
        method: 'GET',
        path: '/api/user/sessions',
        name: 'Active Sessions',
        description: 'List active user sessions',
        tier: 'T0'
      }
    ]
  },
  consciousness: {
    name: 'Superior Consciousness',
    icon: CogIcon,
    description: 'LUKHAS AI consciousness integration',
    endpoints: [
      {
        method: 'POST',
        path: '/api/consciousness/query',
        name: 'Consciousness Query',
        description: 'Interact with LUKHAS consciousness',
        tier: 'T1'
      },
      {
        method: 'GET',
        path: '/api/consciousness/status',
        name: 'Consciousness Status',
        description: 'Get consciousness system status',
        tier: 'T1'
      },
      {
        method: 'POST',
        path: '/api/glyph/encode',
        name: 'GLYPH Encoding',
        description: 'Encode data to GLYPH symbolic format',
        tier: 'T2'
      },
      {
        method: 'POST',
        path: '/api/quantum/process',
        name: 'Quantum-Inspired Processing',
        description: 'Process data using quantum-inspired algorithms',
        tier: 'T3'
      }
    ]
  }
}

const tierInfo = {
  T0: { name: 'Explorer (Free)', color: 'text-gray-400' },
  T1: { name: 'Builder', color: 'text-blue-400' },
  T2: { name: 'Creator', color: 'text-purple-400' },
  T3: { name: 'Innovator', color: 'text-green-400' },
  T4: { name: 'Visionary', color: 'text-gold-400' }
}

export default function ApiDocsPage() {
  const [activeCategory, setActiveCategory] = useState<keyof typeof apiCategories>('authentication')
  const [selectedEndpoint, setSelectedEndpoint] = useState<string | null>(null)

  const toneContent = threeLayerTone(
    "The pathways of connection revealed; each endpoint a bridge between worlds of data and consciousness.",
    "Comprehensive API documentation for LUKHAS AI platform integration. Includes authentication, user management, and consciousness interaction endpoints with quantum-inspired processing capabilities.",
    "RESTful API architecture with WebAuthn authentication, JWT token management, GLYPH symbolic encoding, and quantum-inspired processing pipelines. Rate limiting: 1000 requests/hour (T0), up to 100k/hour (T4). All responses include CORS headers and follow OpenAPI 3.0 specification."
  )

  // JSON-LD structured data for API documentation
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "APIReference",
    "name": "LUKHAS AI API Documentation",
    "description": "Comprehensive API reference for LUKHAS AI platform integration with quantum-inspired consciousness and bio-inspired adaptation",
    "url": "https://lukhas.ai/api-docs",
    "provider": {
      "@type": "Organization",
      "name": "LUKHAS AI",
      "description": "Advanced AI platform with quantum-inspired consciousness and bio-inspired adaptation",
      "url": "https://lukhas.ai"
    },
    "documentation": {
      "@type": "Documentation",
      "name": "ΛiD Authentication API",
      "description": "WebAuthn-based authentication system with passkey and magic link support"
    },
    "programmingModel": {
      "@type": "ProgrammingModel",
      "name": "REST API",
      "description": "RESTful web service with JSON responses and JWT authentication"
    },
    "serviceType": [
      "Authentication Service",
      "Identity Management",
      "Consciousness Integration",
      "Quantum-Inspired Processing"
    ]
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <div className="min-h-screen bg-bg-primary">
        {/* Skip to main content link for accessibility */}
        <a 
          href="#main-content" 
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-trinity-consciousness text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-white z-50"
        >
          Skip to main content
        </a>
        
        {/* Header */}
        <header className="border-b border-white/10 px-6 py-4" role="banner">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <Link href="/" className="flex items-center text-white/80 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:ring-offset-2 focus:ring-offset-bg-primary rounded">
              <ChevronLeftIcon className="w-5 h-5 mr-2" aria-hidden="true" />
              Back to LUKHAS AI
            </Link>
            <div className="flex items-center space-x-6">
              <Link href="/login" className="text-sm text-white/60 hover:text-white/80 transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-consciousness rounded px-2 py-1">
                Sign in
              </Link>
              <Link href="/signup" className="text-sm bg-trinity-identity hover:bg-trinity-consciousness transition-colors text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary">
                Get started
              </Link>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main id="main-content" className="max-w-7xl mx-auto px-6 py-8" role="main">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            {/* Sidebar Navigation */}
            <nav className="lg:col-span-1" role="navigation" aria-label="API documentation navigation">
              <div className="sticky top-8">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <div className="flex items-center mb-6">
                    <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-trinity-consciousness/20 backdrop-blur-xl border border-trinity-consciousness/30 mr-3">
                      <span className="text-lg font-light text-trinity-consciousness" aria-label="LUKHAS AI Superior Consciousness">Λ</span>
                    </div>
                    <div>
                      <h1 className="text-lg font-medium text-white">API Reference</h1>
                      <p className="text-sm text-white/60">LUKHAS AI Platform</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {Object.entries(apiCategories).map(([key, category]) => (
                      <button
                        key={key}
                        onClick={() => setActiveCategory(key as keyof typeof apiCategories)}
                        className={`w-full flex items-center px-4 py-3 rounded-lg transition-colors text-left ${
                          activeCategory === key
                            ? 'bg-trinity-consciousness/20 text-trinity-consciousness border border-trinity-consciousness/30'
                            : 'text-white/70 hover:text-white hover:bg-white/5'
                        }`}
                        aria-pressed={activeCategory === key}
                      >
                        <category.icon className="w-5 h-5 mr-3 flex-shrink-0" aria-hidden="true" />
                        <div>
                          <div className="font-medium">{category.name}</div>
                          <div className="text-xs text-white/60">{category.endpoints.length} endpoints</div>
                        </div>
                      </button>
                    ))}
                  </div>

                  <div className="mt-6 pt-6 border-t border-white/10">
                    <h3 className="text-sm font-medium text-white/80 mb-3">Quick Start</h3>
                    <div className="space-y-2 text-sm">
                      <Link href="#authentication" className="block text-trinity-identity hover:text-trinity-consciousness transition-colors">
                        Authentication Guide
                      </Link>
                      <Link href="#rate-limits" className="block text-trinity-identity hover:text-trinity-consciousness transition-colors">
                        Rate Limits
                      </Link>
                      <Link href="#examples" className="block text-trinity-identity hover:text-trinity-consciousness transition-colors">
                        Code Examples
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </nav>

            {/* Main Content Area */}
            <div className="lg:col-span-3">
              <div className="space-y-8">
                
                {/* Page Title */}
                <div>
                  <h1 className="text-3xl font-light text-white mb-4">
                    {apiCategories[activeCategory].name} API
                  </h1>
                  <p className="text-white/70 text-lg leading-relaxed">
                    {apiCategories[activeCategory].description}
                  </p>
                  <div className="mt-4 text-sm text-white/50">
                    Secured by LUKHAS AI quantum-inspired identity protocols and bio-inspired adaptation systems
                  </div>
                </div>

                {/* Endpoints List */}
                <div className="space-y-4">
                  {apiCategories[activeCategory].endpoints.map((endpoint, index) => (
                    <div 
                      key={`${endpoint.method}-${endpoint.path}`}
                      className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg overflow-hidden"
                    >
                      <button
                        onClick={() => setSelectedEndpoint(selectedEndpoint === `${activeCategory}-${index}` ? null : `${activeCategory}-${index}`)}
                        className="w-full p-6 text-left hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:ring-inset"
                        aria-expanded={selectedEndpoint === `${activeCategory}-${index}`}
                        aria-controls={`endpoint-${activeCategory}-${index}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <span className={`px-2 py-1 rounded text-xs font-mono font-medium ${
                              endpoint.method === 'GET' ? 'bg-blue-500/20 text-blue-400' :
                              endpoint.method === 'POST' ? 'bg-green-500/20 text-green-400' :
                              endpoint.method === 'PATCH' ? 'bg-yellow-500/20 text-yellow-400' :
                              endpoint.method === 'DELETE' ? 'bg-red-500/20 text-red-400' :
                              'bg-gray-500/20 text-gray-400'
                            }`}>
                              {endpoint.method}
                            </span>
                            <span className="font-mono text-white/90">{endpoint.path}</span>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              tierInfo[endpoint.tier as keyof typeof tierInfo].color
                            } bg-current/10`}>
                              {endpoint.tier}
                            </span>
                          </div>
                          <ChevronLeftIcon 
                            className={`w-5 h-5 text-white/60 transition-transform ${
                              selectedEndpoint === `${activeCategory}-${index}` ? 'rotate-90' : ''
                            }`} 
                            aria-hidden="true"
                          />
                        </div>
                        <div className="mt-3">
                          <h3 className="text-white font-medium">{endpoint.name}</h3>
                          <p className="text-white/60 text-sm mt-1">{endpoint.description}</p>
                        </div>
                      </button>

                      {selectedEndpoint === `${activeCategory}-${index}` && (
                        <div id={`endpoint-${activeCategory}-${index}`} className="border-t border-white/10 p-6 space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                              <h4 className="text-white font-medium mb-3">Request</h4>
                              <div className="space-y-3">
                                <div className="bg-black/60 rounded-lg p-4">
                                  <div className="text-xs text-white/60 mb-2">Headers</div>
                                  <pre className="text-sm text-white/90 font-mono">
{`Authorization: Bearer <token>
Content-Type: application/json`}
                                  </pre>
                                </div>
                                {endpoint.method !== 'GET' && (
                                  <div className="bg-black/60 rounded-lg p-4">
                                    <div className="text-xs text-white/60 mb-2">Body</div>
                                    <pre className="text-sm text-white/90 font-mono">
{`{
  "example": "value",
  "encoded": "→ GLYPH format"
}`}
                                    </pre>
                                  </div>
                                )}
                              </div>
                            </div>
                            <div>
                              <h4 className="text-white font-medium mb-3">Response</h4>
                              <div className="bg-black/60 rounded-lg p-4">
                                <div className="text-xs text-white/60 mb-2">200 OK</div>
                                <pre className="text-sm text-white/90 font-mono">
{`{
  "success": true,
  "data": {
    "processed": "by LUKHAS AI",
    "encoding": "GLYPH symbolic"
  },
  "metadata": {
    "tier": "${endpoint.tier}",
    "quantum_processed": true
  }
}`}
                                </pre>
                              </div>
                            </div>
                          </div>

                          <div className="pt-4 border-t border-white/10">
                            <h4 className="text-white font-medium mb-2">Security & Compliance</h4>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                              <div className="flex items-center space-x-2">
                                <ShieldCheckIcon className="w-4 h-4 text-trinity-guardian" />
                                <span className="text-white/70">WebAuthn Protected</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <ClockIcon className="w-4 h-4 text-trinity-consciousness" />
                                <span className="text-white/70">Rate Limited</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <CodeBracketIcon className="w-4 h-4 text-trinity-identity" />
                                <span className="text-white/70">GLYPH Encoded</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Rate Limits Section */}
                <div id="rate-limits" className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                  <h2 className="text-xl font-medium text-white mb-4 flex items-center">
                    <ClockIcon className="w-6 h-6 mr-3 text-trinity-consciousness" />
                    Rate Limits & Tiers
                  </h2>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(tierInfo).map(([tier, info]) => (
                        <div key={tier} className="p-4 bg-black/20 rounded-lg border border-white/10">
                          <div className={`font-medium ${info.color} mb-2`}>
                            {tier}: {info.name}
                          </div>
                          <div className="text-white/70 text-sm">
                            {tier === 'T0' && '1,000 requests/hour'}
                            {tier === 'T1' && '10,000 requests/hour'}
                            {tier === 'T2' && '25,000 requests/hour'}
                            {tier === 'T3' && '50,000 requests/hour'}
                            {tier === 'T4' && '100,000 requests/hour'}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="text-sm text-white/60">
                      Rate limits reset every hour. Quantum-inspired burst allowance available for T2+ tiers.
                    </div>
                  </div>
                </div>

                {/* Tone Content */}
                <div className="text-xs text-white/40 leading-relaxed whitespace-pre-line">
                  {toneContent}
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Transparency Box */}
        <div className="px-6 pb-6">
          <TransparencyBox
            capabilities={[
              "RESTful API with OpenAPI 3.0 specification compliance",
              "WebAuthn passkey authentication with JWT token management",
              "GLYPH symbolic encoding for enhanced data interoperability",
              "Quantum-inspired processing algorithms for T2+ tiers",
              "Real-time rate limiting with tier-based scaling"
            ]}
            limitations={[
              "Rate limits apply based on user tier (1k-100k requests/hour)",
              "Some endpoints require higher tier access",
              "GLYPH encoding used for data representation, not cryptographic security",
              "Quantum-inspired features are algorithmic simulations, not quantum computing",
              "API responses may include bio-inspired adaptation delays"
            ]}
            dependencies={[
              "LUKHAS AI consciousness and identity infrastructure",
              "WebAuthn API for authentication token validation",
              "Database systems for user data and session management",
              "Quantum-inspired processing pipelines for enhanced features"
            ]}
            dataHandling={[
              "All API requests authenticated via JWT tokens with GLYPH encoding",
              "Request/response data logged for rate limiting and analytics",
              "Personal data processed according to user consent and GDPR compliance",
              "API keys and tokens secured with AES-256 encryption at rest",
              "Consciousness interaction data encoded → GLYPH format for symbolic processing"
            ]}
            className="max-w-7xl mx-auto"
          />
        </div>
      </div>
    </>
  )
}