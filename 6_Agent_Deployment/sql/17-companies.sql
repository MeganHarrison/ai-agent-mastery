-- Companies table for managing company information
CREATE TABLE IF NOT EXISTS companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255),
  industry VARCHAR(100),
  size VARCHAR(50),
  location VARCHAR(255),
  website VARCHAR(500),
  description TEXT,
  contact_email VARCHAR(255),
  phone VARCHAR(50),
  status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'prospect', 'archived')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);
CREATE INDEX IF NOT EXISTS idx_companies_created_at ON companies(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_companies_user_id ON companies(user_id);

-- Enable Row Level Security
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Allow users to read all companies (or modify to restrict to their own)
CREATE POLICY "Users can view all companies"
  ON companies
  FOR SELECT
  TO authenticated
  USING (true);

-- Allow users to create companies
CREATE POLICY "Users can create companies"
  ON companies
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own companies
CREATE POLICY "Users can update their own companies"
  ON companies
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own companies
CREATE POLICY "Users can delete their own companies"
  ON companies
  FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_companies_updated_at
  BEFORE UPDATE ON companies
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional - remove in production)
INSERT INTO companies (name, industry, size, location, website, description, contact_email, phone, status)
VALUES
  ('TechCorp Solutions', 'Technology', '50-200', 'San Francisco, CA', 'https://techcorp.example.com', 'Leading provider of cloud solutions', 'contact@techcorp.example.com', '+1-555-0100', 'active'),
  ('Global Marketing Inc', 'Marketing', '10-50', 'New York, NY', 'https://globalmarketing.example.com', 'Digital marketing agency', 'hello@globalmarketing.example.com', '+1-555-0101', 'active'),
  ('DataDrive Analytics', 'Data Analytics', '200-500', 'Austin, TX', 'https://datadrive.example.com', 'Business intelligence and analytics platform', 'info@datadrive.example.com', '+1-555-0102', 'active'),
  ('GreenTech Innovations', 'Clean Energy', '20-50', 'Seattle, WA', 'https://greentech.example.com', 'Renewable energy solutions', 'contact@greentech.example.com', '+1-555-0103', 'prospect'),
  ('FinanceFlow Pro', 'Financial Services', '100-200', 'Chicago, IL', 'https://financeflow.example.com', 'Financial management software', 'support@financeflow.example.com', '+1-555-0104', 'active')
ON CONFLICT DO NOTHING;