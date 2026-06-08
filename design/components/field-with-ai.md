# FieldWithAi

## Purpose

Erweiterung eines Text-Eingabefelds (TextInput oder TextArea) mit KI-Unterstützung — ein AI-Button öffnet einen Kontextmenü oder direkt eine KI-Generierung. Für Felder bei denen KI sinnvoll Vorschläge oder Texte generieren kann.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `suggest` | KI macht einen Vorschlag den der User übernehmen kann | AI-Button öffnet Vorschlag-Panel unter dem Feld |
| `generate` | KI generiert direkt in das Feld | AI-Button mit Ladestate, Inhalt wird ins Feld geschrieben |
| `enhance` | KI verbessert vorhandenen Text | AI-Button nur aktiv wenn Feld nicht leer |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `idle` | Standard | AI-Button sichtbar, nicht aktiv |
| `loading` | KI generiert | Button zeigt Spinner, Feld disabled |
| `suggestion-shown` | Vorschlag vorhanden | Vorschlag-Panel unterhalb sichtbar |
| `error` | KI-Fehler | Fehler-Meldung unterhalb, Button reaktiviert |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `fieldComponent` | `"input" \| "textarea"` | yes | — | Basis-Feld-Typ |
| `value` | `string` | yes | — | Kontrollierter Wert |
| `onChange` | `(value: string) => void` | yes | — | Callback bei Änderung |
| `onAiRequest` | `() => Promise<string>` | yes | — | AI-Anfrage — gibt Text zurück |
| `variant` | `"suggest" \| "generate" \| "enhance"` | no | `"suggest"` | AI-Interaktions-Modus |
| `aiLabel` | `string` | no | — | Tooltip für den AI-Button (via t()-Key) |

---

## Rules

- AI-Button immer rechts im Feld oder als Icons-Overlay
- `enhance`-Variante: AI-Button deaktiviert wenn Feld leer
- KI-Fehler niemals still schlucken — immer Error-State zeigen
- `suggest`-Variante: User muss Vorschlag explizit übernehmen — nie automatisch ins Feld schreiben
- `generate`-Variante: Generierten Text überschreibt Feld-Inhalt — Warnhinweis wenn Feld nicht leer

---

## Accessibility

- AI-Button: `aria-label` beschreibt Aktion (z.B. „KI-Vorschlag generieren")
- Loading: `aria-busy="true"` auf dem Feld-Container
- Vorschlag-Panel: fokussierbar, Escape schließt

---

## Code Pattern

```tsx
<FieldWithAi
  fieldComponent="textarea"
  value={sceneDescription}
  onChange={setSceneDescription}
  onAiRequest={() => generateSceneDescription(sceneId)}
  variant="suggest"
  aiLabel={t("ai.suggest_description")}
/>
```

---

## Do / Don't

❌ KI-Vorschlag automatisch ins Feld schreiben
✅ Immer explizite User-Bestätigung für `suggest`-Variante

❌ AI-Fehler ignorieren
✅ Error-State anzeigen mit sinnvoller Meldung

---

## Missing Information Protocol

```tsx
// TODO(design): AI-Button Icon und Position — Issue #TODO
// TODO(design): Vorschlag-Panel Darstellung — Issue #TODO
// TODO(ux): Unterschied generate vs. suggest Interaction Design — noch nicht spezifiziert — Issue #TODO
// TODO(backend): KI-Provider und API-Kontrakt für Field-Level-Generation — Issue #TODO
```

---

## Related

- `text-input.md` — Basis-Komponente für `input`-Variante
- `text-area.md` — Basis-Komponente für `textarea`-Variante
- `info-card.md` — Für KI-Fehler die längere Erklärung brauchen
