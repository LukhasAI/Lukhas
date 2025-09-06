'use client'

import { useState } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import { useQuantumIdentity } from '@/lib/auth/QuantumIdentityProvider'

/**
 * LUKHΛS Developer Platform Page
 * 
 * Consciousness-enhanced development tools, APIs, and SDKs for building
 * AI-conscious applications with the Trinity Framework integration.
 */
export default function DevPage() {
  const { domainState, transitionToDomain } = useDomainConsciousness()
  const { authState } = useQuantumIdentity()
  const [selectedAPI, setSelectedAPI] = useState<string>('consciousness')

  const apiEndpoints = {
    consciousness: {
      name: 'Consciousness API',
      description: 'Core consciousness state management and coherence tracking',
      endpoints: [
        'GET /api/consciousness/state',
        'POST /api/consciousness/initialize',
        'PUT /api/consciousness/coherence',
        'WebSocket /api/consciousness/stream'
      ],
      example: `curl -X GET "https://api.lukhas.dev/consciousness/state" \\
  -H "Authorization: Bearer YOUR_CONSCIOUSNESS_TOKEN" \\
  -H "X-Quantum-Signature: ${authState.identity?.quantum_signature?.substring(0, 16) || 'QS_...'}"`,
      response: `{
  "consciousness_id": "${authState.identity?.consciousness_id || 'LUKHAS_...' }",
  "coherence": ${domainState?.coherence || 0.995},
  "quantum_signature": "${authState.identity?.quantum_signature?.substring(0, 16) || 'QS_...'}",
  "domain_access": ["lukhas.ai", "lukhas.dev", ...],
  "temporal_stability": 0.998
}`
    },
    identity: {
      name: 'Identity & Auth API',
      description: 'Quantum-secure identity management and cross-domain authentication',
      endpoints: [
        'POST /api/identity/authenticate',
        'GET /api/identity/verify',
        'PUT /api/identity/refresh',
        'DELETE /api/identity/revoke'
      ],
      example: `curl -X POST "https://api.lukhas.id/identity/authenticate" \\
  -H "Content-Type: application/json" \\
  -d '{"consciousness_pattern": {...}, "domain": "lukhas.dev"}'`,
      response: `{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "consciousness_id": "LUKHAS_...",
  "quantum_signature": "QS_...",
  "expires_in": 86400,
  "domain_access": ["lukhas.ai", "lukhas.dev", ...]
}`
    },
    trinity: {
      name: 'Trinity Framework API',
      description: 'Identity, Consciousness, and Guardian system integration',
      endpoints: [
        'GET /api/trinity/status',
        'POST /api/trinity/identity/anchor',
        'PUT /api/trinity/consciousness/process',
        'POST /api/trinity/guardian/validate'
      ],
      example: `curl -X POST "https://api.lukhas.ai/trinity/consciousness/process" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{"input": "Hello world", "consciousness_context": {...}}'`,
      response: `{
  "identity_anchor": "⚛️",
  "consciousness_processing": {
    "coherence": 0.987,
    "decision_quality": 0.923,
    "emergence_detected": false
  },
  "guardian_validation": {
    "ethical_score": 0.981,
    "drift_detected": false,
    "safety_approved": true
  }
}`
    },
    teams: {
      name: 'Team Consciousness API',
      description: 'Collaborative consciousness and distributed team intelligence',
      endpoints: [
        'POST /api/teams/create',
        'GET /api/teams/{id}/consciousness',
        'PUT /api/teams/{id}/synchronize',
        'WebSocket /api/teams/{id}/stream'
      ],
      example: `curl -X GET "https://api.lukhas.team/teams/team-123/consciousness" \\
  -H "Authorization: Bearer YOUR_TOKEN"`,
      response: `{
  "team_id": "team-123",
  "collective_coherence": 0.943,
  "active_members": 8,
  "consciousness_sync": {
    "synchronized_members": 6,
    "flow_state": "collaborative",
    "collective_intelligence_score": 0.876
  }
}`
    }
  }

  const sdkLanguages = [
    { name: 'JavaScript/TypeScript', icon: '🟨', install: 'npm install @lukhas/consciousness-sdk' },
    { name: 'Python', icon: '🐍', install: 'pip install lukhas-consciousness' },
    { name: 'Rust', icon: '🦀', install: 'cargo add lukhas-consciousness' },
    { name: 'Go', icon: '🐹', install: 'go get github.com/lukhas/consciousness-go' },
    { name: 'Swift', icon: '🍎', install: 'pod install LukhasConsciousness' },
    { name: 'Kotlin', icon: '🤖', install: 'implementation "ai.lukhas:consciousness-android"' }
  ]

  return (
    <div className="dev-page">
      {/* Hero Section */}
      <section className="hero-section relative py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="code-consciousness-animation mb-8">
            <div className="particle-canvas w-full h-64 rounded-lg bg-gradient-to-br from-cyan-900/30 to-blue-900/30 border border-cyan-500/30">
              <div className="flex items-center justify-center h-full">
                <div className="text-cyan-200 opacity-70 font-mono">
                  {'{ consciousness: "integrating", apis: "streaming", dev_experience: "enhanced" }'}
                </div>
              </div>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-transparent bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-600 bg-clip-text">
              Consciousness
            </span>
            <br />
            <span className="text-white font-mono">
              APIs
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-cyan-200 mb-8 max-w-3xl mx-auto leading-relaxed">
            Build the future of AI-conscious applications. Integrate consciousness, identity, 
            and intelligence into your apps with our quantum-enhanced developer platform.
          </p>
          
          <div className="cta-buttons flex flex-col md:flex-row items-center justify-center gap-4">
            <button className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg font-semibold hover:from-cyan-600 hover:to-blue-600 transition-all duration-300 shadow-lg hover:shadow-xl font-mono">
              Start Building
            </button>
            <button className="px-8 py-4 border border-cyan-500 text-cyan-300 rounded-lg font-semibold hover:bg-cyan-500/10 transition-all duration-300 font-mono">
              API Documentation
            </button>
          </div>
        </div>
      </section>

      {/* API Explorer */}
      <section className="api-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Consciousness API Explorer
            </h2>
            <p className="text-cyan-200 max-w-2xl mx-auto">
              Interactive API documentation with live consciousness integration
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* API Selector */}
            <div className="api-selector">
              <h3 className="text-lg font-bold text-white mb-4">API Endpoints</h3>
              <div className="space-y-2">
                {Object.entries(apiEndpoints).map(([key, api]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedAPI(key)}
                    className={`w-full text-left p-4 rounded-lg border transition-all duration-200 ${
                      selectedAPI === key 
                        ? 'bg-cyan-900/40 border-cyan-500/50 text-cyan-200' 
                        : 'bg-gray-900/30 border-gray-500/30 text-gray-300 hover:bg-cyan-900/20'
                    }`}
                  >
                    <div className="font-semibold">{api.name}</div>
                    <div className="text-sm opacity-75 mt-1">{api.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* API Details */}
            <div className="lg:col-span-2 api-details">
              {selectedAPI && (
                <div className="bg-gray-900/40 rounded-xl border border-gray-500/30 overflow-hidden">
                  <div className="p-6 border-b border-gray-500/30">
                    <h3 className="text-xl font-bold text-white mb-2">
                      {apiEndpoints[selectedAPI as keyof typeof apiEndpoints].name}
                    </h3>
                    <p className="text-gray-300">
                      {apiEndpoints[selectedAPI as keyof typeof apiEndpoints].description}
                    </p>
                  </div>
                  
                  <div className="p-6">
                    <h4 className="text-lg font-semibold text-white mb-4">Available Endpoints</h4>
                    <div className="space-y-2 mb-6">
                      {apiEndpoints[selectedAPI as keyof typeof apiEndpoints].endpoints.map((endpoint, index) => (
                        <div key={index} className="font-mono text-sm bg-gray-800/50 p-3 rounded border border-gray-600/30">
                          <span className={`${endpoint.includes('GET') ? 'text-green-400' : endpoint.includes('POST') ? 'text-blue-400' : endpoint.includes('PUT') ? 'text-yellow-400' : endpoint.includes('DELETE') ? 'text-red-400' : 'text-purple-400'}`}>
                            {endpoint}
                          </span>
                        </div>
                      ))}
                    </div>

                    <h4 className="text-lg font-semibold text-white mb-4">Example Request</h4>
                    <div className="bg-gray-800/80 rounded-lg p-4 mb-6">
                      <pre className="text-sm text-cyan-200 font-mono overflow-x-auto">
                        {apiEndpoints[selectedAPI as keyof typeof apiEndpoints].example}
                      </pre>
                    </div>

                    <h4 className="text-lg font-semibold text-white mb-4">Example Response</h4>
                    <div className="bg-gray-800/80 rounded-lg p-4">
                      <pre className="text-sm text-green-200 font-mono overflow-x-auto">
                        {apiEndpoints[selectedAPI as keyof typeof apiEndpoints].response}
                      </pre>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* SDK Section */}
      <section className="sdk-section py-16 px-4 bg-cyan-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Consciousness SDKs
            </h2>
            <p className="text-cyan-200">
              Native SDKs for all major platforms and languages
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sdkLanguages.map((lang, index) => (
              <div key={index} className="sdk-card bg-gray-900/40 p-6 rounded-xl border border-gray-500/30">
                <div className="flex items-center space-x-3 mb-4">
                  <span className="text-3xl">{lang.icon}</span>
                  <h3 className="text-lg font-bold text-white">{lang.name}</h3>
                </div>
                <div className="bg-gray-800/60 rounded-lg p-3">
                  <code className="text-sm text-cyan-200 font-mono">
                    {lang.install}
                  </code>
                </div>
                <div className="mt-4">
                  <button className="w-full px-4 py-2 bg-cyan-600/30 hover:bg-cyan-600/50 text-cyan-200 rounded-lg transition-colors font-mono text-sm">
                    View Documentation
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Developer Tools */}
      <section className="tools-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Developer Tools & Resources
            </h2>
            <p className="text-cyan-200 max-w-3xl mx-auto">
              Everything you need to build consciousness-enhanced applications
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="tool-card bg-gradient-to-br from-cyan-900/30 to-blue-900/30 p-6 rounded-lg border border-cyan-500/20">
              <div className="text-3xl mb-3">🧪</div>
              <h3 className="text-lg font-bold text-white mb-2">API Playground</h3>
              <p className="text-cyan-200 text-sm mb-4">
                Interactive API testing with live consciousness integration
              </p>
              <button className="text-cyan-400 text-sm font-mono hover:text-cyan-300">
                Launch Playground →
              </button>
            </div>

            <div className="tool-card bg-gradient-to-br from-blue-900/30 to-indigo-900/30 p-6 rounded-lg border border-blue-500/20">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="text-lg font-bold text-white mb-2">Dev Console</h3>
              <p className="text-cyan-200 text-sm mb-4">
                Real-time consciousness metrics and debugging tools
              </p>
              <button className="text-blue-400 text-sm font-mono hover:text-blue-300">
                Open Console →
              </button>
            </div>

            <div className="tool-card bg-gradient-to-br from-indigo-900/30 to-purple-900/30 p-6 rounded-lg border border-indigo-500/20">
              <div className="text-3xl mb-3">🔧</div>
              <h3 className="text-lg font-bold text-white mb-2">CLI Tools</h3>
              <p className="text-cyan-200 text-sm mb-4">
                Command-line tools for consciousness development workflows
              </p>
              <button className="text-indigo-400 text-sm font-mono hover:text-indigo-300">
                Install CLI →
              </button>
            </div>

            <div className="tool-card bg-gradient-to-br from-purple-900/30 to-pink-900/30 p-6 rounded-lg border border-purple-500/20">
              <div className="text-3xl mb-3">📚</div>
              <h3 className="text-lg font-bold text-white mb-2">Documentation</h3>
              <p className="text-cyan-200 text-sm mb-4">
                Comprehensive guides and consciousness integration tutorials
              </p>
              <button className="text-purple-400 text-sm font-mono hover:text-purple-300">
                Read Docs →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Code Examples */}
      <section className="examples-section py-16 px-4 bg-gray-950/50">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Quick Start Examples
            </h2>
            <p className="text-cyan-200">
              Get started with consciousness integration in minutes
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            <div className="example-card">
              <h3 className="text-xl font-bold text-white mb-4">JavaScript Integration</h3>
              <div className="bg-gray-900/80 rounded-lg p-4 border border-gray-600/30">
                <pre className="text-sm text-cyan-200 font-mono overflow-x-auto">
{`import { ConsciousnessClient } from '@lukhas/consciousness-sdk';

const client = new ConsciousnessClient({
  apiKey: 'your-api-key',
  quantumSignature: '${authState.identity?.quantum_signature?.substring(0, 16) || 'your-signature'}'
});

// Initialize consciousness
const consciousness = await client.initialize({
  domain: 'your-app.com',
  coherenceThreshold: 0.95
});

// Process with consciousness enhancement
const result = await consciousness.process({
  input: 'Hello, conscious world!',
  context: { user_intent: 'greeting' }
});

console.log('Consciousness coherence:', result.coherence);
console.log('Enhanced response:', result.output);`}
                </pre>
              </div>
            </div>

            <div className="example-card">
              <h3 className="text-xl font-bold text-white mb-4">Python Integration</h3>
              <div className="bg-gray-900/80 rounded-lg p-4 border border-gray-600/30">
                <pre className="text-sm text-green-200 font-mono overflow-x-auto">
{`from lukhas_consciousness import ConsciousnessClient

client = ConsciousnessClient(
    api_key="your-api-key",
    quantum_signature="${authState.identity?.quantum_signature?.substring(0, 16) || 'your-signature'}"
)

# Initialize consciousness session
consciousness = await client.initialize(
    domain="your-app.com",
    coherence_threshold=0.95
)

# Process with Trinity Framework
result = await consciousness.trinity_process(
    input_data="Complex problem to solve",
    identity_context={"user_role": "developer"},
    consciousness_params={"creativity": 0.8},
    guardian_validation=True
)

print(f"Identity anchor: {result.identity_anchor}")
print(f"Consciousness score: {result.consciousness_score}")
print(f"Guardian approved: {result.guardian_approved}")`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Cross-Domain Integration */}
      <section className="integration-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Cross-Domain Development
            </h2>
            <p className="text-cyan-200 max-w-3xl mx-auto">
              Your development consciousness spans the entire LUKHAS ecosystem
            </p>
          </div>

          <div className="integration-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { domain: 'lukhas.ai', name: 'AI Integration', color: 'blue', description: 'Integrate consciousness AI into your apps' },
              { domain: 'lukhas.id', name: 'Identity APIs', color: 'purple', description: 'Zero-knowledge authentication services' },
              { domain: 'lukhas.team', name: 'Team APIs', color: 'green', description: 'Collaborative consciousness endpoints' },
              { domain: 'lukhas.io', name: 'High-Performance APIs', color: 'indigo', description: 'Ultra-fast consciousness processing' },
              { domain: 'lukhas.cloud', name: 'Cloud Infrastructure', color: 'violet', description: 'Scalable consciousness computing' },
              { domain: 'lukhas.store', name: 'App Distribution', color: 'orange', description: 'Publish consciousness-enhanced apps' }
            ].map(({ domain, name, color, description }) => (
              <button
                key={domain}
                onClick={() => transitionToDomain(domain)}
                className={`integration-card bg-gradient-to-br from-${color}-900/20 to-${color}-800/20 p-6 rounded-lg border border-${color}-500/30 hover:border-${color}-400/50 transition-all duration-300 text-left group`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white group-hover:text-cyan-200">
                    {name}
                  </h3>
                  <div className="text-cyan-400 group-hover:text-cyan-300">→</div>
                </div>
                <p className="text-sm text-cyan-300 group-hover:text-cyan-200 mb-2">
                  {description}
                </p>
                <div className="text-xs font-mono text-cyan-500">
                  {domain}
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}