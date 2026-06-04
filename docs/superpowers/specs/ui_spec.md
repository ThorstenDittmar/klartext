# UI-Spezifikation: klartext.jetzt

**Datum:** 2026-06-04
**Status:** Arbeitsstand — erste Iteration
**Scope:** Literat-Perspektive und Wissenschaftler-Perspektive.
Leseansicht ist noch nicht spezifiziert.

---

## 1. Designprinzipien

**Look & Feel:** Novelcrafter als primäres Vorbild.
Farbsparsamkeit, klare Typographie, viel Whitespace.
Farben nur semantisch einsetzen — nie dekorativ.

**Farbkonventionen (semantisch):**
- Grün (`#EAF3DE / #3B6D11`) — linked, vollständig, bestätigt
- Amber (`#FAEEDA / #854F0B`) — draft, offen, unvollständig
- Rot (`#FCEBEB / #A32D2D`) — Issue, Fehler, blockiert
- Blau (`#E6F1FB / #0C447C`) — Fokus-Knoten, aktive Auswahl, Info
- Lila (`#EEEDFE / #3C3489`) — Wirkgefüge-Referenz, epistemic link

**Keine Farbe ohne Bedeutung.** Neutrale Elemente sind immer
`var(--color-background-secondary)` mit `var(--color-border-tertiary)`.

---

## 2. Globale Struktur

```
AppShell
  ├── TopBar
  ├── Body
  │     ├── Sidebar (links, 154px)
  │     ├── MainArea (flex: 1)
  │     └── RightPanel (rechts, 160px)
  └── StatusBar (optional, für Hinweise)
```

### TopBar

```
[Logo] [Projektname · Kontext] .............. [PerspectiveToggle]
```

- Projektname wechselt mit Perspektive:
  Literat → `Narrativ: {title}`, Wirkgefüge → `Gefüge: {modelTitle}`
- `PerspectiveToggle`: zwei Buttons `Literat` / `Wirkgefüge`
  Aktiver Button: `background-info + text-info + font-weight:500`

### Sidebar

Zwei Varianten je nach Perspektive (siehe §3 und §4).
Gemeinsames Muster:
- Sektions-Labels: 10px, `color-text-tertiary`, letter-spacing
- Items: 12px, mit Icon + Label + optionalem Zähler-Badge
- Aktives Item: `background-primary`, `font-weight:500`
- Szenen-Einrückung: `padding-left:23px`, aktive Szene mit
  `border-left:2px solid color-border-primary`
- Zähler-Badge: 10px, `border + background-primary`, border-radius:8px

### RightPanel

Zwei Varianten je nach Perspektive (siehe §3 und §4).
Gemeinsames Muster:
- Tab-Bar oben: 2 Tabs, aktiver Tab mit `border-bottom:2px solid`
- Panel-Body: 9px padding, flex column, gap:1px
- Sektion-Labels: 10px, `color-text-tertiary`
- Einträge: 11px, Icon + Label + Badge (margin-left:auto)

---

## 3. Literat-Perspektive

### 3.1 Sidebar (Literat)

```
Struktur
  [file-text] Kapitel 1
    Szene 1 — Anfang     ← aktiv, border-left
    Szene 2 — Wendung
  [file-text] Kapitel 2
    Szene 3 — Ende

Narrativ-Assets
  [users]          Actors    [4]
  [message-circle] Claims    [7]

Wirkgefüge
  [git-branch] Klimawandel   ← aktiv
```

Actors und Claims sind Navigationspunkte — ein Klick öffnet
die vollständige Asset-Liste, nicht das rechte Panel.

### 3.2 MainArea (Literat)

**Toolbar:**
```
[Szenenname]  ..................  [Schreiben] [Analyse]
```
Aktiver View-Tab: `background-primary + border-secondary`.

**Schreiben-View:**
Fließtext mit inline Actor- und Claim-Tags.

```
Actor-Tag:  [user-icon] Name     background:#E1F5EE  color:#0F6E56
Claim linked: [message-icon] Text  background:#EAF3DE  color:#3B6D11
Claim draft:  [message-icon] Text  background:#FAEEDA  color:#854F0B
```

Tags sind klickbar → öffnet `ActorPopup` oder `ClaimPopup` als Overlay.

**Analyse-View:** (Phase 2) Extrahierte Claims und Actors zur Bestätigung.

### 3.3 RightPanel (Literat)

Tab 1: **In dieser Szene** (reaktiv auf aktuelle Szene)

Zeigt nur Actors und Claims die in der aktuellen Szene vorkommen.
Gefiltert über `DocumentLink` → `occurrences()`.

```
Actors
  [user] Maria S.     [3×]
  [user] Zentralbank  [→ Entity]

Claims
  [message] CO₂ steigt    [linked]
  [message] Folgen unklar [draft]

Nicht in dieser Szene: 2 Actors, 5 Claims.
```

Tab 2: **Wirkgefüge** — kompakte Ansicht des verknüpften Modells.

### 3.4 ActorPopup (Overlay)

Öffnet sich über dem Text als Modal-Overlay.
Hintergrund: `rgba(0,0,0,0.18)`.
Popup-Breite: 260px, `background-primary`, `border-secondary`, `border-radius-lg`.

**Header:**
```
Actor · {actor_type}                          [×]
{label}
{N} Vorkommen im Narrativ

[Hüllkurve — SVG-Balkendiagramm der Vorkommen über den Textverlauf]

[Details] [Relationen] [Vorkommen] [Tracking]
```

**Hüllkurve:** SVG Polyline, Höhe 28px, Breite 100%.
Jeder Zacken = ein Vorkommen. X-Achse = Textverlauf (Position),
Y-Achse = Amplitude (immer gleich, nur Präsenz/Absenz).
Stroke: `color-border-primary`, keine Fill.

**Details-Tab:**
```
Typ         {actor_type}
Entity-Link {entity_ref.label} oder —
Szenen      {komma-separierte Liste}
```
Notizfeld: 11px, `color-text-secondary`, immer `AuthorOnly`.

---

## 4. Wissenschaftler-Perspektive

### 4.1 Sidebar (Wissenschaftler)

```
Modelle
  [git-branch] Klimawandel   ← aktiv

Elemente
  [variable]         Slots       [6]
  [arrows-right-left] Relationen [4]
  [layers-difference] Mixins     [1]

Verwendung
  [book]         Narrative  [2]
  [alert-circle] Issues     [1]  ← Issue-Badge: rot
```

Issue-Badge: `background:#FCEBEB`, `color:#A32D2D`, `border:#F09595`.

### 4.2 MainArea (Wissenschaftler) — Graph-View

**Toolbar:**
```
[Elementname · Typ · slot_type]  .....  [Graph] [Text] [Timeline] [Tabelle]
```

**Graph-View (primär — TheBrain + Tinderbox Inspiration):**

Focus-Node-Prinzip:
- Ein Knoten ist immer der Fokus-Knoten (zuletzt angeklickt)
- Fokus-Knoten: `background:#E6F1FB`, `border:1.5px solid #185FA5`,
  `font-weight:500`, `color:#0C447C`
- Direkte Nachbarn: volle Opacity, normale Darstellung
- Nachbarn der Nachbarn: `opacity:0.4`, kleinere Schrift

CausalModel-Grenze:
- Gestrichelter Rahmen um alle Elemente des aktiven CausalModels
- `stroke:color-border-tertiary`, `stroke-dasharray:5 3`, `rx:8`
- Label oben links: `CausalModel: {title} · {zeitscheibe}`, 10px

Verbindungslinien:
- Normale CausalRelation: `stroke:color-border-secondary`, `stroke-width:1`
- Mit Issue: `stroke:#185FA5`, `stroke-width:1`, `stroke-dasharray:4 2`
- Pfeilspitzen: marker-end, 5×5px

Mechanismus-Label: 9px, `color-text-tertiary`, auf der Linie rotiert.

Doppelklick auf Knoten → Knoten wird neuer Fokus-Knoten,
Graph reorganisiert sich um ihn.

**Text-View:** Alle Elemente des Modells als strukturierte Liste.
**Timeline-View:** Zeitscheiben als horizontale Sequenz.
**Tabelle-View:** Slots und Relationen als sortierbare Tabelle.

### 4.3 RightPanel (Wissenschaftler)

Tab 1: **Dieses Element** (reaktiv auf Fokus-Knoten)

```
{label}
{element_type} · {slot_type}
[EpistemicStatus-Badge]

Eingehende
  [arrow-right] Source → Fokus

Ausgehende
  [arrow-right] Fokus → Target

Verwendet in
  [book] {narrativ_title}  [Sz. N]
```

EpistemicStatus-Badges:
- `incomplete`: amber (`#FAEEDA / #854F0B`)
- `axiomatic`: grün (`#EAF3DE / #3B6D11`)
- `derived`: lila (`#EEEDFE / #3C3489`)

Tab 2: **Issues** — alle offenen ModelIssues des Modells.

---

## 5. State-Modell

```typescript
interface AppState {
  perspective: 'literat' | 'wirkgefuge'

  // Literat
  currentNarrativeId: string
  currentSceneId: string
  openPopup: { type: 'actor' | 'claim', id: string } | null

  // Wissenschaftler
  currentModelId: string
  focusNodeId: string
  activeView: 'graph' | 'text' | 'timeline' | 'tabelle'
}
```

**Reaktivitätsregeln:**
- `currentSceneId` → RightPanel filtert Actors und Claims
- `focusNodeId` → Graph zentriert, RightPanel zeigt Element-Details
- `perspective` → Sidebar, MainArea, RightPanel wechseln komplett
- `openPopup` → Overlay erscheint über MainArea

---

## 6. Komponenten-Hierarchie

```
AppShell
  TopBar
    Logo
    ProjectLabel          ← reaktiv auf perspective + currentId
    PerspectiveToggle

  Body
    Sidebar
      LiteratSidebar      ← wenn perspective === 'literat'
      WissenschaftlerSidebar ← wenn perspective === 'wirkgefuge'

    MainArea
      MainToolbar
        NodeTitle
        ViewTabs
      LiteratEditor       ← Schreiben / Analyse
        InlineActorTag    ← klickbar → openPopup
        InlineClaimTag    ← klickbar → openPopup
        ActorPopup        ← Overlay, wenn openPopup gesetzt
          WaveformChart   ← SVG, occurrences als Hüllkurve
      WirkgefuegeGraph    ← Graph / Text / Timeline / Tabelle
        FocusNode
        NeighborNode
        ModelBoundary     ← gestrichelter CausalModel-Rahmen
        RelationLine

    RightPanel
      LiteratPanel        ← gefiltert auf currentSceneId
      WissenschaftlerPanel ← gefiltert auf focusNodeId

  StatusBar               ← Hinweise und Kontext
```

---

## 7. Noch nicht spezifiziert

| Thema | Priorität |
|---|---|
| Leseansicht (dritte Perspektive) | Phase 2 |
| Matrix-View Szenen × Assets | Phase 2 |
| Übergangsanimation beim Perspektiv-Wechsel | Phase 2 |
| Präsentationsmodus | Phase 3 |
| Mobile-Strategie | Phase 3 |
| Onboarding-Flow | Phase 3 |
