'use client'

import { useEffect, useState } from 'react'
import { StandardizedTable, TableColumn } from "@/components/tables/standardized-table"
import { getContacts } from "@/app/actions/contacts-actions"
import { createClient } from "@/lib/supabase/client"
import { Database } from "@/types/database.types"

// Use the database types directly
type Contact = Database['public']['Tables']['contacts']['Row']

interface ContactWithCompany extends Contact {
  company?: {
    id: string
    name: string | null
  } | null
}

const columns: TableColumn<ContactWithCompany>[] = [
  {
    id: "first_name",
    label: "First Name",
    accessor: (item) => item.first_name,
    defaultVisible: true,
    sortable: true,
    renderCell: (value) => value || <span className="text-muted-foreground">-</span>
  },
  {
    id: "last_name",
    label: "Last Name",
    accessor: (item) => item.last_name,
    defaultVisible: true,
    sortable: true,
    renderCell: (value) => value || <span className="text-muted-foreground">-</span>
  },
  {
    id: "company",
    label: "Company",
    accessor: (item) => item.company?.name,
    defaultVisible: true,
    sortable: true,
    renderCell: (value) => value || <span className="text-muted-foreground">-</span>
  },
  {
    id: "role",
    label: "Role",
    accessor: (item) => item.role,
    defaultVisible: true,
    sortable: true,
    renderCell: (value) => value || <span className="text-muted-foreground">-</span>
  },
  {
    id: "email",
    label: "Email",
    accessor: (item) => item.email,
    defaultVisible: true,
    sortable: true,
    renderCell: (value) => value ? (
      <a href={`mailto:${value}`} className="text-blue-600 hover:underline">
        {value}
      </a>
    ) : <span className="text-muted-foreground">-</span>
  },
  {
    id: "phone",
    label: "Phone",
    accessor: (item) => item.phone,
    defaultVisible: true,
    sortable: true,
    renderCell: (value) => value ? (
      <a href={`tel:${value}`} className="text-blue-600 hover:underline">
        {value}
      </a>
    ) : <span className="text-muted-foreground">-</span>
  },
  {
    id: "notes",
    label: "Notes",
    accessor: (item) => item.notes,
    defaultVisible: true,
    sortable: false,
    renderCell: (value) => value ? (
      <span className="max-w-[200px] truncate" title={value}>
        {value}
      </span>
    ) : <span className="text-muted-foreground">-</span>
  }
]

export default function ContactsPage() {
  const [contacts, setContacts] = useState<ContactWithCompany[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadContacts()
  }, [])

  const loadContacts = async () => {
    setLoading(true)
    const data = await getContacts()
    setContacts(data)
    setLoading(false)
  }

  const handleAdd = async (data: Partial<ContactWithCompany>) => {
    const supabase = createClient()

    // Remove the company field as it's not a database column
    const { company, ...contactData } = data

    const { error } = await supabase
      .from("contacts")
      .insert([contactData])

    if (error) {
      throw new Error(error.message)
    }

    await loadContacts()
  }

  const handleUpdate = async (id: string | number, data: Partial<ContactWithCompany>) => {
    const supabase = createClient()

    // Remove the company field as it's not a database column
    const { company, ...contactData } = data

    const { error } = await supabase
      .from("contacts")
      .update(contactData)
      .eq("id", id)

    if (error) {
      throw new Error(error.message)
    }

    await loadContacts()
  }

  const handleDelete = async (id: string | number) => {
    const supabase = createClient()

    const { error } = await supabase
      .from("contacts")
      .delete()
      .eq("id", id)

    if (error) {
      throw new Error(error.message)
    }

    await loadContacts()
  }

  if (loading) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading contacts...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6">
      <StandardizedTable
        data={contacts}
        columns={columns}
        tableName="Contact"
        primaryKey="id"
        onAdd={handleAdd}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
        onRefresh={loadContacts}
        searchableFields={["first_name", "last_name", "email", "phone", "role", "notes"]}
        emptyMessage="No contacts found. Add your first contact to get started."
      />
    </div>
  )
}