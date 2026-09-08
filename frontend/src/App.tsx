import { Link, NavLink, Route, Routes } from "react-router-dom"

import { CustomerImportPage } from "./pages/CustomerImportPage"
import { DashboardPage } from "./pages/DashboardPage"
import { InvoiceEditorPage } from "./pages/InvoiceEditorPage"
import { InvoiceListPage } from "./pages/InvoiceListPage"

function NavItem({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        `border-b-2 px-0.5 py-4 text-sm font-medium transition-colors ${
          isActive
            ? "border-signal text-ink dark:text-paper"
            : "border-transparent text-ink/50 hover:text-ink dark:text-paper/50 dark:hover:text-paper"
        }`
      }
    >
      {children}
    </NavLink>
  )
}

function App() {
  return (
    <div className="min-h-screen bg-paper text-ink dark:bg-ink dark:text-paper">
      <nav className="border-b border-ink/10 dark:border-paper/10">
        <div className="mx-auto flex max-w-6xl items-center gap-8 px-4">
          <Link to="/" className="flex items-center gap-2.5 py-4">
            <span className="flex h-7 w-7 items-center justify-center rounded-[3px] border-[1.5px] border-signal font-mono text-[11px] font-semibold tracking-tight text-signal">
              RW
            </span>
            <span className="font-semibold tracking-tight">Rechnungswerk</span>
          </Link>
          <div className="flex items-center gap-6">
            <NavItem to="/">Dashboard</NavItem>
            <NavItem to="/rechnungen">Rechnungen</NavItem>
            <NavItem to="/kunden/import">Kunden importieren</NavItem>
          </div>
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
