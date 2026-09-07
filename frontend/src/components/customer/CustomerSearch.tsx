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
      <div className="flex items-center justify-between rounded-md border border-neutral-300 bg-neutral-50 px-3 py-2 dark:border-neutral-700 dark:bg-neutral-900">
        <div>
          <div className="font-medium">{selected.name}</div>
          <div className="text-sm text-neutral-500">{selected.city}</div>
        </div>
        <button
          type="button"
          className="text-sm text-blue-600 hover:underline dark:text-blue-400"
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
        placeholder="Kunde suchen (Name, PLZ, USt-IdNr.) ..."
        className="w-full rounded-md border border-neutral-300 px-3 py-2 focus:border-blue-500 focus:outline-none dark:border-neutral-700 dark:bg-neutral-900"
        autoFocus
      />
      {query.trim().length > 0 && (
        <div className="absolute z-10 mt-1 w-full rounded-md border border-neutral-300 bg-white shadow-lg dark:border-neutral-700 dark:bg-neutral-900">
          {isFetching && <div className="px-3 py-2 text-sm text-neutral-500">Suche ...</div>}
          {!isFetching && results?.length === 0 && (
            <button
              type="button"
              className="block w-full px-3 py-2 text-left text-sm text-blue-600 hover:bg-neutral-100 dark:text-blue-400 dark:hover:bg-neutral-800"
              onClick={() => setShowQuickAdd(true)}
            >
              + "{query}" als neuen Kunden anlegen
            </button>
          )}
          {results?.map((customer) => (
            <button
              type="button"
              key={customer.id}
              className="block w-full border-b border-neutral-100 px-3 py-2 text-left last:border-0 hover:bg-neutral-100 dark:border-neutral-800 dark:hover:bg-neutral-800"
              onClick={() => onSelect(customer)}
            >
              <div className="font-medium">{customer.name}</div>
              <div className="text-sm text-neutral-500">
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
      className="absolute z-20 mt-1 w-full space-y-2 rounded-md border border-neutral-300 bg-white p-3 shadow-lg dark:border-neutral-700 dark:bg-neutral-900"
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
        className="w-full rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-800"
      />
      <input
        required
        placeholder="Straße"
        value={form.street}
        onChange={(e) => setForm({ ...form, street: e.target.value })}
        className="w-full rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-800"
      />
      <div className="flex gap-2">
        <input
          required
          placeholder="PLZ"
          value={form.zip_code}
          onChange={(e) => setForm({ ...form, zip_code: e.target.value })}
          className="w-24 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-800"
        />
        <input
          required
          placeholder="Ort"
          value={form.city}
          onChange={(e) => setForm({ ...form, city: e.target.value })}
          className="flex-1 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-800"
        />
      </div>
      <div className="flex justify-end gap-2 pt-1">
        <button
          type="button"
          onClick={onCancel}
          className="rounded px-3 py-1 text-sm text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-neutral-800"
        >
          Abbrechen
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          Anlegen
        </button>
      </div>
    </form>
  )
}
