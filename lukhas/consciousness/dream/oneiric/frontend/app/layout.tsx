/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: layout.tsx
 * MODULE: frontend.src.app
 * DESCRIPTION: Root layout component for Oneiric Core Next.js application.
 *              Provides global providers, navigation, settings overlay, and
 *              application-wide state management for the dream analysis interface.
 * DEPENDENCIES: react, @tanstack/react-query, ../components, ../context
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */

'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import NavBar from '../components/NavBar';
import SettingsOverlay from '../components/SettingsOverlay';
import { SettingsProvider } from '../context/SettingsContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <html lang="en">
      <body className="bg-gray-50">
        <QueryClientProvider client={queryClient}>
          <SettingsProvider>
            <NavBar onOpenSettings={() => setShowSettings(true)} />
            {showSettings && (
              <SettingsOverlay 
                isOpen={true} 
                onClose={() => setShowSettings(false)} 
              />
            )}
            <main className="min-h-screen">{children}</main>
          </SettingsProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
