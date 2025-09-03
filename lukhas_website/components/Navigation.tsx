'use client'

import { usePathname } from 'next/navigation'

export default function Navigation() {
  const pathname = usePathname()
  const isAppRoute = pathname?.startsWith('/studio') || pathname?.startsWith('/settings')

  if (isAppRoute) {
    return null
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-30 bg-black/20 backdrop-blur-md border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <a href="/" className="text-2xl text-white lukhas-brand">LUKHΛS</a>
          </div>
          <div className="hidden md:block">
            <div className="flex items-center space-x-8">
              <a href="/about" className="text-white/80 hover:text-white transition-colors">About</a>
              <a href="/vision" className="text-white/80 hover:text-white transition-colors">Vision</a>
              <a href="/careers" className="text-white/80 hover:text-white transition-colors">Careers</a>
              <a href="/docs" className="text-white/80 hover:text-white transition-colors">Docs</a>
              <a href="/privacy" className="text-white/80 hover:text-white transition-colors">Privacy</a>
              <a href="/terms" className="text-white/80 hover:text-white transition-colors">Terms</a>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <a
              href="/login"
              className="text-white/80 hover:text-white transition-colors"
            >
              Sign In
            </a>
            <a
              href="/studio"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              Enter LUKHΛS Studio
            </a>
          </div>
        </div>
      </div>
    </nav>
  )
}
