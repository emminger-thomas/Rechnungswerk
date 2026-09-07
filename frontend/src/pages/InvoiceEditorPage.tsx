import { useParams } from "react-router-dom"

import { useInvoice } from "../api/invoices"
import { InvoiceForm } from "../components/invoice/InvoiceForm"

export function InvoiceEditorPage() {
  const { id } = useParams<{ id: string }>()
  const { data: invoice, isLoading } = useInvoice(id)

  if (id && isLoading) {
    return <div className="p-4 text-neutral-500">Lädt ...</div>
  }

  return <InvoiceForm invoice={invoice} />
}
