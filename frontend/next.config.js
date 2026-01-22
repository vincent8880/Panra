const path = require('path')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    }
    return config
  },
  async rewrites() {
    // Get API URL from environment, default to localhost for dev
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api'
    // Remove /api from the end if present, then add it back
    const baseUrl = apiUrl.replace(/\/api\/?$/, '')
    
    return [
      {
        source: '/api/:path*',
        destination: `${baseUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig





