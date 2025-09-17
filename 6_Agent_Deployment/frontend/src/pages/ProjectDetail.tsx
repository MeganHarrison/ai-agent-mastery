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
      </div>
    );
  }

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