# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Rechnungswerk is a German micro-SaaS for tradespeople (Handwerker) to create legally compliant
e-invoices. It generates a human-readable PDF with an embedded, machine-readable ZUGFeRD 2.2 /
XRechnung XML (EN 16931 CII), and enforces GoBD revision-safety rules (immutability after issue,
gap-free sequential invoice numbers, append-only audit log). Full functional/legal spec is in
`SPEC.md` (German); product rationale is in `PRD_E_Rechnung_Handwerker_Claude_Code.md`.

Stack: Django 6 + DRF backend (`backend/`), React 19 + TypeScript + Vite + Tailwind v4 frontend
(`frontend/`), PostgreSQL database (used in both dev and prod — there is no sqlite fallback despite
`db.sqlite3` appearing in `.gitignore`).

## Commands

### Backend (`backend/`, Python 3.13, venv at `backend/.venv`)

```
backend\.venv\Scripts\activate.bat        # PowerShell: backend\.venv\Scripts\Activate.ps1
python manage.py runserver                # dev server, settings default to config.settings.dev
python manage.py migrate
python manage.py makemigrations <app>
python manage.py test                     # all tests
python manage.py test invoices            # one app
python manage.py test invoices.tests.test_gobd_lock            # one module
python manage.py test invoices.tests.test_gobd_lock.ClassName.test_method  # one test
```

`DJANGO_SETTINGS_MODULE` defaults to `config.settings.dev` (set in `manage.py`). Dev settings
connect to a local PostgreSQL (`DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` env vars,
defaulting to `rechnungswerk` / `rechnungswerk_app` / `rechnungswerk_dev_pw` / `127.0.0.1` /
`5432`) — a running Postgres instance is required even for local dev/tests. Production
(`config.settings.prod`) requires `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`,
`DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` as env vars (no defaults, will raise `KeyError`).

PDF rendering uses WeasyPrint, which needs native GTK/Pango libraries on Windows; `dev.py` adds
`C:\Program Files\GTK3-Runtime Win64\bin` to `PATH` automatically if present.

### Frontend (`frontend/`)

```
npm run dev       # Vite dev server (expects backend at http://127.0.0.1:8000/api, see .env.development)
npm run build      # tsc -b && vite build
npm run lint       # oxlint
npm run preview
```

No frontend test runner is configured.

## Architecture

### Backend: three Django apps around one core workflow

- **`company`** — `CompanySettings` is a `django-solo` singleton (the single tradesperson/business
  issuing invoices: name, address, tax IDs, IBAN, invoice/storno number prefixes, small-business
  flag). Exposed via `RetrieveUpdateAPIView` at `/api/company-settings` (no list/create — there's
  only ever one row).
- **`customers`** — `Customer` model plus `services/csv_import.py` for the Excel/CSV import wizard
  with column auto-mapping (SPEC.md §4.1).
- **`invoices`** — the core domain: `Invoice`, `InvoiceItem`, `NumberingCounter`,
  `AuditLogEntry` (all in `invoices/models.py`), plus a `services/` package that does the real work:
  - `services/finalize.py` — orchestrates the finalize pipeline: validate → assign invoice number →
    recalculate totals → build XML → render PDF → embed XML into PDF/A-3 → hash → lock. Also
    implements the storno (cancellation) flow, which creates a new `Invoice` with
    `document_type=STORNO`, negated line items, its own number series, referencing the original via
    `cancels_invoice`. Both run inside one `transaction.atomic()` block.
  - `numbering.py` — gap-free sequential numbering per `(prefix, year)` via
    `select_for_update()` on `NumberingCounter`; must always be called inside the same transaction
    that persists the state change consuming the number, so a rollback never leaves a gap.
  - `services/validation.py` — pre-finalize checks (EN 16931 required fields, § 14 UStG).
  - `services/zugferd.py` — builds the UN/CEFACT CII XML (uses `drafthorse`).
  - `services/pdf.py` — renders the human-readable PDF (WeasyPrint + Django templates in
    `invoices/templates/invoices/`).
  - `services/pdfa3.py` — embeds the ZUGFeRD XML into the PDF as PDF/A-3 (uses `factur-x`/`pypdf`).
  - `tax.py` — the four tax scenarios (STANDARD 19%, REDUCED 7%, SMALL_BUSINESS §19 UStG,
    REVERSE_CHARGE §13b UStG) each mapping to a rate, an EN 16931 tax category code, and an optional
    mandatory legal-notice string that must appear on the invoice.
  - `unit_codes.py` — maps German unit labels (Std., Stk., m², …) to UN/ECE Rec 20 codes.
  - `audit.py` — `log_event()` is the only way to write an `AuditLogEntry`; it SHA-256-hashes a
    canonical JSON snapshot of the invoice + items as `payload_hash`.

### GoBD immutability (enforced at three layers, not just one)

1. **Model layer**: `Invoice.save()`/`delete()` and `AuditLogEntry.save()`/`delete()` raise
   `GoBDLockError` (see `invoices/exceptions.py`) if the invoice `is_locked` or the audit entry
   already exists — this is the layer callers must deliberately bypass with
   `save(allow_locked_write=True)`, which only the finalize/cancel services use.
2. **API layer**: `InvoiceNotLocked` (`invoices/permissions.py`) blocks unsafe methods
   (PUT/PATCH/DELETE) on a locked invoice with a 403 before the request reaches the model.
3. **Audit log**: append-only by construction — no update/delete endpoint is ever exposed, and the
   model itself refuses in-place saves/deletes.

Once `Invoice.status` reaches `ISSUED` (`is_locked=True`), the only legal way to "change" it is a
storno document referencing it — never edit a locked invoice directly, in code or via fixtures.

### API surface

Router-registered at `/api/`: `customers` and `invoices` (DRF `ModelViewSet`s), plus
`invoices/{id}/finalize`, `invoices/{id}/cancel`, `invoices/{id}/pdf`, `invoices/{id}/xml` as
extra `@action`s on `InvoiceViewSet`. `/api/company-settings` is a separate singleton endpoint.
See `SPEC.md` §07 for the full intended REST surface (including the DATEV export, not yet
implemented) and §06 for the EN 16931 business-term → XML-path mapping the XML generator must
honor.

### Frontend

Routed with `react-router-dom` (`App.tsx`): `/` and `/rechnungen` → invoice list,
`/rechnungen/neu` and `/rechnungen/:id` → invoice editor, `/kunden/import` → CSV import wizard.
`src/api/client.ts` is a small typed fetch wrapper (`api.get/post/put/patch/delete/blob`) hitting
`VITE_API_BASE_URL` (`.env.development` → `http://127.0.0.1:8000/api`); it throws `ApiError` with
the parsed JSON body on non-2xx responses. Server state is managed with TanStack Query. The
invoice line-item grid (`components/invoice/LineItemGrid.tsx`) implements the Excel-like keyboard
navigation described in SPEC.md §09 (Tab/Shift+Tab, Enter-in-last-column adds a row, Ctrl/Cmd+Enter
finalizes).

## Domain rules worth knowing before touching invoice code

- Four tax scenarios only (`invoices/tax.py`); each has a fixed EN 16931 category code and some
  require a specific German legal-notice string on the invoice — don't hardcode 19%/7% elsewhere,
  derive from `tax.py`.
- Invoice numbers and storno numbers are separate series (`RE-YYYY-NNNN` / `ST-YYYY-NNNN` by
  default, configurable per-`CompanySettings` prefix) and must stay gap-free — always allocate via
  `numbering.get_next_number()` inside the same atomic transaction as the state change.
- A storno is a full new `Invoice` row (not a status flip) with negated `InvoiceItem` quantities,
  linked via `cancels_invoice`; the original invoice transitions to `CANCELLED` but is never
  deleted or mutated beyond that status field.
