# CI/CD Onboarding — Was du wissen musst

Wir haben die Pipeline und lokale Entwicklungsumgebung erweitert.
Lies das bevor du neuen Code schreibst.

---

## Pre-commit Hooks sind aktiv

`bash setup.sh` installiert Hooks automatisch. Ein `git commit` wird
abgelehnt wenn einer dieser Checks fehlschlägt:

- **ruff lint** — Stil, Imports, Naming, Docstrings
- **ruff format** — Einheitliche Formatierung (line-length 100)
- **mypy** — Strikte Typen, Python 3.12
- **tach** — Layer-Grenzen zwischen Architekturschichten
- **eslint** — Frontend TypeScript/TSX Style
- **tsc** — Frontend Typecheck

Hooks manuell ausführen: `pre-commit run --all-files`

---

## Ruff: D- und N-Regeln sind neu

- Jede öffentliche Klasse und Funktion braucht einen Docstring
- @property-Getter, __init__ und Testfunktionen sind ausgenommen
- PEP8-Naming wird geprüft (inkl. Service, Repository als Suffix)

---

## tach: Layer-Grenzen werden erzwungen

```
routers    → services, schemas, models, exceptions, repositories (nur Ports)
services   → repositories, providers, parsers, models, exceptions, schemas
repositories → models, exceptions
providers  → models, exceptions
models     → exceptions
exceptions → (nichts)
```

Verstöße schlagen pre-commit und CI fehl.

---

## Zwei Pflicht-Pattern für neuen Code

**1. Supabase Repositories — records()-Cast:**

```python
from api.repositories._supabase import records

row = records(result.data)[0]          # statt result.data[0]
for row in records(result.data): ...   # statt for row in result.data
```

Ohne diesen Cast schlägt mypy fehl.

**2. Claude API — TextBlock-Guard:**

```python
first_block = response.content[0]
if not isinstance(first_block, anthropic.types.TextBlock):
    raise XxxError(f"Unexpected block type: {type(first_block)}")
raw = first_block.text.strip()
```

In Tests echte TextBlock-Instanzen verwenden, keine MagicMocks:

```python
block = anthropic.types.TextBlock(type="text", text="...")
mock_response.content = [block]
```
