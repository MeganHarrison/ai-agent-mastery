
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
          title: string | null;
          url: string | null;
          created_at: string | null;
          schema: string | null;
          type?: string | null;
          project?: string | null;
          date?: string | null;
          summary?: string | null;
          fireflies_link?: string | null;
          speakers?: string | null;
          transcript?: string | null;
        };
        Insert: {
          id: string;
          title?: string | null;
          url?: string | null;
          created_at?: string | null;
          schema?: string | null;
          type?: string | null;
          project?: string | null;
          date?: string | null;
          summary?: string | null;
          fireflies_link?: string | null;
          speakers?: string | null;
          transcript?: string | null;
        };
        Update: {
          id?: string;
          title?: string | null;
          url?: string | null;
          created_at?: string | null;
          schema?: string | null;
          type?: string | null;
          project?: string | null;
          date?: string | null;
          summary?: string | null;
          fireflies_link?: string | null;
          speakers?: string | null;
          transcript?: string | null;
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
