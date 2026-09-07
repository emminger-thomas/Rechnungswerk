import { useState } from "react"
import { Link } from "react-router-dom"

import {
  downloadDatevExport,
  useCreateReminder,
  useInvoices,
  useMarkInvoicePaid,
} from "../api/invoices"
import type { Invoice, InvoiceStatus } from "../types/models"

const COLUMNS: { status: InvoiceStatus; label: string }[] = [
  { status: "DRAFT", label: "Entwurf" },
  { status: "ISSUED", label: "Offen" },
  { status: "OVERDUE", label: "Überfällig" },
  { status: "PAID", label: "Bezahlt" },
  { status: "CANCELLED", label: "Storniert" },
]

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

function InvoiceCard({ invoice }: { invoice: Invoice }) {
  const [paidDateOpen, setPaidDateOpen] = useState(false)
  const [paidDate, setPaidDate] = useState(todayIso())
  const markPaid = useMarkInvoicePaid()
  const createReminder = useCreateReminder()

  const canAct = invoice.status === "ISSUED" || invoice.status === "OVERDUE"

  return (
    <div className="space-y-2 rounded-md border border-neutral-200 bg-white p-3 text-sm dark:border-neutral-800 dark:bg-neutral-900">
      <Link to={`/rechnungen/${invoice.id}`} className="block">
        <div className="font-medium">
          {invoice.invoice_number ?? "Entwurf"} · {invoice.customer_detail?.name}
        </div>
        <div className="flex items-center justify-between text-neutral-500">
          <span>{invoice.due_date ? `fällig ${invoice.due_date}` : "kein Fälligkeitsdatum"}</span>
          <span className="tabular-nums">{invoice.total_gross} €</span>
        </div>
      </Link>

      {invoice.reminder_count > 0 && (
        <div className="text-xs font-medium text-amber-600 dark:text-amber-400">
          Mahnstufe {invoice.reminder_count}
        </div>
      )}

      {canAct && (
        <div className="flex flex-wrap gap-2 pt-1">
          {paidDateOpen ? (
            <div className="flex items-center gap-1">
              <input
                type="date"
                value={paidDate}
                onChange={(e) => setPaidDate(e.target.value)}
                className="rounded border border-neutral-300 px-1 py-0.5 text-xs dark:border-neutral-700 dark:bg-neutral-800"
              />
              <button
                type="button"
                disabled={markPaid.isPending}
                onClick={() =>
                  markPaid.mutate(
                    { id: invoice.id, paidDate },
                    { onSuccess: () => setPaidDateOpen(false) }
                  )
                }
                className="rounded bg-green-600 px-2 py-0.5 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
              >
                Bestätigen
              </button>
              <button
                type="button"
                onClick={() => setPaidDateOpen(false)}
                className="rounded px-2 py-0.5 text-xs text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100"
              >
                Abbrechen
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setPaidDateOpen(true)}
              className="rounded bg-green-600/10 px-2 py-1 text-xs font-medium text-green-700 hover:bg-green-600/20 dark:text-green-400"
            >
              Als bezahlt markieren
            </button>
          )}
          <button
            type="button"
            disabled={createReminder.isPending}
            onClick={() => createReminder.mutate(invoice.id)}
            className="rounded bg-amber-600/10 px-2 py-1 text-xs font-medium text-amber-700 hover:bg-amber-600/20 disabled:opacity-50 dark:text-amber-400"
          >
            Mahnung erstellen
          </button>
        </div>
      )}
    </div>
  )
}

export function DashboardPage() {
  const { data, isLoading } = useInvoices()
  const [month, setMonth] = useState(todayIso().slice(0, 7))

  const invoicesByStatus = (status: InvoiceStatus) =>
    data?.results.filter((invoice) => invoice.status === status) ?? []

  const handleExport = () => {
    const [year, monthNum] = month.split("-").map(Number)
    downloadDatevExport(year, monthNum)
  }

  return (
    <div className="mx-auto max-w-6xl space-y-4 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <div className="flex items-center gap-2">
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="rounded-md border border-neutral-300 px-2 py-1.5 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
          <button
            type="button"
            onClick={handleExport}
            className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-neutral-700 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-300"
          >
            DATEV-Export
          </button>
          <Link
            to="/rechnungen/neu"
            className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Neue Rechnung
          </Link>
        </div>
      </div>

      {isLoading && <p className="text-neutral-500">Lädt ...</p>}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {COLUMNS.map((column) => {
          const invoices = invoicesByStatus(column.status)
          return (
            <div key={column.status} className="space-y-2">
              <div className="flex items-center justify-between px-1">
                <h2 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">
                  {column.label}
                </h2>
                <span className="text-xs text-neutral-400">{invoices.length}</span>
              </div>
              <div className="space-y-2">
                {invoices.map((invoice) => (
                  <InvoiceCard key={invoice.id} invoice={invoice} />
                ))}
                {invoices.length === 0 && (
                  <div className="rounded-md border border-dashed border-neutral-200 p-3 text-center text-xs text-neutral-400 dark:border-neutral-800">
                    Keine Rechnungen
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
