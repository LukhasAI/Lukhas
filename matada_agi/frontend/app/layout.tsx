import type { Metadata } from 'next'
import '../styles/globals.css'

export const metadata: Metadata = {
  title: 'LUKHAS - Modular Adaptive Temporal Attention Dynamic Architecture',
  description: 'Building consciousness you can trust. MATADA - Every thought becomes a traceable, governed, evolvable node.',
  keywords: 'AGI, MATADA, LUKHAS, artificial intelligence, cognitive architecture, consciousness',
  authors: [{ name: 'LUKHAS AI Systems' }],
  openGraph: {
    title: 'LUKHAS - MATADA AGI',
    description: 'Building consciousness you can trust',
    type: 'website',
    url: 'https://lukhas.ai',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'LUKHAS MATADA AGI',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LUKHAS - MATADA AGI',
    description: 'Building consciousness you can trust',
    images: ['/og-image.png'],
  },
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="/fonts" />
        <link rel="dns-prefetch" href="/fonts" />
      </head>
      <body className="min-h-screen bg-black text-white antialiased">
        <div className="relative">
          {/* Background effects */}
          <div className="fixed inset-0 -z-10">
            <div className="absolute inset-0 bg-gradient-to-b from-gray-900 to-black" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_#2563EB_0%,_transparent_70%)] opacity-10" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_#7C3AED_0%,_transparent_70%)] opacity-10" />
          </div>
          
          {/* Main content */}
          {children}
        </div>
      </body>
    </html>
  )
}