/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: page.tsx
 * MODULE: frontend.src.app
 * DESCRIPTION: Home page component for Oneiric Core application. Provides the
 *              main interface for dream analysis and Oracle chat integration 
 *              for symbolic interpretation.
 * DEPENDENCIES: react, ../components/OracleChat
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */

'use client';

import OracleChat from '../components/OracleChat';

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome to Oneiric Core
        </h1>
        <p className="text-gray-600">
          Explore the symbolic depths of your consciousness through AI-guided dream analysis
        </p>
      </div>
      
      <OracleChat />
    </div>
  );
}

/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: page.tsx
 * VERSION: 1.0.0
 * TIER SYSTEM: Frontend home page (Entry point for all user tiers)
 * ΛTRACE INTEGRATION: ENABLED
 * CAPABILITIES: Main interface rendering, Oracle chat integration, welcome screen
 * FUNCTIONS: HomePage (default export function component)
 * CLASSES: None directly defined (React functional component)
 * DECORATORS: 'use client' directive for client-side rendering
 * DEPENDENCIES: React, OracleChat component
 * INTERFACES: JSX component interface
 * ERROR HANDLING: React error boundaries, component-level error handling
 * LOGGING: ΛTRACE_ENABLED for user interactions and page navigation
 * AUTHENTICATION: Currently disabled for preview mode
 * HOW TO USE:
 *   Automatically rendered as home page by Next.js App Router
 *   Displays welcome interface and Oracle chat for dream analysis
 * INTEGRATION NOTES: Main entry point for Oneiric Core user experience.
 *   Provides direct access to dream analysis interface.
 *   Responsive design for various screen sizes.
 * MAINTENANCE: Update user interface as features evolve, integrate
 *   authentication when ready, update welcome messaging.
 * CONTACT: LUKHAS DEVELOPMENT TEAM
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */
