# klartext.jetzt

**Narrative Epistemik** – Eine Autorenumgebung für transparente, kausal konsistente und narrativ vermittelbare Wirkmodelle.

> Komplexität soll nicht vereinfacht oder versteckt werden. Sie soll sichtbar, erzählbar und vergleichbar gemacht werden.

## Repository-Struktur

```
klartext/
├── frontend/        # React 18 + TypeScript + Vite
├── api/             # Python 3.12 + FastAPI (KI-Serviceschicht)
├── supabase/        # PostgreSQL-Migrations + RLS-Policies
├── docs/            # MkDocs Material – Spezifikationsdokumentation
└── .github/         # GitHub Actions: test, lint, deploy-docs
```

## Schnellstart

### Voraussetzungen

- Python 3.12+
- Node.js 20+
- [Supabase CLI](https://supabase.com/docs/guides/cli)

### API (FastAPI)

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # ANTHROPIC_API_KEY eintragen
uvicorn api.main:app --reload
# → http://localhost:8000/docs
```

### Tests

```bash
cd api && pytest
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
cp .env.example .env.local   # Supabase-Werte eintragen
npm run dev
# → http://localhost:5173
```

### Supabase lokal

```bash
supabase start
# Migrations werden automatisch angewendet
```

### Dokumentation lokal

```bash
pip install -r docs/requirements.txt
mkdocs serve
# → http://localhost:8000
```

## Umgebungsvariablen

| Variable | Wo | Beschreibung |
|---|---|---|
| `ANTHROPIC_API_KEY` | `api/.env` | Claude API Key |
| `VITE_SUPABASE_URL` | `frontend/.env.local` | Supabase-Projekt-URL |
| `VITE_SUPABASE_ANON_KEY` | `frontend/.env.local` | Supabase Anon Key |

## CI/CD

| Workflow | Trigger | Aktion |
|---|---|---|
| `test.yml` | Jeder Push | pytest + Vitest |
| `lint.yml` | Jeder Push | ruff + mypy + tsc |
| `deploy-docs.yml` | Push auf `main` | MkDocs → GitHub Pages |

## Dokumentation

→ [klartext.jetzt Spezifikation](https://thorstendittmar.github.io/klartext/) (GitHub Pages)

Basiert auf Whitepaper V0.24 – Kapitel 1–24 + Appendix A.
