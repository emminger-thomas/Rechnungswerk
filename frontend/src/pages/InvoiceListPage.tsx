import { Link } from "react-router-dom"

import { useInvoices } from "../api/invoices"

const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Entwurf",
  ISSUED: "Offen",
  PAID: "Bezahlt",
  OVERDUE: "Überfällig",
  CANCELLED: "Storniert",
}

export function InvoiceListPage() {
  const { data, isLoading } = useInvoices()

  return (
    <div className="mx-auto max-w-4xl space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Rechnungen</h1>
        <Link
          to="/rechnungen/neu"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          + Neue Rechnung
        </Link>
      </div>

      {isLoading && <p className="text-neutral-500">Lädt ...</p>}

      <div className="divide-y divide-neutral-200 rounded-md border border-neutral-300 dark:divide-neutral-800 dark:border-neutral-700">
        {data?.results.map((invoice) => (
          <Link
            key={invoice.id}
            to={`/rechnungen/${invoice.id}`}
            className="flex items-center justify-between px-4 py-3 hover:bg-neutral-50 dark:hover:bg-neutral-900"
          >
            <div>
              <div className="font-medium">
                {invoice.invoice_number ?? "Entwurf"} · {invoice.customer_detail?.name}
              </div>
              <div className="text-sm text-neutral-500">{STATUS_LABELS[invoice.status]}</div>
            </div>
            <div className="tabular-nums">{invoice.total_gross} €</div>
          </Link>
        ))}
        {data?.results.length === 0 && (
          <div className="px-4 py-6 text-center text-neutral-500">Noch keine Rechnungen.</div>
        )}
      </div>
    </div>
  )
}
