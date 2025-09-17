-- Meetings Table for Project Management
-- Stores meeting information associated with projects

-- Create meeting type enum
CREATE TYPE meeting_type AS ENUM (
    'kickoff',
    'status_update',
    'client_review',
    'technical_review',
    'planning',
    'retrospective',
    'stakeholder',
    'emergency',
    'other'
);

-- Create meeting status enum
CREATE TYPE meeting_status AS ENUM (
    'scheduled',
    'in_progress',
    'completed',
    'cancelled',
    'rescheduled'
);

-- Create meetings table
CREATE TABLE IF NOT EXISTS meetings (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core meeting information
    title TEXT NOT NULL,
    description TEXT,
    meeting_type meeting_type NOT NULL DEFAULT 'status_update',
    meeting_status meeting_status NOT NULL DEFAULT 'scheduled',
    
    -- Project association
    project_id BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    project_name TEXT, -- Denormalized for faster queries
    
    -- Meeting details
    meeting_date TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER,
    location TEXT,
    meeting_link TEXT, -- For virtual meetings
    
    -- Participants
    organizer TEXT,
    attendees TEXT[], -- Array of attendee names/emails
    required_attendees TEXT[], -- Required vs optional attendees
    
    -- Meeting content
    agenda TEXT,
    notes TEXT,
    action_items JSONB, -- Structured action items from the meeting
    decisions JSONB, -- Key decisions made
    attachments JSONB, -- File attachments metadata
    
    -- Recording information
    recording_url TEXT,
    transcript_url TEXT,
    transcript_processed BOOLEAN DEFAULT FALSE,
    
    -- Insights linkage
    has_insights BOOLEAN DEFAULT FALSE,
    insights_count INTEGER DEFAULT 0,
    
    -- Metadata
    tags TEXT[],
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_meetings_project_id ON meetings (project_id);
CREATE INDEX IF NOT EXISTS idx_meetings_project_name ON meetings (project_name);
CREATE INDEX IF NOT EXISTS idx_meetings_meeting_date ON meetings (meeting_date DESC);
CREATE INDEX IF NOT EXISTS idx_meetings_meeting_type ON meetings (meeting_type);
CREATE INDEX IF NOT EXISTS idx_meetings_meeting_status ON meetings (meeting_status);
CREATE INDEX IF NOT EXISTS idx_meetings_organizer ON meetings (organizer);
CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_meetings_has_insights ON meetings (has_insights);

-- GIN indexes for array fields
CREATE INDEX IF NOT EXISTS idx_meetings_attendees_gin ON meetings USING GIN (attendees);
CREATE INDEX IF NOT EXISTS idx_meetings_tags_gin ON meetings USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_meetings_metadata_gin ON meetings USING GIN (metadata);

-- Full-text search index for title, description, agenda and notes
CREATE INDEX IF NOT EXISTS idx_meetings_fts ON meetings USING GIN (
    to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(agenda, '') || ' ' || COALESCE(notes, ''))
);

-- Trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_meetings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_meetings_updated_at
    BEFORE UPDATE ON meetings
    FOR EACH ROW
    EXECUTE FUNCTION update_meetings_timestamp();

-- Add meeting_id to project_insights table for linking
ALTER TABLE project_insights 
ADD COLUMN IF NOT EXISTS meeting_id BIGINT REFERENCES meetings(id);

CREATE INDEX IF NOT EXISTS idx_project_insights_meeting_id ON project_insights (meeting_id);

-- Function to get meetings for a project
CREATE OR REPLACE FUNCTION get_project_meetings(
    p_project_id BIGINT,
    include_cancelled BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
    id BIGINT,
    title TEXT,
    description TEXT,
    meeting_type TEXT,
    meeting_status TEXT,
    meeting_date TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    location TEXT,
    meeting_link TEXT,
    organizer TEXT,
    attendees TEXT[],
    has_insights BOOLEAN,
    insights_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id,
        m.title,
        m.description,
        m.meeting_type::TEXT,
        m.meeting_status::TEXT,
        m.meeting_date,
        m.duration_minutes,
        m.location,
        m.meeting_link,
        m.organizer,
        m.attendees,
        m.has_insights,
        m.insights_count,
        m.created_at
    FROM meetings m
    WHERE m.project_id = p_project_id
        AND (include_cancelled OR m.meeting_status != 'cancelled')
    ORDER BY m.meeting_date DESC;
END;
$$;

-- Function to get meeting insights
CREATE OR REPLACE FUNCTION get_meeting_insights(
    p_meeting_id BIGINT
)
RETURNS TABLE (
    id BIGINT,
    insight_type TEXT,
    title TEXT,
    description TEXT,
    priority TEXT,
    status TEXT,
    assigned_to TEXT,
    due_date TIMESTAMP WITH TIME ZONE,
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pi.id,
        pi.insight_type::TEXT,
        pi.title,
        pi.description,
        pi.priority::TEXT,
        pi.status::TEXT,
        pi.assigned_to,
        pi.due_date,
        pi.confidence_score,
        pi.created_at
    FROM project_insights pi
    WHERE pi.meeting_id = p_meeting_id
    ORDER BY pi.priority DESC, pi.created_at DESC;
END;
$$;

-- Function to update meeting insights count
CREATE OR REPLACE FUNCTION update_meeting_insights_count()
RETURNS TRIGGER AS $$
DECLARE
    meeting_id_val BIGINT;
    insights_cnt INTEGER;
BEGIN
    -- Get the meeting_id from the insight
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        meeting_id_val := NEW.meeting_id;
    ELSIF TG_OP = 'DELETE' THEN
        meeting_id_val := OLD.meeting_id;
    END IF;
    
    -- If there's a meeting_id, update the count
    IF meeting_id_val IS NOT NULL THEN
        -- Count insights for this meeting
        SELECT COUNT(*) INTO insights_cnt
        FROM project_insights
        WHERE meeting_id = meeting_id_val;
        
        -- Update the meeting
        UPDATE meetings
        SET insights_count = insights_cnt,
            has_insights = (insights_cnt > 0)
        WHERE id = meeting_id_val;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update meeting insights count
CREATE TRIGGER trigger_update_meeting_insights_count
    AFTER INSERT OR UPDATE OR DELETE ON project_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_meeting_insights_count();

-- Add helpful comments for documentation
COMMENT ON TABLE meetings IS 'Stores meeting information associated with projects';
COMMENT ON COLUMN meetings.action_items IS 'JSON structure for action items: [{task: string, assigned_to: string, due_date: string, status: string}]';
COMMENT ON COLUMN meetings.decisions IS 'JSON structure for decisions: [{decision: string, rationale: string, impact: string}]';
COMMENT ON COLUMN meetings.attachments IS 'JSON structure for attachments: [{name: string, url: string, type: string, size: number}]';
COMMENT ON FUNCTION get_project_meetings IS 'Get all meetings for a specific project with optional inclusion of cancelled meetings';
COMMENT ON FUNCTION get_meeting_insights IS 'Get all insights associated with a specific meeting';