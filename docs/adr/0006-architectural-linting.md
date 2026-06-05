# ADR 0006: Automatische Architektur-Prüfung

**Status:** Accepted  
**Datum:** 2026-06-05  
**Autoren:** Thorsten Dittmar

---

## Kontext

Architektur-Patterns sind in `CLAUDE.md` und den Skill-Dateien dokumentiert. Diese Dokumentation ist für Menschen und KI-Agenten lesbar — aber kein Tool prüft sie automatisch. Patterns wie "Repository-Methoden müssen zuerst loggen" oder "kein hardcoded String im JSX" werden nur durch Code Review entdeckt, wenn sie verletzt werden.

Das führt zu zwei Problemen:
1. **Drift**: Patterns werden im Laufe der Zeit unbewusst verletzt, besonders in agenten-generiertem Code
2. **Kein Feedback-Loop**: Wer ein Pattern verletzt, erfährt es nicht sofort

---

## Entscheidung

Wir treiben automatische Architektur-Prüfung **so weit wie tooling es erlaubt**.

**Grundregel:** Jedes Pattern das in `CLAUDE.md` oder einem Skill steht und automatisch prüfbar ist, bekommt eine entsprechende Lint-Regel. Nicht morgen — im selben Commit in dem das Pattern etabliert wird.

**Tool-Stack:**
- **Semgrep** — primäres Werkzeug für strukturelle Muster (language-agnostic, YAML-Regeln, ideal für Architektur-Patterns)
- **Custom ruff rules** — für Python-spezifische Patterns die nicht in Semgrep passen
- **Custom eslint rules** — für TypeScript/React-Patterns
- **Pre-commit hooks** — für Patterns die keine AST-Analyse brauchen (z.B. Dateinamen-Konventionen)

Semgrep ist das primäre Tool weil es:
- Muster auf Syntax-Ebene prüft (kein Regex auf Textebene)
- Cross-file Analysen ermöglicht
- Regeln in YAML schreibbar sind (lesbar, versionierbar)
- Python und TypeScript gleichermaßen abdeckt

---

## Patterns und ihre Regeln

### Backend (Python)

| Pattern | CLAUDE.md-Quelle | Semgrep-Regel |
|---|---|---|
| Repository-Methoden loggen als erste Aktion | Repository Logging | `klartext/repo-logs-first` |
| `debug` für Reads, `info` für Writes | Repository Logging | `klartext/repo-log-level` |
| Factory Methods `create()` + `from_record()` | Factory Methods | `klartext/factory-methods` |
| Kein direkter DB-Aufruf aus Service | Architektur | `klartext/no-db-in-service` |
| Exception-Klassen enden auf `Error` | Naming | `klartext/exception-naming` |
| Service-Klassen enden auf `Service` | Naming | `klartext/service-naming` |
| Repository-Klassen enden auf `Repository` | Naming | `klartext/repository-naming` |
| Jeder Router hat `/health`-Endpoint | Health Subendpoint | `klartext/router-health` |
| Kein `Optional[X]` — nur `X \| None` | Type Hints | via ruff UP007 (bereits aktiv) |
| Type Hints überall | Type Hints | via mypy (bereits aktiv) |

### Frontend (TypeScript/React)

| Pattern | Skill-Quelle | eslint-Regel |
|---|---|---|
| Kein `async` Handler ohne `finally` | frontend skill | `klartext/async-finally` |
| Keine String-Literale im JSX | i18n.md | `klartext/no-jsx-strings` |
| Keine Raw-Hex in `style={}` | do-dont.md | `klartext/no-hex-in-style` |
| Kein `width` auf Text-Elementen | i18n.md | `klartext/no-fixed-text-width` |
| Imports nur aus `lib/api.ts`, nicht aus `api/` | frontend skill | via tsc path aliases |

---

## Konsequenzen

- Semgrep wird in `api/` und `frontend/src/` als pre-commit Hook und CI-Check eingebunden
- Neue Patterns in CLAUDE.md oder Skills: erst Regel schreiben, dann Pattern dokumentieren — kein Pattern ohne Regel
- Falsch-Positive sind Anlass zur Regel-Verbesserung, nicht zum Ignorieren
- Die Regel-Dateien liegen unter `.semgrep/rules/` — versioniert, reviewed wie Code

---

## Alternativen die verworfen wurden

- **Nur Code Review**: Skaliert nicht mit agenten-generiertem Code — Menschen übersehen Patterns, Agenten auch
- **Nur mypy/ruff**: Decken Typ- und Stil-Patterns ab, aber keine Architektur-Patterns
- **pylint custom rules**: Mächtiger als ruff für custom checks, aber komplexer — Semgrep ist für diesen Use Case besser geeignet
