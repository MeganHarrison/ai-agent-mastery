import assert from "node:assert/strict"
import test from "node:test"
// Node's built-in TypeScript stripper requires explicit extensions for local imports.
// @ts-expect-error TypeScript project config does not enable import extensions.
import { pickEditableCompanyFields, requireCompanyId } from "../src/app/actions/companies-input.ts"

test("company input accepts editable fields and drops protected columns", () => {
  assert.deepEqual(
    pickEditableCompanyFields({ name: "Acme", status: "active", id: "forged", tax_id: "secret", is_admin: true }),
    { name: "Acme", status: "active" },
  )
})

test("company input rejects non-object and non-text field values", () => {
  assert.throws(() => pickEditableCompanyFields(null), /must be an object/)
  assert.throws(() => pickEditableCompanyFields({ name: 12 }), /must be text or null/)
})

test("company IDs must be UUIDs before reaching a write query", () => {
  assert.equal(requireCompanyId("  62f3a2af-6c6e-4cd4-aeb0-7f0b7d30991f  "), "62f3a2af-6c6e-4cd4-aeb0-7f0b7d30991f")
  assert.throws(() => requireCompanyId(""), /valid company ID/)
  assert.throws(() => requireCompanyId("not-a-uuid"), /valid company ID/)
})
