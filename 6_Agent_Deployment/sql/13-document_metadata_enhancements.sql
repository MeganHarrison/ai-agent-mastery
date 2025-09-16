-- Add additional columns to document_metadata table for meeting tracking
-- This migration adds columns for project, date, summary, fireflies_link, type, speakers, and transcript

-- Add new columns to document_metadata table
ALTER TABLE document_metadata
ADD COLUMN IF NOT EXISTS type TEXT,
ADD COLUMN IF NOT EXISTS project TEXT,
ADD COLUMN IF NOT EXISTS date DATE,
ADD COLUMN IF NOT EXISTS summary TEXT,
ADD COLUMN IF NOT EXISTS fireflies_link TEXT,
ADD COLUMN IF NOT EXISTS speakers TEXT,
ADD COLUMN IF NOT EXISTS transcript TEXT;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_document_metadata_type ON document_metadata(type);
CREATE INDEX IF NOT EXISTS idx_document_metadata_project ON document_metadata(project);
CREATE INDEX IF NOT EXISTS idx_document_metadata_date ON document_metadata(date);

-- Add comments for documentation
COMMENT ON COLUMN document_metadata.type IS 'Type of document (e.g., meeting, SOP, document)';
COMMENT ON COLUMN document_metadata.project IS 'Associated project name';
COMMENT ON COLUMN document_metadata.date IS 'Date of the document or meeting';
COMMENT ON COLUMN document_metadata.summary IS 'Brief summary of the document content';
COMMENT ON COLUMN document_metadata.fireflies_link IS 'Link to Fireflies.ai recording if applicable';
COMMENT ON COLUMN document_metadata.speakers IS 'List of speakers or participants';
COMMENT ON COLUMN document_metadata.transcript IS 'Full transcript of the meeting or document';

-- Example data (optional - uncomment to insert sample data)
-- INSERT INTO document_metadata (id, title, type, project, date, summary, fireflies_link, speakers)
-- VALUES 
--   ('sample-1', 'Project Kickoff Meeting', 'meeting', 'Project Alpha', '2024-01-15', 'Initial project planning and timeline discussion', 'https://fireflies.ai/view/meeting1', 'John Doe, Jane Smith'),
--   ('sample-2', 'Technical Review', 'meeting', 'Project Beta', '2024-01-20', 'Architecture review and technical decisions', 'https://fireflies.ai/view/meeting2', 'Tech Team'),
--   ('sample-3', 'Safety Guidelines', 'SOPs', 'General', '2024-01-10', 'Company safety procedures', NULL, NULL),
--   ('sample-4', 'Development Standards', 'documents', 'Engineering', '2024-01-05', 'Coding standards and best practices', NULL, NULL);