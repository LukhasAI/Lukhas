import dynamic from 'next/dynamic'
import StateLayout from '@/components/state-layout'
import CMP from '@/components/cmp'
import type { Metadata } from 'next'
import { Providers } from '@/components/providers'
import './globals.css'
import '../styles/auth-accessibility.css'

const NeuralBackground = dynamic(() => import('@/components/neural-background'), { ssr: false })

export const metadata: Metadata = {
  title: 'LUKHΛS — AI Web Studio',
  description: 'Logical Unified Knowledge Hyper-Adaptive Superior Systems. Consciousness technology platform powered by MΛTRIZ cognitive architecture and Trinity Framework.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const bgEnabled = process.env.NEXT_PUBLIC_BG_ENABLED !== 'false'

  return (
    <html lang="en" suppressHydrationWarning>
      <body className="text-white antialiased">
        <Providers>
          {bgEnabled && <NeuralBackground mode="landing" />}
          <StateLayout>
            {children}
          </StateLayout>
          <CMP />
        </Providers>
      </body>
    </html>
  )
}
