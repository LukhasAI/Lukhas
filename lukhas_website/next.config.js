/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost', 'lukhas.ai'],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
  // Note: For HTTPS in development, use: next dev --experimental-https
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(self), geolocation=()'
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob: data:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; connect-src 'self' https://api.openai.com https://api.anthropic.com https://generativelanguage.googleapis.com; worker-src 'self' blob:; frame-src 'none';"
          },
        ],
      },
      {
        source: '/.well-known/jwks.json',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400, must-revalidate',
          },
          {
            key: 'Content-Type',
            value: 'application/json'
          },
        ],
      },
      {
        source: '/fonts/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
  async redirects() {
    return [
      // MATRIZ rebrand redirects
      {
        source: '/matada',
        destination: '/matriz',
        permanent: true,
      },
      {
        source: '/matada/:path*',
        destination: '/matriz/:path*',
        permanent: true,
      },
      {
        source: '/MATADA',
        destination: '/matriz',
        permanent: true,
      },
      {
        source: '/MATADA/:path*',
        destination: '/matriz/:path*',
        permanent: true,
      },
      // Handle lambda character in URLs (should not happen but fallback)
      {
        source: '/m%CE%BBtriz',
        destination: '/matriz',
        permanent: true,
      },
      {
        source: '/mλtriz',
        destination: '/matriz',
        permanent: true,
      },
    ]
  },
  async rewrites() {
    return [
      // New API service rewrites for development - all point to dev server
      { source: "/api/identity/:path*", destination: "http://localhost:7402/:path*" },
      { source: "/api/wallet/:path*",   destination: "http://localhost:7402/:path*" },
      { source: "/api/qrg/:path*",      destination: "http://localhost:7402/:path*" },
      { source: "/api/consent/:path*",  destination: "http://localhost:7402/:path*" },
      // Legacy LUKHAS backend fallback
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*', // LUKHAS backend
      },
    ]
  },
  webpack: (config) => {
    config.module.rules.push({
      test: /\.(woff|woff2|eot|ttf|otf)$/,
      use: {
        loader: 'file-loader',
        options: {
          publicPath: '/_next/static/fonts/',
          outputPath: 'static/fonts/',
        },
      },
    })

    return config
  },
}

module.exports = nextConfig
