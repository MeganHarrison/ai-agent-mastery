
export interface FileAttachment {
  fileName: string;
  content: string; // Base64 encoded content
  mimeType: string;
}

export interface Database {
  public: {
    Tables: {
      document_metadata: {
        Row: {
          id: string;
          title: string;
          url: string | null;
          created_at: string;
          schema: string | null;
          project_name?: string | null;
          meeting_type?: string | null;
        };
        Insert: {
          id: string;
          title: string;
          url?: string | null;
          created_at?: string;
          schema?: string | null;
          project_name?: string | null;
          meeting_type?: string | null;
        };
        Update: {
          id?: string;
          title?: string;
          url?: string | null;
          created_at?: string;
          schema?: string | null;
          project_name?: string | null;
          meeting_type?: string | null;
        };
      };
      documents: {
        Row: {
          id: number;
          content: string;
          metadata: any;
          embedding: number[] | null;
        };
        Insert: {
          id?: number;
          content: string;
          metadata?: any;
          embedding?: number[] | null;
        };
        Update: {
          id?: number;
          content?: string;
          metadata?: any;
          embedding?: number[] | null;
        };
      };
      project_insights: {
        Row: {
          id: number;
          insight_type: 'action_item' | 'decision' | 'risk' | 'milestone' | 'opportunity' | 'issue' | 'follow_up' | 'requirement';
          title: string;
          description: string;
          confidence_score: number | null;
          priority: 'critical' | 'high' | 'medium' | 'low';
          status: 'open' | 'in_progress' | 'completed' | 'cancelled';
          project_name: string | null;
          assigned_to: string | null;
          due_date: string | null;
          source_document_id: string | null;
          source_meeting_title: string | null;
          source_date: string | null;
          speakers: string[] | null;
          keywords: string[] | null;
          metadata: any;
          related_insights: string[] | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: number;
          insight_type: 'action_item' | 'decision' | 'risk' | 'milestone' | 'opportunity' | 'issue' | 'follow_up' | 'requirement';
          title: string;
          description: string;
          confidence_score?: number | null;
          priority?: 'critical' | 'high' | 'medium' | 'low';
          status?: 'open' | 'in_progress' | 'completed' | 'cancelled';
          project_name?: string | null;
          assigned_to?: string | null;
          due_date?: string | null;
          source_document_id?: string | null;
          source_meeting_title?: string | null;
          source_date?: string | null;
          speakers?: string[] | null;
          keywords?: string[] | null;
          metadata?: any;
          related_insights?: string[] | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: number;
          insight_type?: 'action_item' | 'decision' | 'risk' | 'milestone' | 'opportunity' | 'issue' | 'follow_up' | 'requirement';
          title?: string;
          description?: string;
          confidence_score?: number | null;
          priority?: 'critical' | 'high' | 'medium' | 'low';
          status?: 'open' | 'in_progress' | 'completed' | 'cancelled';
          project_name?: string | null;
          assigned_to?: string | null;
          due_date?: string | null;
          source_document_id?: string | null;
          source_meeting_title?: string | null;
          source_date?: string | null;
          speakers?: string[] | null;
          keywords?: string[] | null;
          metadata?: any;
          related_insights?: string[] | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      conversations: {
        Row: {
          id: string;
          user_id: string;
          session_id: string;
          title: string;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          session_id: string;
          title: string;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          session_id?: string;
          title?: string;
          created_at?: string;
        };
      };
      messages: {
        Row: {
          id: string;
          session_id: string;
          computed_session_user_id: string;
          message: {
            type: 'human' | 'ai';
            content: string;
            files?: FileAttachment[];
          };
          created_at: string;
        };
        Insert: {
          id?: string;
          session_id: string;
          computed_session_user_id: string;
          message: {
            type: 'human' | 'ai';
            content: string;
            files?: FileAttachment[];
          };
          created_at?: string;
        };
        Update: {
          id?: string;
          session_id?: string;
          computed_session_user_id?: string;
          message?: {
            type: 'human' | 'ai';
            content: string;
            files?: FileAttachment[];
          };
          created_at?: string;
        };
      };
      profiles: {
        Row: {
          id: string;
          email: string;
          avatar_url: string | null;
          full_name: string | null;
          updated_at: string | null;
        };
        Insert: {
          id: string;
          email: string;
          avatar_url?: string | null;
          full_name?: string | null;
          updated_at?: string | null;
        };
        Update: {
          id?: string;
          email?: string;
          avatar_url?: string | null;
          full_name?: string | null;
          updated_at?: string | null;
        };
      };
    };
  };
}

export type Conversation = Database['public']['Tables']['conversations']['Row'];
export type Message = Database['public']['Tables']['messages']['Row'];
export type Profile = Database['public']['Tables']['profiles']['Row'];
export type DocumentMetadata = Database['public']['Tables']['document_metadata']['Row'];
export type Document = Database['public']['Tables']['documents']['Row'];
export type ProjectInsight = Database['public']['Tables']['project_insights']['Row'];
