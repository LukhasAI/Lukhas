/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: next.config.js
 * MODULE: frontend
 * DESCRIPTION: Next.js configuration for Oneiric Core frontend. Configures
 *              experimental features, image optimization, environment variables,
 *              and build settings for the React-based dream analysis interface.
 * DEPENDENCIES: next.js, image optimization, environment variables
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['via.placeholder.com', 'images.unsplash.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
  },
}

module.exports = nextConfig

/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: next.config.js
 * VERSION: 1.0.0
 * TIER SYSTEM: Frontend configuration (Application layer for all user tiers)
 * ΛTRACE INTEGRATION: ENABLED
 * CAPABILITIES: Next.js framework configuration, image optimization, environment
 *               variable management, experimental features, build optimization
 * FUNCTIONS: Configuration object export for Next.js build process
 * CLASSES: None directly defined (exports configuration object)
 * DECORATORS: None
 * DEPENDENCIES: Next.js framework, image optimization, process environment
 * INTERFACES: Next.js configuration interface, build system API
 * ERROR HANDLING: Configuration validation by Next.js build system
 * LOGGING: ΛTRACE_ENABLED for build process and configuration tracking
 * AUTHENTICATION: Environment variable configuration for Clerk.dev integration
 * HOW TO USE:
 *   Automatically used by Next.js during build and development
 *   Environment variables available in frontend components
 *   Image optimization for placeholder and unsplash domains
 * INTEGRATION NOTES: Configures frontend build pipeline for Oneiric Core.
 *   Manages API URL configuration and authentication service integration.
 *   Supports experimental App Router for modern React patterns.
 * MAINTENANCE: Update configuration as Next.js evolves, manage environment
 *   variables, update image domains as needed, maintain build optimization.
 * CONTACT: LUKHAS DEVELOPMENT TEAM
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */
