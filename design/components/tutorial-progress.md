# TutorialProgress

## Purpose

Fortschritts-Anzeige für mehrstufige Onboarding-Tutorials — zeigt Schritt-Nummer, Gesamt-Anzahl und optional einen Fortschritts-Balken. Wird in Tutorial-Modals und Onboarding-Flows verwendet.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `steps` | Klare Schritt-Abfolge | „Schritt 2 von 5" + Fortschritts-Balken |
| `dots` | Kompakter Tutorial-Indikator | Punktreihe, aktiver Punkt hervorgehoben |
| `checklist` | Nicht-lineare Aufgaben | Checkliste mit Häkchen pro erledigtem Punkt |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `in-progress` | Nicht alle Schritte erledigt | Fortschritts-Balken teilweise gefüllt |
| `completed` | Alle Schritte erledigt | Voller Balken, optionale Erfolgs-Animation |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `currentStep` | `number` | yes | — | Aktueller Schritt (1-basiert) |
| `totalSteps` | `number` | yes | — | Gesamt-Anzahl Schritte |
| `variant` | `"steps" \| "dots" \| "checklist"` | no | `"steps"` | Anzeigeformat |
| `stepLabels` | `string[] \| null` | no | `null` | Optionale Labels pro Schritt (für `checklist`) |

---

## Rules

- `currentStep` ist 1-basiert
- `stepLabels` muss genau `totalSteps` Einträge haben wenn übergeben
- `checklist`-Variante zeigt alle Schritte als Liste — `currentStep` markiert wie viele erledigt sind

---

## Accessibility

- `aria-label` beschreibt den Fortschritt: `"Schritt 2 von 5"`
- Fortschritts-Balken: `role="progressbar"` + `aria-valuenow` + `aria-valuemax`
- Dots: `aria-label` auf aktivem Dot

---

## Code Pattern

```tsx
<TutorialProgress
  currentStep={tutorialStep}
  totalSteps={5}
  variant="dots"
/>
```

---

## Do / Don't

❌ TutorialProgress außerhalb von Tutorial/Onboarding-Kontext
✅ Für alle mehrstufigen Onboarding-Flows konsistent verwenden

---

## Missing Information Protocol

```tsx
// TODO(design): Fortschritts-Balken-Farbe als Token — Issue #TODO
// TODO(design): Dot-Größe und Abstand — Issue #TODO
// TODO(ux): Tutorial-Inhalte und Schritte noch nicht definiert — Issue #TODO
```

---

## Related

- `step-indicator.md` — Einzelner Schritt-Indikator in Wizard-Flows
- `modal.md` — TutorialProgress oft innerhalb von Tutorial-Modals
