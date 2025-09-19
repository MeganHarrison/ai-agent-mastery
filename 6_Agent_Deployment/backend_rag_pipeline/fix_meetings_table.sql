-- Fix the missing meetings table constraint issue
-- This creates a minimal meetings table to satisfy foreign key constraints

CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    content TEXT,
    document_type TEXT DEFAULT 'meeting',
    project_id INTEGER,
    meeting_date TIMESTAMP WITH TIME ZONE,
    participants TEXT[],
    duration_minutes INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_meetings_project_id ON meetings(project_id);

-- Insert comment to track fix
COMMENT ON TABLE meetings IS 'Created to fix foreign key constraint from ai_insights table - 2025-09-18';