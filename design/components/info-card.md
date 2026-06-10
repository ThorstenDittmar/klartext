# InfoCard

## Purpose

Umrandete Karte für systemische Hinweise die eine Nutzer-Aktion erfordern — z.B. fehlende Konfiguration, Verbindungsproblem, Onboarding-Schritt. Nicht für Erfolgs- oder Fehler-Feedback auf Aktionen.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `info` | Neutrale Information oder Setup-Hinweis | Blau/neutral, Icon optional |
| `warning` | Warnung vor potentiellem Problem | Gelb/orange |
| `error` | Fehlerzustand der Aufmerksamkeit erfordert | Rot |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `dismissible` | Card kann geschlossen werden | Schließen-X in der oberen rechten Ecke |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `title` | `string` | yes | — | Kurze prägnante Überschrift |
| `description` | `string` | yes | — | Erklärungstext |
| `variant` | `"info" \| "warning" \| "error"` | no | `"info"` | Visueller Typ |
| `actionLabel` | `string \| null` | no | `null` | Label für CTA-Button |
| `onAction` | `(() => void) \| null` | no | `null` | Callback für CTA |
| `onDismiss` | `(() => void) \| null` | no | `null` | Schließen — null = nicht schließbar |

---

## Rules

- Titel und Description immer via `t('key')`
- InfoCard ist kein Toast — bleibt sichtbar bis der Nutzer reagiert oder sie dismisst
- Maximal eine InfoCard pro Seitenbereich

---

## Accessibility

- `role="status"` für info-Variante, `role="alert"` für error-Variante
- CTA-Button folgt Button-Spec
- Schließen-Button mit `aria-label`

---

## Code Pattern

```tsx
<InfoCard
  title={t("ai.connection_required.title")}
  description={t("ai.connection_required.description")}
  actionLabel={t("ai.connection_required.action")}
  onAction={() => navigate("/settings")}
/>
```

---

## Do / Don't

❌ InfoCard für Erfolgs-Feedback nach Aktionen
✅ Toast oder inline Success-State für Aktions-Feedback

❌ InfoCard mitten in Fließtext einbetten
✅ InfoCard als eigenständigen Block zwischen Inhaltsbereichen

---

## Missing Information Protocol

```tsx
// TODO(design): Varianten-Farben als Tokens — Issue #TODO
// TODO(design): Rand-Stil (dashed/solid) definieren — Issue #TODO
```

---

## Related

- `empty-state.md` — für leere Datenbereiche
- `modal.md` — für blockierende Hinweise die eine Entscheidung erfordern
- `button.md` — CTA in der InfoCard
