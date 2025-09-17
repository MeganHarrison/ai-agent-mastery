import { useParams, useNavigate, Link } from 'react-router-dom';
import { useProject } from '@/hooks/useProject';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  ArrowLeft, 
  Calendar, 
  DollarSign, 
  MapPin, 
  Users, 
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  Edit,
  Save,
  X
} from 'lucide-react';
import { useState } from 'react';
import { format } from 'date-fns';
import { toast } from '@/components/ui/use-toast';

export const ProjectDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { project, meetings, insights, loading, error, updateProject } = useProject(id);
  const [isEditing, setIsEditing] = useState(false);
  const [editedProject, setEditedProject] = useState<any>(null);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="animate-pulse">Loading project details...</div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error || 'Project not found'}</p>
          <Button onClick={() => navigate('/projects')}>Back to Projects</Button>
        </div>
      </div>
    );
  }

  const handleEdit = () => {
    setEditedProject({ ...project });
    setIsEditing(true);
  };

  const handleCancel = () => {
    setEditedProject(null);
    setIsEditing(false);
  };

  const handleSave = async () => {
    if (!editedProject) return;

    const { data, error } = await updateProject(editedProject);
    if (error) {
      toast({
        title: "Error",
        description: "Failed to update project",
        variant: "destructive",
      });
    } else {
      toast({
        title: "Success",
        description: "Project updated successfully",
      });
      setIsEditing(false);
      setEditedProject(null);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setEditedProject((prev: any) => ({
      ...prev,
      [field]: value
    }));
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      active: "default",
      completed: "secondary",
      on_hold: "outline",
      cancelled: "destructive",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  const getPriorityBadge = (priority: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      critical: "destructive",
      high: "destructive",
      medium: "default",
      low: "secondary",
    };
    return <Badge variant={variants[priority] || "default"}>{priority}</Badge>;
  };

  const openInsights = insights.filter(i => i.status === 'open' || i.status === 'in_progress');
  const criticalInsights = insights.filter(i => i.priority === 'critical' && (i.status === 'open' || i.status === 'in_progress'));
  const upcomingMeetings = meetings.filter(m => new Date(m.meeting_date) > new Date());

  return (
    <div className="flex flex-col min-h-screen">
      <div className="border-b">
        <div className="flex items-center justify-between px-4 py-2">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/projects')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Projects
            </Button>
            <h1 className="text-lg font-semibold">{project.name}</h1>
            {getStatusBadge(project.status)}
          </div>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <Button size="sm" onClick={handleSave}>
                  <Save className="mr-2 h-4 w-4" />
                  Save
                </Button>
                <Button size="sm" variant="outline" onClick={handleCancel}>
                  <X className="mr-2 h-4 w-4" />
                  Cancel
                </Button>
              </>
            ) : (
              <Button size="sm" variant="outline" onClick={handleEdit}>
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Metrics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Meetings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{meetings.length}</div>
                <p className="text-xs text-muted-foreground">
                  {upcomingMeetings.length} upcoming
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{insights.length}</div>
                <p className="text-xs text-muted-foreground">
                  {openInsights.length} open
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Critical Items</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-500">{criticalInsights.length}</div>
                <p className="text-xs text-muted-foreground">Requires attention</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Completion</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{project.completion_percentage || 0}%</div>
                <div className="w-full bg-secondary h-2 rounded-full mt-2">
                  <div 
                    className="bg-primary h-2 rounded-full transition-all"
                    style={{ width: `${project.completion_percentage || 0}%` }}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="details" className="space-y-4">
            <TabsList>
              <TabsTrigger value="details">Project Details</TabsTrigger>
              <TabsTrigger value="meetings">
                Meetings ({meetings.length})
              </TabsTrigger>
              <TabsTrigger value="insights">
                Insights ({insights.length})
              </TabsTrigger>
              <TabsTrigger value="financials">Financials</TabsTrigger>
            </TabsList>

            <TabsContent value="details" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Project Information</CardTitle>
                  <CardDescription>Core project details and metadata</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Client</Label>
                      {isEditing ? (
                        <Input
                          value={editedProject?.client_name || ''}
                          onChange={(e) => handleInputChange('client_name', e.target.value)}
                        />
                      ) : (
                        <p className="text-sm">{project.client_name || 'N/A'}</p>
                      )}
                    </div>
                    <div>
                      <Label>Project Manager</Label>
                      {isEditing ? (
                        <Input
                          value={editedProject?.project_manager || ''}
                          onChange={(e) => handleInputChange('project_manager', e.target.value)}
                        />
                      ) : (
                        <p className="text-sm">{project.project_manager || 'N/A'}</p>
                      )}
                    </div>
                    <div>
                      <Label>Start Date</Label>
                      {isEditing ? (
                        <Input
                          type="date"
                          value={editedProject?.start_date || ''}
                          onChange={(e) => handleInputChange('start_date', e.target.value)}
                        />
                      ) : (
                        <p className="text-sm">
                          {project.start_date ? format(new Date(project.start_date), 'MMM dd, yyyy') : 'N/A'}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Estimated Completion</Label>
                      {isEditing ? (
                        <Input
                          type="date"
                          value={editedProject?.estimated_completion || ''}
                          onChange={(e) => handleInputChange('estimated_completion', e.target.value)}
                        />
                      ) : (
                        <p className="text-sm">
                          {project.estimated_completion ? format(new Date(project.estimated_completion), 'MMM dd, yyyy') : 'N/A'}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Location</Label>
                      {isEditing ? (
                        <Input
                          value={editedProject?.location || ''}
                          onChange={(e) => handleInputChange('location', e.target.value)}
                        />
                      ) : (
                        <p className="text-sm flex items-center">
                          <MapPin className="h-3 w-3 mr-1" />
                          {project.location || 'N/A'}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Risk Level</Label>
                      {project.risk_level && getPriorityBadge(project.risk_level)}
                    </div>
                  </div>

                  <div>
                    <Label>Notes</Label>
                    {isEditing ? (
                      <Textarea
                        value={editedProject?.notes || ''}
                        onChange={(e) => handleInputChange('notes', e.target.value)}
                        className="min-h-[100px]"
                      />
                    ) : (
                      <p className="text-sm whitespace-pre-wrap">{project.notes || 'No notes available'}</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="meetings" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Project Meetings</CardTitle>
                  <CardDescription>All meetings associated with this project</CardDescription>
                </CardHeader>
                <CardContent>
                  {meetings.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No meetings scheduled</p>
                  ) : (
                    <div className="space-y-3">
                      {meetings.map((meeting) => (
                        <div key={meeting.id} className="border rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <h4 className="font-medium">{meeting.title}</h4>
                                <Badge variant="outline">{meeting.meeting_type}</Badge>
                                <Badge>{meeting.meeting_status}</Badge>
                              </div>
                              <p className="text-sm text-muted-foreground">{meeting.description}</p>
                              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                <span className="flex items-center">
                                  <Calendar className="h-3 w-3 mr-1" />
                                  {format(new Date(meeting.meeting_date), 'MMM dd, yyyy HH:mm')}
                                </span>
                                {meeting.location && (
                                  <span className="flex items-center">
                                    <MapPin className="h-3 w-3 mr-1" />
                                    {meeting.location}
                                  </span>
                                )}
                                {meeting.organizer && (
                                  <span className="flex items-center">
                                    <Users className="h-3 w-3 mr-1" />
                                    {meeting.organizer}
                                  </span>
                                )}
                              </div>
                            </div>
                            {meeting.has_insights && (
                              <Badge variant="secondary">
                                {meeting.insights_count} insights
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="insights" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Project Insights</CardTitle>
                  <CardDescription>AI-generated insights from meetings and documents</CardDescription>
                </CardHeader>
                <CardContent>
                  {insights.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No insights available</p>
                  ) : (
                    <div className="space-y-3">
                      {insights.map((insight) => (
                        <div key={insight.id} className="border rounded-lg p-3">
                          <div className="space-y-2">
                            <div className="flex items-start justify-between">
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <h4 className="font-medium">{insight.title}</h4>
                                  {getPriorityBadge(insight.priority)}
                                  <Badge variant="outline">{insight.insight_type}</Badge>
                                </div>
                                <p className="text-sm text-muted-foreground">{insight.description}</p>
                              </div>
                              <Badge>{insight.status}</Badge>
                            </div>
                            <div className="flex items-center gap-4 text-xs text-muted-foreground">
                              {insight.assigned_to && (
                                <span>Assigned to: {insight.assigned_to}</span>
                              )}
                              {insight.due_date && (
                                <span className="flex items-center">
                                  <Clock className="h-3 w-3 mr-1" />
                                  Due: {format(new Date(insight.due_date), 'MMM dd, yyyy')}
                                </span>
                              )}
                              {insight.confidence_score && (
                                <span>Confidence: {(insight.confidence_score * 100).toFixed(0)}%</span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="financials" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Financial Overview</CardTitle>
                  <CardDescription>Project revenue, costs, and profitability</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <Label>Revenue</Label>
                      {isEditing ? (
                        <Input
                          type="number"
                          value={editedProject?.revenue || ''}
                          onChange={(e) => handleInputChange('revenue', parseFloat(e.target.value))}
                        />
                      ) : (
                        <p className="text-lg font-semibold">
                          ${project.revenue?.toLocaleString() || '0'}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Budget</Label>
                      {isEditing ? (
                        <Input
                          type="number"
                          value={editedProject?.budget || ''}
                          onChange={(e) => handleInputChange('budget', parseFloat(e.target.value))}
                        />
                      ) : (
                        <p className="text-lg font-semibold">
                          ${project.budget?.toLocaleString() || '0'}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Spent</Label>
                      {isEditing ? (
                        <Input
                          type="number"
                          value={editedProject?.spent || ''}
                          onChange={(e) => handleInputChange('spent', parseFloat(e.target.value))}
                        />
                      ) : (
                        <p className="text-lg font-semibold">
                          ${project.spent?.toLocaleString() || '0'}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Profit</Label>
                      {isEditing ? (
                        <Input
                          type="number"
                          value={editedProject?.profit || ''}
                          onChange={(e) => handleInputChange('profit', parseFloat(e.target.value))}
                        />
                      ) : (
                        <p className="text-lg font-semibold text-green-600">
                          ${project.profit?.toLocaleString() || '0'}
                        </p>
                      )}
                    </div>
                  </div>

                  {project.profit_margin && (
                    <div className="border-t pt-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Profit Margin</span>
                        <span className="text-lg font-bold flex items-center">
                          <TrendingUp className="h-4 w-4 mr-1 text-green-600" />
                          {project.profit_margin}%
                        </span>
                      </div>
                    </div>
                  )}

                  {project.budget && project.spent && (
                    <div className="border-t pt-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">Budget Usage</span>
                          <span className="text-sm">
                            {((project.spent / project.budget) * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-secondary h-2 rounded-full">
                          <div 
                            className="bg-primary h-2 rounded-full transition-all"
                            style={{ width: `${Math.min((project.spent / project.budget) * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetail;