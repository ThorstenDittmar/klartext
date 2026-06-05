# Design System Changelog

Jede Änderung am Design System wird hier geloggt.
Format: Datum | Was geändert | Warum | Betroffene Komponenten | Pending Task

---

## 2026-06-05 — Initiale Einrichtung

**Was:** Living Style Guide und Design Tokens initial angelegt.

**Inhalt:**
- `design/tokens/colors.json` — alle Farben aus `frontend/src/index.css` übertragen
- `design/tokens/typography.json` — Schrift-Stack und Größen-Scale definiert
- `design/tokens/spacing.json` — Spacing-Scale 4–64px
- `design/tokens/radii.json` — Border-Radius-Scale
- `design/tokens/shadows.json` — Shadow-Scale (flat-first)
- `design/tokens/breakpoints.json` — Breakpoints (desktop-first)
- `design/do-dont.md` — Verbotene Muster
- `design/i18n.md` — Mehrsprachigkeits-Regeln
- `design/accessibility.md` — A11y-Vorgaben
- `design/components/_template.md` — Vorlage für Komponenten-Specs
- `docs/superpowers/skills/frontend.md` — Frontend-Agent-Skill

**Warum:** Bisher waren Designwerte nur in `frontend/src/index.css` als CSS Custom Properties
vorhanden — kein maschinenlesbares Format, keine Dokumentation der Semantik.

**Betroffene Komponenten:** Alle bestehenden Screens verwenden die CSS Custom Properties
bereits korrekt. Keine Code-Änderungen nötig.

**Pending Task:** Keine — bestehender Code ist bereits kompatibel.

---

<!--
  TEMPLATE für neue Einträge:

  ## YYYY-MM-DD — [Kurzbeschreibung]

  **Was:** Token / Komponenten-Spec / Pattern geändert

  **Datei:** `design/tokens/colors.json` → `color.semantic.green.bg`
  Alter Wert: `#EAF3DE`
  Neuer Wert: `#...`

  **Warum:** [Begründung]

  **Betroffene Komponenten:**
  - `NarrativeAnalyse.tsx` — verwendet `--color-green-bg` für bestätigte Claims
  - `CausalModelEditor.tsx` — EpistemicBadge mit axiomatic state

  **Pending Task:** GitHub Issue #XX angelegt:
  "Komponente NarrativeAnalyse.tsx laut Style Guide Abschnitt design/tokens/colors.json
  aktualisieren, weil Token color.semantic.green.bg geändert wurde."
-->
