# HelpMenu

## Purpose

Dropdown-Menü für Hilfe und Support-Ressourcen — öffnet über einen „?" oder Hilfe-Button in der AppBar oder BottomBar. Enthält Links zu Dokumentation, Tastenkürzel, Tutorial-Start und Support-Kontakt.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standard Hilfe-Dropdown | Vertikale Liste mit Hilfe-Items |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `closed` | Standard | Nur Trigger-Button sichtbar |
| `open` | Klick auf Trigger | Dropdown-Liste sichtbar |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `isOpen` | `boolean` | yes | — | Sichtbarkeit |
| `onClose` | `() => void` | yes | — | Schließen-Callback |
| `onStartTutorial` | `(() => void) \| null` | no | `null` | Tutorial starten |
| `onShowShortcuts` | `(() => void) \| null` | no | `null` | Tastenkürzel-Übersicht |
| `docsUrl` | `string \| null` | no | `null` | Link zur Dokumentation |

---

## Rules

- HelpMenu öffnet nie extern ohne Bestätigung — externe Links öffnen in neuem Tab
- Tastenkürzel-Item zeigt Modal oder Panel — kein direktes Navigieren
- Tutorial-Item startet den Onboarding-Flow neu
- Menü schließt bei Auswahl oder Klick außerhalb

---

## Accessibility

- Analog zu `context-menu.md`: `role="menu"` + `role="menuitem"`
- Keyboard: Arrow Keys + Enter + Escape

---

## Code Pattern

```tsx
<HelpMenu
  isOpen={helpOpen}
  onClose={() => setHelpOpen(false)}
  onStartTutorial={startTutorial}
  onShowShortcuts={() => setShortcutsModalOpen(true)}
  docsUrl="https://docs.klartext.jetzt"
/>
```

---

## Do / Don't

❌ Anwendungs-Aktionen (Speichern, Export) im HelpMenu
✅ Nur Hilfe und Dokumentations-Ressourcen

---

## Missing Information Protocol

```tsx
// TODO(ux): Welche Hilfe-Items konkret enthalten sein sollen — Issue #TODO
// TODO(ux): Tastenkürzel-Panel — eigene Komponente oder Modal? — Issue #TODO
// TODO(design): Trigger-Button Stil und Position — Issue #TODO
```

---

## Related

- `context-menu.md` — Technisch ähnlich, anderen Kontext
- `modal.md` — Tastenkürzel-Übersicht öffnet Modal
- `tutorial-progress.md` — Tutorial wird über HelpMenu gestartet
- `bottom-bar.md` — HelpMenu-Trigger oft in der BottomBar
