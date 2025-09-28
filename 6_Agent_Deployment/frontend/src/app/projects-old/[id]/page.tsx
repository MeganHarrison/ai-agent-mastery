"use client"

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
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
  MessageSquare,
  Edit,
  Trash2,
  Flag,
  Loader2
} from 'lucide-react';
import { format } from 'date-fns';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';

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

export default function ProjectDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [loading, setLoading] = useState(true);
  const [projectDetails, setProjectDetails] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    // Simulate loading project details
    const loadProject = async () => {
      try {
        setLoading(true);
        // This would typically fetch from your API
        // For now, just simulate loading
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock project data
        setProjectDetails({
          id,
          name: `Project ${id}`,
          status: 'in_progress',
          priority: 'high',
          description: 'Sample project description',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      } catch (err) {
        setError('Failed to load project details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadProject();
    }
  }, [id]);

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
      <div className="flex flex-col items-center justify-center min-h-screen">
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Error Loading Project</h1>
        <p className="text-muted-foreground mb-4">
          {error || 'Project not found'}
        </p>
        <Button asChild>
          <Link href="/projects">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <div className="border-b">
        <div className="flex items-center justify-between px-4 py-2">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/projects">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <div>
              <h1 className="text-xl font-semibold">{projectDetails.name}</h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                {getStatusIcon(projectDetails.status)}
                <span>{projectDetails.status?.replace('_', ' ').toUpperCase()}</span>
                <Badge className={getPriorityColor(projectDetails.priority)}>
                  {projectDetails.priority?.toUpperCase()}
                </Badge>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button variant="outline" size="sm">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-4">
        <div className="max-w-7xl mx-auto">
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="tasks">Tasks</TabsTrigger>
              <TabsTrigger value="documents">Documents</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Project Overview</CardTitle>
                  <CardDescription>
                    {projectDetails.description || 'No description available'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        Created
                      </div>
                      <p className="text-sm">
                        {projectDetails.created_at ? format(new Date(projectDetails.created_at), 'PPP') : 'N/A'}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        Last Updated
                      </div>
                      <p className="text-sm">
                        {projectDetails.updated_at ? format(new Date(projectDetails.updated_at), 'PPP') : 'N/A'}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Flag className="h-4 w-4" />
                        Priority
                      </div>
                      <Badge className={getPriorityColor(projectDetails.priority)}>
                        {projectDetails.priority?.toUpperCase() || 'LOW'}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <TrendingUp className="h-4 w-4" />
                        Status
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(projectDetails.status)}
                        <span className="text-sm">
                          {projectDetails.status?.replace('_', ' ').toUpperCase() || 'PENDING'}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="tasks">
              <Card>
                <CardHeader>
                  <CardTitle>Project Tasks</CardTitle>
                  <CardDescription>
                    Manage and track tasks for this project
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">No tasks found for this project.</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="documents">
              <Card>
                <CardHeader>
                  <CardTitle>Project Documents</CardTitle>
                  <CardDescription>
                    Files and documents related to this project
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">No documents found for this project.</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="insights">
              <Card>
                <CardHeader>
                  <CardTitle>Project Insights</CardTitle>
                  <CardDescription>
                    AI-generated insights and analysis
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">No insights available for this project.</p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}