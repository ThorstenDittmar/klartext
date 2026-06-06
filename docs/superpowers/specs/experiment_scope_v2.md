# Experiment Scope V2: Narrativ → Claims/Actors → Wirkgefüge

**Datum:** 2026-06-04
**Änderung gegenüber V1:** Narrativ-Verwaltung als eigener Bereich,
Frontend-Neuaufbau mit sauberem Screen-Flow.

---

## Was bereits funktioniert und nicht angefasst wird

- Narrativ-Import (.docx, .md) via Server-Pfad
- Analyse-Endpunkt: POST /narratives/{id}/analyse
- Actor- und Claim-Extraktion via Claude API
- Wirkgefüge-Vorschläge: POST /narratives/{id}/suggest-wirkgefuege
- CausalModel mit Slots und Relationen anlegen und speichern
- Alle bestehenden API-Endpunkte

---

## Fachliche Erweiterung: Meine Werke

Es wird ein neuer Bereich "Meine Werke" eingeführt. Das ist der
zentrale Einstiegspunkt des Autors in die Anwendung.

Hier verwaltet der Autor alle seine Narrative. Er kann neue Narrative
anlegen, bestehende öffnen und Narrative importieren. Der Import
einer Datei (.docx oder .md) gehört ausschliesslich in diesen Bereich
und ist nicht mehr Teil der Narrativ-Detail-Ansicht.

Ein Narrativ hat in dieser Übersicht folgende sichtbare Eigenschaften:
Titel, Anzahl der Szenen, Anzahl der Actors, Anzahl der Claims,
und ob bereits ein Wirkgefüge verknüpft ist.

---

## Screen-Flow (vollständig)

Der Autor durchläuft folgende Screens in dieser Reihenfolge:


SCREEN 0 — Meine Werke (neu, Einstiegspunkt)

Der Autor sieht alle seine Narrative als Übersichtsliste oder -kacheln.
Er kann ein bestehendes Narrativ öffnen oder ein neues anlegen.
Er kann eine Datei importieren. Nach dem Import landet er direkt
auf Screen 1 des importierten Narrativs.


SCREEN 1 — Narrativ-Detail

Der Autor sieht den Titel des Narrativs und die Liste der enthaltenen
Szenen. Er kann einzelne Szenen lesen.

Unten oder oben gibt es einen primären Aktions-Button "Analysieren".
Beim Klick startet die Analyse (POST /narratives/{id}/analyse).
Während die Analyse läuft ist der Button deaktiviert und zeigt
einen Ladezustand. Nach erfolgreicher Analyse wird automatisch
zu Screen 2 weitergeleitet.

Wenn bereits Actors und Claims vorhanden sind (vorherige Analyse),
werden diese hier sichtbar angezeigt — Actors als eine Liste,
Claims als eine separate Liste, jeweils mit ihrem Status.


SCREEN 2 — Analyse-Ergebnis

Der Autor sieht die Ergebnisse der Analyse: vorgeschlagene Actors
und vorgeschlagene Claims, jeweils als Liste von Karten.

Jede Actor-Karte zeigt: Name, Typ, in welchen Szenen er vorkommt,
und ob das System eine Entity im Wirkgefüge vorschlägt.

Jede Claim-Karte zeigt: Label, Originaltext aus dem Narrativ,
Claim-Typ, Konfidenz der Extraktion, und den Wirkgefüge-Vorschlag
(welcher Slot oder welche Relation dieser Claim impliziert).

Der Autor kann jeden Eintrag einzeln bestätigen oder verwerfen.
Er kann auch alle auf einmal bestätigen.

Am Ende der Seite gibt es einen Button "Wirkgefüge-Vorschläge
generieren". Dieser ist nur aktiv wenn mindestens ein Claim
bestätigt wurde. Nach dem Klick wird zu Screen 3 weitergeleitet.


SCREEN 3 — Wirkgefüge-Vorschlag

Das System hat aus den bestätigten Claims ein minimales Wirkgefüge
abgeleitet und zeigt die vorgeschlagenen Slots und Kausalrelationen.

Der Autor kann jeden Slot und jede Relation einzeln verwerfen.
Er kann den Identifier eines Slots umbenennen.
Er kann den Mechanismus einer Relation bearbeiten.
Er kann den EpistemicStatus einer Relation setzen (incomplete oder
axiomatic).

Er vergibt einen Namen für das neue CausalModel.

Der primäre Aktions-Button "Speichern" legt das CausalModel an,
fügt alle nicht verworfenen Slots und Relationen ein, verknüpft
das Narrativ mit dem Modell, und setzt alle bestätigten Claims
auf den Status LINKED. Nach dem Speichern wird zu Screen 4
weitergeleitet.


SCREEN 4 — CausalModel-Detail

Der Autor sieht das gespeicherte CausalModel mit allen Slots,
Kausalrelationen und Axiomen. Er sieht welche Narrative mit
diesem Modell verknüpft sind.

---

## Design

Das Frontend folgt dem Living Style Guide des Projekts.
Alle vier Workflow-Screens sind listenbasierte Layouts ohne
Sidebar oder Graph. Kein komplexes Layout in diesem Scope.

Der Bereich "Meine Werke" (Screen 0) darf eine Kachel- oder
Listenansicht verwenden.

---

## Was explizit nicht in diesem Scope ist

- DocumentNode-Baum (Section, Paragraph, Sentence etc.)
- Scope auf Slots und Relationen
- CausalModelFederation und Zeitscheiben
- Vollständige DocumentLink-Navigation
- Migration bestehender Daten
- Community-Features
- Die vollständige Zielarchitektur aus ui_spec.md

---

## Erfolgskriterium

Der Autor öffnet die Anwendung, landet auf "Meine Werke",
importiert eine Datei, durchläuft den Analyse-Workflow,
bestätigt Actors und Claims, bearbeitet die Wirkgefüge-Vorschläge
und speichert ein CausalModel. Auf Screen 1 sieht er nach der
Analyse seine bestätigten Actors und Claims.
