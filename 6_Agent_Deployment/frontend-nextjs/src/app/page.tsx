'use client'

import Link from 'next/link'
import { FileText, Home } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-5xl font-bold mb-8 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          AI Agent Mastery
        </h1>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mt-12">
          <Link 
            href="/documents" 
            className="group relative overflow-hidden rounded-lg bg-gray-800/50 backdrop-blur border border-gray-700 p-6 hover:border-purple-500 transition-all duration-200"
          >
            <div className="flex items-center gap-4 mb-3">
              <FileText className="h-8 w-8 text-purple-400" />
              <h2 className="text-2xl font-semibold">Documents</h2>
            </div>
            <p className="text-gray-300">
              View and manage your meeting documents and transcripts
            </p>
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
          </Link>
          
          <div className="group relative overflow-hidden rounded-lg bg-gray-800/50 backdrop-blur border border-gray-700 p-6 hover:border-blue-500 transition-all duration-200">
            <div className="flex items-center gap-4 mb-3">
              <Home className="h-8 w-8 text-blue-400" />
              <h2 className="text-2xl font-semibold">Dashboard</h2>
            </div>
            <p className="text-gray-300">
              Coming soon - View your dashboard and analytics
            </p>
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>
      </div>
    </div>
  )

import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { Loader } from 'lucide-react'

export default function Home() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.push('/chat')
      } else {
        router.push('/login')
      }
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return null
}