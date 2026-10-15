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
] as const

export function pickEditableCompanyFields(input: unknown): Record<string, string | null> {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new Error("Company data must be an object.")
  }

  const source = input as Record<string, unknown>
  const values: Record<string, string | null> = {}

  for (const field of editableCompanyFields) {
    const value = source[field]
    if (value === undefined) continue
    if (value !== null && typeof value !== "string") {
      throw new Error(`Company field '${field}' must be text or null.`)
    }
    values[field] = value
  }

  return values
}

export function requireCompanyId(input: unknown): string {
  if (typeof input !== "string" || !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(input.trim())) {
    throw new Error("A valid company ID is required.")
  }

  return input.trim()
}
