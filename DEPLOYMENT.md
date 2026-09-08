# Deployment-Runbook

Zielarchitektur: Frontend auf **Vercel**, Backend auf **Railway**, Objektspeicher (PDF-Archiv)
auf **Cloudflare R2**, Domain über **Cloudflare Registrar**. Vercel selbst eignet sich nicht
für das Django-Backend (kein WSGI-Server, WeasyPrint braucht native GTK/Pango-Libraries,
lokale Mediendateien wären dort nicht persistent).

Der Code-seitige Teil (Dockerfile, `dj-database-url`, S3/R2-Storage-Konfiguration, CI) ist
bereits im Repo vorhanden. Was hier folgt, sind die Konten-/Dashboard-Schritte, die nur mit
eigenen Accounts ausführbar sind.

## Ausführungsreihenfolge

1. ~~Domain bei Cloudflare registrieren~~ — **erledigt**: `rechnungswerk.online` ist
   registriert (Cloudflare Registrar).
2. **Railway**: Projekt aus dem GitHub-Repo anlegen, Postgres-Plugin hinzufügen, Env-Vars
   setzen (siehe unten), Root-Directory auf `backend/` stellen, ersten Deploy auslösen, mit
   Railways Temp-Domain verifizieren.
3. **Cloudflare R2**: Bucket + API-Token anlegen, Credentials in Railway eintragen,
   PDF-Upload nach Finalisieren einer Rechnung testen.
4. **Vercel**: Projekt aus dem GitHub-Repo importieren, Root-Directory `frontend/`,
   `VITE_API_BASE_URL` erstmal auf Railways Temp-Domain setzen, deployen, verifizieren.
5. **DNS**: `rechnungswerk.online` (Apex) → Vercel, `api.rechnungswerk.online` → Railway
   (beide als CNAME; Cloudflare flattened den Apex-CNAME automatisch, kein A-Record nötig).
6. **Env-Vars auf finale Domain umstellen** (`DJANGO_ALLOWED_HOSTS=api.rechnungswerk.online`,
   `CORS_ALLOWED_ORIGINS=https://rechnungswerk.online` in Railway;
   `VITE_API_BASE_URL=https://api.rechnungswerk.online/api` in Vercel), beide Seiten
   redeployen.
7. **End-to-End-Smoke-Test** auf der echten Domain (siehe unten).
8. Separat/später: Nutzer-Auth + echte Mandantentrennung + Stripe-Billing (eigenes Vorhaben,
   siehe SPEC.md §10 — das Schema ist bereits dafür vorbereitet, s. Commit
   "Make schema tenant-ready...").

## Railway: benötigte Env-Vars

| Variable | Wert |
|---|---|
| `DJANGO_SECRET_KEY` | neu generieren (z.B. `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `AUDIT_LOG_SECRET_KEY` | neu generieren, eigenständig von `DJANGO_SECRET_KEY` |
| `DJANGO_ALLOWED_HOSTS` | erst Railway-Temp-Domain, dann final `api.rechnungswerk.online` |
| `CORS_ALLOWED_ORIGINS` | erst Vercel-Preview-URL, dann final `https://rechnungswerk.online` |
| `DATABASE_URL` | von Railways Postgres-Plugin automatisch bereitgestellt |
| `AWS_ACCESS_KEY_ID` | aus dem R2-API-Token |
| `AWS_SECRET_ACCESS_KEY` | aus dem R2-API-Token |
| `AWS_STORAGE_BUCKET_NAME` | Name des R2-Buckets |
| `AWS_S3_ENDPOINT_URL` | R2-Endpoint (`https://<account-id>.r2.cloudflarestorage.com`) |

Railway erkennt `backend/Dockerfile` automatisch, sofern Root-Directory auf `backend/`
gesetzt ist.

## Vercel: Konfiguration

- Root-Directory: `frontend/`
- Build-Command: `npm run build` (Standard)
- Output-Directory: `dist/` (Standard)
- Env-Var `VITE_API_BASE_URL`: im Vercel-Dashboard setzen (überschreibt
  `frontend/.env.production` zur Build-Zeit — bevorzugt, da Domain-Änderungen dann keinen
  Code-Commit brauchen).

## Verifikation

- `python manage.py test` (Backend) läuft automatisch in CI (`.github/workflows/ci.yml`)
  bei jedem Push/PR.
- Docker-Build lokal prüfen, sofern Docker verfügbar ist (in dieser Session nicht der Fall
  gewesen — noch unverifiziert): `docker build -t rechnungswerk-backend backend/` und
  Container starten, `import weasyprint` muss funktionieren.
- Nach Railway-Deploy: `curl` gegen `/api/company-settings` und `/api/invoices/` auf der
  Railway-Temp-Domain.
- Nach Vercel-Deploy: Frontend lädt, Netzwerk-Tab zeigt erfolgreiche Calls gegen die
  Railway-API (CORS greift).
- Nach DNS-Umstellung: `curl -I https://api.rechnungswerk.online` und
  `https://rechnungswerk.online` liefern gültiges TLS (beide Plattformen provisionieren
  automatisch, sobald DNS korrekt zeigt).
- End-to-End auf der finalen Domain: Kunde anlegen → Rechnung erfassen → finalisieren →
  PDF-Vorschau öffnet, PDF enthält eingebettetes ZUGFeRD-XML → GoBD-Sperre verhindert
  Bearbeitung → DATEV-Export liefert ZIP mit CSV + PDF.
