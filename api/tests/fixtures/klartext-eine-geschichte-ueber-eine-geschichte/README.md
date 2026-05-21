# Testfall: „Klartext – Eine Geschichte über eine Geschichte"

**Zweck:** Primärer Entwicklungs- und Integrationstestfall für klartext.jetzt

Dieser Testfall ist metafiktional: Die Geschichte beschreibt die Entstehung von klartext.jetzt selbst.
Sie eignet sich als Fixture weil sie das zentrale Wirkmodell der Plattform (epistemische Transparenz)
narrativ verkörpert und mehrere Claim-Typen, implizite Annahmen und Kausalrelationen enthält.

## Dateien

| Datei | Inhalt |
|---|---|
| `narrative.md` | Vollständiger narrativer Text (15 Szenen) |
| `wirkmodell.md` | Axiomraum, Claims und Kausalrelationen der Geschichte |

## Verwendung in Tests

```python
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures/klartext-eine-geschichte-ueber-eine-geschichte"

def load_narrative() -> str:
    return (FIXTURE / "narrative.md").read_text()

def load_wirkmodell() -> dict:
    # Wirkmodell als strukturierte Testdaten
    ...
```

## Erwartete Claim-Extraktion (Referenzwerte)

Bei `POST /extract-claims` mit Szene 2 werden mindestens folgende Claims erwartet:

- **kausaler_claim:** Unsichtbare Annahmen führen zu Scheindiskursen
- **kausaler_claim:** Fehlende Explizierung von Annahmen erzeugt Polarisierung
- **empirischer_claim:** Diskursteilnehmer kennen die Grundannahmen ihrer Gesprächspartner nicht
