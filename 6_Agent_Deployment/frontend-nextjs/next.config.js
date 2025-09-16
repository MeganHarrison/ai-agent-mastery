/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    NEXT_PUBLIC_AGENT_ENDPOINT: process.env.NEXT_PUBLIC_AGENT_ENDPOINT,
    NEXT_PUBLIC_ENABLE_STREAMING: process.env.NEXT_PUBLIC_ENABLE_STREAMING,
    NEXT_PUBLIC_LANGFUSE_HOST_WITH_PROJECT: process.env.NEXT_PUBLIC_LANGFUSE_HOST_WITH_PROJECT,
  },
}

module.exports = nextConfig