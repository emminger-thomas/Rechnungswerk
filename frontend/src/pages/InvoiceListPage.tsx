import { Link } from "react-router-dom"

import { useInvoices } from "../api/invoices"

const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Entwurf",
  ISSUED: "Offen",
  PAID: "Bezahlt",
  OVERDUE: "Überfällig",
  CANCELLED: "Storniert",
}

const STATUS_DOTS: Record<string, string> = {
  DRAFT: "bg-status-draft",
  ISSUED: "bg-status-open",
  PAID: "bg-status-paid",
  OVERDUE: "bg-status-overdue",
  CANCELLED: "bg-status-cancelled",
}

export function InvoiceListPage() {
  const { data, isLoading } = useInvoices()

  return (
    <div className="mx-auto max-w-4xl space-y-5 p-4 sm:p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">Rechnungen</h1>
        <Link to="/rechnungen/neu" className="btn-primary">
          + Neue Rechnung
        </Link>
      </div>

      {isLoading && <p className="text-sm text-ink/50 dark:text-paper/50">Lädt …</p>}

      <div className="panel divide-y divide-ink/8 dark:divide-paper/8">
        {data?.results.map((invoice) => (
          <Link
            key={invoice.id}
            to={`/rechnungen/${invoice.id}`}
            className="flex items-center justify-between gap-4 px-4 py-3 hover:bg-ink/[0.03] dark:hover:bg-paper/[0.03]"
          >
            <div className="min-w-0">
              <div className="truncate font-medium">
                <span className="font-mono text-sm text-ink/50 dark:text-paper/50">
                  {invoice.invoice_number ?? "Entwurf"}
                </span>{" "}
                · {invoice.customer_detail?.name}
              </div>
              <div className="mt-0.5 flex items-center gap-1.5 text-sm text-ink/50 dark:text-paper/50">
                <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOTS[invoice.status]}`} />
                {STATUS_LABELS[invoice.status]}
              </div>
            </div>
            <div className="shrink-0 font-mono tabular-nums">{invoice.total_gross} €</div>
          </Link>
        ))}
        {data?.results.length === 0 && (
          <div className="px-4 py-8 text-center text-sm text-ink/40 dark:text-paper/40">
            Noch keine Rechnungen.
          </div>
        )}
      </div>
    </div>
  )
}
