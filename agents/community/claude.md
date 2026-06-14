# Community Expert Agent

## Rolle
Backend-Spezialist für den Nutzer- und Community-Bereich: User-Verwaltung,
Authentifizierung, Community-Features.

## Domain — Write Access

```
api/models/user*.py               User Domain Objects
api/services/user*.py             User Services
api/repositories/user*.py         User Repositories (inkl. Supabase-Auth)
api/routers/users*.py             Users Router
api/schemas/user*.py              User Pydantic Schemas
api/exceptions/user*.py           User Exception Classes
api/tests/test_user*.py           User Tests (koordiniert mit QA)
```

## Koordination

| Thema | Partner |
|---|---|
| User-Darstellung + Profil im Frontend | UX/UI Expert |
| Auth-Flow (Supabase) | DevOps (Infra-Änderungen) |
| User-Beziehungen zu Narrativen | Narrative Expert |

## Auth und Supabase

Authentifizierung läuft über Supabase Auth.
RLS-Policies (Row Level Security) sind Infrastructure — DevOps Briefing erforderlich für Änderungen.
User-Objekte in `api/models/user*.py` bilden den Auth-State ab.

## Skills

| Skill | Wann aufrufen |
|---|---|
| `tdd` | Bei jeder neuen Feature-Implementierung |
| `qa-review` | Nach jeder Implementierung |

## DevOps Briefing

```
DevOps Briefing
Need:      [z.B. neue RLS-Policy oder Supabase-Config]
Why:       [Fachlicher Grund]
Domain:    [Database oder Config]
Impact:    [Community Domain, ggf. alle Agents die Auth nutzen]
```

## RC6 — Tacit Assumptions im Auth-Flow

Der Auth-Flow (`api/*/user*`) trägt besonders viele implizite Contracts:
- Pflichtfelder bei der Registrierung
- Erwartete Error-Codes im Frontend (z.B. bei doppelter E-Mail)
- Session-Handling-Semantik

Vor jeder Frontend-Welle: explizite Contracts formulieren und mit UX/UI abgleichen,
bevor die erste Zeile implementiert wird. (Mapping: RC6 — "unborn assumptions at seams")

## Erweiterung durch Community Expert Agent

Diese Datei enthält die Basis-Struktur. Der Community Expert ergänzt hier:
- User-Rollen und Berechtigungskonzept
- Community-Features (Kommentare, Bewertungen etc.)
- Auth-Flow im Detail
- Onboarding-Prozess für neue User
