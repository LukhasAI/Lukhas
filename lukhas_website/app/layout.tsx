'use client'

import NeuralBackgroundWrapper from '@/components/neural-background-wrapper'
import StateLayout from '@/components/state-layout'
import CMP from '@/components/cmp'
import { Toaster } from 'sonner'
import { usePathname } from 'next/navigation'
import { QuantumIdentityProvider } from '@/lib/auth/QuantumIdentityProvider'
import { LayoutBoundary } from '@/components/LayoutBoundary'
import './globals.css'
import '../styles/auth-accessibility.css'
import '../styles/domain-themes.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const bgEnabled = process.env.NEXT_PUBLIC_BG_ENABLED !== 'false'
  const isAppRoute = pathname?.startsWith('/studio') || pathname?.startsWith('/settings')

  // Debug: Log layout rendering chain in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[CONSTELLATION ROOT] Layout rendering', {
      timestamp: new Date().toISOString(),
      pathname: typeof window !== 'undefined' ? window.location.pathname : 'SSR',
      bgEnabled,
      isAppRoute,
      framework: 'constellation-8-star'
    })
  }

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <title>LUKHΛS — AI Web Studio</title>
        <meta name="description" content="Consciousness technology platform navigating by eight stars through fertile uncertainty. MΛTRIZ cognitive architecture with constellation framework guidance: Identity, Memory, Vision, Bio-adaptation, Dream, Ethics, Guardian, and Quantum dimensions." />
        {/* Layout debugging styles */}
        {process.env.NODE_ENV === 'development' && (
          <style dangerouslySetInnerHTML={{
            __html: `
              /* Layout debugging - visual indicators */
              body[data-debug="layout"] .layout-container::before {
                content: "ROOT LAYOUT";
                position: fixed;
                top: 10px;
                left: 10px;
                z-index: 99999;
                background: rgba(107, 70, 193, 0.8);
                color: white;
                padding: 4px 8px;
                font-size: 12px;
                border-radius: 4px;
                font-family: monospace;
              }
            `
          }} />
        )}
      </head>
      <body 
        className="text-white antialiased layout-container"
        data-layout="root" 
        data-framework="constellation"
        data-debug={process.env.NODE_ENV === 'development' ? 'layout' : undefined}
      >
        <LayoutBoundary layoutName="RootLayout">
          <QuantumIdentityProvider>
            <LayoutBoundary layoutName="QuantumIdentityProvider">
              {bgEnabled && <NeuralBackgroundWrapper mode="landing" />}
              <LayoutBoundary layoutName="StateLayout">
                <StateLayout>
                  {children}
                </StateLayout>
              </LayoutBoundary>
              <Toaster richColors />
              {!isAppRoute && <CMP />}
            </LayoutBoundary>
          </QuantumIdentityProvider>
        </LayoutBoundary>
      </body>
    </html>
  )
}
