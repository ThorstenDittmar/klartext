# klartext.jetzt – Narrative Epistemik

**Projektskizze / Whitepaper V0.24**

Eine Autorenumgebung für transparente, kausal konsistente und narrativ vermittelbare Wirkmodelle.

---

## Was ist klartext.jetzt?

klartext.jetzt ist eine epistemische Publikationsplattform, die narrative Texte mit formalen Wirkmodellen verbindet. Das System besteht aus drei Schichten:

1. **Wissenschaftlich-kausale Ebene** – Fachleute definieren Axiome, Begriffe, Regeln, Wirkmechanismen und Abhängigkeiten
2. **Narrative Ebene** – Autoren entwickeln Geschichten innerhalb eines gewählten Wirkmodells und Axiomraums
3. **KI-gestützte Konsistenzschicht** – Fortlaufende Prüfung ob das Narrativ dem Wirkmodell entspricht

## Übergeordnete Vision

> Komplexität soll nicht vereinfacht oder versteckt werden. Sie soll sichtbar, erzählbar und vergleichbar gemacht werden.

## Repository-Struktur

```
klartext/
├── frontend/        # React + TypeScript + Vite
├── api/             # Python + FastAPI (KI-Serviceschicht)
├── supabase/        # Migrations, Schema, RLS-Policies
├── docs/            # Diese Dokumentation (MkDocs)
└── .github/         # GitHub Actions Workflows
```

## Schnellstart

| Komponente | Technologie | Status |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite | 🚧 Phase 1 |
| API | Python 3.12 + FastAPI | 🚧 Phase 1 |
| Datenbank | Supabase (PostgreSQL + RLS) | 🚧 Phase 1 |
| Docs | MkDocs Material | ✅ |

## Kapitelübersicht

Diese Dokumentation folgt der Struktur des Whitepapers V0.24.
Navigiere über die Tabs oben oder die Seitenleiste links.
