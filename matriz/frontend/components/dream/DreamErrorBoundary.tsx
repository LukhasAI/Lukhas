'use client'

import { Component, ReactNode, ErrorInfo } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, RotateCcw } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export default class DreamErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Dream Weaver Error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen bg-black flex items-center justify-center p-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            className="max-w-md text-center"
          >
            {/* Error Icon */}
            <div className="relative mb-8">
              <div className="w-24 h-24 mx-auto bg-red-500/20 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-12 h-12 text-red-400" />
              </div>
              <div className="absolute inset-0 w-24 h-24 mx-auto bg-red-500/10 rounded-full animate-pulse" />
            </div>

            {/* Error Message */}
            <h2 className="text-2xl font-light text-white mb-4">
              Consciousness Stream Interrupted
            </h2>
            <p className="text-white/60 mb-8 leading-relaxed">
              The dream realm encountered a disturbance. Your consciousness seed remains safe,
              but we need to restart the journey.
            </p>

            {/* Reset Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                this.setState({ hasError: false, error: undefined })
                window.location.reload()
              }}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full font-medium hover:from-purple-500 hover:to-blue-500 transition-all duration-300 flex items-center gap-2 mx-auto"
            >
              <RotateCcw className="w-5 h-5" />
              Return to Portal
            </motion.button>

            {/* Error Details (Development) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-8 text-left">
                <summary className="text-white/40 text-sm cursor-pointer mb-2">
                  Error Details (Dev Mode)
                </summary>
                <pre className="text-xs text-red-400 bg-black/50 p-4 rounded-lg overflow-auto max-h-32">
                  {this.state.error.stack}
                </pre>
              </details>
            )}
          </motion.div>
        </div>
      )
    }

    return this.props.children
  }
}
