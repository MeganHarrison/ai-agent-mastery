// Project-related type definitions

export type ProjectStatus = 'active' | 'completed' | 'on_hold' | 'cancelled';
export type ProjectType = 'construction' | 'maintenance' | 'other';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type MeetingType = 'kickoff' | 'status_update' | 'client_review' | 'technical_review' | 
                          'planning' | 'retrospective' | 'stakeholder' | 'emergency' | 'other';
export type MeetingStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'rescheduled';

export type InsightType = 'action_item' | 'decision' | 'risk' | 'milestone' | 'blocker' | 
                          'dependency' | 'budget_update' | 'timeline_change' | 'stakeholder_feedback' | 
                          'technical_issue' | 'opportunity' | 'concern';
export type InsightPriority = 'critical' | 'high' | 'medium' | 'low';
export type InsightStatus = 'open' | 'in_progress' | 'completed' | 'cancelled';

export interface Project {
  id: number;
  name: string;
  aliases?: string[];
  keywords?: string[];
  client_name?: string;
  project_type: ProjectType;
  status: ProjectStatus;
  start_date?: string;
  end_date?: string;
  estimated_completion?: string;
  actual_completion?: string;
  description?: string;
  revenue?: number;
  profit?: number;
  profit_margin?: number;
  budget?: number;
  spent?: number;
  location?: string;
  location_coordinates?: {
    lat: number;
    lng: number;
  };
  notes?: string;
  project_manager?: string;
  team_members?: string[];
  tags?: string[];
  risk_level?: RiskLevel;
  priority?: number;
  completion_percentage?: number;
  is_archived?: boolean;
  attachments?: Array<{
    name: string;
    url: string;
    type: string;
    size: number;
  }>;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Meeting {
  id: number;
  title: string;
  description?: string;
  meeting_type: MeetingType;
  meeting_status: MeetingStatus;
  project_id?: number;
  project_name?: string;
  meeting_date: string;
  duration_minutes?: number;
  location?: string;
  meeting_link?: string;
  organizer?: string;
  attendees?: string[];
  required_attendees?: string[];
  agenda?: string;
  notes?: string;
  action_items?: Array<{
    task: string;
    assigned_to: string;
    due_date: string;
    status: string;
  }>;
  decisions?: Array<{
    decision: string;
    rationale: string;
    impact: string;
  }>;
  attachments?: Array<{
    name: string;
    url: string;
    type: string;
    size: number;
  }>;
  recording_url?: string;
  transcript_url?: string;
  transcript_processed?: boolean;
  has_insights?: boolean;
  insights_count?: number;
  tags?: string[];
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface ProjectInsight {
  id: number;
  insight_type: InsightType;
  title: string;
  description: string;
  confidence_score?: number;
  priority: InsightPriority;
  status: InsightStatus;
  project_id?: number;
  project_name?: string;
  meeting_id?: number;
  assigned_to?: string;
  due_date?: string;
  source_document_id?: string;
  source_meeting_title?: string;
  source_date?: string;
  speakers?: string[];
  keywords?: string[];
  metadata?: Record<string, any>;
  related_insights?: string[];
  processing_metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  processed_by?: string;
}

export interface ProjectMetrics {
  total_meetings: number;
  upcoming_meetings: number;
  total_insights: number;
  open_insights: number;
  critical_insights: number;
  overdue_insights: number;
  completion_percentage?: number;
  days_until_completion?: number;
  budget_usage_percentage?: number;
  profit_margin?: number;
}

export interface ProjectWithMetrics extends Project {
  metrics?: ProjectMetrics;
  meetings?: Meeting[];
  insights?: ProjectInsight[];
}