# 19. Umsetzung & Technik

Dieses Kapitel bildet den Einstieg in den Implementierungsteil des Dokuments. Es beschreibt die Umsetzungsstrategie, das Drei-Phasen-Modell, den TDD-Ansatz und die technischen Entscheidungen für die erste Phase. Die nachfolgenden Kapitel 20 bis 24 liefern die detaillierte Spezifikationsbasis: Workflows (Kap. 20–22), Community und Trust Network (Kap. 23) und das technische Datenmodell (Kap. 24).
Leserhinweis: Wer das Konzept der Plattform verstehen möchte, findet alles Wesentliche in Kap. 1–18. Wer die Plattform implementieren möchte, liest ab Kap. 19. Die Kapitel 20–24 sind als Spezifikation angelegt – sie beschreiben was das System leisten soll und wie es strukturiert ist, nicht wie es implementiert wird. Kap. 19 (dieses Kapitel) beschreibt, in welcher Reihenfolge und mit welchen Werkzeugen die Implementierung angeangen wird.

## 19.1 Drei-Phasen-Modell
Die Implementierung folgt einem Drei-Phasen-Modell. Jede Phase hat einen klar definierten Zweck, einen eigenen Scope und einen eigenen Stack. Der Übergang zwischen den Phasen ist kein Schnitt, sondern ein kontinuierlicher Aufbau auf dem Fundament der vorherigen Phase.
Allen drei Phasen gemeinsam ist ein TDD-Ansatz (Test-Driven Development): Die Test Suite entsteht parallel zur Implementierung, wächst durch alle Phasen und wird kontinuierlich erweitert und vertieft. Sie ist das lebende Dokument des Systems – sie beschreibt nicht nur was gebaut wurde, sondern was gebaut werden muss.

PHASE 1 – TECHNISCHER DURCHSTICH (SPIKE)
> → Zweck: Technische Machbarkeit beweisen. Nicht Funktionsumfang, sondern Durchstich durch alle wesentlichen Kernfunktionalitäten.
> → Prinzip: Jede Kernfunktionalität wird mit minimalem Aufwand berührt. Kein Feature wird vollständig implementiert. Alles kann und wird in Phase 2 ersetzt oder überschrieben.
> → Ergebnis: Ein lauffähiges System, das zeigt dass die Architektur funktioniert. Kein Produkt für Endnutzer.

PHASE 2 – FUNKTIONSFÄHIGER PROTOTYP (TEASER)
> → Zweck: Einen guten Eindruck des Gesamtsystems vermitteln. Alle wesentlichen Funktionen sind vorhanden, aber noch nicht production-ready.
> → Prinzip: Funktionsumfang vor Performance und Skalierbarkeit. Ein echter Nutzer kann das System verstehen und seine Kernfunktionen erleben.
> → Ergebnis: Ein demonstrierbarer Prototyp für potenzielle Partner, Investoren und frühe Nutzer.
> → Hinweis: Scope und Stack können durch Erkenntnisse aus Phase 1 angepasst werden. Die Beschreibung in Kap. 19.4 ist daher ein Teaser, kein verbindlicher Plan.

PHASE 3 – ERSTE PRODUKTIONSREIFE VERSION (V1)
> → Zweck: Eine erste Version, die echten Nutzern zur Verfügung gestellt werden kann.
> → Prinzip: Performance, Skalierbarkeit, Sicherheit und Stabilität rücken in den Vordergrund. High-End-Features werden hinzugefügt.
> → Ergebnis: Ein produktionsreifes System, das öffentlich deployed werden kann.
> → Hinweis: Scope und Stack können durch Erkenntnisse aus Phase 1 und Phase 2 erheblich von der aktuellen Erwartung abweichen. Die Beschreibung in Kap. 19.5 ist ein grober Teaser.

## 19.2 TDD-Ansatz
Der TDD-Ansatz (Test-Driven Development) bedeutet: Tests werden vor oder parallel zur Implementierung geschrieben, nicht danach. Die Test Suite ist das primäre Qualitätssicherungsinstrument durch alle drei Phasen.
Aufbau der Test Suite
> → Unit Tests: Testen einzelne Funktionen und Klassen in Isolation. Laufen bei jedem Commit.
> → Integration Tests: Testen das Zusammenspiel von Datenbankschema, API-Endpunkten und KI-Serviceschicht. Laufen bei jedem Pull Request.
> → End-to-End Tests: Testen vollständige Nutzerflüsse durch die Anwendung. Laufen vor jedem Release.
> → KI-Evaluierungstests: Testen die Qualität der Claim-Extraktion und Konsistenzprüfung gegen bekannte Testfälle. Laufen wöchentlich und bei Änderungen am Prompting.
Wachstum der Test Suite durch die Phasen
> → Phase 1: Minimale Test Suite für den Durchstich. Jede berührte Kernfunktionalität hat mindestens einen Happy-Path-Test und einen Fehlerfall-Test.
> → Phase 2: Erweiterung um Integrationstests für alle Nutzerflüsse. Regressionsschutz für Phase-1-Funktionalität.
> → Phase 3: Vollständige Test Coverage für alle öffentlichen API-Endpunkte. Performance-Tests. Sicherheitstests.

## 19.3 Phase 1: Scope und Stack
19.3.1 Scope des Durchstichs
Der Durchstich berührt alle wesentlichen Kernfunktionalitäten mit minimalem Funktionsumfang. Das Ziel ist nicht ein nutzbares Produkt, sondern der Nachweis dass die Architektur trägt.
Folgende Funktionalitäten werden im Durchstich berührt:

NUTZER UND AUTHENTIFIZIERUNG
> → Registrierung und Login. Kein Trust Network, kein Profil, keine Rollen. Nur: ein Nutzer kann sich anmelden.

WIRKMODELL ANLEGEN
> → Ein Nutzer kann ein minimales Wirkmodell anlegen: Wirkraum, ein Axiom, ein Claim, eine Kausalrelation. Kein vollständiges Objektmodell, kein Statusmodell, keine Versionierung. Nur: das Schema funktioniert.

NARRATIV SCHREIBEN
> → Ein Nutzer kann eine Szene schreiben und speichern. Kein Volltext-Editor, keine Hierarchie (Werk/Kapitel/Szene), keine Metadaten. Nur: Text kann gespeichert werden.

KI-PRÜFUNG
> → Das System extrahiert nach dem Speichern einer Szene voräufige Claims via Claude API. Kein vollständiges Prüfverfahren, kein Axiomraum-Abgleich. Nur: die KI-Integration funktioniert und gibt strukturierte Ergebnisse zurück.

TRANSPARENZBERICHT
> → Das System generiert einen minimalen Transparenzbericht aus den extrahierten Claims. Kein vollständiger Bericht, keine Versionierung. Nur: ein Bericht kann erzeugt und angezeigt werden.

LESEANSICHT
> → Ein Nutzer kann einen Text und seinen Transparenzbericht lesen. Keine Leseumgebung, keine Personalisierung. Nur: Text und Bericht sind sichtbar.

19.3.2 Stack für Phase 1

DATENBANK: POSTGRESQL VIA SUPABASE
> → Supabase Cloud als Datenbankhost. PostgreSQL mit Row-Level Security für Privacy-by-Design. Supabase Auth für Authentifizierung. Kein separates Auth-System.
> → Begründung: PostgreSQL ist bereits im Datenmodell (Kap. 24) entschieden. Supabase vereint Datenbank, Auth und Row-Level Security in einem Dienst und reduziert den Infrastruktur-Overhead in Phase 1 erheblich.

KI-SERVICESCHICHT: PYTHON / FASTAPI + CLAUDE API
> → Separater Microservice für alle KI-Operationen: Claim-Extraktion, Konsistenzprüfung, Wirkmodell-Abgleich. Python wegen reichhaltiger NLP- und KI-Bibliotheken.
> → FastAPI wegen automatischer OpenAPI-Dokumentation, Type-Hints und asynchroner Unterstützung. Claude API (Anthropic) als LLM-Provider.
> → In Phase 1: Ein einziger Endpunkt für Claim-Extraktion aus Freitext. Der Service wird in Phase 2 erweitert.

FRONTEND: REACT
> → React mit TypeScript. Kein UI-Framework in Phase 1 – minimales Styling, Fokus auf Funktionalität. Supabase JS Client für Datenbankzugriff direkt aus dem Frontend.
> → In Phase 1: Vier Screens – Login, Wirkmodell-Editor (minimal), Narrativ-Editor (minimal), Leseansicht.

HOSTING: VERCEL + SUPABASE CLOUD
> → Vercel für Frontend-Deployment (zero-config für React). Supabase Cloud für Datenbank und Auth. FastAPI-Service auf Railway oder Render – einfachstes Deployment für Python-Microservices.

TESTING: PYTEST + VITEST + PLAYWRIGHT
> → pytest für Python/FastAPI Unit- und Integrationstests. Vitest für React-Komponenten-Tests. Playwright für End-to-End-Tests der vier Phase-1-Screens.

## 19.4 Phase 2: Teaser
Phase 2 baut auf dem Durchstich auf und erweitert ihn zum demonstrierbaren Prototyp. Der genaue Scope wird nach Abschluss von Phase 1 definiert – die Erkenntnisse aus dem Durchstich können Prioritäten verschieben.
Voraussichtlicher Funktionsumfang (kann sich ändern):
> → Vollständiger Wirkmodell-Editor mit allen Objektklassen aus Kap. 24, Graph-View und Text-View.
> → Vollständiger Narrativ-Editor mit Werk/Kapitel/Szene-Hierarchie, Metadaten (Cover, Klappentext, Tags) und Recycling.
> → Vollständige Konsistenzprüfung und Gateway-Logik.
> → Gegenrede-Mechanismus für Narrative und Wirkmodelle.
> → Minimale Leseumgebung mit Transparenzbericht und Wirkmodell-Exploration.
> → Minimales Community-System: Diskussionsbereich und strukturiertes Feedback.
> → Minimales Trust Network: Akzeptanz aussprechen und Systemakzeptanz berechnen.
Teaser Stack-Änderungen
> → Real-time: Supabase Realtime für kollaboratives Schreiben und Community-Updates. In Phase 1 noch nicht nötig.
> → UI-Framework: Einführung eines Komponentensystems (voraussichtlich shadcn/ui oder ähnlich).
> → Graphdarstellung: Einführung einer Graphbibliothek für den Wirkmodell-Graph-View (voraussichtlich React Flow oder Cytoscape.js).

## 19.5 Phase 3: Teaser
Phase 3 bringt den Prototypen in einen produktionsreifen Zustand. Scope und Stack werden nach Abschluss von Phase 2 definiert. Die folgenden Punkte sind grobe Erwartungen, keine Verpflichtungen.
> → Performance-Optimierung: Caching (Redis), Datenbankindizes, Query-Optimierung.
> → Skalierbarkeit: Horizontale Skalierung des FastAPI-Services, Connection Pooling für PostgreSQL.
> → Sicherheit: Penetrationstests, Rate Limiting, OWASP-Compliance.
> → Vollständiges Präsentationsmodus-Feature mit Kamera-Stream-Integration.
> → Vollständiges Statusmodell für Wirkmodelle (alle acht Status aus Kap. 21.3).
> → Admin-Workflows und Moderationswerkzeuge.
> → Mobile-Optimierung der Leseumgebung.
> → Erste öffentliche Beta.

## 19.6 Spezifikationsbasis für die Implementierung
Die folgenden Kapitel bilden die vollständige Spezifikation des Systems. Sie beschreiben was gebaut werden soll – dieses Kapitel beschreibt wie und in welcher Reihenfolge.

KAP. 20 – LITERATEN-WORKFLOW
> → Vollständiger Arbeitsablauf für schreibende Personen: Onboarding, vier Einstiegspfade, Schreibprozess, Veröffentlichungs-Gateway, Recycling.
> ↗ Querverweis: Literaten-Workflow – vgl. Kap. 20

KAP. 21 – WIRKMODELL-AUTOR-WORKFLOW
> → Vollständiger Arbeitsablauf für modellierende Personen: MVC-Prinzip, Fokusprinzip, fünf Einstiegspfade, Import-Formate, Statusmodell.
> ↗ Querverweis: Wirkmodell-Autor-Workflow – vgl. Kap. 21

KAP. 22 – LESER-WORKFLOW
> → Vollständiger Arbeitsablauf für lesende Personen: Entdeckung, Leseumgebung, Feedback, Community, Rollenwechsel, Präsentationsmodus.
> ↗ Querverweis: Leser-Workflow – vgl. Kap. 22

KAP. 23 – COMMUNITY, TRUST NETWORK UND NUTZERPROFIL
> → Zensur-Logik, Akzeptanz-System, Nutzerprofil und Moderationsregeln.
> ↗ Querverweis: Community, Trust Network, Nutzerprofil – vgl. Kap. 23

KAP. 24 – TECHNISCHES DATENMODELL
> → Vollständiges PostgreSQL-Schema mit allen Tabellen, Feldern, Relationen, Indizes und Designentscheidungen.
> ↗ Querverweis: Technisches Datenmodell – vgl. Kap. 24

## 19.7 Geparkte Entscheidungen
ADMIN-WORKFLOWS
⏸ Geparkt: Beschreibung der Admin- und Moderations-Workflows. Wird nach Phase 1 angegangen, wenn das Backend-Grundgerüst steht.

GARBAGE COLLECTOR FÜR MODELLE
⏸ Geparkt: Mechanismus zum Aufräumen verwaister oder ungenutzter Modellelemente. Erklärung und Spezifikation folgt.

EXECUTIVE SUMMARY AKTUALISIEREN
⏸ Geparkt: Kap. 1 spiegelt noch V0.9. Muss auf den Stand der aktuellen Konzeption gebracht werden.

STACK PHASE 2 UND 3 FINALISIEREN
⏸ Geparkt: Graphbibliothek, Real-time-Strategie, Caching. Wird nach Phase 1 konkretisiert.

MOBILE-STRATEGIE
⏸ Geparkt: Native App vs. Progressive Web App. Noch nicht entschieden.
