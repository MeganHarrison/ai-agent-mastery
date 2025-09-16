import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/lib/supabase";
import { DocumentMetadata } from "@/types/database.types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, ExternalLink, Edit2, Save, X, Calendar, Folder, Users, FileText } from "lucide-react";
import { format } from "date-fns";
import { toast } from "@/components/ui/use-toast";

const Documents = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState<DocumentMetadata | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editedDoc, setEditedDoc] = useState<Partial<DocumentMetadata>>({});

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('document_metadata')
        .select('*')
        .not('type', 'in', '("SOPs","documents")')
        .order('date', { ascending: false });

      if (error) throw error;
      setDocuments(data || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast({
        title: "Error",
        description: "Failed to fetch documents",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (doc: DocumentMetadata) => {
    setEditingId(doc.id);
    setEditedDoc({
      title: doc.title,
      project: doc.project,
      date: doc.date,
      summary: doc.summary,
      fireflies_link: doc.fireflies_link,
    });
  };

  const handleSave = async () => {
    if (!editingId) return;

    try {
      const { error } = await supabase
        .from('document_metadata')
        .update(editedDoc)
        .eq('id', editingId);

      if (error) throw error;

      setDocuments(docs =>
        docs.map(doc =>
          doc.id === editingId ? { ...doc, ...editedDoc } : doc
        )
      );
      
      if (selectedDocument?.id === editingId) {
        setSelectedDocument({ ...selectedDocument, ...editedDoc });
      }

      toast({
        title: "Success",
        description: "Document updated successfully",
      });

      setEditingId(null);
      setEditedDoc({});
    } catch (error) {
      console.error('Error updating document:', error);
      toast({
        title: "Error",
        description: "Failed to update document",
        variant: "destructive",
      });
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditedDoc({});
  };

  const handleRowClick = (doc: DocumentMetadata) => {
    if (editingId !== doc.id) {
      setSelectedDocument(doc);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    try {
      return format(new Date(dateStr), 'MMM dd, yyyy');
    } catch {
      return dateStr;
    }
  };

  const renderTableView = () => (
    <Card className="bg-card/50 backdrop-blur border-border/50">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Meeting Documents
          </CardTitle>
          <Badge variant="secondary" className="ml-2">
            {documents.length} documents
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-lg border border-border/50 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-border/50">
                <TableHead className="font-semibold">Title</TableHead>
                <TableHead className="font-semibold">Project</TableHead>
                <TableHead className="font-semibold">Date</TableHead>
                <TableHead className="font-semibold">Summary</TableHead>
                <TableHead className="font-semibold text-center">Meeting Link</TableHead>
                <TableHead className="font-semibold text-center">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {documents.map((doc) => (
                <TableRow
                  key={doc.id}
                  className="cursor-pointer hover:bg-muted/50 transition-colors border-border/50"
                  onClick={() => handleRowClick(doc)}
                >
                  <TableCell className="font-medium">
                    {editingId === doc.id ? (
                      <Input
                        value={editedDoc.title || ''}
                        onChange={(e) => setEditedDoc({ ...editedDoc, title: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        className="h-8"
                      />
                    ) : (
                      <span className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        {doc.title || 'Untitled'}
                      </span>
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === doc.id ? (
                      <Input
                        value={editedDoc.project || ''}
                        onChange={(e) => setEditedDoc({ ...editedDoc, project: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        className="h-8"
                      />
                    ) : (
                      <span className="flex items-center gap-2">
                        <Folder className="h-4 w-4 text-muted-foreground" />
                        {doc.project || 'N/A'}
                      </span>
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === doc.id ? (
                      <Input
                        type="date"
                        value={editedDoc.date || ''}
                        onChange={(e) => setEditedDoc({ ...editedDoc, date: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        className="h-8"
                      />
                    ) : (
                      <span className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        {formatDate(doc.date)}
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="max-w-xs">
                    {editingId === doc.id ? (
                      <Input
                        value={editedDoc.summary || ''}
                        onChange={(e) => setEditedDoc({ ...editedDoc, summary: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        className="h-8"
                      />
                    ) : (
                      <span className="truncate block">{doc.summary || 'No summary available'}</span>
                    )}
                  </TableCell>
                  <TableCell className="text-center">
                    {editingId === doc.id ? (
                      <Input
                        value={editedDoc.fireflies_link || ''}
                        onChange={(e) => setEditedDoc({ ...editedDoc, fireflies_link: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        className="h-8"
                      />
                    ) : doc.fireflies_link ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(doc.fireflies_link, '_blank');
                        }}
                        className="hover:bg-primary/10"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-center">
                    {editingId === doc.id ? (
                      <div className="flex gap-1 justify-center" onClick={(e) => e.stopPropagation()}>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleSave}
                          className="hover:bg-green-500/10"
                        >
                          <Save className="h-4 w-4 text-green-600" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleCancel}
                          className="hover:bg-red-500/10"
                        >
                          <X className="h-4 w-4 text-red-600" />
                        </Button>
                      </div>
                    ) : (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(doc);
                        }}
                        className="hover:bg-primary/10"
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );

  const renderDetailView = () => {
    if (!selectedDocument) return null;

    return (
      <Card className="h-full bg-card/50 backdrop-blur border-border/50">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedDocument(null)}
                className="hover:bg-muted/50"
              >
                <X className="h-4 w-4" />
              </Button>
              <CardTitle className="text-xl font-bold">
                {selectedDocument.title || 'Untitled Document'}
              </CardTitle>
            </div>
            {selectedDocument.fireflies_link && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open(selectedDocument.fireflies_link!, '_blank')}
                className="hover:bg-primary/10"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View Meeting
              </Button>
            )}
          </div>
        </CardHeader>
        <Separator className="mx-6 w-auto" />
        <CardContent className="pt-6">
          <ScrollArea className="h-[calc(100vh-250px)]">
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Folder className="h-4 w-4" />
                    <span>Project</span>
                  </div>
                  <p className="font-medium">{selectedDocument.project || 'Not specified'}</p>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    <span>Date</span>
                  </div>
                  <p className="font-medium">{formatDate(selectedDocument.date)}</p>
                </div>
              </div>

              {selectedDocument.speakers && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Users className="h-4 w-4" />
                    <span>Speakers</span>
                  </div>
                  <p className="font-medium">{selectedDocument.speakers}</p>
                </div>
              )}

              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-muted-foreground">Summary</h3>
                <Card className="p-4 bg-muted/30">
                  <p className="text-sm leading-relaxed">
                    {selectedDocument.summary || 'No summary available for this document.'}
                  </p>
                </Card>
              </div>

              {selectedDocument.transcript && (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold text-muted-foreground">Transcript</h3>
                  <Card className="p-4 bg-muted/30">
                    <ScrollArea className="h-96">
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">
                        {selectedDocument.transcript}
                      </p>
                    </ScrollArea>
                  </Card>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-pulse">Loading documents...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="hover:bg-muted/50"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Chat
          </Button>
        </div>

        {selectedDocument ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="lg:col-span-1">
              {renderTableView()}
            </div>
            <div className="lg:col-span-1">
              {renderDetailView()}
            </div>
          </div>
        ) : (
          renderTableView()
        )}
      </div>
    </div>
  );
};

export default Documents;