import { useParams, Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Edit, Trash2, Clock, User, Flag, TrendingUp } from 'lucide-react';
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

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'completed';
  createdAt: string;
  lastModified: string;
  owner: string;
  priority: 'low' | 'medium' | 'high';
  progress: number;
  details?: {
    goals: string[];
    team: string[];
    timeline: {
      start: string;
      end: string;
    };
    budget?: number;
    technologies: string[];
  };
}

const mockProjectDetails: Record<string, Project> = {
  '1': {
    id: '1',
    name: 'AI Agent Development',
    description: 'Building advanced AI agents with Pydantic and LangChain for automated task execution and intelligent decision making',
    status: 'active',
    createdAt: '2024-01-15',
    lastModified: '2024-01-20',
    owner: 'John Doe',
    priority: 'high',
    progress: 75,
    details: {
      goals: [
        'Implement core agent architecture',
        'Integrate with LangChain for LLM operations',
        'Add memory and context management',
        'Deploy to production environment'
      ],
      team: ['John Doe', 'Jane Smith', 'Bob Johnson'],
      timeline: {
        start: '2024-01-15',
        end: '2024-03-15'
      },
      budget: 50000,
      technologies: ['Python', 'Pydantic', 'LangChain', 'FastAPI', 'PostgreSQL']
    }
  },
  '2': {
    id: '2',
    name: 'RAG Pipeline Implementation',
    description: 'Implementing retrieval augmented generation for document processing and intelligent information extraction',
    status: 'active',
    createdAt: '2024-01-10',
    lastModified: '2024-01-18',
    owner: 'Jane Smith',
    priority: 'medium',
    progress: 50,
    details: {
      goals: [
        'Set up vector database',
        'Implement document ingestion pipeline',
        'Create retrieval mechanisms',
        'Integrate with LLM for generation'
      ],
      team: ['Jane Smith', 'Mike Wilson'],
      timeline: {
        start: '2024-01-10',
        end: '2024-02-28'
      },
      budget: 30000,
      technologies: ['Python', 'Pinecone', 'OpenAI', 'Supabase', 'Docker']
    }
  },
  '3': {
    id: '3',
    name: 'Frontend Dashboard',
    description: 'Creating React-based dashboard with real-time data visualization and interactive components',
    status: 'completed',
    createdAt: '2023-12-20',
    lastModified: '2024-01-05',
    owner: 'Mike Johnson',
    priority: 'low',
    progress: 100,
    details: {
      goals: [
        'Design UI/UX mockups',
        'Implement React components',
        'Add real-time data streaming',
        'Create data visualization charts'
      ],
      team: ['Mike Johnson', 'Sarah Lee'],
      timeline: {
        start: '2023-12-20',
        end: '2024-01-05'
      },
      budget: 20000,
      technologies: ['React', 'TypeScript', 'Tailwind CSS', 'Chart.js', 'WebSockets']
    }
  },
  '4': {
    id: '4',
    name: 'Docker Deployment',
    description: 'Containerizing applications for production deployment with orchestration and monitoring',
    status: 'inactive',
    createdAt: '2023-11-15',
    lastModified: '2023-12-10',
    owner: 'Sarah Wilson',
    priority: 'medium',
    progress: 30,
    details: {
      goals: [
        'Create Dockerfiles for all services',
        'Set up Docker Compose configuration',
        'Implement CI/CD pipeline',
        'Add monitoring and logging'
      ],
      team: ['Sarah Wilson'],
      timeline: {
        start: '2023-11-15',
        end: '2024-01-30'
      },
      budget: 15000,
      technologies: ['Docker', 'Docker Compose', 'GitHub Actions', 'Prometheus', 'Grafana']
    }
  }
};

export const ProjectDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const project = id ? mockProjectDetails[id] : null;

  if (!project) {
    return (
      <div className="flex flex-col min-h-screen items-center justify-center">
        <h1 className="text-2xl font-semibold mb-4">Project not found</h1>
        <Button asChild>
          <Link to="/projects">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>
        </Button>
      </div>
    );
  }

  const getStatusColor = (status: Project['status']) => {
    switch(status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-gray-500';
      case 'completed': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityColor = (priority: Project['priority']) => {
    switch(priority) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'outline';
    }
  };

  const handleEdit = () => {
    toast({
      title: "Edit mode",
      description: "Edit functionality would be implemented here",
    });
  };

  const handleDelete = () => {
    toast({
      title: "Delete project",
      description: "Project deletion would be implemented here",
    });
    navigate('/projects');
  };

  return (
    <div className="flex flex-col min-h-screen">
      <div className="border-b">
        <div className="flex items-center justify-between px-4 py-2">
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
                  <span className="text-sm">{project.owner}</span>
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
                    {project.details?.goals.map((goal, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <TrendingUp className="h-4 w-4 mt-0.5 text-primary" />
                        <span>{goal}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              
              {project.details?.budget && (
                <Card>
                  <CardHeader>
                    <CardTitle>Budget</CardTitle>
                    <CardDescription>Allocated project budget</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      ${project.details.budget.toLocaleString()}
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
                    {project.details?.team.map((member, index) => (
                      <div key={index} className="flex items-center gap-3 p-2 rounded-lg bg-secondary">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <User className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="font-medium">{member}</div>
                          <div className="text-sm text-muted-foreground">
                            {member === project.owner ? 'Project Owner' : 'Team Member'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
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
                      <div className="font-medium">{project.details?.timeline.start}</div>
                    </div>
                  </div>
                  <Separator />
                  <div className="flex items-center gap-3">
                    <Flag className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <div className="text-sm text-muted-foreground">End Date</div>
                      <div className="font-medium">{project.details?.timeline.end}</div>
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
                    {project.details?.technologies.map((tech, index) => (
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