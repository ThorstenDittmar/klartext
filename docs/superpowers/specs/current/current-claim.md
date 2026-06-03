# Spec: Claim — aktueller Implementierungsstand

**Datum:** 2026-05-29
**Status:** Implementiert
**Scope:** Claim-Extraktion und -Speicherung. Beschreibt was heute im
Code existiert, nicht die Zielarchitektur.

Zur Zielarchitektur: → `specs/2026-06-03-claim.md`

---

## Überblick

Ein Claim ist heute ein reines Analyseprodukt: eine Aussage die aus
dem Text einer Szene per LLM extrahiert wurde, mit Typ und
Confidence-Wert. Er ist kein `DocumentAsset` und hat keine Verbindung
zum Wirkgefüge.

---

## Claim

### Attribute

| Attribut | Typ | Beschreibung |
|---|---|---|
| `id` | `str` | UUID |
| `text` | `str` | Extrahierter Wortlaut der Aussage |
| `typ` | `str` | Claim-Typ (siehe unten) |
| `confidence` | `float` | 0.0–1.0; Sicherheit der Extraktion |

### Claim-Typen

```
empirischer_claim
kausaler_claim
definitorischer_claim
normativer_claim
prognostischer_claim
kontrafaktischer_claim
methodischer_claim
unsicherheitsclaim
```

Die Typen stammen aus dem Konzeptdokument (Kap. 7.3.6). Sie sind
reine String-Werte — kein Python-Enum.

**Hinweis:** Die Zielarchitektur bildet diese Typen auf Wirkgefüge-Strukturen
ab (z.B. `kausaler_claim` → `CausalRelation`). In der aktuellen
Implementierung ist der Typ nur ein Label.

---

## Extraktion

### ClaimExtractorService

Orchestriert die Extraktion. Delegiert den LLM-Aufruf an einen
`ClaimExtractionProvider`.

```python
service.extract_claims(scene_text: str) -> list[Claim]
```

### ClaudeClaimExtractionProvider

Konkrete Implementierung des `ClaimExtractionProvider`-Ports.
Schickt den Szenentext an Claude (Anthropic API) und parst das
JSON-Ergebnis zurück zu einer `list[Claim]`.

### Ports-and-Adapters

```
ClaimExtractionProvider (abstrakt, Port)
  └── ClaudeClaimExtractionProvider (Adapter)
```

In Tests: `FakeClaimExtractionProvider` gibt deterministische Claims zurück.

---

## Speicherung

Claims werden pro Szene extrahiert und persistent gespeichert.
Eine neue Extraktion überschreibt vorhandene Claims der Szene.

### Datenbank

Tabelle: `claims`

| Spalte | Typ | Anmerkung |
|---|---|---|
| `id` | UUID PK | |
| `scene_id` | UUID NOT NULL | FK → `narrative_units.id` ON DELETE CASCADE |
| `text` | TEXT NOT NULL | |
| `typ` | TEXT NOT NULL | Claim-Typ-String |
| `confidence` | DOUBLE PRECISION | CHECK: 0.0–1.0 |
| `created_at` | TIMESTAMPTZ | |

---

## API-Endpunkte

```
POST /narratives/{id}/scenes/{scene_id}/extract-claims
    → Extraktion auslösen; liefert {claims: [...]}

GET  /narratives/{id}/scenes/{scene_id}/claims
    → Gespeicherte Claims einer Szene abrufen

POST /claims/extract
    → Extraktion aus freiem Text ohne Narrativ-Kontext {text: str}
```

---

## Was fehlt (bewusste Vereinfachungen)

- Kein `ClaimStatus` (kein `DRAFT`, `LINKED`, `UNRESOLVED`)
- Keine Verbindung zum Wirkgefüge (`wirkgefuege_ref`)
- Keine `DocumentLink`-Navigation (wo kommt der Claim im Text vor?)
- Kein `label` — nur `text` (der ursprüngliche Wortlaut)
- Claims blockieren nicht die Veröffentlichung
- Keine Audience-Steuerung
