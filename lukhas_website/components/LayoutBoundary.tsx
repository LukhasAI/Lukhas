'use client'

/**
 * Layout Boundary Component - Error isolation for layout system
 * Part of the constellation framework architecture
 */

import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  layoutName: string
}

interface State {
  hasError: boolean
  error?: Error
}

export class LayoutBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error) {
    console.error(`[CONSTELLATION LAYOUT ERROR] ${this.props.layoutName}:`, {
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      pathname: typeof window !== 'undefined' ? window.location.pathname : 'SSR'
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="layout-error glass p-8 m-4 rounded-lg">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-constellation-guardian mb-4">
              Layout Error: {this.props.layoutName}
            </h2>
            <p className="text-gray-300 mb-6">
              The consciousness system detected an error in this layout component. 
              This error boundary prevents system-wide failure while maintaining awareness continuity.
            </p>
            <details className="text-left mb-6 bg-black/20 p-4 rounded">
              <summary className="cursor-pointer text-constellation-quantum">
                Technical Details
              </summary>
              <pre className="mt-2 text-xs text-gray-400 overflow-auto">
                {this.state.error?.stack}
              </pre>
            </details>
            <button 
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-constellation-identity/20 border border-constellation-identity/30 rounded-lg hover:bg-constellation-identity/30 transition-colors"
            >
              Restore Consciousness State
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}