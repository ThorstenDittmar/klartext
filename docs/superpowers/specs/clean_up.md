# Clean Up — Inkonsistenzen und offene Zuordnungsfragen

**Datum:** 2026-06-03
**Zweck:** Dokumentation aller identifizierten Widersprüche,
Inkonsistenzen und nicht zugeordneter Punkte aus der Spec-Analyse.
Alle hier aufgeführten Punkte sind in causal_model.md und
narrative_model.md bereits aufgelöst — dieses Dokument erklärt warum.

---

## 1. Aufgelöste Inkonsistenzen

### I-01: SpatialRef vs SpatialRegion, DisciplineRef vs Discipline

**Problem:** `2026-06-03-timeslice.md` verwendete `SpatialRef` und
`DisciplineRef`. `2026-06-03-scope.md` verwendete `SpatialRegion` und
`Discipline`.

**Auflösung:** `SpatialRegion` und `Discipline` — aus scope.md. Diese
Spec ist detaillierter und wurde nach timeslice.md erstellt.

---

### I-02: TimeSlice doppelt definiert

**Problem:** Sowohl `2026-06-03-scope.md` als auch
`2026-06-03-timeslice.md` definierten `TimeSlice`, mit leicht
unterschiedlichen Methoden und ohne Querverweis.

**Auflösung:** Zusammengeführt in causal_model.md §6. Kanonische
Definition hat `identifier`, `start`, `end`, `__post_init__` für
auto-identifier, `includes()` und `intersects()`.

---

### I-03: T-09 und T-18 in timeslice.md noch offen

**Problem:** `2026-06-03-timeslice.md` listete T-09 und T-18 als offen,
obwohl beide durch spätere Specs geschlossen wurden.

**Auflösung:** In causal_model.md §14 als geschlossen markiert.
timeslice.md war ein Zwischenstand.

---

### I-04: Scope.is_compatible() vs Scope.includes()

**Problem:** Das core design doc definierte `is_compatible(other)` für
Scope-Überlappung. scope.md definierte `includes(other)` für
Enthaltensein.

**Auflösung:** Beide Methoden werden gebraucht — mit verschiedener
Semantik:
- `includes()` — für add()-Prüfung (liegt Element im Modell-Scope?)
- `is_compatible()` — für Konfliktprüfung (überlappen sich zwei Scopes?)

Beide in causal_model.md §6 aufgenommen.

---

### I-05: EpistemicStatus.DERIVED

**Problem:** Das core design doc sagt klar "DERIVED wird nicht
gespeichert, sondern berechnet". `2026-06-03-zustand-und-trend.md`
referenzierte `epistemic_status = DERIVED` als setzbaren Wert auf Zustand.

**Auflösung:** DERIVED ist und bleibt eine berechnete Eigenschaft
(`is_derived: bool = derivation_source is not None`). Das Enum kennt
nur INCOMPLETE und AXIOMATIC. In zustand.md war das missverständlich
formuliert — in causal_model.md §9 klar gestellt.

---

### I-06: Actor.label vs Actor.name

**Problem:** Ziel-Spec `2026-06-03-actor.md` verwendete `label`.
Aktuelle Implementierung `current-narrative-domain.md` verwendete `name`.

**Auflösung:** `label` — konsistent mit DocumentAsset-Muster und
CausalComponent-Muster. Migration der Datenbankspalte notwendig.

---

### I-07: ActorType fehlt in Ziel-Spec

**Problem:** Aktuelle Implementierung hat `ActorType`-Enum (individual,
organisation, group, institution, abstract_entity). Ziel-Spec hatte
keinen ActorType.

**Auflösung:** ActorType in Zielarchitektur aufgenommen
(narrative_model.md §4). Der Typ ist semantisch sinnvoll und sollte
erhalten bleiben.

---

### I-08: Actor per Narrativ vs plattformweites DocumentAsset

**Problem:** Aktuelle Implementierung: Actor hängt via FK an ein
Narrativ (`narrative_actors.narrative_id`). Zielarchitektur: Actor ist
ein plattformweites DocumentAsset mit DocumentLink-Navigation.

**Auflösung:** Fundamentale Architekturänderung, kein Fehler. In
narrative_model.md §4 als Migrationslücke explizit dokumentiert. Die
Migration betrifft:
- Tabellenstruktur: `narrative_actors` → `document_assets` (asset_type='actor')
- Verknüpfungsstruktur: FK auf Narrativ → DocumentLink-Referenzen

---

### I-09: confidence in Claim

**Problem:** Aktuelle Implementierung hat `confidence: float` (LLM-
Extraktions-Konfidenz). Ziel-Spec hatte kein confidence-Feld.

**Auflösung:** confidence in Zielarchitektur aufgenommen
(narrative_model.md §5). Es ist ein nützlicher Metawert für die
Extraktionsqualität.

---

### I-10: narrative_units vs document_nodes

**Problem:** Aktuelle Implementierung nutzt `narrative_units` mit altem
`typ`-Check ('work','part','chapter','scene','fragment').
Zielarchitektur nutzt `document_nodes` mit `node_type` und anderen
Enum-Werten (work, part, chapter, section, paragraph, sentence,
string, character).

**Auflösung:** Migrationslücke — kein konzeptioneller Widerspruch.
`narrative_units` bleibt für Phase 1, wird in Phase 2 zu
`document_nodes` migriert.

---

## 2. Nicht zugeordnete Punkte

### N-01: precondition-postcondition.md im RTF-Format

Die Datei `precondition-postcondition.md` wurde als RTF gespeichert
(enthält `\rtf1\ansi...`-Header). Der Inhalt ist korrekt und identisch
mit der Spec. Empfehlung: Datei als reines Markdown neu speichern.

---

### N-02: Claim-Typen aus aktueller Implementierung

Die aktuellen Claim-Typen (`empirischer_claim`, `kausaler_claim`, etc.)
sind reine String-Werte ohne formale Enum-Definition. In der
Zielarchitektur werden diese Typen nicht mehr benötigt — stattdessen
zeigt `wirkgefuege_ref` direkt auf das entsprechende Wirkgefüge-Element.

Die Typen sind aber nützlich für die LLM-Extraktion als Hint.
Empfehlung: Als internen Extraktions-Hint behalten, aber nicht als
formales Attribut des Claim-Domänenobjekts.

---

### N-03: Wirkgefüge-Design-Principles noch nicht in CLAUDE.md

`wirkgefuege-design-principles.md` ist explizit als "noch nicht ins
Projekt integriert" markiert. Muss in `CLAUDE.md` und Projektdoku
eingearbeitet werden.

---

### N-04: CausalModelFederation noch nicht spezifiziert

In keiner Spec vollständig beschrieben. Nur die Methoden
`get_successors()`, `validate_transition()` und
`get_active_postconditions()` sind bekannt.

---

### N-05: Namespace als Klasse

Im core design doc als Konzept beschrieben aber nie als Python-Klasse
spezifiziert. Struktur (hierarchisch, typisiert, mit qualified names)
ist klar — Implementierungsdetails fehlen.

---

### N-06: Community Model ohne Specs

Für das Community Model (User, Acceptance, CommunityPost, Violations)
existieren noch keine technischen Spec-Dateien. Konzeptionelle
Grundlage in Projektskizze Kap. 22–23.

---

## 3. Empfohlene nächste Schritte

1. `precondition-postcondition.md` als reines Markdown neu speichern
2. `wirkgefuege-design-principles.md` in CLAUDE.md einarbeiten
3. CausalModelFederation vollständig spezifizieren
4. Namespace als Klasse spezifizieren
5. Community Model Specs anlegen (User, Acceptance, CommunityPost)
6. Migrationspfad narrative_actors → document_assets planen
