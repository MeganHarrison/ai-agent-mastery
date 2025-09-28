"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabase"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Loader2,
  FileText,
  Briefcase,
  ChevronLeft,
  ChevronRight,
  Grid3x3,
  MoreVertical,
  ExternalLink
} from "lucide-react"
import { format } from "date-fns"
import { Database } from "@/types/database.types"
import { useToast } from "@/hooks/use-toast"
import { cn } from "@/lib/utils"
import { useRouter } from 'next/navigation'

type Project = Database["public"]["Tables"]["projects"]["Row"]
type DocumentMetadata = Database["public"]["Tables"]["document_metadata"]["Row"]
type DocumentInsight = Database["public"]["Tables"]["document_insights"]["Row"]

export default function ProjectsDashboard() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [meetings, setMeetings] = useState<DocumentMetadata[]>([])
  const [insights, setInsights] = useState<DocumentInsight[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingDetails, setLoadingDetails] = useState(false)
  const { toast } = useToast()

  const fetchProjects = async () => {
    try {
      setLoading(true)

      const { data, error } = await supabase
        .from("projects")
        .select("*")
        .order("created_at", { ascending: false })

      if (error) throw error

      // Filter for only current projects (phase = "current")
      const currentProjects = (data || []).filter(project => {
        const phase = project.phase?.toLowerCase()
        // Only show projects where phase is explicitly set to "current"
        return phase === 'current'
      })

      setProjects(currentProjects)

      // Auto-select first project if none selected
      if (currentProjects.length > 0 && !selectedProject) {
        setSelectedProject(currentProjects[0])
      }
    } catch (err: any) {
      console.error("Error fetching projects:", err)
      toast({
        title: "Error",
        description: "Failed to load projects",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchProjectDetails = async (projectId: number) => {
    try {
      setLoadingDetails(true)

      // Fetch meetings associated with this project
      // First, try without the category filter to see if there's any data
      const { data: allDocsData } = await supabase
        .from("document_metadata")
        .select("*")
        .eq("project_id", projectId)
        .order("date", { ascending: false })

      console.log("All documents for project", projectId, ":", allDocsData)

      // Also try with the meeting category filter
      const { data: meetingsData, error: meetingsError } = await supabase
        .from("document_metadata")
        .select("*")
        .eq("project_id", projectId)
        .eq("category", "meeting")
        .order("date", { ascending: false })

      console.log("Meeting documents for project", projectId, ":", meetingsData)

      if (meetingsError) throw meetingsError
      // Use all documents if no meetings with specific category found
      setMeetings(meetingsData && meetingsData.length > 0 ? meetingsData : (allDocsData || []))

      // Fetch insights for this project
      const { data: insightsData, error: insightsError } = await supabase
        .from("document_insights")
        .select("*")
        .eq("project_id", projectId)
        .order("created_at", { ascending: false })

      if (insightsError) throw insightsError
      setInsights(insightsData || [])

    } catch (err: any) {
      console.error("Error fetching project details:", err)
      toast({
        title: "Error",
        description: "Failed to load project details",
        variant: "destructive"
      })
    } finally {
      setLoadingDetails(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    if (selectedProject) {
      fetchProjectDetails(selectedProject.id)
    }
  }, [selectedProject])

  const formatCurrency = (amount: number | null) => {
    if (amount === null) return "$0"
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-white">
      {/* Left Sidebar - Projects List */}
      <div className="w-[40%] bg-gray-50 border-r border-gray-200 flex flex-col">
        <div className="px-10 py-8 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-4xl font-light text-gray-900">Projects</h2>
            <div className="flex gap-1">
              <Button size="icon" variant="ghost" className="h-8 w-8 text-gray-500 hover:text-gray-900">
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button size="icon" variant="ghost" className="h-8 w-8 text-gray-500 hover:text-gray-900">
                <Grid3x3 className="h-4 w-4" />
              </Button>
              <Button size="icon" variant="ghost" className="h-8 w-8 text-gray-500 hover:text-gray-900">
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <p className="text-sm text-gray-600">All active projects</p>
        </div>

        <ScrollArea className="flex-1">
          <div className="py-8 space-y-8">
            {/* Group projects by client */}
            {Object.entries(
              projects.reduce((acc, project) => {
                const client = project.client || 'UNASSIGNED'
                if (!acc[client]) acc[client] = []
                acc[client].push(project)
                return acc
              }, {} as Record<string, typeof projects>)
            ).map(([client, clientProjects]) => (
              <div key={client} className="space-y-3">
                <p className="text-xs font-medium text-gray-600 uppercase tracking-wider px-10">
                  {client}
                </p>
                <div className="space-y-2">
                  {clientProjects.map((project) => {
                    const isSelected = selectedProject?.id === project.id
                    return (
                      <div
                        key={project.id}
                        onClick={() => setSelectedProject(project)}
                        className={cn(
                          "py-4 cursor-pointer transition-all",
                          isSelected
                            ? "bg-blue-50 text-gray-900 px-10 border-l-4 border-blue-500"
                            : "hover:bg-gray-100 text-gray-700 px-10 border-l-4 border-transparent"
                        )}
                      >
                        <h3 className="font-medium text-base mb-2">
                          {project.name || 'Untitled Project'}
                        </h3>
                        <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                          {project.description || 'No description available'}
                        </p>
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Right Panel - Project Details */}
      <div className="w-[60%] bg-white overflow-hidden flex flex-col">
        {selectedProject ? (
          <ScrollArea className="flex-1">
            <div className="h-full flex flex-col">
            {/* Project Header */}
            <div className="bg-gray-50 px-12 py-10 border-b border-gray-200">
              <p className="text-xs font-medium text-gray-600 uppercase tracking-wider mb-4">
                {selectedProject.client || 'COLLECTIVE GROUP'}
              </p>
              <h1 className="text-5xl font-light text-gray-900 mb-8">
                {selectedProject.name}
              </h1>

              <div className="grid grid-cols-3 gap-8">
                <div>
                  <p className="text-xs font-medium text-gray-600 mb-1">START DATE:</p>
                  <p className="text-sm text-gray-900 font-medium">
                    {selectedProject["start date"] ?
                      format(new Date(selectedProject["start date"]), 'MMMM d, yyyy').toUpperCase() :
                      'NOT SET'}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-600 mb-1">EST BUDGET:</p>
                  <p className="text-sm text-gray-900 font-medium">
                    {formatCurrency(selectedProject.budget)}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-600 mb-1">EST PROFIT:</p>
                  <p className="text-sm text-gray-900 font-medium">
                    {formatCurrency(selectedProject["est revenue"] || 0)}
                  </p>
                </div>
              </div>
            </div>

            {/* Project Description */}
            <div className="px-12 py-10 border-b border-gray-200">
              <div className="text-gray-700 text-base leading-relaxed whitespace-pre-wrap">
                {selectedProject.description ? (
                  selectedProject.description
                    .replace(/￼/g, '') // Remove special characters
                    .replace(/⸻/g, '\n\n') // Replace dividers with line breaks
                    .replace(/•/g, '\n•') // Add line break before bullets
                    .replace(/→/g, '\n  →') // Format arrows with indentation
                    .trim()
                ) : (
                  'This project represents a complex coordination challenge involving multiple building systems, specialized infrastructure, and comprehensive planning requirements.'
                )}
              </div>
            </div>

            {/* Insights Section */}
            <div className="px-12 py-10">
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-8">INSIGHTS</h3>

              {loadingDetails ? (
                <div className="flex items-center justify-center h-32">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
                </div>
              ) : insights.length === 0 && meetings.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600">No insights or meetings recorded yet</p>
                </div>
              ) : (
                <div className="overflow-x-auto pb-10">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-gray-200">
                        <TableHead className="text-gray-600 font-medium">Type</TableHead>
                        <TableHead className="text-gray-600 font-medium">Description</TableHead>
                        <TableHead className="text-gray-600 font-medium">Date</TableHead>
                        <TableHead className="text-gray-600 font-medium">Category</TableHead>
                        <TableHead className="text-gray-600 font-medium w-[40px]"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {/* Display insights */}
                      {insights.map((insight) => (
                        <TableRow key={`insight-${insight.id}`} className="border-gray-200">
                          <TableCell className="text-gray-700 font-medium">
                            {insight.title || 'Insight'}
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {insight.description || 'No description'}
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {insight.created_at ? format(new Date(insight.created_at), 'MMM d, yyyy') : '-'}
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {insight.insight_type || 'General'}
                          </TableCell>
                          <TableCell>
                            <Button size="icon" variant="ghost" className="h-6 w-6 text-gray-500">
                              <MoreVertical className="h-3 w-3" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}

                      {/* Display meetings as insights */}
                      {meetings.map((meeting) => (
                        <TableRow
                          key={`meeting-${meeting.id}`}
                          className="border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
                          onClick={() => router.push(`/meetings/${meeting.id}`)}
                        >
                          <TableCell className="text-gray-700 font-medium">
                            Meeting
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {meeting.title || meeting.summary || 'Meeting notes'}
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {meeting.date ? format(new Date(meeting.date), 'MMM d, yyyy') : '-'}
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {meeting.source || 'Meeting'}
                          </TableCell>
                          <TableCell>
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-6 w-6 text-gray-500 hover:text-gray-900"
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation()
                                router.push(`/meetings/${meeting.id}`)
                              }}
                            >
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
            </div>
          </ScrollArea>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-white">
            <div className="text-center space-y-3">
              <Briefcase className="h-12 w-12 mx-auto text-gray-400" />
              <div>
                <h3 className="font-semibold text-gray-900">Select a Project</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Choose a project from the list to view details
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}