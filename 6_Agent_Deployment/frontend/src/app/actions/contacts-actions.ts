"use server"

import { createClient } from "@/utils/supabase/server"
import { Database } from "@/types/database.types"

// Import the database types directly for type safety
type Contact = Database['public']['Tables']['contacts']['Row']

interface Company {
  id: string
  name: string | null
}

type ContactWithLegacyCompany = Contact & {
  company_id?: string | null
}

interface ContactWithCompany extends Contact {
  company_id?: string | null
  company?: Company | null
}

export async function getContacts(): Promise<ContactWithCompany[]> {
  const supabase = await createClient()

  const { data, error } = await supabase
    .from("contacts")
    .select("*")
    .order("created_at", { ascending: false })

  if (error) {
    throw new Error(`Failed to fetch contacts: ${error.message}`)
  }

  // `company_id` exists on legacy contacts rows and is deliberately preserved
  // by the schema migration. Some already-migrated projects omit it.
  const contacts = (data ?? []) as ContactWithLegacyCompany[]
  const companyIds = [...new Set(
    contacts
      .map((contact) => contact.company_id)
      .filter((companyId): companyId is string => Boolean(companyId))
  )]

  if (companyIds.length === 0) {
    return contacts.map((contact) => ({ ...contact, company: null }))
  }

  const { data: companies, error: companiesError } = await supabase
    .from("companies")
    .select("id, name")
    .in("id", companyIds)

  if (companiesError) {
    throw new Error(`Failed to fetch contact companies: ${companiesError.message}`)
  }

  const companiesById = new Map<string, Company>(
    (companies ?? []).map((company) => [company.id, company] as const)
  )

  const unresolvedCompanyLinks = companyIds.filter((companyId) => !companiesById.has(companyId))
  if (unresolvedCompanyLinks.length > 0) {
    throw new Error(`Failed to resolve ${unresolvedCompanyLinks.length} contact company link(s).`)
  }

  return contacts.map((contact) => ({
    ...contact,
    company: contact.company_id ? companiesById.get(contact.company_id) ?? null : null,
  }))
}

export async function getContactById(id: string): Promise<Contact | null> {
  const supabase = await createClient()

  const { data, error } = await supabase
    .from("contacts")
    .select("*")
    .eq("id", parseInt(id))
    .single()

  if (error) {
    console.error("Error fetching contact:", error)
    return null
  }

  return data
}

// Get contacts that are employees (have roles)
export async function getEmployees(): Promise<Contact[]> {
  const supabase = await createClient()

  const { data, error } = await supabase
    .from("contacts")
    .select("*")
    .not("role", "is", null)
    .order("created_at", { ascending: false })

  if (error) {
    console.error("Error fetching employees:", error)
    return []
  }

  return data || []
}
