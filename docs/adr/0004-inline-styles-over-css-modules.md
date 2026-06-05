# ADR 0004: Inline Styles statt CSS Modules

**Status:** Accepted  
**Datum:** 2026-06-05  
**Autoren:** Thorsten Dittmar

---

## Kontext

Das Frontend verwendet React 18 + TypeScript + Vite. Für das Styling gibt es drei gängige Ansätze:
- **CSS Modules** — lokale CSS-Klassen pro Komponente, Build-Tool-Integration nötig
- **Tailwind CSS** — Utility-Klassen, umfangreiche Konfiguration, eigene Konventionen
- **Inline Styles** — direkte Style-Objekte in JSX, kein Build-Tool

Das Projekt verwendet agenten-getriebene Frontend-Entwicklung: KI-Agenten schreiben Komponenten nach einem Living Style Guide. Konsistenz und Nachvollziehbarkeit haben Vorrang vor Entwickler-Ergonomie.

---

## Entscheidung

Wir verwenden **ausschließlich Inline Styles** für alle Komponenten-spezifischen Styles.

Globale CSS Custom Properties (Design Tokens) werden einmalig in `frontend/src/index.css` definiert und per `var(--token-name)` in Inline Styles referenziert.

---

## Begründung

**Für Inline Styles:**
- Kein Build-Tool-Coupling — Styles sind reines JavaScript/TypeScript
- Für Agenten einfacher konsistent zu halten: der Stil ist direkt im JSX sichtbar, kein Wechsel zwischen Dateien nötig
- Design Tokens via `var(--color-*)` bleiben nutzbar
- Keine Naming-Konventionen für CSS-Klassen nötig (kein BEM, kein Tailwind-Klassen-Mapping)

**Gegen CSS Modules:**
- Erfordern Build-Tool-Konfiguration und Import-Boilerplate
- Stile und Markup in getrennten Dateien — erschwert Agenten-Konsistenz
- Bei agenten-generiertem Code oft inkonsistente Klassenbenennungen

**Gegen Tailwind:**
- Große Lernkurve für Tailwind-Konventionen
- Utility-Klassen sind für Agenten schwerer konsistent anzuwenden als explizite Pixel-Werte
- Erzwingt Tailwind als Dependency mit eigener Konfiguration

---

## Konsequenzen

- `frontend/src/index.css` enthält ausschließlich CSS Custom Properties und globale Resets — keine Komponenten-Klassen
- Agenten lesen `design/tokens/*.json` und übersetzen Token-Werte direkt in Inline Style-Objekte
- Hover-States erfordern `onMouseEnter`/`onMouseLeave` oder CSS-Pseudo-Klassen via `<style>` Tags — kein `:hover` in Inline Styles möglich (bekannte Einschränkung, akzeptiert für diesen Projektstand)
- Bei Bedarf kann Style Dictionary später CSS Custom Properties aus den Token-JSONs generieren

---

## Alternativen die verworfen wurden

- **CSS Modules**: Abgelehnt wegen Build-Coupling und Agentkonsistenz
- **Tailwind**: Abgelehnt wegen Lernkurve und Dependency-Overhead
- **Styled Components / Emotion**: Abgelehnt — CSS-in-JS-Libraries mit Runtime-Overhead
