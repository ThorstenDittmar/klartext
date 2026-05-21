# Appendix A: Offene Punkte und To-dos

Diese Liste enthält alle offenen Punkte aus dem Whitepaper V0.24.

## Datenmodell

- [ ] Performance-Tests mit realistischen Datenvolumina; Entscheidung Graphdatenbank vs. PostgreSQL
- [ ] Maximale JSONB-Snapshot-Größe und Kompressionsstrategien für große Wirkmodellverbünde
- [ ] Caching-Strategie für Systemakzeptanz, Katalog und Transparenzberichte
- [ ] Volltext-Sucharchitektur (PostgreSQL tsvector vs. Elasticsearch)
- [ ] Garbage Collector: Datenbankschema für Referenz-Tracking verwaister Modellelemente

## Konsistenzprüfung

- [ ] Konsistenzprüfung axiomatischer Elemente: System soll erkennen wenn ein axiomatisch gesetztes Element durch Modelllogik verändert wird
- [ ] Technische Spezifikation der Werkzeuge für Wirkmodell-Einzug, Axiom-Mapping und Szenen-Diff

## Community & Trust Network

- [ ] Systemakzeptanz-Gewichtung: Relative Gewichte der drei Quellen
- [ ] Trust Network Skalierung: EigenTrust+ bei sehr großen Nutzerzahlen
- [ ] Spam- und Bot-Schutz im Akzeptanz-System
- [ ] Moderationslogik: Präzise Abgrenzung klar/unklar vs. wahr/unwahr
- [ ] Profildeaktivierung: Umgang mit Werken bei Account-Löschung

## UI & UX

- [ ] Präsentationsmodus: Kamera-Stream-Integration und Flag-Synchronisation für Zuschauer
- [ ] Farbkodierung der Zensurkategorien: Genaue Farbwahl und Accessibility
- [ ] Leser-Onboarding: Vollständige Spezifikation der Personalisierungsoptionen
- [ ] Barrierefreiheit: Schriftgröße, Kontrast, Screenreader, Vorlesefunktion
- [ ] Weitere View-Typen: Matrixansicht, Netzwerkkarte, Prüfprofil-Ansicht

## Technisch & API

- [ ] API-Kontrakte: Schnittstellen Autoren-/Konsistenz-/Leserumgebung
- [ ] Rollensystem und Authentifizierung: Vollständiges Rollenmodell
- [ ] Domänenontologien: SNOMED, MeSH, ENVO als Standardreferenzrahmen
- [ ] Notification-System: Drei Abonnementstufen; Broadcast-Logik bei Wirkmodell-Änderungen
- [ ] Logging: Protokollierung unter Berücksichtigung Rechtsraum-Logik

## Kollaboration & Rechte

- [ ] Kollaborations-Konfliktlösung: Uneinige gleichberechtigte Autoren bei Freigabeentscheidung
- [ ] Verbund-Governance: Rechte bei Änderungen in Verbundstrukturen
- [ ] Urheberrecht beim Import: Fair Use, Open Access, Lizenztypen
- [ ] Recycling-Benachrichtigungen: Wann wird der Originalautor informiert?
- [ ] Recycling-Ketten: Wie werden mehrstufige Ketten navigierbar dargestellt?

## Empfehlungsalgorithmus

- [ ] Gewichtungskriterien und Transparenz der Katalogsortierung
- [ ] Community-Validierung: Voting-Mechanismus; Governance für Status „akzeptiert"
