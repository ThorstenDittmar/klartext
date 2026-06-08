# ADR-0007: Eigene Komponentenbibliothek statt externer UI-Framework

**Status:** Accepted  
**Datum:** 2026-06-08  
**Entscheider:** System Architect, UX/UI Expert

---

## Kontext

Das klartext-Frontend verwendet ausschließlich Inline-Styles (kein CSS Modules, kein Tailwind, kein styled-components). Diese Entscheidung ist in ADR-0004 dokumentiert.

Eigene Design Tokens (colors, spacing, typography, radii) sind unter `design/tokens/` definiert und bilden die Grundlage für alle visuellen Entscheidungen. Komponenten-Specs liegen unter `design/components/*.md`.

Die Frage ist: Bauen wir UI-Komponenten auf einer externen Bibliothek auf, oder entwickeln wir eine eigene?

---

## Entscheidung

Wir entwickeln eine eigene Komponentenbibliothek in `frontend/src/components/`, die direkt auf unseren Design Tokens aufbaut.

---

## Betrachtete Alternativen

### Option A: Material UI (MUI)
- **Pro:** Vollständig, gut dokumentiert, große Community, starke Accessibility-Basis
- **Contra:** Setzt auf CSS-in-JS oder CSS Custom Properties; Theme-Overrides kollidieren mit Inline-Styles-only-Regel; erheblicher Bundle-Overhead; Styling-Schicht kämpft gegen unser Token-System

### Option B: shadcn/ui
- **Pro:** Copy-paste-Modell, keine Runtime-Dependency, gute Radix-Basis für Accessibility
- **Contra:** Baut auf Tailwind-Klassen auf — fundamental unvereinbar mit Inline-Styles-only; Entfernen der Tailwind-Abhängigkeit würde den Kern der Library zerstören

### Option C: Radix UI Primitives (headless)
- **Pro:** Keine Styling-Meinung, exzellente Accessibility-Primitive (ARIA, Keyboard, Focus-Management), aktiv gepflegt
- **Contra:** Kein vollständiges Komponentenset; wir bauen die Styling-Schicht selbst — faktisch eine eigene Library mit Radix als Accessibility-Unterbau
- **Notiz:** Radix Primitives können als **optionaler Unterbau** für komplexe Komponenten (Dialog, Dropdown, Tooltip) verwendet werden, ohne die Entscheidung zu kippen

### Option D: Eigene Library (gewählt)
- **Pro:** Vollständige Kontrolle über Styling und Token-Integration; keine Konflikte mit Inline-Styles-only; Accessibility nach eigenem Standard implementierbar; kein Framework-Update-Druck; Token-Änderungen schlagen direkt durch
- **Contra:** Höherer initialer Aufwand; Accessibility muss selbst implementiert und getestet werden; keine Community-Patches

---

## Trade-offs

| Kriterium | Extern (MUI/shadcn) | Eigen |
|---|---|---|
| Initialer Aufwand | Niedrig | Hoch |
| Langfristige Kontrolle | Niedrig | Hoch |
| Inline-Styles-Kompatibilität | Nicht gegeben | Vollständig |
| Token-Integration | Aufwändig (Override) | Direkt |
| Accessibility | Mitgeliefert | Selbst verantwortlich |
| Bundle-Size | Groß (ohne Tree-Shaking-Aufwand) | Minimal |
| Update-Risiko | Hoch (Breaking Changes) | Keine externe Abhängigkeit |

---

## Konsequenzen

**Positiv:**
- Komponenten sind direkte Ausdrücke unserer Design Tokens — kein Übersetzungsaufwand
- Keine Konflikte mit der Inline-Styles-only-Entscheidung
- Storybook dokumentiert Komponenten in ihrer tatsächlichen Form, ohne Framework-Wrapper

**Negativ / Risiken:**
- Accessibility ist unsere Verantwortung. Für interaktive Komponenten (Modal, Dropdown, Tooltip) prüfen wir ob Radix Primitives als headless Unterbau eingesetzt werden können, um ARIA-Pattern-Fehler zu vermeiden.
- Wachsender Pflegeaufwand bei vielen Komponenten. Gegenmittel: strikte Konvention (siehe `frontend.md`), kein Wildwuchs ohne Spec.

**Rahmenbedingungen die diese Entscheidung tragen:**
- Inline-Styles-only bleibt unverändert (ADR-0004)
- Design Tokens bleiben die einzige Quelle der Wahrheit für visuelle Werte
- Komponenten-Struktur und Importregeln sind in `frontend.md` dokumentiert

---

## Review-Trigger

Dieses ADR sollte neu bewertet werden wenn:
- Die Inline-Styles-only-Regel aufgehoben wird
- Die Anzahl der selbst gepflegten Komponenten 30+ übersteigt und der Aufwand nicht mehr tragbar ist
- Ein headless Accessibility-Framework (z.B. Radix) faktisch zur Pflicht wird für alle interaktiven Komponenten
