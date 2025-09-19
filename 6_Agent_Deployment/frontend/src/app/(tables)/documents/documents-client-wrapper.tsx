"use client"

import { useEffect } from "react"
import { EditableDocumentsTable } from "@/components/tables/editable-documents-table";
import { AddDocumentButton } from "@/components/table-buttons/add-document-button";
import { useActionButton } from "../layout";

interface DocumentsClientWrapperProps {
  documents: any[]
  error?: string
}

export function DocumentsClientWrapper({ documents, error }: DocumentsClientWrapperProps) {
  const { setActionButton } = useActionButton()

  useEffect(() => {
    setActionButton(<AddDocumentButton />)
    
    // Cleanup when component unmounts
    return () => setActionButton(null)
  }, [setActionButton])

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-800 rounded-lg border border-red-200">
        <h3 className="font-medium">Error loading documents</h3>
        <p className="text-sm mt-1">{error}</p>
        <p className="text-sm mt-2">
          Make sure the documents table exists in your Supabase database.
        </p>
      </div>
    )
  }

  return <EditableDocumentsTable documents={documents} />
}