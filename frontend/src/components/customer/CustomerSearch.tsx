import { useState } from "react"

import { useCreateCustomer, useCustomerSearch } from "../../api/customers"
import type { CustomerLookup } from "../../types/models"

interface CustomerSearchProps {
  selected: CustomerLookup | null
  onSelect: (customer: CustomerLookup) => void
}

export function CustomerSearch({ selected, onSelect }: CustomerSearchProps) {
  const [query, setQuery] = useState("")
  const [showQuickAdd, setShowQuickAdd] = useState(false)
  const { data: results, isFetching } = useCustomerSearch(query)
  const createCustomer = useCreateCustomer()

  if (selected) {
    return (
      <div className="panel flex items-center justify-between px-3 py-2.5">
        <div>
          <div className="font-medium">
            {selected.name}{" "}
            <span className="font-mono text-sm text-ink/45 dark:text-paper/45">
              · {selected.customer_number}
            </span>
          </div>
          <div className="text-sm text-ink/50 dark:text-paper/50">{selected.city}</div>
        </div>
        <button
          type="button"
          className="text-sm font-medium text-signal hover:underline"
          onClick={() => {
            setQuery("")
            onSelect(null as unknown as CustomerLookup)
          }}
        >
          Ändern
        </button>
      </div>
    )
  }

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Kunde suchen (Name, Kundennummer, PLZ, USt-IdNr.) ..."
        className="field py-2.5"
        autoFocus
      />
      {query.trim().length > 0 && (
        <div className="panel absolute z-10 mt-1 w-full shadow-lg">
          {isFetching && (
            <div className="px-3 py-2 text-sm text-ink/50 dark:text-paper/50">Suche ...</div>
          )}
          {!isFetching && results?.length === 0 && (
            <button
              type="button"
              className="block w-full px-3 py-2 text-left text-sm font-medium text-signal hover:bg-ink/[0.03] dark:hover:bg-paper/[0.03]"
              onClick={() => setShowQuickAdd(true)}
            >
              + "{query}" als neuen Kunden anlegen
            </button>
          )}
          {results?.map((customer) => (
            <button
              type="button"
              key={customer.id}
              className="block w-full border-b border-ink/8 px-3 py-2 text-left last:border-0 hover:bg-ink/[0.03] dark:border-paper/8 dark:hover:bg-paper/[0.03]"
              onClick={() => onSelect(customer)}
            >
              <div className="font-medium">
                {customer.name}{" "}
                <span className="font-mono text-sm text-ink/45 dark:text-paper/45">
                  · {customer.customer_number}
                </span>
              </div>
              <div className="text-sm text-ink/50 dark:text-paper/50">
                {customer.city}
                {customer.vat_id ? ` · ${customer.vat_id}` : ""}
              </div>
            </button>
          ))}
        </div>
      )}
      {showQuickAdd && (
        <QuickAddCustomerForm
          initialName={query}
          onCancel={() => setShowQuickAdd(false)}
          onCreated={(customer) => {
            setShowQuickAdd(false)
            onSelect(customer)
          }}
          isSubmitting={createCustomer.isPending}
          onSubmit={(data) =>
            createCustomer.mutateAsync(data).then((customer) => customer as unknown as CustomerLookup)
          }
        />
      )}
    </div>
  )
}

interface QuickAddCustomerFormProps {
  initialName: string
  onCancel: () => void
  onCreated: (customer: CustomerLookup) => void
  onSubmit: (data: Record<string, string>) => Promise<CustomerLookup>
  isSubmitting: boolean
}

function QuickAddCustomerForm({
  initialName,
  onCancel,
  onCreated,
  onSubmit,
  isSubmitting,
}: QuickAddCustomerFormProps) {
  const [form, setForm] = useState({
    name: initialName,
    street: "",
    zip_code: "",
    city: "",
    country: "DE",
  })

  return (
    <form
      className="panel absolute z-20 mt-1 w-full space-y-2 p-3 shadow-lg"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit(form).then(onCreated)
      }}
    >
      <div className="text-sm font-medium">Neuen Kunden anlegen</div>
      <input
        required
        placeholder="Name"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        className="field py-1.5"
      />
      <input
        required
        placeholder="Straße"
        value={form.street}
        onChange={(e) => setForm({ ...form, street: e.target.value })}
        className="field py-1.5"
      />
      <div className="flex gap-2">
        <input
          required
          placeholder="PLZ"
          value={form.zip_code}
          onChange={(e) => setForm({ ...form, zip_code: e.target.value })}
          className="field w-24 py-1.5"
        />
        <input
          required
          placeholder="Ort"
          value={form.city}
          onChange={(e) => setForm({ ...form, city: e.target.value })}
          className="field flex-1 py-1.5"
        />
      </div>
      <div className="flex justify-end gap-2 pt-1">
        <button type="button" onClick={onCancel} className="btn-ghost">
          Abbrechen
        </button>
        <button type="submit" disabled={isSubmitting} className="btn-primary">
          Anlegen
        </button>
      </div>
    </form>
  )
}
