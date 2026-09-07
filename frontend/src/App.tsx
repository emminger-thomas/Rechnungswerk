import { Link, Route, Routes } from "react-router-dom"

import { CustomerImportPage } from "./pages/CustomerImportPage"
import { DashboardPage } from "./pages/DashboardPage"
import { InvoiceEditorPage } from "./pages/InvoiceEditorPage"
import { InvoiceListPage } from "./pages/InvoiceListPage"

function App() {
  return (
    <div className="min-h-screen bg-white text-neutral-900 dark:bg-neutral-950 dark:text-neutral-100">
      <nav className="border-b border-neutral-200 px-4 py-3 dark:border-neutral-800">
        <div className="mx-auto flex max-w-4xl items-center gap-4">
          <Link to="/" className="font-semibold">
            Rechnungswerk
          </Link>
          <Link to="/" className="text-sm text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100">
            Dashboard
          </Link>
          <Link to="/rechnungen" className="text-sm text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100">
            Rechnungen
          </Link>
          <Link
            to="/kunden/import"
            className="text-sm text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100"
          >
            Kunden importieren
          </Link>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/rechnungen" element={<InvoiceListPage />} />
        <Route path="/rechnungen/neu" element={<InvoiceEditorPage />} />
        <Route path="/rechnungen/:id" element={<InvoiceEditorPage />} />
        <Route path="/kunden/import" element={<CustomerImportPage />} />
      </Routes>
    </div>
  )
}

export default App
