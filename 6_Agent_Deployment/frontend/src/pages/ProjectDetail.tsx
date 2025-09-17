import { useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useProjectDetails } from '@/hooks/useProjectDetails';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  ArrowLeft, 
  Calendar, 
  MapPin, 
  DollarSign, 
  User, 
  FileText,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  Target,
  Users,
  MessageSquare
} from 'lucide-react';
import { format } from 'date-fns';

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'critical': return 'bg-red-500';
    case 'high': return 'bg-orange-500';
    case 'medium': return 'bg-yellow-500';
    case 'low': return 'bg-green-500';
    default: return 'bg-gray-500';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
    case 'in_progress': return <Clock className="h-4 w-4 text-yellow-500" />;
    case 'cancelled': return <AlertCircle className="h-4 w-4 text-red-500" />;
    default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
  }
};

const getInsightIcon = (type: string) => {
  switch (type) {
    case 'action_item': return <Target className="h-4 w-4" />;
    case 'decision': return <CheckCircle className="h-4 w-4" />;
    case 'risk': return <AlertCircle className="h-4 w-4" />;
    case 'milestone': return <TrendingUp className="h-4 w-4" />;
    case 'opportunity': return <DollarSign className="h-4 w-4" />;
    default: return <FileText className="h-4 w-4" />;
  }
};
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Edit, Trash2, Clock, User, Flag, TrendingUp, Loader2 } from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { Project, ProjectStatus, ProjectPriority } from '@/types/project.types';
import { useProject, useUpdateProject, useDeleteProject } from '@/hooks/useProjects';


export const ProjectDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { projectDetails, loading, error } = useProjectDetails(id || '');

  useEffect(() => {
    if (!id) {
      navigate('/');
    }
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="flex flex-col min-h-screen">
        <div className="border-b">
          <div className="flex items-center justify-between px-4 py-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-8 w-32" />
          </div>
        </div>
        <div className="flex-1 p-4">
          <div className="max-w-7xl mx-auto space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        </div>
  const { toast } = useToast();
  const { project, loading, error } = useProject(id);
  const { updateProject, loading: updateLoading } = useUpdateProject();
  const { deleteProject, loading: deleteLoading } = useDeleteProject();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error || !projectDetails) {
    return (
      <div className="flex flex-col min-h-screen">
        <div className="border-b">
          <div className="flex items-center justify-between px-4 py-2">
            <h1 className="text-lg font-semibold">Project Details</h1>
            <Button variant="outline" size="sm" asChild>
              <Link to="/">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Link>
            </Button>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Error loading project</h2>
            <p className="text-gray-500 mb-4">{error || 'Project not found'}</p>
            <Button variant="outline" asChild>
              <Link to="/">Return to Home</Link>
            </Button>
          </div>
        </div>
  if (error || !project) {
    return (
      <div className="flex flex-col min-h-screen items-center justify-center">
        <h1 className="text-2xl font-semibold mb-4">{error || 'Project not found'}</h1>
        <Button asChild>
          <Link to="/projects">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>
        </Button>
      </div>
    );
  }


  const getStatusColor = (status: ProjectStatus) => {
    switch(status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-gray-500';
      case 'completed': return 'bg-blue-500';
      case 'on_hold': return 'bg-yellow-500';
      case 'planning': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityColor = (priority: ProjectPriority) => {
    switch(priority) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'outline';
    }
  };

  const handleEdit = () => {
    // Navigate to edit page or open edit dialog
    navigate(`/projects/${id}/edit`);
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) return;
    
    const result = await deleteProject(project.id);
    if (result) {
      navigate('/projects');
    }
  };


  return (
    <div className="flex flex-col min-h-screen">
      <div className="border-b">
        <div className="flex items-center justify-between px-4 py-2">
          <h1 className="text-lg font-semibold">{projectDetails.projectName}</h1>
          <Button variant="outline" size="sm" asChild>
            <Link to="/">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Link>
          </Button>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-4">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Project Overview Card */}
          <Card>
            <CardHeader>
              <CardTitle>Project Overview</CardTitle>
              <CardDescription>Key information about {projectDetails.projectName}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projectDetails.client && (
                  <div className="flex items-start space-x-2">
                    <User className="h-5 w-5 text-gray-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Client</p>
                      <p className="text-sm text-gray-600">{projectDetails.client}</p>
                    </div>
                  </div>
                )}
                
                {projectDetails.startDate && (
                  <div className="flex items-start space-x-2">
                    <Calendar className="h-5 w-5 text-gray-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Start Date</p>
                      <p className="text-sm text-gray-600">{projectDetails.startDate}</p>
                    </div>
                  </div>
                )}
                
                {projectDetails.estimatedCompletion && (
                  <div className="flex items-start space-x-2">
                    <Clock className="h-5 w-5 text-gray-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Est. Completion</p>
                      <p className="text-sm text-gray-600">{projectDetails.estimatedCompletion}</p>
                    </div>
                  </div>
                )}
                
                {projectDetails.revenue !== undefined && (
                  <div className="flex items-start space-x-2">
                    <DollarSign className="h-5 w-5 text-gray-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Revenue</p>
                      <p className="text-sm text-gray-600">${projectDetails.revenue?.toLocaleString()}</p>
                    </div>
                  </div>
                )}
                
                {projectDetails.profit !== undefined && (
                  <div className="flex items-start space-x-2">
                    <TrendingUp className="h-5 w-5 text-gray-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Profit</p>
                      <p className="text-sm text-gray-600">${projectDetails.profit?.toLocaleString()}</p>
                    </div>
                  </div>
                )}
                
                {projectDetails.location && (
                  <div className="flex items-start space-x-2">
                    <MapPin className="h-5 w-5 text-gray-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Location</p>
                      <p className="text-sm text-gray-600">{projectDetails.location}</p>
                    </div>
                  </div>
                )}
              </div>
              
              {projectDetails.notes && (
                <div className="mt-4 pt-4 border-t">
                  <div className="flex items-start space-x-2">
                    <FileText className="h-5 w-5 text-gray-500 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium mb-1">Notes</p>
                      <p className="text-sm text-gray-600 whitespace-pre-wrap">{projectDetails.notes}</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Tabs for Meetings and Insights */}
          <Tabs defaultValue="insights" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="insights" className="flex items-center gap-2">
                <Target className="h-4 w-4" />
                Insights ({projectDetails.insights.length})
              </TabsTrigger>
              <TabsTrigger value="meetings" className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Meetings ({projectDetails.meetings.length})
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="insights" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Project Insights</CardTitle>
                  <CardDescription>
                    AI-generated insights from meetings and documents
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {projectDetails.insights.length === 0 ? (
                    <div className="text-center py-8">
                      <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">No insights generated yet</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {projectDetails.insights.map((insight) => (
                        <div 
                          key={insight.id} 
                          className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {getInsightIcon(insight.insight_type)}
                              <h4 className="font-medium">{insight.title}</h4>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge className={getPriorityColor(insight.priority)}>
                                {insight.priority}
                              </Badge>
                              {getStatusIcon(insight.status)}
                            </div>
                          </div>
                          
                          <p className="text-sm text-gray-600 mb-3">{insight.description}</p>
                          
                          <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                            {insight.assigned_to && (
                              <div className="flex items-center gap-1">
                                <Users className="h-3 w-3" />
                                {insight.assigned_to}
                              </div>
                            )}
                            {insight.due_date && (
                              <div className="flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                {format(new Date(insight.due_date), 'MMM dd, yyyy')}
                              </div>
                            )}
                            {insight.source_meeting_title && (
                              <div className="flex items-center gap-1">
                                <MessageSquare className="h-3 w-3" />
                                {insight.source_meeting_title}
                              </div>
                            )}
                            {insight.confidence_score && (
                              <div className="flex items-center gap-1">
                                Confidence: {(insight.confidence_score * 100).toFixed(0)}%
                              </div>
                            )}
                          </div>
                          
                          {insight.keywords && insight.keywords.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-3">
                              {insight.keywords.map((keyword, idx) => (
                                <Badge key={idx} variant="secondary" className="text-xs">
                                  {keyword}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/projects">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <div>
              <h1 className="text-lg font-semibold">{project.name}</h1>
              <p className="text-sm text-muted-foreground">{project.description}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleEdit}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Button>
            <Button variant="destructive" size="sm" onClick={handleDelete}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        <div className="max-w-[1200px] mx-auto space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Status</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge className={`${getStatusColor(project.status)} text-white`}>
                  {project.status}
                </Badge>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Priority</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant={getPriorityColor(project.priority)}>
                  {project.priority}
                </Badge>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Progress</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Progress value={project.progress} className="flex-1" />
                  <span className="text-sm font-medium">{project.progress}%</span>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Owner</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  <span className="text-sm">{project.owner_name}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Information Tabs */}
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-gray-100 dark:bg-gray-800">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="team">Team</TabsTrigger>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="technologies">Technologies</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Project Goals</CardTitle>
                  <CardDescription>Key objectives and milestones</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {project.goals?.map((goal, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <TrendingUp className="h-4 w-4 mt-0.5 text-primary" />
                        <span>{goal}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              
              {project.budget && (
                <Card>
                  <CardHeader>
                    <CardTitle>Budget</CardTitle>
                    <CardDescription>Allocated project budget</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      ${project.budget.toLocaleString()}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
            
            <TabsContent value="team" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Team Members</CardTitle>
                  <CardDescription>People working on this project</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {project.team_members?.map((member, index) => (
                      <div key={index} className="flex items-center gap-3 p-2 rounded-lg bg-secondary">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <User className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="font-medium">{member}</div>
                          <div className="text-sm text-muted-foreground">
                            {member === project.owner_name ? 'Project Owner' : 'Team Member'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="meetings" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Meeting Transcripts</CardTitle>
                  <CardDescription>
                    All meetings and documents associated with this project
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {projectDetails.meetings.length === 0 ? (
                    <div className="text-center py-8">
                      <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">No meetings recorded yet</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {projectDetails.meetings.map((meeting) => (
                        <div 
                          key={meeting.id}
                          className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-medium mb-1">{meeting.title}</h4>
                              {meeting.url && (
                                <a 
                                  href={meeting.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-sm text-blue-500 hover:underline"
                                >
                                  View Document
                                </a>
                              )}
                            </div>
                            <div className="text-sm text-gray-500">
                              {format(new Date(meeting.created_at), 'MMM dd, yyyy h:mm a')}
                            </div>
                          </div>
                          
                          {meeting.meeting_type && (
                            <Badge variant="outline" className="mt-2">
                              {meeting.meeting_type}
                            </Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
            <TabsContent value="timeline" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Project Timeline</CardTitle>
                  <CardDescription>Schedule and important dates</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Clock className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <div className="text-sm text-muted-foreground">Start Date</div>
                      <div className="font-medium">{project.start_date || 'Not set'}</div>
                    </div>
                  </div>
                  <Separator />
                  <div className="flex items-center gap-3">
                    <Flag className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <div className="text-sm text-muted-foreground">End Date</div>
                      <div className="font-medium">{project.end_date || 'Not set'}</div>
                    </div>
                  </div>
                  <Separator />
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">Created</div>
                    <div className="font-medium">{project.createdAt}</div>
                    <div className="text-sm text-muted-foreground">Last Modified</div>
                    <div className="font-medium">{project.lastModified}</div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="technologies" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Technology Stack</CardTitle>
                  <CardDescription>Tools and technologies used in this project</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {project.technologies?.map((tech, index) => (
                      <Badge key={index} variant="secondary" className="px-3 py-1">
                        {tech}
                      </Badge>
                    ))}
                  </div>
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