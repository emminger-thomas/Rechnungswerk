import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { ApiError } from "../../api/client"
import {
  useCreateInvoice,
  useFinalizeInvoice,
  useUpdateInvoice,
  downloadInvoicePdf,
  previewInvoicePdf,
} from "../../api/invoices"
import type { CustomerLookup, Invoice, InvoiceItem } from "../../types/models"
import { CustomerSearch } from "../customer/CustomerSearch"
import { LegalNotices } from "./LegalNotices"
import { LineItemGrid } from "./LineItemGrid"

function computeTotals(items: InvoiceItem[]) {
  let net = 0
  let tax = 0
  for (const item of items) {
    const quantity = parseFloat(item.quantity.replace(",", "."))
    const price = parseFloat(item.unit_price.replace(",", "."))
    const rateMap: Record<string, number> = {
      STANDARD: 19,
      REDUCED: 7,
      SMALL_BUSINESS: 0,
      REVERSE_CHARGE: 0,
    }
    if (Number.isNaN(quantity) || Number.isNaN(price)) continue
    const lineNet = quantity * price
    net += lineNet
    tax += (lineNet * rateMap[item.tax_scenario]) / 100
  }
  return { net, tax, gross: net + tax }
}

export function InvoiceForm({ invoice }: { invoice?: Invoice }) {
  const navigate = useNavigate()
  const [customer, setCustomer] = useState<CustomerLookup | null>(
    invoice?.customer_detail ?? null,
  )
  const [items, setItems] = useState<InvoiceItem[]>(invoice?.items ?? [])
  const [invoiceId, setInvoiceId] = useState<string | undefined>(invoice?.id)
  const [errors, setErrors] = useState<string[]>([])
  const [pdfReady, setPdfReady] = useState<Invoice | null>(null)

  const createInvoice = useCreateInvoice()
  const updateInvoice = useUpdateInvoice()
  const finalizeInvoice = useFinalizeInvoice()

  const isLocked = invoice?.is_locked ?? false
  const totals = computeTotals(items)

  // Autosave draft ~800ms after the last edit, once a customer is selected.
  useEffect(() => {
    if (!customer || isLocked) return
    const timeout = setTimeout(() => {
      const payload = {
        customer: customer.id,
        items: items.filter((item) => item.description.trim() || item.quantity.trim()),
      }
      if (invoiceId) {
        updateInvoice.mutate({ id: invoiceId, data: payload })
      } else if (payload.items.length > 0) {
        createInvoice.mutate(payload, {
          onSuccess: (created) => setInvoiceId(created.id),
        })
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, 800)
    return () => clearTimeout(timeout)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [customer, items])

  async function handleFinalize() {
    if (!invoiceId) return
    setErrors([])
    try {
      const result = await finalizeInvoice.mutateAsync(invoiceId)
      if ("errors" in result) {
        setErrors(result.errors)
        return
      }
      setPdfReady(result)
      await previewInvoicePdf(result.id)
      navigate(`/rechnungen/${result.id}`, { replace: true })
    } catch (err) {
      if (err instanceof ApiError && err.body && typeof err.body === "object" && "errors" in err.body) {
        setErrors((err.body as { errors: string[] }).errors)
      } else {
        setErrors(["Rechnung konnte nicht finalisiert werden."])
      }
    }
  }

  useEffect(() => {
    function handleGlobalKeydown(e: globalThis.KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault()
        handleFinalize()
      }
    }
    window.addEventListener("keydown", handleGlobalKeydown)
    return () => window.removeEventListener("keydown", handleGlobalKeydown)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [invoiceId])

  return (
    <div className="mx-auto max-w-4xl space-y-5 p-4 sm:p-6">
      <h1 className="text-xl font-semibold tracking-tight">
        {invoice?.invoice_number ? (
          <span className="font-mono">{invoice.invoice_number}</span>
        ) : (
          "Neue Rechnung"
        )}
        {invoice?.status === "DRAFT" && (
          <span className="ml-2 text-sm font-normal text-ink/45 dark:text-paper/45">(Entwurf)</span>
        )}
      </h1>

      <CustomerSearch selected={customer} onSelect={setCustomer} />

      <LineItemGrid items={items} onChange={setItems} disabled={isLocked} />

      <LegalNotices items={items} />

      <div className="ml-auto w-64 space-y-1.5 text-sm">
        <div className="flex justify-between">
          <span className="text-ink/50 dark:text-paper/50">Nettosumme</span>
          <span className="font-mono tabular-nums">{totals.net.toFixed(2)} €</span>
        </div>
        <div className="flex justify-between">
          <span className="text-ink/50 dark:text-paper/50">zzgl. USt.</span>
          <span className="font-mono tabular-nums">{totals.tax.toFixed(2)} €</span>
        </div>
        <div className="flex justify-between border-t-2 border-ink/15 pt-1.5 text-base font-semibold dark:border-paper/15">
          <span>Gesamtbetrag</span>
          <span className="font-mono tabular-nums">{totals.gross.toFixed(2)} €</span>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="rounded-[4px] border border-status-overdue/30 bg-status-overdue/10 px-3 py-2 text-sm text-status-overdue">
          <ul className="list-inside list-disc">
            {errors.map((error) => (
              <li key={error}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {pdfReady && (
        <div className="flex items-center justify-between rounded-[4px] border border-status-paid/30 bg-status-paid/10 px-3 py-2 text-sm text-status-paid">
          <span>Rechnung {pdfReady.invoice_number} finalisiert — PDF-Vorschau geöffnet.</span>
          <button
            type="button"
            className="font-medium underline hover:no-underline"
            onClick={() => downloadInvoicePdf(pdfReady.id, pdfReady.invoice_number ?? "rechnung")}
          >
            PDF herunterladen
          </button>
        </div>
      )}

      {!isLocked && (
        <div className="flex justify-end">
          <button
            type="button"
            disabled={!invoiceId || !customer || finalizeInvoice.isPending}
            onClick={handleFinalize}
            className="btn-primary px-4 py-2.5"
          >
            Rechnung finalisieren &amp; ZUGFeRD-PDF erstellen
          </button>
        </div>
      )}
    </div>
  )
}
