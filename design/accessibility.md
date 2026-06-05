# Accessibility

## Grundprinzip

Accessibility ist kein nachträglicher Add-on. Jede Komponente wird von Anfang an
zugänglich gebaut. Diese Regeln sind verbindlich — kein "schöner, aber nicht nötig".

---

## Interaktive Elemente

### Zugänglicher Name (Pflicht)

Jedes interaktive Element braucht einen zugänglichen Namen.
Screenreader können ohne ihn die Funktion nicht kommunizieren.

**Button mit sichtbarem Text:** kein Extra-Attribut nötig
```tsx
<button>{t('actions.save')}</button>
```

**Icon-Button ohne sichtbaren Text:** `aria-label` Pflicht
```tsx
<button aria-label={t('actions.close_panel')} onClick={onClose}>
  ✕
</button>
```

**Button mit Spinner statt Text im Loading-State:**
```tsx
<button disabled={isLoading} aria-busy={isLoading}>
  {isLoading ? <Spinner aria-hidden="true" /> : t('actions.save')}
</button>
```

### Fokus-Sichtbarkeit

Alle interaktiven Elemente müssen einen sichtbaren Fokus-Indikator haben.
Browser-Standard (`outline`) ist akzeptabel — nur entfernen wenn gleichwertiger Ersatz vorhanden.

❌
```tsx
style={{ outline: "none" }}  // Fokus unsichtbar — verboten
```

✅
```tsx
// Browser-Standard belassen — oder expliziter Custom-Fokus-Ring
style={{ outlineOffset: "2px" }}
```

---

## Farbe als einziges Unterscheidungsmerkmal

Farbe darf **nie** das einzige Unterscheidungsmerkmal sein.

❌ Nur Farbe zeigt den Status:
```tsx
<span style={{ color: "var(--color-red-text)" }}>{t('status.error')}</span>
```

✅ Farbe + Text + (optional) Icon:
```tsx
<span style={{ color: "var(--color-red-text)" }}>
  ⚠ {t('status.error')}
</span>
```

**Gilt für:** Status-Badges, Formulare (Fehler-Felder), Diagramme, Karten.

---

## Semantisches HTML

Native HTML-Elemente verwenden wo möglich — sie bringen Semantik und Keyboard-Support kostenlos.

| Wenn... | Dann... |
|---|---|
| Klick führt eine Aktion aus | `<button>` |
| Klick navigiert zu einer URL | `<a href="...">` |
| Eingabe eines Wertes | `<input>` |
| Auswahl aus Optionen | `<select>` oder `<fieldset>` + `<input type="radio">` |
| Strukturelle Überschrift | `<h1>` bis `<h6>` (Hierarchie einhalten) |
| Navigationsbereiche | `<nav>` |
| Hauptinhalt | `<main>` |

❌
```tsx
<div onClick={handleSave}>Speichern</div>   // kein Keyboard, kein Screenreader
```

✅
```tsx
<button onClick={handleSave}>{t('actions.save')}</button>
```

---

## Formulare

Jedes Formularfeld braucht ein sichtbares oder programmatisch verknüpftes Label.

```tsx
// Explizites Label via htmlFor
<label htmlFor="narrative-title">{t('fields.title')}</label>
<input id="narrative-title" type="text" value={title} onChange={...} />

// Oder aria-label wenn kein sichtbares Label möglich
<input
  aria-label={t('fields.search')}
  type="search"
  placeholder={t('fields.search_placeholder')}
/>
```

Fehlermeldungen mit `role="alert"` damit Screenreader sie sofort vorlesen:
```tsx
{error && (
  <p role="alert" style={{ color: "var(--color-red-text)" }}>
    {t('errors.save_failed')}
  </p>
)}
```

---

## Keyboard-Navigation

Modale Dialoge und Overlays: Fokus muss beim Öffnen ins Modal wechseln,
beim Schließen zurück zum auslösenden Element.

Escape: schließt Overlays, Dropdowns, Modals (Konvention, wird erwartet).

Tab-Reihenfolge: folgt der visuellen Lesereihenfolge (kein tabIndex > 0).

---

## Bilder und Icons

Dekorative Icons (kein inhaltlicher Mehrwert):
```tsx
<span aria-hidden="true">→</span>
```

Informative Icons (tragen Bedeutung):
```tsx
<img src="..." alt={t('icons.causal_model_alt')} />
// oder
<span role="img" aria-label={t('icons.causal_model_alt')}>⊕</span>
```

---

## ARIA-Regeln

- `aria-*`-Attribute nur wenn kein natives HTML-Äquivalent existiert
- `aria-hidden="true"` für rein dekorative Elemente
- `aria-busy="true"` für Bereiche die sich asynchron aktualisieren
- `aria-live="polite"` für Status-Updates die nicht sofort vorgelesen werden sollen
- `role="alert"` nur für Fehler und wichtige Statusänderungen (wird sofort vorgelesen)

---

## Nicht in Scope (vorerst)

Diese Punkte sind bekannt aber derzeit nicht priorisiert:

- Vollständige WCAG 2.1 AA Zertifizierung
- Screen-Magnification-Tests
- Hoher Kontrast-Modus (Windows High Contrast)
- Sprachausgabe-Tests mit NVDA / JAWS

Sie werden als Issues erfasst wenn das Produkt in Richtung Public Beta geht.
