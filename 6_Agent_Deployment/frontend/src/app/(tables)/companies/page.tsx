'use client'

import { useEffect, useState } from 'react'
import { StandardizedTable, type TableColumn } from "@/components/tables/standardized-table"
import {
  createCompany,
  deleteCompany,
  getCompanies,
  type Company,
  updateCompany,
} from "@/app/actions/companies-actions"
import { Badge } from "@/components/ui/badge"

const editableCompanyFields = [
  "name",
  "title",
  "type",
  "address",
  "city",
  "state",
  "website",
  "status",
  "contact_name",
  "contact_email",
  "contact_phone",
  "notes",
] as const satisfies readonly (keyof Company)[]

function pickEditableCompanyFields(data: Partial<Company>): Partial<Company> {
  return Object.fromEntries(
    editableCompanyFields
      .filter((field) => data[field] !== undefined)
      .map((field) => [field, data[field]])
  )
}

function websiteHref(value: string): string | null {
  try {
    const normalized = new URL(value.includes("://") ? value : `https://${value}`)
    return normalized.protocol === "http:" || normalized.protocol === "https:"
      ? normalized.href
      : null
  } catch {
    return null
  }
}

const columns: TableColumn<Company>[] = [
  {
    id: "name",
    label: "Company Name",
    accessor: (item) => item.name,
    defaultVisible: true,
    sortable: true,
  },
  {
    id: "title",
    label: "Title",
    accessor: (item) => item.title,
    defaultVisible: true,
    sortable: true,
  },
  {
    id: "type",
    label: "Type",
    accessor: (item) => item.type,
    defaultVisible: true,
    sortable: true,
    filterable: true,
    renderCell: (value) => value ? (
      <Badge variant="secondary">{value}</Badge>
    ) : <span className="text-muted-foreground">-</span>
  },
  {
    id: "city",
    label: "City",
    accessor: (item) => item.city,
    defaultVisible: true,
    sortable: true,
  },
  {
    id: "state",
    label: "State",
    accessor: (item) => item.state,
    defaultVisible: true,
    sortable: true,
  },
  {
    id: "address",
    label: "Address",
    accessor: (item) => item.address,
    defaultVisible: false,
  },
  {
    id: "contact_name",
    label: "Contact",
    accessor: (item) => item.contact_name,
    defaultVisible: false,
  },
  {
    id: "contact_email",
    label: "Email",
    accessor: (item) => item.contact_email,
    defaultVisible: true,
    renderCell: (value) => value ? (
      <a href={`mailto:${value}`} className="text-blue-600 hover:underline">
        {value}
      </a>
    ) : <span className="text-muted-foreground">-</span>
  },
  {
    id: "contact_phone",
    label: "Phone",
    accessor: (item) => item.contact_phone,
    defaultVisible: false,
    renderCell: (value) => value ? (
      <a href={`tel:${value}`} className="text-blue-600 hover:underline">
        {value}
      </a>
    ) : <span className="text-muted-foreground">-</span>
  },
  {
    id: "website",
    label: "Website",
    accessor: (item) => item.website,
    defaultVisible: true,
    renderCell: (value) => {
      if (typeof value !== "string" || !value) return <span className="text-muted-foreground">-</span>
      const href = websiteHref(value)
      return href ? (
        <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
          {new URL(href).hostname}
        </a>
      ) : <span>{value}</span>
    }
  },
  {
    id: "status",
    label: "Status",
    accessor: (item) => item.status,
    defaultVisible: true,
    sortable: true,
    filterable: true,
    renderCell: (value) => {
      const variant = value === "active" ? "default" :
                      value === "inactive" ? "secondary" :
                      value === "prospect" ? "outline" : "secondary"
      return value ? (
        <Badge variant={variant}>{value}</Badge>
      ) : <span className="text-muted-foreground">-</span>
    }
  },
  {
    id: "notes",
    label: "Notes",
    accessor: (item) => item.notes,
    defaultVisible: false,
    renderCell: (value) => value ? (
      <span className="line-clamp-2 max-w-xs">{value}</span>
    ) : <span className="text-muted-foreground">-</span>
  },
]

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    void loadCompanies()
  }, [])

  const loadCompanies = async () => {
    setLoading(true)
    try {
      const { companies: data, error } = await getCompanies()
      if (error) {
        setLoadError(error)
        setCompanies([])
        return
      }
      setLoadError(null)
      setCompanies(data)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : "Unable to load companies.")
      setCompanies([])
    } finally {
      setLoading(false)
    }
  }

  // Get unique values for filter options
  const types = Array.from(new Set(companies.map(c => c.type).filter(Boolean)))
  const statuses = Array.from(new Set(companies.map(c => c.status).filter(Boolean)))

  const handleAdd = async (data: Partial<Company>) => {
    const companyData = pickEditableCompanyFields(data)
    if (!companyData.name?.trim()) {
      throw new Error("Company name is required.")
    }
    const { error } = await createCompany({ ...companyData, name: companyData.name.trim() })
    if (error) throw new Error(error)

    await loadCompanies()
  }

  const handleUpdate = async (id: string | number, data: Partial<Company>) => {
    const companyData = pickEditableCompanyFields(data)
    if (typeof id !== "string") throw new Error("Invalid company ID.")
    const { error } = await updateCompany(id, companyData)
    if (error) throw new Error(error)

    await loadCompanies()
  }

  const handleDelete = async (id: string | number) => {
    if (typeof id !== "string") throw new Error("Invalid company ID.")
    const { error } = await deleteCompany(id)
    if (error) throw new Error(error)

    await loadCompanies()
  }

  if (loading) {
    return (
      <div>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading companies...</div>
        </div>
      </div>
    )
  }

  if (loadError) {
    return <div role="alert" className="p-4 text-destructive">{loadError}</div>
  }

  return (
    <div>
      <StandardizedTable
        data={companies}
        columns={columns}
        tableName="Company"
        primaryKey="id"
        onAdd={handleAdd}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
        onRefresh={loadCompanies}
        searchableFields={["name", "title", "type", "city", "state", "address", "contact_name", "contact_email", "contact_phone", "notes"]}
        filterOptions={[
          {
            field: "type",
            label: "Type",
            options: types.map(t => ({ value: t!, label: t! }))
          },
          {
            field: "status",
            label: "Status",
            options: statuses.map(s => ({ value: s!, label: s! }))
          }
        ]}
        emptyMessage="No companies found. Add your first company to get started."
      />
    </div>
  )
}
