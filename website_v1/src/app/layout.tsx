import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@/components/ui/ThemeProvider';
import Header from '@/components/ui/Header';
// import CursorFollower from '@/components/ui/CursorFollower';
import PageTransition from '@/components/ui/PageTransition';
import './globals.css';

const inter = Inter({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600'],
  variable: '--font-inter'
});

export const viewport = 'width=device-width, initial-scale=1';

export const metadata: Metadata = {
  title: 'Lucas - One box. One brain. All your tools.',
  description: 'Unified AI workspace with adaptive canvas and orchestration.',
  keywords: ['AI', 'workspace', 'productivity', 'unified', 'tools'],
  authors: [{ name: 'Lucas' }],
  openGraph: {
    title: 'Lucas - One box. One brain. All your tools.',
    description: 'Unified AI workspace with adaptive canvas and orchestration.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Lucas - One box. One brain. All your tools.',
    description: 'Unified AI workspace with adaptive canvas and orchestration.',
  },
  robots: 'index, follow',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} dark`}>
      <body className="antialiased overflow-x-hidden">
        <ThemeProvider>
          <Header />
          {/* <CursorFollower /> */}
          <PageTransition>
            {children}
          </PageTransition>
        </ThemeProvider>
      </body>
    </html>
  );
}