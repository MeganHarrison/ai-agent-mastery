"use server"

import { createClient } from "@/lib/supabase/server"
import { createServiceClient } from "@/utils/supabase/service"
import type { Database } from "@/types/database.types"
import { pickEditableCompanyFields, requireCompanyId } from "./companies-input"

export type Company = Database["public"]["Tables"]["companies"]["Row"]

async function getAdminCompaniesClient(): Promise<ReturnType<typeof createServiceClient>> {
  const authClient = await createClient()
  const { data: { user }, error: authError } = await authClient.auth.getUser()

  if (authError || !user) {
    throw new Error("Sign in to access company records.")
  }

  const { data: profile, error: profileError } = await authClient
    .from("user_profiles")
    .select("is_admin")
    .eq("id", user.id)
    .maybeSingle()

  if (profileError) {
    console.error("Unable to verify company administrator access:", profileError)
    throw new Error("Unable to verify administrator access.")
  }
  if (profile?.is_admin !== true) {
    throw new Error("Administrator access is required to manage company records.")
  }

  return createServiceClient()
}

export async function getCompanies(): Promise<{ companies: Company[]; error?: string }> {
  try {
    const supabase = await getAdminCompaniesClient()
    
    const { data, error } = await supabase
      .from('companies')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching companies:', error)
      return { 
        companies: [], 
        error: `Failed to fetch companies: ${error.message}` 
      }
    }

    return { companies: data || [] }
  } catch (error) {
    console.error('Unexpected error fetching companies:', error)
    return { 
      companies: [], 
      error: error instanceof Error ? error.message : "Unable to load companies.",
    }
  }
}

export async function createCompany(companyData: Partial<Company>): Promise<{ company?: Company; error?: string }> {
  try {
    const safeCompanyData = pickEditableCompanyFields(companyData) as Partial<Company>
    if (!safeCompanyData.name?.trim()) {
      return { error: "Company name is required." }
    }

    const supabase = await getAdminCompaniesClient()
    
    const { data, error } = await supabase
      .from('companies')
      .insert({ ...safeCompanyData, name: safeCompanyData.name.trim() })
      .select()
      .single()

    if (error) {
      console.error('Error creating company:', error)
      return { error: `Failed to create company: ${error.message}` }
    }

    return { company: data }
  } catch (error) {
    console.error('Unexpected error creating company:', error)
    return { error: error instanceof Error ? error.message : "Unable to create company." }
  }
}

export async function updateCompany(id: string, updates: Partial<Company>): Promise<{ company?: Company; error?: string }> {
  try {
    const companyId = requireCompanyId(id)
    const safeUpdates = pickEditableCompanyFields(updates) as Partial<Company>
    if (Object.keys(safeUpdates).length === 0) {
      return { error: "Provide at least one editable company field." }
    }
    if (safeUpdates.name !== undefined && !safeUpdates.name?.trim()) {
      return { error: "Company name cannot be blank." }
    }

    const supabase = await getAdminCompaniesClient()
    
    const { data, error } = await supabase
      .from('companies')
      .update({ ...safeUpdates, ...(safeUpdates.name ? { name: safeUpdates.name.trim() } : {}) })
      .eq('id', companyId)
      .select()
      .single()

    if (error) {
      console.error('Error updating company:', error)
      return { error: `Failed to update company: ${error.message}` }
    }

    return { company: data }
  } catch (error) {
    console.error('Unexpected error updating company:', error)
    return { error: error instanceof Error ? error.message : "Unable to update company." }
  }
}

export async function deleteCompany(id: string): Promise<{ success?: boolean; error?: string }> {
  try {
    const companyId = requireCompanyId(id)

    const supabase = await getAdminCompaniesClient()
    
    const { error } = await supabase
      .from('companies')
      .delete()
      .eq('id', companyId)

    if (error) {
      console.error('Error deleting company:', error)
      return { error: `Failed to delete company: ${error.message}` }
    }

    return { success: true }
  } catch (error) {
    console.error('Unexpected error deleting company:', error)
    return { error: error instanceof Error ? error.message : "Unable to delete company." }
  }
}
