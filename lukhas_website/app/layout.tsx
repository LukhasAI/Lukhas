'use client'

import NeuralBackgroundWrapper from '@/components/neural-background-wrapper'
import StateLayout from '@/components/state-layout'
import CMP from '@/components/cmp'
import { Toaster } from 'sonner'
import { usePathname } from 'next/navigation'
import './globals.css'
import '../styles/auth-accessibility.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const bgEnabled = process.env.NEXT_PUBLIC_BG_ENABLED !== 'false'
  const isAppRoute = pathname?.startsWith('/studio') || pathname?.startsWith('/settings')

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <title>LUKHΛS — AI Web Studio</title>
        <meta name="description" content="Logical Unified Knowledge Hyper-Adaptive Superior Systems. Consciousness technology platform powered by MΛTRIZ cognitive architecture and Trinity Framework." />
      </head>
      <body className="text-white antialiased">
        {bgEnabled && <NeuralBackgroundWrapper mode="landing" />}
        <StateLayout>
          {children}
        </StateLayout>
        <Toaster richColors />
        {!isAppRoute && <CMP />}
      </body>
    </html>
  )
}
