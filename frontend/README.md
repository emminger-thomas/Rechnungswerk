# Rechnungswerk — Frontend

React 19 + TypeScript + Vite + Tailwind CSS v4 client for the Rechnungswerk invoicing app.
See the [repository root README](../README.md) for the full project overview and how to run
the backend.

## Commands

```bash
npm install
npm run dev       # Vite dev server at http://localhost:5173, expects the backend on :8000
npm run build      # tsc -b && vite build
npm run lint       # oxlint
npm run preview
```

`VITE_API_BASE_URL` is read from `.env.development` / `.env.production`.
