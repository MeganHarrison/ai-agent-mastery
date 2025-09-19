'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Users, 
  DollarSign,
  Target,
  MessageSquare,
  Building,
  Calendar,
  Brain,
  ArrowRight,
  BarChart3,
  Activity,
  Zap
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useDashboardMetrics } from '@/hooks/useDashboardMetrics'
import { useProjects } from '@/hooks/useProjects'
import { useActiveInsights } from '@/hooks/useInsights'
import { useAuth } from '@/hooks/useAuth'

interface MetricCardProps {
  title: string
  value: string | number
  change?: string
  trend?: 'up' | 'down' | 'neutral'
  icon: React.ReactNode
  description?: string
}

function MetricCard({ title, value, change, trend, icon, description }: MetricCardProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : null
  const trendColor = trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-400'
  
  return (
    <Card className="bg-gray-800/50 border-gray-700 hover:border-blue-500/50 transition-all duration-200">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-300">{title}</CardTitle>
        <div className="text-blue-400">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white">{value}</div>
        {change && (
          <div className={`flex items-center text-xs ${trendColor}`}>
            {TrendIcon && <TrendIcon className="h-3 w-3 mr-1" />}
            {change}
          </div>
        )}
        {description && (
          <p className="text-xs text-gray-400 mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  )
}

interface ProjectHealthProps {
  name: string
  status: 'healthy' | 'warning' | 'critical'
  completion: number
  nextMilestone: string
  budget: string
}

function ProjectHealthCard({ name, status, completion, nextMilestone, budget }: ProjectHealthProps) {
  const statusColor = {
    healthy: 'bg-green-500',
    warning: 'bg-yellow-500', 
    critical: 'bg-red-500'
  }
  
  const statusIcon = {
    healthy: <CheckCircle className="h-4 w-4" />,
    warning: <AlertTriangle className="h-4 w-4" />,
    critical: <AlertTriangle className="h-4 w-4" />
  }

  return (
    <Card className="bg-gray-800/50 border-gray-700">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-white">{name}</CardTitle>
          <Badge className={`${statusColor[status]} text-white`}>
            {statusIcon[status]}
            <span className="ml-1 capitalize">{status}</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Progress</span>
            <span className="text-white">{completion}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-500" 
              style={{ width: `${completion}%` }}
            />
          </div>
        </div>
        <div className="text-xs text-gray-400">
          Next: <span className="text-white">{nextMilestone}</span>
        </div>
        <div className="text-xs text-gray-400">
          Budget: <span className="text-green-400">{budget}</span>
        </div>
      </CardContent>
    </Card>
  )
}

interface InsightProps {
  type: 'opportunity' | 'risk' | 'action' | 'milestone'
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  source: string
}

function InsightCard({ type, title, description, priority, source }: InsightProps) {
  const typeConfig = {
    opportunity: { icon: <Zap className="h-4 w-4" />, color: 'text-green-400', bg: 'bg-green-500/20' },
    risk: { icon: <AlertTriangle className="h-4 w-4" />, color: 'text-red-400', bg: 'bg-red-500/20' },
    action: { icon: <Target className="h-4 w-4" />, color: 'text-blue-400', bg: 'bg-blue-500/20' },
    milestone: { icon: <CheckCircle className="h-4 w-4" />, color: 'text-purple-400', bg: 'bg-purple-500/20' }
  }
  
  const priorityColor = {
    high: 'bg-red-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500'
  }

  return (
    <Card className="bg-gray-800/50 border-gray-700">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className={`p-2 rounded-lg ${typeConfig[type].bg}`}>
            <div className={typeConfig[type].color}>{typeConfig[type].icon}</div>
          </div>
          <Badge className={`${priorityColor[priority]} text-white text-xs`}>
            {priority.toUpperCase()}
          </Badge>
        </div>
        <h4 className="font-semibold text-white mb-1">{title}</h4>
        <p className="text-sm text-gray-400 mb-2">{description}</p>
        <p className="text-xs text-gray-500">Source: {source}</p>
      </CardContent>
    </Card>
  )
}

export default function HomePage() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const { user, loading } = useAuth()
  const router = useRouter()
  const { metrics: dashboardMetrics, loading: metricsLoading } = useDashboardMetrics()
  const { projects, loading: projectsLoading } = useProjects()
  const { insights, loading: insightsLoading } = useActiveInsights()
  
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Real metrics from database
  const metrics = dashboardMetrics ? [
    {
      title: "Active Projects",
      value: dashboardMetrics.activeProjects,
      change: `${dashboardMetrics.projectsOnTrack} on track, ${dashboardMetrics.projectsAtRisk} at risk, ${dashboardMetrics.projectsDelayed} delayed`,
      trend: dashboardMetrics.projectsAtRisk > 0 ? "down" as const : "up" as const,
      icon: <Building className="h-4 w-4" />,
      description: dashboardMetrics.projectsAtRisk > 0 ? "Attention needed" : "All projects tracking well"
    },
    {
      title: "Total Revenue Pipeline",
      value: dashboardMetrics.totalRevenue,
      change: "Budget remaining",
      trend: "up" as const,
      icon: <DollarSign className="h-4 w-4" />,
      description: "Active project budgets"
    },
    {
      title: "Team Utilization",
      value: dashboardMetrics.teamUtilization,
      change: "Current capacity",
      trend: "up" as const,
      icon: <Users className="h-4 w-4" />,
      description: "Based on project load"
    },
    {
      title: "AI Insights Generated",
      value: dashboardMetrics.aiInsightsGenerated,
      change: "Total insights",
      trend: "up" as const,
      icon: <Brain className="h-4 w-4" />,
      description: "From conversations & documents"
    }
  ] : []

  // Real project health from database
  const projectHealth = projects.slice(0, 3).map(project => ({
    name: project.name,
    status: project.priority === 'critical' ? 'critical' as const : 
           project.priority === 'high' ? 'warning' as const : 'healthy' as const,
    completion: project.progress,
    nextMilestone: "Next milestone",
    budget: project.budget ? `$${(project.budget / 1000).toFixed(0)}K remaining` : "No budget set"
  }))

  // Real insights from database
  const realInsights = insights.slice(0, 4).map(insight => ({
    type: insight.insight_type === 'opportunity' ? 'opportunity' as const :
          insight.insight_type === 'risk' ? 'risk' as const :
          insight.insight_type === 'action_item' ? 'action' as const :
          'milestone' as const,
    title: insight.title,
    description: insight.description,
    priority: insight.priority as 'high' | 'medium' | 'low',
    source: insight.source_meeting_title || 'AI Analysis'
  }))

  // Redirect unauthenticated users to login
  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    }
  }, [loading, user, router]);

  // Show loading while auth is resolving
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
      </div>
    )
  }

  // This fallback shouldn't be reached due to the redirect above, but just in case
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Welcome to Executive Dashboard</h1>
          <p className="text-gray-400 mb-8">Please sign in to view your dashboard</p>
          <Button asChild>
            <Link href="/auth/login">Sign In</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Executive Dashboard
            </h1>
            <p className="text-gray-400 mt-1">
              {currentTime.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })} • {currentTime.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </p>
          </div>
          <div className="flex gap-3">
            <Button asChild variant="outline" className="border-gray-600 hover:border-blue-500">
              <Link href="/chat">
                <MessageSquare className="h-4 w-4 mr-2" />
                AI Assistant
              </Link>
            </Button>
            <Button asChild className="bg-blue-600 hover:bg-blue-700">
              <Link href="/projects">
                <BarChart3 className="h-4 w-4 mr-2" />
                Full Dashboard
              </Link>
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          {metricsLoading ? (
            Array.from({ length: 4 }).map((_, index) => (
              <Card key={index} className="bg-gray-800/50 border-gray-700 animate-pulse">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="h-4 bg-gray-600 rounded w-24"></div>
                  <div className="h-4 w-4 bg-gray-600 rounded"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-8 bg-gray-600 rounded w-16 mb-2"></div>
                  <div className="h-3 bg-gray-600 rounded w-20"></div>
                </CardContent>
              </Card>
            ))
          ) : (
            metrics.map((metric, index) => (
              <MetricCard key={index} {...metric} />
            ))
          )}
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Project Health Overview */}
          <div className="lg:col-span-2">
            <Card className="bg-gray-800/30 border-gray-700">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-white">Project Health Overview</CardTitle>
                    <CardDescription className="text-gray-400">
                      Real-time status of active construction projects
                    </CardDescription>
                  </div>
                  <Button asChild variant="ghost" size="sm">
                    <Link href="/projects">
                      View All <ArrowRight className="h-4 w-4 ml-1" />
                    </Link>
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {projectsLoading ? (
                    Array.from({ length: 3 }).map((_, index) => (
                      <Card key={index} className="bg-gray-800/50 border-gray-700 animate-pulse">
                        <CardContent className="p-4">
                          <div className="h-4 bg-gray-600 rounded w-32 mb-2"></div>
                          <div className="h-3 bg-gray-600 rounded w-20 mb-3"></div>
                          <div className="h-2 bg-gray-600 rounded w-full"></div>
                        </CardContent>
                      </Card>
                    ))
                  ) : projectHealth.length > 0 ? (
                    projectHealth.map((project, index) => (
                      <ProjectHealthCard key={index} {...project} />
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8 text-gray-400">
                      No active projects found. <Link href="/projects" className="text-blue-400 hover:underline">Create your first project</Link>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AI Insights & Alerts */}
          <div>
            <Card className="bg-gray-800/30 border-gray-700">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-white flex items-center">
                      <Activity className="h-5 w-5 mr-2 text-blue-400" />
                      AI Insights
                    </CardTitle>
                    <CardDescription className="text-gray-400">
                      Strategic recommendations and alerts
                    </CardDescription>
                  </div>
                  <Button asChild variant="ghost" size="sm">
                    <Link href="/admin">
                      <Brain className="h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {insightsLoading ? (
                    Array.from({ length: 4 }).map((_, index) => (
                      <Card key={index} className="bg-gray-800/50 border-gray-700 animate-pulse">
                        <CardContent className="p-4">
                          <div className="h-4 bg-gray-600 rounded w-40 mb-2"></div>
                          <div className="h-3 bg-gray-600 rounded w-full mb-1"></div>
                          <div className="h-3 bg-gray-600 rounded w-20"></div>
                        </CardContent>
                      </Card>
                    ))
                  ) : realInsights.length > 0 ? (
                    realInsights.map((insight, index) => (
                      <InsightCard key={index} {...insight} />
                    ))
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      No insights available. Start conversations to generate insights.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <Card className="bg-gray-800/30 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Quick Actions</CardTitle>
              <CardDescription className="text-gray-400">
                Frequently used tools and reports
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Button asChild variant="outline" className="h-auto p-4 border-gray-600 hover:border-purple-500">
                  <Link href="/chat" className="flex flex-col items-center text-center">
                    <MessageSquare className="h-6 w-6 mb-2 text-purple-400" />
                    <span className="font-semibold">Chat with AI</span>
                    <span className="text-xs text-gray-400">Ask questions, get insights</span>
                  </Link>
                </Button>
                
                <Button asChild variant="outline" className="h-auto p-4 border-gray-600 hover:border-green-500">
                  <Link href="/projects" className="flex flex-col items-center text-center">
                    <Building className="h-6 w-6 mb-2 text-green-400" />
                    <span className="font-semibold">Project Status</span>
                    <span className="text-xs text-gray-400">Detailed project views</span>
                  </Link>
                </Button>
                
                <Button asChild variant="outline" className="h-auto p-4 border-gray-600 hover:border-blue-500">
                  <Link href="/admin" className="flex flex-col items-center text-center">
                    <Brain className="h-6 w-6 mb-2 text-blue-400" />
                    <span className="font-semibold">Admin Panel</span>
                    <span className="text-xs text-gray-400">Manage users & insights</span>
                  </Link>
                </Button>
                
                <Button asChild variant="outline" className="h-auto p-4 border-gray-600 hover:border-yellow-500">
                  <Link href="/documents" className="flex flex-col items-center text-center">
                    <Calendar className="h-6 w-6 mb-2 text-yellow-400" />
                    <span className="font-semibold">Documents</span>
                    <span className="text-xs text-gray-400">Meeting notes & files</span>
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}