import { ThemeProvider } from '@/components/theme-provider'
import { TranslationProvider } from '@/components/translation-provider'
import type { Metadata } from 'next'
import './globals.css'

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
      <body className="bg-bg-primary text-text-primary antialiased">
        <ThemeProvider defaultTheme="system" storageKey="lukhas-theme">
          <TranslationProvider>
            {children}
          </TranslationProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}