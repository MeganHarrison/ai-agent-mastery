import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  MessageSquare, 
  Plus, 
  LayoutGrid, 
  List, 
  Table as TableIcon,
  MoreVertical,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

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
}

const mockProjects: Project[] = [
  {
    id: '1',
    name: 'AI Agent Development',
    description: 'Building advanced AI agents with Pydantic and LangChain',
    status: 'active',
    createdAt: '2024-01-15',
    lastModified: '2024-01-20',
    owner: 'John Doe',
    priority: 'high',
    progress: 75
  },
  {
    id: '2',
    name: 'RAG Pipeline Implementation',
    description: 'Implementing retrieval augmented generation for document processing',
    status: 'active',
    createdAt: '2024-01-10',
    lastModified: '2024-01-18',
    owner: 'Jane Smith',
    priority: 'medium',
    progress: 50
  },
  {
    id: '3',
    name: 'Frontend Dashboard',
    description: 'Creating React-based dashboard with real-time data visualization',
    status: 'completed',
    createdAt: '2023-12-20',
    lastModified: '2024-01-05',
    owner: 'Mike Johnson',
    priority: 'low',
    progress: 100
  },
  {
    id: '4',
    name: 'Docker Deployment',
    description: 'Containerizing applications for production deployment',
    status: 'inactive',
    createdAt: '2023-11-15',
    lastModified: '2023-12-10',
    owner: 'Sarah Wilson',
    priority: 'medium',
    progress: 30
  }
];

export const Projects = () => {
  const [viewMode, setViewMode] = useState<'card' | 'list' | 'table'>('card');
  const [projects, setProjects] = useState<Project[]>(mockProjects);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'active' as Project['status'],
    priority: 'medium' as Project['priority'],
    owner: ''
  });
  const { toast } = useToast();

  const handleCreate = () => {
    const newProject: Project = {
      id: String(projects.length + 1),
      name: formData.name,
      description: formData.description,
      status: formData.status,
      priority: formData.priority,
      owner: formData.owner || 'Current User',
      createdAt: new Date().toISOString().split('T')[0],
      lastModified: new Date().toISOString().split('T')[0],
      progress: 0
    };

    setProjects([...projects, newProject]);
    setIsCreateDialogOpen(false);
    setFormData({
      name: '',
      description: '',
      status: 'active',
      priority: 'medium',
      owner: ''
    });
    toast({
      title: "Project created",
      description: "New project has been successfully created.",
    });
  };

  const handleEdit = (project: Project) => {
    const updatedProjects = projects.map(p => 
      p.id === project.id 
        ? { ...project, lastModified: new Date().toISOString().split('T')[0] }
        : p
    );
    setProjects(updatedProjects);
    setEditingProject(null);
    toast({
      title: "Project updated",
      description: "Project has been successfully updated.",
    });
  };

  const handleDelete = (id: string) => {
    setProjects(projects.filter(p => p.id !== id));
    toast({
      title: "Project deleted",
      description: "Project has been successfully deleted.",
    });
  };

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

  const CardView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {projects.map(project => (
        <Card key={project.id} className="relative">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-lg">{project.name}</CardTitle>
                <div className="flex gap-2 mt-2">
                  <Badge className={getStatusColor(project.status)}>
                    {project.status}
                  </Badge>
                  <Badge variant={getPriorityColor(project.priority)}>
                    {project.priority}
                  </Badge>
                </div>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Actions</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to={`/projects/${project.id}`}>
                      <Eye className="mr-2 h-4 w-4" />
                      View Details
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setEditingProject(project)}>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => handleDelete(project.id)}
                    className="text-red-600"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </CardHeader>
          <CardContent>
            <CardDescription>{project.description}</CardDescription>
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Progress</span>
                <span>{project.progress}%</span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2">
                <div 
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{ width: `${project.progress}%` }}
                />
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <div className="flex justify-between w-full text-sm text-muted-foreground">
              <span>Owner: {project.owner}</span>
              <span>{project.lastModified}</span>
            </div>
          </CardFooter>
        </Card>
      ))}
    </div>
  );

  const ListView = () => (
    <div className="space-y-2">
      {projects.map(project => (
        <Card key={project.id}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div>
                  <CardTitle className="text-base">{project.name}</CardTitle>
                  <CardDescription className="text-sm mt-1">
                    {project.description}
                  </CardDescription>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex gap-2">
                  <Badge className={getStatusColor(project.status)}>
                    {project.status}
                  </Badge>
                  <Badge variant={getPriorityColor(project.priority)}>
                    {project.priority}
                  </Badge>
                </div>
                <div className="flex space-x-2">
                  <Button variant="ghost" size="sm" asChild>
                    <Link to={`/projects/${project.id}`}>
                      <Eye className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => setEditingProject(project)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => handleDelete(project.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
            <div className="flex items-center justify-between mt-3 text-sm text-muted-foreground">
              <span>Owner: {project.owner}</span>
              <span>Progress: {project.progress}%</span>
              <span>Modified: {project.lastModified}</span>
            </div>
          </CardHeader>
        </Card>
      ))}
    </div>
  );

  const TableView = () => (
    <Table>
      <TableCaption>A list of all projects in the system</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Priority</TableHead>
          <TableHead>Owner</TableHead>
          <TableHead>Progress</TableHead>
          <TableHead>Last Modified</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {projects.map(project => (
          <TableRow key={project.id}>
            <TableCell className="font-medium">
              <div>
                <div>{project.name}</div>
                <div className="text-sm text-muted-foreground">{project.description}</div>
              </div>
            </TableCell>
            <TableCell>
              <Badge className={getStatusColor(project.status)}>
                {project.status}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge variant={getPriorityColor(project.priority)}>
                {project.priority}
              </Badge>
            </TableCell>
            <TableCell>{project.owner}</TableCell>
            <TableCell>{project.progress}%</TableCell>
            <TableCell>{project.lastModified}</TableCell>
            <TableCell className="text-right">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Actions</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to={`/projects/${project.id}`}>
                      <Eye className="mr-2 h-4 w-4" />
                      View Details
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setEditingProject(project)}>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => handleDelete(project.id)}
                    className="text-red-600"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );

  return (
    <div className="flex flex-col min-h-screen">
      <div className="border-b">
        <div className="flex items-center justify-between px-4 py-2">
          <h1 className="text-lg font-semibold">Projects</h1>
          <div className="flex items-center gap-2">
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="default" size="sm">
                  <Plus className="mr-2 h-4 w-4" />
                  New Project
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>Create New Project</DialogTitle>
                  <DialogDescription>
                    Add a new project to your workspace.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="name" className="text-right">
                      Name
                    </Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="col-span-3"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="description" className="text-right">
                      Description
                    </Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="col-span-3"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="status" className="text-right">
                      Status
                    </Label>
                    <Select 
                      value={formData.status}
                      onValueChange={(value) => setFormData({...formData, status: value as Project['status']})}
                    >
                      <SelectTrigger className="col-span-3">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="priority" className="text-right">
                      Priority
                    </Label>
                    <Select 
                      value={formData.priority}
                      onValueChange={(value) => setFormData({...formData, priority: value as Project['priority']})}
                    >
                      <SelectTrigger className="col-span-3">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="owner" className="text-right">
                      Owner
                    </Label>
                    <Input
                      id="owner"
                      value={formData.owner}
                      onChange={(e) => setFormData({...formData, owner: e.target.value})}
                      className="col-span-3"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" onClick={handleCreate}>Create Project</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <Button variant="outline" size="sm" asChild>
              <Link to="/">
                <MessageSquare className="mr-2 h-4 w-4" />
                Back to Chat
              </Link>
            </Button>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-4">
        <div className="max-w-[1400px] mx-auto">
          <Tabs 
            defaultValue="card" 
            value={viewMode}
            onValueChange={(value) => setViewMode(value as typeof viewMode)}
            className="w-full"
          >
            <div className="flex justify-between items-center mb-4">
              <TabsList className="bg-gray-100 dark:bg-gray-800">
                <TabsTrigger 
                  value="card" 
                  className="transition-all data-[state=active]:bg-blue-500 data-[state=active]:text-white"
                >
                  <LayoutGrid className="mr-2 h-4 w-4" />
                  Card View
                </TabsTrigger>
                <TabsTrigger 
                  value="list" 
                  className="transition-all data-[state=active]:bg-blue-500 data-[state=active]:text-white"
                >
                  <List className="mr-2 h-4 w-4" />
                  List View
                </TabsTrigger>
                <TabsTrigger 
                  value="table" 
                  className="transition-all data-[state=active]:bg-blue-500 data-[state=active]:text-white"
                >
                  <TableIcon className="mr-2 h-4 w-4" />
                  Table View
                </TabsTrigger>
              </TabsList>
              <div className="text-sm text-muted-foreground">
                {projects.length} projects
              </div>
            </div>
            
            <TabsContent value="card" className="mt-4">
              <CardView />
            </TabsContent>
            
            <TabsContent value="list" className="mt-4">
              <ListView />
            </TabsContent>
            
            <TabsContent value="table" className="mt-4">
              <TableView />
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Edit Dialog */}
      {editingProject && (
        <Dialog open={!!editingProject} onOpenChange={() => setEditingProject(null)}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Edit Project</DialogTitle>
              <DialogDescription>
                Make changes to your project here.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-name" className="text-right">
                  Name
                </Label>
                <Input
                  id="edit-name"
                  value={editingProject.name}
                  onChange={(e) => setEditingProject({...editingProject, name: e.target.value})}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-description" className="text-right">
                  Description
                </Label>
                <Textarea
                  id="edit-description"
                  value={editingProject.description}
                  onChange={(e) => setEditingProject({...editingProject, description: e.target.value})}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-status" className="text-right">
                  Status
                </Label>
                <Select 
                  value={editingProject.status}
                  onValueChange={(value) => setEditingProject({...editingProject, status: value as Project['status']})}
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-priority" className="text-right">
                  Priority
                </Label>
                <Select 
                  value={editingProject.priority}
                  onValueChange={(value) => setEditingProject({...editingProject, priority: value as Project['priority']})}
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-owner" className="text-right">
                  Owner
                </Label>
                <Input
                  id="edit-owner"
                  value={editingProject.owner}
                  onChange={(e) => setEditingProject({...editingProject, owner: e.target.value})}
                  className="col-span-3"
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" onClick={() => handleEdit(editingProject)}>Save changes</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default Projects;