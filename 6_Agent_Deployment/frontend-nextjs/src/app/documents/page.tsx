'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { DocumentMetadata } from '../../../database-types'
import { format } from 'date-fns'
import { 
  FileText, 
  Folder, 
  Calendar, 
  Edit2, 
  Save, 
  X, 
  ExternalLink,
  ArrowLeft,
  Video,
  User
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from '@/hooks/use-toast'
import Link from 'next/link'

// Input sanitization utility
const sanitizeInput = (value: string): string => {
  // Remove potential script tags and dangerous HTML
  return value
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/<iframe[^>]*>.*?<\/iframe>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .trim();
};

// Validation utility for URL
const isValidUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch {
    return false;
  }
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editedDoc, setEditedDoc] = useState<Partial<DocumentMetadata>>({})
  const [selectedDoc, setSelectedDoc] = useState<DocumentMetadata | null>(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const { data, error } = await supabase
        .from('document_metadata')
        .select('*')
        .or('type.is.null,type.not.in.("SOPs","documents")')
        .order('date', { ascending: false })

      if (error) throw error
      setDocuments(data || [])
    } catch (error) {
      console.error('Error fetching documents:', error)
      toast({
        title: 'Error',
        description: 'Failed to load documents',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (doc: DocumentMetadata) => {
    setEditingId(doc.id)
    setEditedDoc(doc)
  }

  const handleSave = async () => {
    try {
      if (!editingId) {
        toast({
          title: 'Error',
          description: 'No document selected for editing',
          variant: 'destructive',
        })
        return
      }

      // Validate and sanitize inputs
      const sanitizedDoc: Partial<DocumentMetadata> = {}
      
      // Sanitize text fields
      if (editedDoc.title !== undefined) {
        sanitizedDoc.title = sanitizeInput(editedDoc.title)
        if (sanitizedDoc.title.length < 1 || sanitizedDoc.title.length > 500) {
          throw new Error('Title must be between 1 and 500 characters')
        }
      }
      
      if (editedDoc.project !== undefined) {
        sanitizedDoc.project = sanitizeInput(editedDoc.project || '')
        if (sanitizedDoc.project.length > 200) {
          throw new Error('Project name must be less than 200 characters')
        }
      }
      
      if (editedDoc.summary !== undefined) {
        sanitizedDoc.summary = sanitizeInput(editedDoc.summary || '')
        if (sanitizedDoc.summary.length > 5000) {
          throw new Error('Summary must be less than 5000 characters')
        }
      }
      
      // Validate URL field
      if (editedDoc.fireflies_link !== undefined) {
        const link = editedDoc.fireflies_link || ''
        if (link && !isValidUrl(link)) {
          throw new Error('Recording link must be a valid URL')
        }
        sanitizedDoc.fireflies_link = link
      }
      
      // Validate date field
      if (editedDoc.date !== undefined) {
        sanitizedDoc.date = sanitizeInput(editedDoc.date || '')
        // Simple date format validation (YYYY-MM-DD)
        if (sanitizedDoc.date && !/^\d{4}-\d{2}-\d{2}/.test(sanitizedDoc.date)) {
          throw new Error('Date must be in valid format')
        }
      }

      const { error } = await supabase
        .from('document_metadata')
        .update(sanitizedDoc)
        .eq('id', editingId)

      if (error) throw error

      setDocuments(documents.map(doc => 
        doc.id === editingId ? { ...doc, ...sanitizedDoc } : doc
      ))
      
      if (selectedDoc?.id === editingId) {
        setSelectedDoc({ ...selectedDoc, ...sanitizedDoc })
      }

      setEditingId(null)
      setEditedDoc({})
      
      toast({
        title: 'Success',
        description: 'Document updated successfully',
      })
    } catch (error) {
      console.error('Error updating document:', error)
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to update document',
        variant: 'destructive',
      })
    }
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditedDoc({})
  }

  const handleRowClick = (doc: DocumentMetadata) => {
    if (editingId !== doc.id) {
      setSelectedDoc(doc)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    try {
      return format(new Date(dateString), 'MMM dd, yyyy')
    } catch {
      return dateString
    }
  }

  const truncateSummary = (summary?: string, maxLength = 100) => {
    if (!summary) return 'No summary available'
    if (summary.length <= maxLength) return summary
    return summary.substring(0, maxLength) + '...'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading documents...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            Documents
          </h1>
          <Link href="/">
            <Button variant="outline" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Home
            </Button>
          </Link>
        </div>

        {/* Main Content */}
        <div className={`flex gap-6 ${selectedDoc ? 'flex-row' : ''}`}>
          {/* Table View */}
          <div className={`${selectedDoc ? 'w-1/2' : 'w-full'} transition-all duration-300`}>
            <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-white">
                  <thead className="bg-gray-800/80 border-b border-gray-700">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Title</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Project</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Date</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Summary</th>
                      <th className="px-6 py-4 text-center text-sm font-semibold text-gray-300">Recording</th>
                      <th className="px-6 py-4 text-center text-sm font-semibold text-gray-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {documents.map((doc) => (
                      <tr
                        key={doc.id}
                        className={`hover:bg-gray-700/50 cursor-pointer transition-colors ${
                          selectedDoc?.id === doc.id ? 'bg-purple-900/20' : ''
                        }`}
                        onClick={() => handleRowClick(doc)}
                      >
                        <td className="px-6 py-4">
                          {editingId === doc.id ? (
                            <Input
                              type="text"
                              value={editedDoc.title || ''}
                              onChange={(e) => setEditedDoc({ ...editedDoc, title: e.target.value })}
                              onClick={(e) => e.stopPropagation()}
                              className="bg-gray-700 border-gray-600 text-white"
                              maxLength={500}
                              required
                              placeholder="Document title"
                            />
                          ) : (
                            <div className="flex items-center gap-2">
                              <FileText className="h-4 w-4 text-purple-400" />
                              <span className="text-sm">{doc.title}</span>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {editingId === doc.id ? (
                            <Input
                              type="text"
                              value={editedDoc.project || ''}
                              onChange={(e) => setEditedDoc({ ...editedDoc, project: e.target.value })}
                              onClick={(e) => e.stopPropagation()}
                              className="bg-gray-700 border-gray-600 text-white"
                              maxLength={200}
                              placeholder="Project name"
                            />
                          ) : (
                            <div className="flex items-center gap-2">
                              <Folder className="h-4 w-4 text-blue-400" />
                              <span className="text-sm">{doc.project || 'N/A'}</span>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {editingId === doc.id ? (
                            <Input
                              type="date"
                              value={editedDoc.date || ''}
                              onChange={(e) => setEditedDoc({ ...editedDoc, date: e.target.value })}
                              onClick={(e) => e.stopPropagation()}
                              className="bg-gray-700 border-gray-600 text-white"
                              placeholder="YYYY-MM-DD"
                            />
                          ) : (
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4 text-green-400" />
                              <span className="text-sm">{formatDate(doc.date)}</span>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {editingId === doc.id ? (
                            <Input
                              type="text"
                              value={editedDoc.summary || ''}
                              onChange={(e) => setEditedDoc({ ...editedDoc, summary: e.target.value })}
                              onClick={(e) => e.stopPropagation()}
                              className="bg-gray-700 border-gray-600 text-white"
                              maxLength={5000}
                              placeholder="Brief summary"
                            />
                          ) : (
                            <span className="text-sm text-gray-300">
                              {truncateSummary(doc.summary)}
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-center">
                          {editingId === doc.id ? (
                            <Input
                              type="url"
                              value={editedDoc.fireflies_link || ''}
                              onChange={(e) => setEditedDoc({ ...editedDoc, fireflies_link: e.target.value })}
                              onClick={(e) => e.stopPropagation()}
                              className="bg-gray-700 border-gray-600 text-white"
                              placeholder="https://..."
                              pattern="https?://.*"
                            />
                          ) : (
                            doc.fireflies_link && (
                              <a
                                href={doc.fireflies_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="inline-flex items-center justify-center text-purple-400 hover:text-purple-300 transition-colors"
                              >
                                <Video className="h-5 w-5" />
                              </a>
                            )
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center justify-center gap-2">
                            {editingId === doc.id ? (
                              <>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleSave()
                                  }}
                                  className="text-green-400 hover:text-green-300"
                                >
                                  <Save className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleCancel()
                                  }}
                                  className="text-red-400 hover:text-red-300"
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              </>
                            ) : (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleEdit(doc)
                                }}
                                className="text-blue-400 hover:text-blue-300"
                              >
                                <Edit2 className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Detail View */}
          {selectedDoc && (
            <div className="w-1/2 bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 p-6 overflow-y-auto max-h-[calc(100vh-200px)]">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-white">{selectedDoc.title}</h2>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setSelectedDoc(null)}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <div className="space-y-4">
                {/* Metadata */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-semibold text-gray-400">Project</label>
                    <p className="text-white flex items-center gap-2 mt-1">
                      <Folder className="h-4 w-4 text-blue-400" />
                      {selectedDoc.project || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-semibold text-gray-400">Date</label>
                    <p className="text-white flex items-center gap-2 mt-1">
                      <Calendar className="h-4 w-4 text-green-400" />
                      {formatDate(selectedDoc.date)}
                    </p>
                  </div>
                </div>

                {/* Speakers */}
                {selectedDoc.speakers && selectedDoc.speakers.length > 0 && (
                  <div>
                    <label className="text-sm font-semibold text-gray-400 mb-2 block">Speakers</label>
                    <div className="flex flex-wrap gap-2">
                      {selectedDoc.speakers.map((speaker, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-gray-700 rounded-full text-sm text-white flex items-center gap-1"
                        >
                          <User className="h-3 w-3" />
                          {speaker}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Summary */}
                <div>
                  <label className="text-sm font-semibold text-gray-400 mb-2 block">Summary</label>
                  <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-lg p-4">
                    <p className="text-gray-200 leading-relaxed">
                      {selectedDoc.summary || 'No summary available'}
                    </p>
                  </div>
                </div>

                {/* Fireflies Link */}
                {selectedDoc.fireflies_link && (
                  <div>
                    <a
                      href={selectedDoc.fireflies_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                    >
                      <Video className="h-4 w-4" />
                      View Recording
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                )}

                {/* Transcript */}
                {selectedDoc.transcript && (
                  <div>
                    <label className="text-sm font-semibold text-gray-400 mb-2 block">Transcript</label>
                    <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-4 max-h-96 overflow-y-auto">
                      <pre className="text-gray-200 text-sm whitespace-pre-wrap font-mono">
                        {selectedDoc.transcript}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Empty State */}
        {documents.length === 0 && (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No documents found</p>
            <p className="text-gray-500 text-sm mt-2">
              Documents will appear here once they are added to the system
            </p>
          </div>
        )}
      </div>
    </div>
  )
}