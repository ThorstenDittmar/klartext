# Modal

## Purpose

Zentriertes Overlay-Fenster mit Backdrop — für Aktionen die eine explizite Nutzerentscheidung erfordern (Bestätigung, Formular, Tip-Anzeige). Blockiert die darunter liegende UI.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `confirm` | Destruktive oder irreversible Aktionen bestätigen | Titel, Text, Abbrechen + Bestätigen-Button |
| `info` | Information oder Tutorial-Tip anzeigen | Titel, Inhalt, Zurück/Weiter-Navigation, Schließen |
| `form` | Formular-Eingabe im Dialog | Titel, Formular-Felder, Abbrechen + Speichern |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `open` | Modal wird geöffnet | Backdrop erscheint, Modal-Container zentriert |
| `closed` | Schließen-Button oder Backdrop-Klick | Modal + Backdrop ausgeblendet |
| `loading` | Async-Aktion im Modal läuft | Primary-Button disabled + Loading-State |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `isOpen` | `boolean` | yes | — | Sichtbarkeit des Modals |
| `onClose` | `() => void` | yes | — | Callback beim Schließen |
| `title` | `string` | yes | — | Modal-Titel (via t()-Key) |
| `children` | `React.ReactNode` | yes | — | Modal-Inhalt |
| `onConfirm` | `(() => Promise<void>) \| null` | no | `null` | Primäre Bestätigungs-Aktion |
| `confirmLabel` | `string` | no | — | Label für Bestätigen-Button |
| `isDestructive` | `boolean` | no | `false` | Confirm-Button in Danger-Farbe |
| `closeOnBackdrop` | `boolean` | no | `true` | Klick auf Backdrop schließt Modal |

---

## Rules

- Focus wird beim Öffnen in den Modal-Container verschoben (Focus Trap)
- Escape schließt das Modal immer (außer während Async-Aktion)
- Titel immer via `t('key')`, nie hardcoded
- Backdrop verhindert Scroll des darunter liegenden Inhalts
- Kein Modal über Modal — maximal ein Modal zur Zeit

---

## Accessibility

- `role="dialog"` + `aria-modal="true"` auf dem Modal-Container
- `aria-labelledby` zeigt auf die Titel-ID
- Focus Trap: Tab-Navigation bleibt im Modal
- Escape schließt den Dialog
- Backdrop: nicht fokussierbar, aber klickbar zum Schließen

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
// Referenz: Radix UI Dialog Primitive als headless Unterbau erwägen (ADR-0007)
```

---

## Do / Don't

❌ Modal für nicht-kritische Information verwenden
✅ Toast/InfoCard für nicht-blockierende Nachrichten

❌ Modal ohne Focus Trap implementieren
✅ Radix Dialog Primitive oder eigene Focus-Trap-Logik verwenden

---

## Missing Information Protocol

```tsx
// TODO(design): Backdrop-Farbe und Opacity — Issue #TODO
// TODO(design): Modal-Breite Varianten — Issue #TODO
// TODO(design): Entry/Exit-Animation — Issue #TODO
// TODO(pattern): Focus Trap Implementierung — Issue #TODO
```

---

## Related

- `button.md` — Aktions-Buttons im Modal-Footer
- `detail-panel.md` — Alternative für nicht-blockierende Detail-Ansichten
- `design/patterns/` — dialog-pattern (noch nicht geschrieben)
