import { useState } from "react"
import { Link } from "react-router-dom"

import {
  downloadDatevExport,
  useCreateReminder,
  useInvoices,
  useMarkInvoicePaid,
} from "../api/invoices"
import type { Invoice, InvoiceStatus } from "../types/models"

const COLUMNS: { status: InvoiceStatus; label: string; dot: string; border: string }[] = [
  { status: "DRAFT", label: "Entwurf", dot: "bg-status-draft", border: "border-l-status-draft" },
  { status: "ISSUED", label: "Offen", dot: "bg-status-open", border: "border-l-status-open" },
  { status: "OVERDUE", label: "Überfällig", dot: "bg-status-overdue", border: "border-l-status-overdue" },
  { status: "PAID", label: "Bezahlt", dot: "bg-status-paid", border: "border-l-status-paid" },
  { status: "CANCELLED", label: "Storniert", dot: "bg-status-cancelled", border: "border-l-status-cancelled" },
]

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

function InvoiceCard({ invoice, border }: { invoice: Invoice; border: string }) {
  const [paidDateOpen, setPaidDateOpen] = useState(false)
  const [paidDate, setPaidDate] = useState(todayIso())
  const markPaid = useMarkInvoicePaid()
  const createReminder = useCreateReminder()

  const canAct = invoice.status === "ISSUED" || invoice.status === "OVERDUE"

  return (
    <div className={`panel space-y-2 border-l-[3px] p-3 text-sm ${border}`}>
      <Link to={`/rechnungen/${invoice.id}`} className="block">
        <div className="flex items-baseline justify-between gap-2">
          <span className="truncate font-medium">{invoice.customer_detail?.name}</span>
          <span className="shrink-0 font-mono text-xs tabular-nums text-ink/50 dark:text-paper/50">
            {invoice.invoice_number ?? "—"}
          </span>
        </div>
        <div className="mt-1 flex items-center justify-between gap-2 text-xs text-ink/50 dark:text-paper/50">
          <span className="truncate">{invoice.due_date ? `fällig ${invoice.due_date}` : "kein Fälligkeitsdatum"}</span>
          <span className="shrink-0 font-mono tabular-nums text-sm text-ink dark:text-paper">
            {invoice.total_gross} €
          </span>
        </div>
      </Link>

      {invoice.reminder_count > 0 && (
        <div className="text-xs font-medium text-status-overdue">
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
                className="rounded-[3px] border border-ink/15 bg-transparent px-1 py-0.5 text-xs dark:border-paper/15"
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
                className="rounded-[3px] bg-status-paid px-2 py-0.5 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50"
              >
                Bestätigen
              </button>
              <button
                type="button"
                onClick={() => setPaidDateOpen(false)}
                className="btn-ghost px-2 py-0.5 text-xs"
              >
                Abbrechen
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setPaidDateOpen(true)}
              className="rounded-[3px] bg-status-paid/10 px-2 py-1 text-xs font-medium text-status-paid hover:bg-status-paid/20"
            >
              Als bezahlt markieren
            </button>
          )}
          <button
            type="button"
            disabled={createReminder.isPending}
            onClick={() => createReminder.mutate(invoice.id)}
            className="rounded-[3px] bg-status-overdue/10 px-2 py-1 text-xs font-medium text-status-overdue hover:bg-status-overdue/20 disabled:opacity-50"
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
    <div className="mx-auto max-w-6xl space-y-5 p-4 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold tracking-tight">Dashboard</h1>
        <div className="flex items-center gap-2">
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="field w-auto py-1.5"
          />
          <button type="button" onClick={handleExport} className="btn-secondary">
            DATEV-Export
          </button>
          <Link to="/rechnungen/neu" className="btn-primary">
            + Neue Rechnung
          </Link>
        </div>
      </div>

      {isLoading && <p className="text-sm text-ink/50 dark:text-paper/50">Lädt …</p>}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {COLUMNS.map((column) => {
          const invoices = invoicesByStatus(column.status)
          return (
            <div key={column.status} className="space-y-2.5">
              <div className="flex items-center gap-2 border-b-2 border-ink/10 pb-2 dark:border-paper/10">
                <span className={`h-2 w-2 rounded-full ${column.dot}`} />
                <h2 className="text-sm font-medium">{column.label}</h2>
                <span className="ml-auto font-mono text-xs tabular-nums text-ink/40 dark:text-paper/40">
                  {invoices.length}
                </span>
              </div>
              <div className="space-y-2">
                {invoices.map((invoice) => (
                  <InvoiceCard key={invoice.id} invoice={invoice} border={column.border} />
                ))}
                {invoices.length === 0 && (
                  <div className="rounded-[4px] border border-dashed border-ink/15 p-3 text-center text-xs text-ink/35 dark:border-paper/15 dark:text-paper/35">
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
