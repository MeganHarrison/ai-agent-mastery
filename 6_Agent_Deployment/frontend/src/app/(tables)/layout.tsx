"use client"

import React from "react"
import { usePathname } from "next/navigation"
import { PageHeader } from "@/components/page-header"

// Route-to-title mapping configuration
const ROUTE_CONFIG = {
  "/companies": {
    title: "Companies",
    description: "Manage company profiles, contacts, and business relationships"
  },
  "/contacts": {
    title: "Contacts", 
    description: "Manage individual contacts and their associated information"
  },
  "/documents": {
    title: "Documents",
    description: "Manage and view all documents in the system"
  },
  "/employees": {
    title: "Employees",
    description: "Manage employee information and organizational structure"
  },
  "/clients": {
    title: "Clients",
    description: "Manage client relationships and project assignments"
  },
  "/prospects": {
    title: "Prospects", 
    description: "Track potential clients and sales opportunities"
  },
  "/sales": {
    title: "Sales",
    description: "Monitor sales activities, deals, and revenue tracking"
  },
  "/team": {
    title: "Team",
    description: "Manage team members and organizational structure"
  },
  "/subcontractors": {
    title: "Subcontractors",
    description: "Manage subcontractor relationships and project assignments"
  },
  "/notion-projects": {
    title: "Notion Projects",
    description: "Sync and manage projects from Notion workspace"
  },
  "/project-tasks": {
    title: "Project Tasks", 
    description: "Track and manage individual project tasks and deliverables"
  },
  "/ai-insights": {
    title: "AI Insights",
    description: "AI-generated insights from meeting transcripts and project documents"
  }
} as const

interface TablesLayoutHeaderProps {
  actionButton?: React.ReactNode
}

function TablesLayoutHeader({ actionButton }: TablesLayoutHeaderProps) {
  const pathname = usePathname()
  
  // Extract the main route from pathname (e.g., "/companies" from "/companies/upload")
  const mainRoute = Object.keys(ROUTE_CONFIG).find(route => 
    pathname.startsWith(route)
  )
  
  const config = mainRoute ? ROUTE_CONFIG[mainRoute as keyof typeof ROUTE_CONFIG] : null
  
  // Fallback for unknown routes
  if (!config) {
    const routeName = pathname.split('/').pop() || 'Data'
    const title = routeName.charAt(0).toUpperCase() + routeName.slice(1).replace(/-/g, ' ')
    return (
      <div className="flex items-start justify-between mb-8 pb-6">
        <PageHeader 
          title={title}
          description="Manage and view data in the system"
        />
        {actionButton && (
          <div className="flex-shrink-0 ml-6">
            {actionButton}
          </div>
        )}
      </div>
    )
  }
  
  return (
    <div className="flex items-start justify-between pb-4 mb-6">
      <div className="flex-1">
        <PageHeader 
          title={config.title}
          description={config.description}
        />
      </div>
      {actionButton && (
        <div className="flex-shrink-0 ml-6">
          {actionButton}
        </div>
      )}
    </div>
  )
}

// Context to pass action button from page to layout
const ActionButtonContext = React.createContext<{
  setActionButton: (button: React.ReactNode) => void
} | null>(null)

export function useActionButton() {
  const context = React.useContext(ActionButtonContext)
  if (!context) {
    throw new Error('useActionButton must be used within TablesLayout')
  }
  return context
}

export default function TablesLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [actionButton, setActionButton] = React.useState<React.ReactNode>(null)

  return (
    <ActionButtonContext.Provider value={{ setActionButton }}>
      <div className="space-y-4 p-2 sm:p-4 md:p-6 w-[95%] sm:w-full mx-auto">
        <TablesLayoutHeader actionButton={actionButton} />
        <div className="space-y-6">
          {children}
        </div>
      </div>
    </ActionButtonContext.Provider>
  )
}