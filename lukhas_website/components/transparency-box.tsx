'use client'

import React, { useState } from 'react'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'

interface TransparencyBoxProps {
  capabilities: string[]
  limitations: string[]
  dependencies: string[]
  dataHandling: string[]
  className?: string
  defaultExpanded?: boolean
}

export default function TransparencyBox({ 
  capabilities, 
  limitations, 
  dependencies, 
  dataHandling,
  className = '',
  defaultExpanded = false 
}: TransparencyBoxProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
    
    // Analytics event for transparency engagement
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'transparency_toggle', {
        event_category: 'engagement',
        event_label: isExpanded ? 'collapse' : 'expand'
      })
    }
  }

  return (
    <div 
      className={`transparency-box bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg overflow-hidden ${className}`}
      role="complementary"
      aria-labelledby="transparency-title"
    >
      <button
        onClick={toggleExpanded}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-inset"
        aria-expanded={isExpanded}
        aria-controls="transparency-content"
      >
        <h3 id="transparency-title" className="text-sm font-medium text-white/90">
          🔍 Transparency & Limitations
        </h3>
        {isExpanded ? (
          <ChevronUpIcon className="w-4 h-4 text-white/60" aria-hidden="true" />
        ) : (
          <ChevronDownIcon className="w-4 h-4 text-white/60" aria-hidden="true" />
        )}
      </button>

      {isExpanded && (
        <div id="transparency-content" className="px-4 pb-4 space-y-4">
          {/* What It Does */}
          <section>
            <h4 className="text-xs font-semibold text-green-400 uppercase tracking-wide mb-2">
              ✅ What MATRIZ Does
            </h4>
            <ul className="text-sm text-white/70 space-y-1">
              {capabilities.map((capability, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-green-400 mr-2 mt-0.5">•</span>
                  {capability}
                </li>
              ))}
            </ul>
          </section>

          {/* What It Doesn't Do */}
          <section>
            <h4 className="text-xs font-semibold text-yellow-400 uppercase tracking-wide mb-2">
              ⚠️ Limitations
            </h4>
            <ul className="text-sm text-white/70 space-y-1">
              {limitations.map((limitation, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-yellow-400 mr-2 mt-0.5">•</span>
                  {limitation}
                </li>
              ))}
            </ul>
          </section>

          {/* Dependencies */}
          <section>
            <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wide mb-2">
              🔧 Dependencies
            </h4>
            <ul className="text-sm text-white/70 space-y-1">
              {dependencies.map((dependency, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-400 mr-2 mt-0.5">•</span>
                  {dependency}
                </li>
              ))}
            </ul>
          </section>

          {/* Data Handling */}
          <section>
            <h4 className="text-xs font-semibold text-purple-400 uppercase tracking-wide mb-2">
              🛡️ Data Handling
            </h4>
            <ul className="text-sm text-white/70 space-y-1">
              {dataHandling.map((policy, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-purple-400 mr-2 mt-0.5">•</span>
                  {policy}
                </li>
              ))}
            </ul>
          </section>

          {/* Footer Note */}
          <div className="pt-3 border-t border-white/10">
            <p className="text-xs text-white/50">
              This transparency information is required on all LUKHAS AI product pages. 
              Report issues via <a href="/support" className="text-purple-400 hover:text-purple-300">support</a>.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

// Pre-configured component for MATRIZ page
export function MatrizTransparencyBox(props: { className?: string; defaultExpanded?: boolean }) {
  return (
    <TransparencyBox
      capabilities={[
        "Tracks AI decision-making processes in real-time",
        "Creates audit trails for compliance requirements",
        "Visualizes reasoning chains and data dependencies",
        "Monitors system behavior for drift detection",
        "Integrates with LUKHAS identity and governance systems"
      ]}
      limitations={[
        "Does not guarantee decision accuracy or validity",
        "Coverage depends on system configuration (typically 85-95%)",
        "Cannot trace decisions from external AI systems",
        "Requires integration with LUKHAS core modules v2.1+",
        "Real-time monitoring may impact system latency (<100ms p95)"
      ]}
      dependencies={[
        "LUKHAS Core Identity System (ΛID v2.1 or higher)",
        "Guardian System for ethical oversight validation",
        "Memory system for persistent audit trail storage",
        "Network connectivity for distributed tracing",
        "Minimum 4GB RAM and 10GB storage for local deployment"
      ]}
      dataHandling={[
        "Decision metadata encrypted at rest (AES-256)",
        "User consent required before any data collection",
        "Audit trails automatically purged after 90 days (configurable)",
        "No personal data processed without explicit permission",
        "Full GDPR/CCPA compliance with data export/deletion rights",
        "Third-party API calls logged but not stored permanently"
      ]}
      {...props}
    />
  )
}