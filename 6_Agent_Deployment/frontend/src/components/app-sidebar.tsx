import * as React from "react"
import { GalleryVerticalEnd } from "lucide-react"
import Link from "next/link"
import { useAuth } from "@/hooks/useAuth"

import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"

// This is sample data.
const data = {
  navMain: [
    {
      title: "Navigation",
      url: "#",
      items: [
        {
          title: "Dashboard",
          url: "/",
        },
        {
          title: "Projects",
          url: "/projects",
        },
        {
          title: "Meetings",
          url: "/meetings",
        },
        {
          title: "Chat",
          url: "/chat",
        },
      ],
    },
    {
      title: "Tables",
      url: "#",
      items: [
        {
          title: "Clients",
          url: "/clients",
        },
        {
          title: "Prospects",
          url: "/prospects",
          isActive: true,
        },
        {
          title: "Contacts",
          url: "/contacts",
        },
        {
          title: "Companies",
          url: "/company",
        },
        {
          title: "Team",
          url: "#",
        },
        {
          title: "Documents",
          url: "/documents",
        },
        {
          title: "Tasks",
          url: "/tasks",
        },
        {
          title: "Subcontractors",
          url: "/subcontractors",
        },
        {
          title: "AI Insights",
          url: "/ai-insights",
        },
      ],
    },
    {
      title: "FM Global",
      url: "#",
      items: [
        {
          title: "Form",
          url: "#",
        },
      ],
    },
    {
      title: "Account",
      url: "#",
      items: [
        {
          title: "Settings",
          url: "/settings",
        },
      ],
    },
  ],
  user: {
    name: "John Doe",
    email: "john.doe@example.com", 
    avatar: "/avatars/default.jpg",
  },
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { user } = useAuth()

  const userData = user ? {
    name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'User',
    email: user.email || '',
    avatar: user.user_metadata?.avatar_url || ''
  } : data.user

  return (
    <Sidebar variant="floating" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <GalleryVerticalEnd className="size-4" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-semibold">Alleato Group</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu className="gap-2">
            {data.navMain.map((item) => (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton asChild>
                  <Link href={item.url} className="font-medium">
                    {item.title}
                  </Link>
                </SidebarMenuButton>
                {item.items?.length ? (
                  <SidebarMenuSub className="ml-0 border-l-0 px-1.5">
                    {item.items.map((item) => (
                      <SidebarMenuSubItem key={item.title}>
                        <SidebarMenuSubButton asChild isActive={item.isActive}>
                          <Link href={item.url}>{item.title}</Link>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    ))}
                  </SidebarMenuSub>
                ) : null}
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={userData} />
      </SidebarFooter>
    </Sidebar>
  )
}
