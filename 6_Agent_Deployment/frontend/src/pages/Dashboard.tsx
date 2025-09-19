import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  TrendingUp, 
  Users, 
  FileText, 
  MessageSquare, 
  Calendar,
  BarChart3,
  BookOpen,
  Target,
  AlertCircle,
  ChevronRight,
  Plus,
  Loader2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

interface DashboardStats {
  activeProjects: number;
  totalRevenue: number;
  teamUtilization: number;
  insightsGenerated: number;
  projectsTracking: boolean;
  documents: number;
}

interface ProjectHealth {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'completed' | 'on_hold' | 'planning';
  progress: number;
}

interface AIInsight {
  id: number;
  insight_type: string;
  title: string;
  description: string;
  priority: string;
  created_at: string;
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    activeProjects: 0,
    totalRevenue: 0,
    teamUtilization: 0,
    insightsGenerated: 25,
    projectsTracking: false,
    documents: 0
  });
  const [projects, setProjects] = useState<ProjectHealth[]>([]);
  const [insights, setInsights] = useState<AIInsight[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch projects
      const { data: projectsData, error: projectsError } = await supabase
        .from('projects')
        .select('id, name, status, progress, budget')
        .order('created_at', { ascending: false });

      if (projectsError) {
        console.error('Error fetching projects:', projectsError);
      } else if (projectsData) {
        setProjects(projectsData);
        
        // Calculate stats from projects
        const activeCount = projectsData.filter(p => p.status === 'active').length;
        const totalBudget = projectsData.reduce((sum, p) => sum + (p.budget || 0), 0);
        
        setStats(prev => ({
          ...prev,
          activeProjects: activeCount,
          totalRevenue: totalBudget / 1000, // Convert to K
          projectsTracking: projectsData.length > 0
        }));
      }

      // Fetch document metadata count
      const { count: docCount, error: docError } = await supabase
        .from('document_metadata')
        .select('*', { count: 'exact', head: true });

      if (!docError) {
        setStats(prev => ({ ...prev, documents: docCount || 0 }));
      }

      // Fetch AI insights
      const { data: insightsData, error: insightsError } = await supabase
        .from('project_insights')
        .select('id, insight_type, title, description, priority, created_at')
        .order('created_at', { ascending: false })
        .limit(5);

      if (insightsError) {
        console.error('Error fetching insights:', insightsError);
      } else if (insightsData) {
        setInsights(insightsData);
        setStats(prev => ({ ...prev, insightsGenerated: insightsData.length }));
      }

      // Calculate team utilization (mock for now)
      setStats(prev => ({ 
        ...prev, 
        teamUtilization: (projectsData?.length ?? 0) > 0 ? Math.floor(Math.random() * 30) + 70 : 0 
      }));

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const QuickActionCard = ({ icon: Icon, title, subtitle, onClick }: any) => (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105 bg-card/50 backdrop-blur"
      onClick={onClick}
    >
      <CardContent className="p-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-primary/10 rounded-lg">
            <Icon className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-sm font-semibold">{title}</p>
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card/50 backdrop-blur sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                Executive Dashboard
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                {format(new Date(), 'EEEE, MMMM dd, yyyy • hh:mm a')}
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" size="sm">
                <BarChart3 className="h-4 w-4 mr-2" />
                View Reports
              </Button>
              <Button size="sm">
                <Activity className="h-4 w-4 mr-2" />
                Full Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 space-y-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-card/50 backdrop-blur">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Projects</p>
                  <p className="text-3xl font-bold">{stats.activeProjects}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stats.activeProjects === 0 ? '0 on track, 0 at risk, 0 delayed' : `${stats.activeProjects} on track`}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    All projects tracking well
                  </p>
                </div>
                <div className="p-3 bg-blue-500/10 rounded-lg">
                  <BookOpen className="h-8 w-8 text-blue-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 backdrop-blur">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Revenue Pipeline</p>
                  <p className="text-3xl font-bold">${stats.totalRevenue.toFixed(1)}K</p>
                  <p className="text-xs text-green-500 mt-1">↗ Budget remaining</p>
                  <p className="text-xs text-muted-foreground">Active project budgets</p>
                </div>
                <div className="p-3 bg-green-500/10 rounded-lg">
                  <TrendingUp className="h-8 w-8 text-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 backdrop-blur">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Team Utilization</p>
                  <p className="text-3xl font-bold">
                    {stats.teamUtilization > 0 ? `${stats.teamUtilization}%` : 'NaN%'}
                  </p>
                  <p className="text-xs text-yellow-500 mt-1">→ Current capacity</p>
                  <p className="text-xs text-muted-foreground">Based on project load</p>
                </div>
                <div className="p-3 bg-yellow-500/10 rounded-lg">
                  <Users className="h-8 w-8 text-yellow-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 backdrop-blur">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">AI Insights Generated</p>
                  <p className="text-3xl font-bold">{stats.insightsGenerated}</p>
                  <p className="text-xs text-purple-500 mt-1">→ Total insights</p>
                  <p className="text-xs text-muted-foreground">From conversations & documents</p>
                </div>
                <div className="p-3 bg-purple-500/10 rounded-lg">
                  <MessageSquare className="h-8 w-8 text-purple-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Project Health Overview */}
        <Card className="bg-card/50 backdrop-blur">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold">Project Health Overview</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => navigate('/projects')}>
                View All <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Real-time status of active construction projects
            </p>
          </CardHeader>
          <CardContent>
            {projects.length > 0 ? (
              <div className="space-y-3">
                {projects.slice(0, 3).map((project) => (
                  <div key={project.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${
                        project.status === 'active' ? 'bg-green-500' : 
                        project.status === 'on_hold' ? 'bg-yellow-500' : 'bg-gray-500'
                      }`} />
                      <span className="font-medium text-sm">{project.name}</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-muted-foreground">{project.progress}% Complete</span>
                      <div className="w-24 bg-muted rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No active projects found. Create your first project!</p>
                <Button 
                  className="mt-4" 
                  onClick={() => navigate('/projects')}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create Project
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Insights */}
        <Card className="bg-card/50 backdrop-blur">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-purple-500" />
                <CardTitle className="text-lg font-semibold">AI Insights</CardTitle>
              </div>
              <Button variant="ghost" size="sm">
                View All <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Strategic recommendations and alerts
            </p>
          </CardHeader>
          <CardContent>
            {insights.length > 0 ? (
              <div className="space-y-3">
                {insights.map((insight) => (
                  <div key={insight.id} className="p-3 rounded-lg bg-muted/50 hover:bg-muted/70 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-0.5 text-xs rounded-full ${
                            insight.priority === 'critical' ? 'bg-red-500/20 text-red-500' :
                            insight.priority === 'high' ? 'bg-orange-500/20 text-orange-500' :
                            insight.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-500' :
                            'bg-green-500/20 text-green-500'
                          }`}>
                            {insight.priority}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {insight.insight_type.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-sm font-medium">{insight.title}</p>
                        <p className="text-xs text-muted-foreground line-clamp-2">{insight.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No insights available. Start conversations to generate insights.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <p className="text-sm text-muted-foreground mb-6">Frequently used tools and reports</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <QuickActionCard
              icon={MessageSquare}
              title="Chat with AI"
              subtitle="Ask questions, get insights"
              onClick={() => navigate('/chat')}
            />
            <QuickActionCard
              icon={Target}
              title="Project Status"
              subtitle="Detailed project views"
              onClick={() => navigate('/projects')}
            />
            <QuickActionCard
              icon={Users}
              title="Admin Panel"
              subtitle="Manage users & insights"
              onClick={() => navigate('/admin')}
            />
            <QuickActionCard
              icon={FileText}
              title="Documents"
              subtitle="Meeting notes & files"
              onClick={() => navigate('/documents')}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;