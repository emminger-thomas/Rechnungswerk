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
    <div className="mx-auto max-w-3xl space-y-5 p-4 sm:p-6">
      <h1 className="text-xl font-semibold tracking-tight">Kunden aus Excel/CSV importieren</h1>

      <div
        className="cursor-pointer rounded-[4px] border-2 border-dashed border-ink/20 p-8 text-center text-sm text-ink/50 transition-colors hover:border-signal hover:text-ink/70 dark:border-paper/20 dark:text-paper/50 dark:hover:text-paper/70"
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

      {importMutation.isPending && (
        <p className="text-sm text-ink/50 dark:text-paper/50">Wird verarbeitet ...</p>
      )}

      {preview && (
        <div className="space-y-3">
          <div className="text-sm">
            <span className="font-medium text-status-paid">{preview.valid_count} gültig</span> von{" "}
            {preview.total_count} Zeilen erkannt.
          </div>

          {preview.unmapped_columns.length > 0 && (
            <div className="rounded-[4px] border border-status-overdue/30 bg-status-overdue/10 px-3 py-2 text-sm text-status-overdue">
              Nicht zugeordnete Spalten: {preview.unmapped_columns.join(", ")}
            </div>
          )}

          <div className="panel max-h-80 overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-ink/10 text-xs text-ink/45 dark:border-paper/10 dark:text-paper/45">
                <tr>
                  <th className="px-3 py-2 font-medium">Name</th>
                  <th className="px-3 py-2 font-medium">Ort</th>
                  <th className="px-3 py-2 font-medium">Fehler</th>
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((row, index) => (
                  <tr
                    key={index}
                    className={
                      row.errors.length > 0
                        ? "bg-status-overdue/10"
                        : "border-t border-ink/6 dark:border-paper/6"
                    }
                  >
                    <td className="px-3 py-1.5">{row.data.name}</td>
                    <td className="px-3 py-1.5">{row.data.city}</td>
                    <td className="px-3 py-1.5 text-status-overdue">{row.errors.join("; ")}</td>
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
              className="btn-ghost"
            >
              Abbrechen
            </button>
            <button
              type="button"
              disabled={preview.valid_count === 0}
              onClick={handleConfirm}
              className="btn-primary"
            >
              {preview.valid_count} Kunden importieren
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="rounded-[4px] border border-status-paid/30 bg-status-paid/10 px-3 py-2 text-sm text-status-paid">
          {result}
        </div>
      )}
    </div>
  )
}
