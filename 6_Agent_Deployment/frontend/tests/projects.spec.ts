import { test, expect } from '@playwright/test';
import { setupUnauthenticatedMocks, setupAgentAPIMocks, setupModuleMocks } from './mocks';

// Mock project data
const mockProjects = [
  {
    id: 1,
    name: 'Construction Project Alpha',
    client_name: 'ABC Corporation',
    status: 'active',
    project_type: 'construction',
    start_date: '2024-01-01',
    estimated_completion: '2024-12-31',
    revenue: 500000,
    budget: 400000,
    spent: 200000,
    profit: 100000,
    profit_margin: 20,
    location: 'New York, NY',
    project_manager: 'John Doe',
    completion_percentage: 50,
    risk_level: 'medium',
    priority: 3,
    is_archived: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-06-01T00:00:00Z'
  },
  {
    id: 2,
    name: 'Maintenance Project Beta',
    client_name: 'XYZ Industries',
    status: 'completed',
    project_type: 'maintenance',
    start_date: '2023-06-01',
    actual_completion: '2024-03-01',
    revenue: 250000,
    profit: 50000,
    profit_margin: 20,
    location: 'Los Angeles, CA',
    project_manager: 'Jane Smith',
    completion_percentage: 100,
    is_archived: false,
    created_at: '2023-06-01T00:00:00Z',
    updated_at: '2024-03-01T00:00:00Z'
  }
];

const mockMeetings = [
  {
    id: 1,
    title: 'Project Kickoff Meeting',
    description: 'Initial project planning and requirements gathering',
    meeting_type: 'kickoff',
    meeting_status: 'completed',
    project_id: 1,
    meeting_date: '2024-01-15T10:00:00Z',
    duration_minutes: 60,
    location: 'Conference Room A',
    organizer: 'John Doe',
    attendees: ['John Doe', 'Jane Smith', 'Bob Johnson'],
    has_insights: true,
    insights_count: 5,
    created_at: '2024-01-10T00:00:00Z'
  },
  {
    id: 2,
    title: 'Weekly Status Update',
    meeting_type: 'status_update',
    meeting_status: 'scheduled',
    project_id: 1,
    meeting_date: '2024-12-20T14:00:00Z',
    duration_minutes: 30,
    meeting_link: 'https://meet.example.com/abc123',
    organizer: 'Jane Smith',
    has_insights: false,
    insights_count: 0,
    created_at: '2024-06-01T00:00:00Z'
  }
];

const mockInsights = [
  {
    id: 1,
    insight_type: 'action_item',
    title: 'Complete environmental impact assessment',
    description: 'Environmental assessment needs to be completed before construction begins',
    priority: 'critical',
    status: 'open',
    project_id: 1,
    assigned_to: 'Bob Johnson',
    due_date: '2024-07-01T00:00:00Z',
    confidence_score: 0.95,
    created_at: '2024-01-15T00:00:00Z'
  },
  {
    id: 2,
    insight_type: 'risk',
    title: 'Weather delays possible in Q4',
    description: 'Historical data suggests high probability of weather delays in Q4',
    priority: 'high',
    status: 'in_progress',
    project_id: 1,
    confidence_score: 0.8,
    created_at: '2024-01-15T00:00:00Z'
  }
];

test.describe('Projects Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupUnauthenticatedMocks(page);
    await setupAgentAPIMocks(page);
    await setupModuleMocks(page);
    
    // Mock the projects API call
    await page.route('**/rest/v1/projects*', async (route) => {
      if (route.request().url().includes('is_archived=eq.false')) {
        await route.fulfill({
          status: 200,
          json: mockProjects
        });
      } else {
        await route.fulfill({
          status: 200,
          json: []
        });
      }
    });
  });

  test('should display list of projects', async ({ page }) => {
    await page.goto('/projects');
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Projects');
    
    // Check summary cards
    await expect(page.locator('text=Total Projects')).toBeVisible();
    await expect(page.locator('text=Active Projects')).toBeVisible();
    
    // Check project cards are displayed
    await expect(page.locator('text=Construction Project Alpha')).toBeVisible();
    await expect(page.locator('text=ABC Corporation')).toBeVisible();
    await expect(page.locator('text=Maintenance Project Beta')).toBeVisible();
    await expect(page.locator('text=XYZ Industries')).toBeVisible();
  });

  test('should navigate to project detail page on click', async ({ page }) => {
    await page.goto('/projects');
    
    // Click on the first project
    await page.locator('text=Construction Project Alpha').click();
    
    // Should navigate to project detail page
    await expect(page).toHaveURL(/\/projects\/1/);
  });

  test('should show correct project status badges', async ({ page }) => {
    await page.goto('/projects');
    
    // Check status badges
    const activeProject = page.locator('text=Construction Project Alpha').locator('..');
    await expect(activeProject.locator('text=active')).toBeVisible();
    
    const completedProject = page.locator('text=Maintenance Project Beta').locator('..');
    await expect(completedProject.locator('text=completed')).toBeVisible();
  });
});

test.describe('Project Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupUnauthenticatedMocks(page);
    await setupAgentAPIMocks(page);
    await setupModuleMocks(page);
    
    // Mock the project detail API call
    await page.route('**/rest/v1/projects*', async (route) => {
      if (route.request().url().includes('id=eq.1')) {
        await route.fulfill({
          status: 200,
          json: mockProjects[0]
        });
      } else {
        await route.fulfill({
          status: 200,
          json: mockProjects
        });
      }
    });
    
    // Mock meetings API call
    await page.route('**/rest/v1/meetings*', async (route) => {
      if (route.request().url().includes('project_id=eq.1')) {
        await route.fulfill({
          status: 200,
          json: mockMeetings
        });
      } else {
        await route.fulfill({
          status: 200,
          json: []
        });
      }
    });
    
    // Mock insights API call
    await page.route('**/rest/v1/project_insights*', async (route) => {
      if (route.request().url().includes('project_id=eq.1')) {
        await route.fulfill({
          status: 200,
          json: mockInsights
        });
      } else {
        await route.fulfill({
          status: 200,
          json: []
        });
      }
    });
  });

  test('should display project details', async ({ page }) => {
    await page.goto('/projects/1');
    
    // Check project name and status
    await expect(page.locator('h1')).toContainText('Construction Project Alpha');
    await expect(page.locator('text=active')).toBeVisible();
    
    // Check metrics cards
    await expect(page.locator('text=Total Meetings')).toBeVisible();
    await expect(page.locator('text=Total Insights')).toBeVisible();
    await expect(page.locator('text=Critical Items')).toBeVisible();
    await expect(page.locator('text=Completion')).toBeVisible();
    
    // Check completion percentage
    await expect(page.locator('text=50%')).toBeVisible();
  });

  test('should display project information in details tab', async ({ page }) => {
    await page.goto('/projects/1');
    
    // Click on details tab (should be default)
    const detailsTab = page.locator('button[role="tab"]:has-text("Project Details")');
    await expect(detailsTab).toHaveAttribute('data-state', 'active');
    
    // Check project information is displayed
    await expect(page.locator('text=ABC Corporation')).toBeVisible();
    await expect(page.locator('text=John Doe')).toBeVisible();
    await expect(page.locator('text=New York, NY')).toBeVisible();
  });

  test('should display meetings in meetings tab', async ({ page }) => {
    await page.goto('/projects/1');
    
    // Click on meetings tab
    await page.locator('button[role="tab"]:has-text("Meetings")').click();
    
    // Check meetings are displayed
    await expect(page.locator('text=Project Kickoff Meeting')).toBeVisible();
    await expect(page.locator('text=Weekly Status Update')).toBeVisible();
    await expect(page.locator('text=Conference Room A')).toBeVisible();
  });

  test('should display insights in insights tab', async ({ page }) => {
    await page.goto('/projects/1');
    
    // Click on insights tab
    await page.locator('button[role="tab"]:has-text("Insights")').click();
    
    // Check insights are displayed
    await expect(page.locator('text=Complete environmental impact assessment')).toBeVisible();
    await expect(page.locator('text=Weather delays possible in Q4')).toBeVisible();
    await expect(page.locator('text=critical')).toBeVisible();
    await expect(page.locator('text=high')).toBeVisible();
  });

  test('should display financial information in financials tab', async ({ page }) => {
    await page.goto('/projects/1');
    
    // Click on financials tab
    await page.locator('button[role="tab"]:has-text("Financials")').click();
    
    // Check financial data is displayed
    await expect(page.locator('text=$500,000')).toBeVisible(); // Revenue
    await expect(page.locator('text=$400,000')).toBeVisible(); // Budget
    await expect(page.locator('text=$200,000')).toBeVisible(); // Spent
    await expect(page.locator('text=$100,000')).toBeVisible(); // Profit
    await expect(page.locator('text=20%')).toBeVisible(); // Profit margin
  });

  test('should enable edit mode when edit button is clicked', async ({ page }) => {
    await page.goto('/projects/1');
    
    // Click edit button
    await page.locator('button:has-text("Edit")').click();
    
    // Check save and cancel buttons appear
    await expect(page.locator('button:has-text("Save")')).toBeVisible();
    await expect(page.locator('button:has-text("Cancel")')).toBeVisible();
    
    // Check input fields are editable
    const clientInput = page.locator('input').first();
    await expect(clientInput).toBeEditable();
  });

  test('should navigate back to projects list', async ({ page }) => {
    await page.goto('/projects/1');
    
    // Click back button
    await page.locator('button:has-text("Back to Projects")').click();
    
    // Should navigate back to projects list
    await expect(page).toHaveURL('/projects');
  });
});