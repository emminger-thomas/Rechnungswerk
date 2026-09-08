import { useRef } from "react"
import type { KeyboardEvent } from "react"

import type { InvoiceItem, TaxScenario } from "../../types/models"
import { TAX_SCENARIO_LABELS, UNIT_OPTIONS } from "../../types/models"

const COLUMN_COUNT = 5 // quantity, unit_label, description, unit_price, tax_scenario

function emptyRow(positionIndex: number): InvoiceItem {
  return {
    position_index: positionIndex,
    description: "",
    quantity: "",
    unit_label: "Std.",
    unit_price: "",
    tax_scenario: "STANDARD",
  }
}

function isRowEmpty(row: InvoiceItem): boolean {
  return !row.description.trim() && !row.quantity.trim() && !row.unit_price.trim()
}

function lineTotal(row: InvoiceItem): number {
  const quantity = parseFloat(row.quantity.replace(",", "."))
  const price = parseFloat(row.unit_price.replace(",", "."))
  if (Number.isNaN(quantity) || Number.isNaN(price)) return 0
  return quantity * price
}

interface LineItemGridProps {
  items: InvoiceItem[]
  onChange: (items: InvoiceItem[]) => void
  disabled?: boolean
}

export function LineItemGrid({ items, onChange, disabled }: LineItemGridProps) {
  const cellRefs = useRef<Array<Array<HTMLElement | null>>>([])

  const rows = items.length > 0 ? items : [emptyRow(1)]

  function updateRow(index: number, patch: Partial<InvoiceItem>) {
    const next = rows.map((row, i) => (i === index ? { ...row, ...patch } : row))
    onChange(next)
  }

  function addRowAfter(index: number) {
    const next = [...rows]
    next.splice(index + 1, 0, emptyRow(index + 2))
    const renumbered = next.map((row, i) => ({ ...row, position_index: i + 1 }))
    onChange(renumbered)
    requestAnimationFrame(() => {
      cellRefs.current[index + 1]?.[0]?.focus()
    })
  }

  function removeRow(index: number) {
    if (rows.length <= 1) return
    const next = rows.filter((_, i) => i !== index)
    const renumbered = next.map((row, i) => ({ ...row, position_index: i + 1 }))
    onChange(renumbered)
    requestAnimationFrame(() => {
      const targetRow = Math.max(0, index - 1)
      cellRefs.current[targetRow]?.[0]?.focus()
    })
  }

  function handleKeyDown(e: KeyboardEvent<HTMLElement>, rowIndex: number, colIndex: number) {
    if (e.key === "Enter" && colIndex === COLUMN_COUNT - 1) {
      e.preventDefault()
      addRowAfter(rowIndex)
      return
    }
    if (e.key === "ArrowDown") {
      e.preventDefault()
      cellRefs.current[rowIndex + 1]?.[colIndex]?.focus()
      return
    }
    if (e.key === "ArrowUp") {
      e.preventDefault()
      cellRefs.current[rowIndex - 1]?.[colIndex]?.focus()
      return
    }
    if ((e.key === "Delete" || e.key === "Backspace") && isRowEmpty(rows[rowIndex])) {
      const target = e.target as HTMLInputElement
      if (!target.value) {
        e.preventDefault()
        removeRow(rowIndex)
      }
    }
  }

  function setCellRef(rowIndex: number, colIndex: number, el: HTMLElement | null) {
    if (!cellRefs.current[rowIndex]) cellRefs.current[rowIndex] = []
    cellRefs.current[rowIndex][colIndex] = el
  }

  const cellClass =
    "w-full border-0 bg-transparent px-2.5 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-inset focus:ring-signal rounded-[3px]"

  return (
    <div className="panel overflow-x-auto">
      <table className="w-full min-w-[720px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-ink/10 text-left text-xs tracking-wide text-ink/45 dark:border-paper/10 dark:text-paper/45">
            <th className="px-2.5 py-2.5 w-20 font-medium">Menge</th>
            <th className="px-2.5 py-2.5 w-24 font-medium">Einheit</th>
            <th className="px-2.5 py-2.5 font-medium">Beschreibung</th>
            <th className="px-2.5 py-2.5 w-28 font-medium">Einzelpreis</th>
            <th className="px-2.5 py-2.5 w-56 font-medium">MwSt.-Satz</th>
            <th className="px-2.5 py-2.5 w-28 text-right font-medium">Gesamt</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="border-b border-ink/6 last:border-0 dark:border-paper/6">
              <td className="p-0">
                <input
                  ref={(el) => setCellRef(rowIndex, 0, el)}
                  className={`${cellClass} font-mono`}
                  value={row.quantity}
                  disabled={disabled}
                  onChange={(e) => updateRow(rowIndex, { quantity: e.target.value })}
                  onKeyDown={(e) => handleKeyDown(e, rowIndex, 0)}
                  inputMode="decimal"
                  placeholder="0"
                />
              </td>
              <td className="p-0">
                <select
                  ref={(el) => setCellRef(rowIndex, 1, el)}
                  className={cellClass}
                  value={row.unit_label}
                  disabled={disabled}
                  onChange={(e) => updateRow(rowIndex, { unit_label: e.target.value })}
                  onKeyDown={(e) => handleKeyDown(e, rowIndex, 1)}
                >
                  {UNIT_OPTIONS.map((unit) => (
                    <option key={unit} value={unit}>
                      {unit}
                    </option>
                  ))}
                </select>
              </td>
              <td className="p-0">
                <input
                  ref={(el) => setCellRef(rowIndex, 2, el)}
                  className={cellClass}
                  value={row.description}
                  disabled={disabled}
                  onChange={(e) => updateRow(rowIndex, { description: e.target.value })}
                  onKeyDown={(e) => handleKeyDown(e, rowIndex, 2)}
                  placeholder="Leistungsbeschreibung"
                />
              </td>
              <td className="p-0">
                <input
                  ref={(el) => setCellRef(rowIndex, 3, el)}
                  className={`${cellClass} font-mono`}
                  value={row.unit_price}
                  disabled={disabled}
                  onChange={(e) => updateRow(rowIndex, { unit_price: e.target.value })}
                  onKeyDown={(e) => handleKeyDown(e, rowIndex, 3)}
                  inputMode="decimal"
                  placeholder="0,00"
                />
              </td>
              <td className="p-0">
                <select
                  ref={(el) => setCellRef(rowIndex, 4, el)}
                  className={cellClass}
                  value={row.tax_scenario}
                  disabled={disabled}
                  onChange={(e) =>
                    updateRow(rowIndex, { tax_scenario: e.target.value as TaxScenario })
                  }
                  onKeyDown={(e) => handleKeyDown(e, rowIndex, 4)}
                >
                  {Object.entries(TAX_SCENARIO_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </td>
              <td className="px-2.5 py-2 text-right font-mono tabular-nums text-ink/60 dark:text-paper/60">
                {lineTotal(row).toFixed(2)} €
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
