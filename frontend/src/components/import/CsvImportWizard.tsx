import { useRef, useState } from "react"

import { useImportCustomersCsv } from "../../api/customers"
import type { ImportPreviewResponse } from "../../api/customers"

export function CsvImportWizard() {
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const importMutation = useImportCustomersCsv()

  async function handleFileSelected(selected: File) {
    setFile(selected)
    setResult(null)
    const response = await importMutation.mutateAsync({ file: selected, dryRun: true })
    setPreview(response)
  }

  async function handleConfirm() {
    if (!file) return
    const response = await importMutation.mutateAsync({ file, dryRun: false })
    setResult(`${response.created_count ?? 0} Kunden importiert.`)
    setPreview(null)
    setFile(null)
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4 p-4">
      <h1 className="text-xl font-semibold">Kunden aus Excel/CSV importieren</h1>

      <div
        className="cursor-pointer rounded-md border-2 border-dashed border-neutral-300 p-8 text-center text-neutral-500 hover:border-blue-400 dark:border-neutral-700"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault()
          const dropped = e.dataTransfer.files[0]
          if (dropped) handleFileSelected(dropped)
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx"
          className="hidden"
          onChange={(e) => {
            const selected = e.target.files?.[0]
            if (selected) handleFileSelected(selected)
          }}
        />
        {file ? file.name : "Datei hierher ziehen oder klicken zum Auswählen (.csv, .xlsx)"}
      </div>

      {importMutation.isPending && <p className="text-sm text-neutral-500">Wird verarbeitet ...</p>}

      {preview && (
        <div className="space-y-3">
          <div className="text-sm">
            <span className="font-medium text-green-700 dark:text-green-400">
              {preview.valid_count} gültig
            </span>{" "}
            von {preview.total_count} Zeilen erkannt.
          </div>

          {preview.unmapped_columns.length > 0 && (
            <div className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200">
              Nicht zugeordnete Spalten: {preview.unmapped_columns.join(", ")}
            </div>
          )}

          <div className="max-h-80 overflow-auto rounded-md border border-neutral-300 dark:border-neutral-700">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs uppercase text-neutral-500 dark:bg-neutral-900">
                <tr>
                  <th className="px-2 py-1">Name</th>
                  <th className="px-2 py-1">Ort</th>
                  <th className="px-2 py-1">Fehler</th>
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((row, index) => (
                  <tr
                    key={index}
                    className={
                      row.errors.length > 0
                        ? "bg-red-50 dark:bg-red-950"
                        : "bg-white dark:bg-neutral-950"
                    }
                  >
                    <td className="px-2 py-1">{row.data.name}</td>
                    <td className="px-2 py-1">{row.data.city}</td>
                    <td className="px-2 py-1 text-red-700 dark:text-red-400">
                      {row.errors.join("; ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => {
                setPreview(null)
                setFile(null)
              }}
              className="rounded px-3 py-2 text-sm text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-neutral-800"
            >
              Abbrechen
            </button>
            <button
              type="button"
              disabled={preview.valid_count === 0}
              onClick={handleConfirm}
              className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {preview.valid_count} Kunden importieren
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="rounded-md border border-green-300 bg-green-50 px-3 py-2 text-sm text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-300">
          {result}
        </div>
      )}
    </div>
  )
}
