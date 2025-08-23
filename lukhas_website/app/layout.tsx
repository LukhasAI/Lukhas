import { ThemeProvider } from '@/components/theme-provider'
import { TranslationProvider } from '@/components/translation-provider'
import StateLayout from '@/components/state-layout'
import type { Metadata } from 'next'
import './globals.css'
import '../styles/auth-accessibility.css'

export const metadata: Metadata = {
  title: 'LUKHAS AI - Building Consciousness You Can Trust',
  description: 'Logical Unified Knowledge Hyper-Adaptive Superior Systems. Consciousness technology platform powered by MATRIZ cognitive architecture and Trinity Framework.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="text-text-primary antialiased">
        <ThemeProvider defaultTheme="system" storageKey="lukhas-theme">
          <TranslationProvider>
            <StateLayout>
              {children}
            </StateLayout>
          </TranslationProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}