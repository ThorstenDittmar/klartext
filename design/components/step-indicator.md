# StepIndicator

## Purpose

Visueller Indikator für einen einzelnen Schritt in einem mehrstufigen Wizard oder Setup-Flow — zeigt Schritt-Nummer oder Icon plus Titel und optional Status (abgeschlossen, aktiv, ausstehend). Mehrere StepIndicators bilden gemeinsam eine Wizard-Navigation.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `horizontal` | Wizard-Header (oben) | Schritt-Kreise in einer Zeile verbunden durch Linien |
| `vertical` | Sidebar-Wizard | Schritt-Kreise untereinander mit vertikalen Verbindungslinien |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `pending` | Schritt noch nicht erreicht | Grauer Kreis, gedimmter Text |
| `active` | Aktueller Schritt | Hervorgehobener Kreis (Primärfarbe), fetter Text |
| `completed` | Schritt abgeschlossen | Checkmark-Icon im Kreis, grün |
| `error` | Schritt hat Fehler | Fehler-Icon im Kreis, rot |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `stepNumber` | `number` | yes | — | Schritt-Nummer (1-basiert) |
| `label` | `string` | yes | — | Schritt-Titel (via t()-Key) |
| `status` | `"pending" \| "active" \| "completed" \| "error"` | yes | — | Aktueller Status |
| `variant` | `"horizontal" \| "vertical"` | no | `"horizontal"` | Ausrichtung |
| `isClickable` | `boolean` | no | `false` | Erlaubt Navigation zu abgeschlossenen Schritten |
| `onClick` | `(() => void) \| null` | no | `null` | Callback wenn `isClickable` |

---

## Rules

- StepIndicator ist read-only außer wenn `isClickable = true`
- Nur `completed`-Schritte können navigierbar sein
- Verbindungs-Linie zwischen Schritten gehört zum StepIndicator-Wrapper, nicht zum einzelnen Indikator
- Labels kurz halten (max ~3 Wörter)

---

## Accessibility

- `aria-label` beschreibt Schritt und Status: „Schritt 2: Kapitel — abgeschlossen"
- Aktiver Schritt: `aria-current="step"`
- Klickbarer Schritt: Fokussierbar, Enter aktiviert

---

## Code Pattern

```tsx
<div className="wizard-steps">
  {steps.map((step, i) => (
    <StepIndicator
      key={step.id}
      stepNumber={i + 1}
      label={t(step.labelKey)}
      status={getStepStatus(i, currentStep)}
      isClickable={i < currentStep}
      onClick={i < currentStep ? () => goToStep(i) : null}
    />
  ))}
</div>
```

---

## Do / Don't

❌ Mehr als 6 Schritte in einem Wizard
✅ Wizard bei komplexen Flows in Phasen aufteilen

❌ `pending`-Schritt klickbar machen
✅ Nur `completed`-Schritte navigierbar

---

## Missing Information Protocol

```tsx
// TODO(design): Schritt-Kreis-Größe und Verbindungs-Linie als Tokens — Issue #TODO
// TODO(design): Status-Farben und Icons — Issue #TODO
// TODO(ux): Wann werden Wizard-Flows im Produkt eingesetzt? — Issue #TODO
```

---

## Related

- `tutorial-progress.md` — Für Tutorial-Onboarding (nicht Wizards)
- `modal.md` — Wizard oft in einem Modal
