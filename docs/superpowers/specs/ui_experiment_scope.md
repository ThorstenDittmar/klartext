# UI-Addendum: Experiment Scope

**Datum:** 2026-06-04
**Bezug:** experiment_scope.md
**Scope:** Minimale UI-Erweiterungen für den Experiment-Workflow.
Kein vollständiges UI — Erweiterung der bestehenden React-Screens.
Zielarchitektur aus ui_spec.md wird NICHT implementiert.

---

## Prinzip

Alle vier Screens sind einfache listenbasierte Layouts.
Kein Sidebar, kein RightPanel, kein Graph.
Jeder Screen hat einen klaren primären Aktionsbereich.
Farben folgen den semantischen Konventionen aus ui_spec.md.

---

## Screen 1 — Narrativ-Detail

Bestehender Screen. Einzige Änderung: ein neuer Button.

```
[Narrativ-Titel]
[Szenen-Liste]

──────────────────────────────────
[Analysieren →]
──────────────────────────────────
```

**Button "Analysieren":**
- Primär-Button, volle Breite oder rechtsbündig
- Ladezustand: `Analyse läuft...` + Spinner, Button disabled
- Erfolgszustand: weiterleiten zu Screen 2
- Fehlerzustand: Inline-Fehlermeldung unter dem Button

---

## Screen 2 — Analyse-Ergebnis

Neuer Screen. Erreichbar nach erfolgreichem `/narratives/{id}/analyse`.

**Layout:**

```
← Zurück zu Narrativ

Analyse: {narrativ_title}
{N} Actors gefunden · {M} Claims gefunden

────────────────────────────────────────
ACTORS
────────────────────────────────────────

[Actor-Karte]
[Actor-Karte]
...

[Alle bestätigen]

────────────────────────────────────────
CLAIMS
────────────────────────────────────────

[Claim-Karte]
[Claim-Karte]
...

[Alle bestätigen]

────────────────────────────────────────
[Wirkgefüge-Vorschläge generieren →]
```

**Actor-Karte:**
```
┌─────────────────────────────────────────┐
│ [user-icon] Maria Schneider             │
│ individual · Szene 1, Szene 3           │
│                          [✓] [✗]        │
└─────────────────────────────────────────┘
```
- Bestätigt: grüner linker Rand (`border-left:3px solid #1D9E75`)
- Verworfen: ausgegraut, durchgestrichen
- `entity_suggestion` wenn vorhanden:
  `→ Entity-Vorschlag: "zentralbank"` in amber

**Claim-Karte:**
```
┌─────────────────────────────────────────┐
│ CO₂-Emissionen steigen          91%     │
│ "Die Emissionen stiegen seit Jahren..." │
│ empirischer_claim                       │
│ → Slot: co2_emissionen / steigend       │
│                          [✓] [✗]        │
└─────────────────────────────────────────┘
```
- Confidence-Prozent: rechtsbündig, 11px
  ≥80%: grün, 60–79%: amber, <60%: rot
- Wirkgefüge-Vorschlag: kursiv, `color-text-secondary`
- Bestätigt: grüner linker Rand
- Verworfen: ausgegraut

**Button "Wirkgefüge-Vorschläge generieren":**
- Nur aktiv wenn mindestens ein Claim bestätigt wurde
- Führt `/narratives/{id}/suggest-wirkgefuege` aus
- Weiterleitung zu Screen 3

---

## Screen 3 — Wirkgefüge-Vorschlag

Neuer Screen. Erreichbar nach `/narratives/{id}/suggest-wirkgefuege`.

**Layout:**

```
← Zurück zur Analyse

Wirkgefüge-Vorschlag für: {narrativ_title}

────────────────────────────────────────
SLOTS ({N})
────────────────────────────────────────

[Slot-Karte]
[Slot-Karte]
...

────────────────────────────────────────
KAUSALRELATIONEN ({M})
────────────────────────────────────────

[Relation-Karte]
[Relation-Karte]
...

────────────────────────────────────────
Modellname: [________________]
[CausalModel anlegen und speichern →]
```

**Slot-Karte:**
```
┌─────────────────────────────────────────┐
│ co2_emissionen                  [✎]     │
│ physical_quantity               [✗]     │
│ Aus Claim: "CO₂-Emissionen steigen"     │
└─────────────────────────────────────────┘
```
- Identifier editierbar via Inline-Edit `[✎]`
- `slot_type` als Dropdown: physical_quantity / trend /
  social_quantity / abstract_entity
- Aus-Claim-Referenz: 10px, `color-text-tertiary`

**Relation-Karte:**
```
┌─────────────────────────────────────────┐
│ co2_emissionen (hoch)                   │
│   → Treibhauseffekt →                   │
│ global_temperatur (steigend)            │
│                                         │
│ Mechanismus: [Treibhauseffekt____] [✎]  │
│ EpistemicStatus: [incomplete ▾]         │
│ Aus Claim: "Hohe Emissionen verur..."   │
│                              [✗]        │
└─────────────────────────────────────────┘
```
- Mechanismus: inline editierbar
- EpistemicStatus: Dropdown: incomplete / axiomatic
- Verworfen: ausgegraut

**Modellname-Input:** Pflichtfeld, blockiert Speichern wenn leer.

**Button "CausalModel anlegen und speichern":**
- Legt CausalModel an, fügt alle bestätigten Slots und Relationen ein,
  verknüpft Narrativ, setzt alle bestätigten Claims auf LINKED
- Ladezustand: `Speichere...`
- Weiterleitung zu Screen 4

---

## Screen 4 — CausalModel-Detail

Bestehender Screen erweitert. Bisher nur Axiome — jetzt auch
Slots und Relationen.

**Layout:**

```
[CausalModel-Titel]
Status: {status}

────────────────────────────────────────
SLOTS ({N})
────────────────────────────────────────
identifier          slot_type           epistemic_status
co2_emissionen      physical_quantity   incomplete
global_temperatur   physical_quantity   incomplete

────────────────────────────────────────
KAUSALRELATIONEN ({M})
────────────────────────────────────────
Quelle              Ziel                Mechanismus
co2_emissionen      global_temperatur   Treibhauseffekt
  (hoch) →            (steigend)

────────────────────────────────────────
AXIOME ({K})           ← bestehend
────────────────────────────────────────
...

────────────────────────────────────────
VERKNÜPFTE NARRATIVE
────────────────────────────────────────
[book] Klartext  →
```

**Tabellen-Stil:**
- `font-size:12px`
- Kopfzeile: `color-text-tertiary`, `border-bottom`
- Zeilen: `border-bottom:color-border-tertiary`
- EpistemicStatus als Badge (amber = incomplete, grün = axiomatic)

---

## Farb- und Badge-Referenz

| Zustand | Hintergrund | Text |
|---|---|---|
| bestätigt / linked | #EAF3DE | #3B6D11 |
| draft / incomplete | #FAEEDA | #854F0B |
| verworfen / error | #FCEBEB | #A32D2D |
| entity-vorschlag | #E1F5EE | #0F6E56 |
| confidence ≥80% | #EAF3DE | #3B6D11 |
| confidence 60–79% | #FAEEDA | #854F0B |
| confidence <60% | #FCEBEB | #A32D2D |

---

## Was explizit NICHT gebaut wird

- Kein Sidebar, kein RightPanel, kein Graph-View
- Keine Hüllkurve, kein Popup-Overlay
- Keine PerspectiveToggle-Logik
- Kein Focus-Node-Prinzip
- Alles aus ui_spec.md — das ist Phase 2
