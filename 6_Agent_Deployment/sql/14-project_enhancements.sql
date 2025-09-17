-- Enhancements to Projects Table
-- Adds financial and additional tracking fields to projects table

-- Add new columns to projects table if they don't exist
ALTER TABLE projects 
ADD COLUMN IF NOT EXISTS estimated_completion DATE,
ADD COLUMN IF NOT EXISTS actual_completion DATE,
ADD COLUMN IF NOT EXISTS revenue DECIMAL(15, 2),
ADD COLUMN IF NOT EXISTS profit DECIMAL(15, 2),
ADD COLUMN IF NOT EXISTS profit_margin DECIMAL(5, 2), -- Percentage
ADD COLUMN IF NOT EXISTS location TEXT,
ADD COLUMN IF NOT EXISTS location_coordinates JSONB, -- {lat: number, lng: number}
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS budget DECIMAL(15, 2),
ADD COLUMN IF NOT EXISTS spent DECIMAL(15, 2),
ADD COLUMN IF NOT EXISTS project_manager TEXT,
ADD COLUMN IF NOT EXISTS team_members TEXT[],
ADD COLUMN IF NOT EXISTS tags TEXT[],
ADD COLUMN IF NOT EXISTS risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 5),
ADD COLUMN IF NOT EXISTS completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS attachments JSONB; -- Document attachments

-- Create indexes for new fields
CREATE INDEX IF NOT EXISTS idx_projects_client_name ON projects (client_name);
CREATE INDEX IF NOT EXISTS idx_projects_project_manager ON projects (project_manager);
CREATE INDEX IF NOT EXISTS idx_projects_risk_level ON projects (risk_level);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects (priority);
CREATE INDEX IF NOT EXISTS idx_projects_is_archived ON projects (is_archived);
CREATE INDEX IF NOT EXISTS idx_projects_estimated_completion ON projects (estimated_completion);
CREATE INDEX IF NOT EXISTS idx_projects_tags_gin ON projects USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_projects_team_members_gin ON projects USING GIN (team_members);

-- Function to calculate project metrics
CREATE OR REPLACE FUNCTION calculate_project_metrics(
    p_project_id BIGINT
)
RETURNS TABLE (
    total_meetings BIGINT,
    upcoming_meetings BIGINT,
    total_insights BIGINT,
    open_insights BIGINT,
    critical_insights BIGINT,
    overdue_insights BIGINT,
    completion_percentage INTEGER,
    days_until_completion INTEGER,
    budget_usage_percentage DECIMAL,
    profit_margin DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    project_rec RECORD;
BEGIN
    -- Get project details
    SELECT * INTO project_rec FROM projects WHERE id = p_project_id;
    
    IF NOT FOUND THEN
        RETURN;
    END IF;
    
    RETURN QUERY
    SELECT
        -- Meeting metrics
        (SELECT COUNT(*) FROM meetings WHERE project_id = p_project_id)::BIGINT as total_meetings,
        (SELECT COUNT(*) FROM meetings 
         WHERE project_id = p_project_id 
         AND meeting_date > NOW() 
         AND meeting_status != 'cancelled')::BIGINT as upcoming_meetings,
        
        -- Insights metrics
        (SELECT COUNT(*) FROM project_insights WHERE project_id = p_project_id)::BIGINT as total_insights,
        (SELECT COUNT(*) FROM project_insights 
         WHERE project_id = p_project_id 
         AND status IN ('open', 'in_progress'))::BIGINT as open_insights,
        (SELECT COUNT(*) FROM project_insights 
         WHERE project_id = p_project_id 
         AND priority = 'critical' 
         AND status IN ('open', 'in_progress'))::BIGINT as critical_insights,
        (SELECT COUNT(*) FROM project_insights 
         WHERE project_id = p_project_id 
         AND due_date < NOW() 
         AND status IN ('open', 'in_progress'))::BIGINT as overdue_insights,
        
        -- Project metrics
        project_rec.completion_percentage,
        CASE 
            WHEN project_rec.estimated_completion IS NOT NULL 
            THEN (project_rec.estimated_completion - CURRENT_DATE)::INTEGER
            ELSE NULL
        END as days_until_completion,
        CASE 
            WHEN project_rec.budget IS NOT NULL AND project_rec.budget > 0 
            THEN ROUND((project_rec.spent / project_rec.budget * 100)::DECIMAL, 2)
            ELSE NULL
        END as budget_usage_percentage,
        project_rec.profit_margin;
END;
$$;

-- Function to get project summary with all details
CREATE OR REPLACE FUNCTION get_project_details(
    p_project_id BIGINT
)
RETURNS TABLE (
    id BIGINT,
    name TEXT,
    client_name TEXT,
    project_type TEXT,
    status TEXT,
    start_date DATE,
    estimated_completion DATE,
    actual_completion DATE,
    revenue DECIMAL,
    profit DECIMAL,
    profit_margin DECIMAL,
    budget DECIMAL,
    spent DECIMAL,
    location TEXT,
    notes TEXT,
    project_manager TEXT,
    team_members TEXT[],
    risk_level TEXT,
    priority INTEGER,
    completion_percentage INTEGER,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    total_meetings BIGINT,
    upcoming_meetings BIGINT,
    total_insights BIGINT,
    open_insights BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        p.client_name,
        p.project_type,
        p.status,
        p.start_date,
        p.estimated_completion,
        p.actual_completion,
        p.revenue,
        p.profit,
        p.profit_margin,
        p.budget,
        p.spent,
        p.location,
        p.notes,
        p.project_manager,
        p.team_members,
        p.risk_level,
        p.priority,
        p.completion_percentage,
        p.tags,
        p.created_at,
        p.updated_at,
        (SELECT COUNT(*) FROM meetings m WHERE m.project_id = p.id)::BIGINT as total_meetings,
        (SELECT COUNT(*) FROM meetings m 
         WHERE m.project_id = p.id 
         AND m.meeting_date > NOW() 
         AND m.meeting_status != 'cancelled')::BIGINT as upcoming_meetings,
        (SELECT COUNT(*) FROM project_insights pi WHERE pi.project_id = p.id)::BIGINT as total_insights,
        (SELECT COUNT(*) FROM project_insights pi 
         WHERE pi.project_id = p.id 
         AND pi.status IN ('open', 'in_progress'))::BIGINT as open_insights
    FROM projects p
    WHERE p.id = p_project_id;
END;
$$;

-- Function to update profit margin automatically
CREATE OR REPLACE FUNCTION update_project_profit_margin()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.revenue IS NOT NULL AND NEW.revenue > 0 AND NEW.profit IS NOT NULL THEN
        NEW.profit_margin := ROUND((NEW.profit / NEW.revenue * 100)::DECIMAL, 2);
    ELSE
        NEW.profit_margin := NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update profit margin
CREATE TRIGGER trigger_update_profit_margin
    BEFORE INSERT OR UPDATE ON projects
    FOR EACH ROW
    WHEN (NEW.revenue IS DISTINCT FROM OLD.revenue OR NEW.profit IS DISTINCT FROM OLD.profit)
    EXECUTE FUNCTION update_project_profit_margin();

-- Create view for active projects dashboard
CREATE OR REPLACE VIEW active_projects_dashboard AS
SELECT 
    p.id,
    p.name,
    p.client_name,
    p.project_type,
    p.status,
    p.start_date,
    p.estimated_completion,
    p.revenue,
    p.profit,
    p.profit_margin,
    p.budget,
    p.spent,
    p.location,
    p.project_manager,
    p.risk_level,
    p.priority,
    p.completion_percentage,
    p.tags,
    CASE 
        WHEN p.estimated_completion < CURRENT_DATE THEN TRUE 
        ELSE FALSE 
    END as is_overdue,
    (SELECT COUNT(*) FROM meetings m WHERE m.project_id = p.id)::INTEGER as total_meetings,
    (SELECT COUNT(*) FROM meetings m 
     WHERE m.project_id = p.id AND m.meeting_date > NOW())::INTEGER as upcoming_meetings,
    (SELECT COUNT(*) FROM project_insights pi WHERE pi.project_id = p.id)::INTEGER as total_insights,
    (SELECT COUNT(*) FROM project_insights pi 
     WHERE pi.project_id = p.id AND pi.status IN ('open', 'in_progress'))::INTEGER as open_insights,
    (SELECT COUNT(*) FROM project_insights pi 
     WHERE pi.project_id = p.id AND pi.priority = 'critical' 
     AND pi.status IN ('open', 'in_progress'))::INTEGER as critical_insights
FROM projects p
WHERE p.status = 'active' AND p.is_archived = FALSE
ORDER BY p.priority DESC, p.estimated_completion ASC NULLS LAST;

-- Add helpful comments
COMMENT ON COLUMN projects.revenue IS 'Total project revenue in currency units';
COMMENT ON COLUMN projects.profit IS 'Total project profit in currency units';
COMMENT ON COLUMN projects.profit_margin IS 'Profit margin as percentage (auto-calculated)';
COMMENT ON COLUMN projects.location_coordinates IS 'GPS coordinates as JSON: {lat: number, lng: number}';
COMMENT ON COLUMN projects.risk_level IS 'Project risk assessment: low, medium, high, critical';
COMMENT ON COLUMN projects.priority IS 'Project priority from 1 (lowest) to 5 (highest)';
COMMENT ON FUNCTION calculate_project_metrics IS 'Calculate comprehensive metrics for a project';
COMMENT ON FUNCTION get_project_details IS 'Get complete project details including related metrics';
COMMENT ON VIEW active_projects_dashboard IS 'Dashboard view of active projects with key metrics';