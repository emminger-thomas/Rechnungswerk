import { TAX_SCENARIO_LEGAL_NOTICE } from "../../types/models"
import type { InvoiceItem } from "../../types/models"

export function LegalNotices({ items }: { items: InvoiceItem[] }) {
  const notices = Array.from(
    new Set(
      items
        .map((item) => TAX_SCENARIO_LEGAL_NOTICE[item.tax_scenario])
        .filter((notice): notice is string => Boolean(notice)),
    ),
  )

  if (notices.length === 0) return null

  return (
    <div className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200">
      {notices.map((notice) => (
        <p key={notice}>{notice}</p>
      ))}
    </div>
  )
}
