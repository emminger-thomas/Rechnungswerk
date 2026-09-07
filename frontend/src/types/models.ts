export type TaxScenario = "STANDARD" | "REDUCED" | "SMALL_BUSINESS" | "REVERSE_CHARGE"

export const TAX_SCENARIO_LABELS: Record<TaxScenario, string> = {
  STANDARD: "Standard (19%)",
  REDUCED: "Ermäßigt (7%)",
  SMALL_BUSINESS: "Kleinunternehmer (§19 UStG)",
  REVERSE_CHARGE: "Bauleistung (§13b UStG)",
}

export const TAX_SCENARIO_LEGAL_NOTICE: Record<TaxScenario, string | null> = {
  STANDARD: null,
  REDUCED: null,
  SMALL_BUSINESS: "Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.",
  REVERSE_CHARGE:
    "Steuerschuldnerschaft des Leistungsempfängers (Reverse Charge / § 13b UStG).",
}

export const UNIT_OPTIONS = ["Std.", "Stk.", "m²", "m", "kg", "Tag", "Pauschal"] as const
export type UnitLabel = (typeof UNIT_OPTIONS)[number]

export type InvoiceStatus = "DRAFT" | "ISSUED" | "PAID" | "OVERDUE" | "CANCELLED"
export type DocumentType = "INVOICE" | "STORNO"

export interface Customer {
  id: string
  name: string
  contact_person: string
  street: string
  zip_code: string
  city: string
  country: string
  vat_id: string
  leitweg_id: string
  email: string
  phone: string
  notes: string
  created_at: string
  updated_at: string
}

export type CustomerInput = Omit<Customer, "id" | "created_at" | "updated_at">

export interface CustomerLookup {
  id: string
  name: string
  city: string
  vat_id: string
  leitweg_id: string
}

export interface InvoiceItem {
  id?: string
  position_index: number
  description: string
  quantity: string
  unit_label: string
  unit_code?: string
  unit_price: string
  tax_scenario: TaxScenario
  tax_rate?: string
  tax_category_code?: string
  line_total?: string
}

export interface Invoice {
  id: string
  customer: string
  customer_detail?: CustomerLookup
  invoice_number: string | null
  document_type: DocumentType
  cancels_invoice: string | null
  status: InvoiceStatus
  is_locked: boolean
  issue_date: string | null
  delivery_date: string
  due_date: string | null
  notes: string
  total_net: string
  total_tax: string
  total_gross: string
  sha256_hash: string
  created_at: string
  updated_at: string
  items: InvoiceItem[]
}

export type InvoiceDraftInput = Pick<Invoice, "customer" | "delivery_date" | "due_date" | "notes"> & {
  items: InvoiceItem[]
}
