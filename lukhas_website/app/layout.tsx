import type { Metadata } from 'next'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { TranslationProvider } from '@/components/translation-provider'

export const metadata: Metadata = {
  title: 'LUKHAS AI - Building Consciousness You Can Trust',
  description: 'Logical Unified Knowledge Hyper-Adaptive Superior Systems. Revolutionary AI platform powered by MATADA cognitive architecture and Trinity Framework.',
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