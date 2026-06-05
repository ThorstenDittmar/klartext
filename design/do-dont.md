# Do / Don't — Verbotene Muster

Diese Datei ist Teil des Quality Checks vor jeder Code-Ausgabe.
Der Frontend-Agent prüft jede dieser Regeln bevor er committed.

---

## Farben

❌ Raw Hex-Werte direkt im Style-Objekt
```tsx
style={{ color: "#1A1A1A", background: "#EAF3DE" }}
```

✅ CSS Custom Properties aus den Design Tokens
```tsx
style={{ color: "var(--color-text-primary)", background: "var(--color-green-bg)" }}
```

**Warum:** Wenn ein Token geändert wird, zieht die Änderung durch alle Komponenten.
Hardcoded Hex-Werte erzeugen stille Abweichungen.

---

## Breiten auf Textelementen

❌ Feste Breite auf Buttons oder Labels
```tsx
<button style={{ width: "80px" }}>Speichern</button>
<button style={{ width: "120px" }}>{t("actions.confirm")}</button>
```

✅ Innenabstand statt Breite
```tsx
<button style={{ padding: "8px 16px" }}>{t("actions.confirm")}</button>
```

**Warum:** Deutsch ist typischerweise 20-40% länger als Englisch.
Feste Breiten führen zu abgeschnittenen oder gestauchten Texten bei Sprachwechsel.

---

## Hardcoded User-Facing Strings

❌ Direkt eingebetteter Text (egal in welcher Sprache)
```tsx
<button>Speichern</button>
<p>Es ist ein Fehler aufgetreten.</p>
<h2>Narrativ-Editor</h2>
```

✅ i18n-Key via t()
```tsx
<button>{t("actions.save")}</button>
<p>{t("errors.generic")}</p>
<h2>{t("screens.narrative_editor.title")}</h2>
```

**Ausnahme:** Technische Platzhalter in Entwicklung: `t("TODO.component.element")` —
muss als Issue markiert und vor Release aufgelöst werden.

---

## Async ohne Loading-Reset

❌ Loading-State wird nur im Fehlerfall zurückgesetzt
```tsx
const handleSave = async () => {
  setLoading(true);
  try {
    await save();
    // vergisst setLoading(false) im Erfolgsfall
  } catch (e) {
    setLoading(false);
  }
};
```

❌ Loading-State wird überhaupt nicht zurückgesetzt
```tsx
const handleSave = async () => {
  setLoading(true);
  await save();
  // kein Reset — Button bleibt dauerhaft deaktiviert
};
```

✅ finally garantiert den Reset auf beiden Pfaden
```tsx
const handleSave = async () => {
  setLoading(true);
  try {
    await save();
  } finally {
    setLoading(false); // immer — Erfolg UND Fehler
  }
};
```

---

## Imports aus dem Backend

❌ Direktimport aus dem API-Layer
```tsx
import { NarrativeService } from "../../../api/services/narrative_service";
import type { NarrativeAnalysisResult } from "../../../api/providers/...";
```

✅ Nur über die Frontend-API-Schicht
```tsx
import { api } from "../lib/api";
// Typen nur aus api.ts importieren
import type { AnalyseNarrativeResponse } from "../lib/api";
```

---

## Eigene Designentscheidungen

❌ Einen fehlenden Token erfinden
```tsx
// Token fehlt → einfach einen neuen Wert nehmen
style={{ color: "#2C5F2E" }}  // nicht in colors.json
```

❌ Eine undokumentierte Komponenten-Variante einführen
```tsx
// "warning"-Variante existiert nicht im Button-Spec
<Button variant="warning">…</Button>
```

✅ Fehlenden Token als GitHub Issue melden
```tsx
// TODO(token): needs color.semantic.success — Issue #XX
style={{ color: "var(--color-green-text)" }}  // vorläufiger Closest-Match
```

---

## CSS in index.css

❌ Komponentenspezifische Styles in die globale index.css schreiben
```css
/* index.css */
.narrative-card { border-radius: 8px; padding: 16px; }
```

✅ Inline Styles direkt an der Komponente
```tsx
<div style={{ borderRadius: "8px", padding: "16px" }}>…</div>
```

**Ausnahme:** `index.css` enthält nur CSS Custom Properties (Design Tokens)
und globale Resets (`*, body`). Niemals Komponenten-Styles.

---

## Spacing-Werte

❌ Beliebige Pixel-Werte
```tsx
style={{ padding: "13px", margin: "7px", gap: "22px" }}
```

✅ Werte aus dem Spacing-Token-Set (spacing.json)
```tsx
style={{ padding: "12px", margin: "8px", gap: "20px" }}
//       spacing.md=12    spacing.sm=8  spacing.xl=20
```

---

## Fehlende Informationen

❌ Annahmen stillschweigend treffen und keine Markierung hinterlassen

✅ Explizit markieren und Issue anlegen
```tsx
// TODO(design): no spec for error state of this component — Issue #XX
// Using amber semantic color as interim assumption
style={{ background: "var(--color-amber-bg)" }}
```
