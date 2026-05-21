# 21. Wirkmodell-Autor-Workflow

Dieser Workflow beschreibt den Arbeitsablauf für Personen, die Wirkmodelle anlegen, pflegen und veröffentlichen. Analog zu Kap. 20, aber mit zwei grundlegend verschiedenen Dimensionen: UI-Modell (MVC-Prinzip + Fokusprinzip) und Import (prominenter und wissenschaftlich spezialisierter).
> ↗ Querverweis: Literaten-Workflow – vgl. Kap. 20
> ↗ Querverweis: Objekt- und Lebenszyklusmodell – vgl. Kap. 7.4

## 20.1 Onboarding
Schritt 1: Einstiegspfad
Fünf Optionen gleichwertig.

OPTION A – LEERES MODELL
> → Leerer Wirkraum. Leitfragen: thematischer, zeitlicher und räumlicher Geltungsbereich, Abstraktionsebene, Modellzweck.
> ↗ Querverweis: Wirkraum – vgl. Kap. 7.3.1

OPTION B – IMPORT
> → Formate: JATS XML, BibTeX/RIS, PDF, OWL/RDF. Vollwertiger Einstiegspfad, kein Hilfsmittel. Details: vgl. Kap. 21.4.

OPTION C – GEGENENTWURF
> → Variante A: gleicher Wirkraum, abweichender Axiomraum. Variante B: gleicher Wirkraum, erweiterte Modelltiefe. Variante C: konkurrierendes Wirkmodell mit anderem Wirkraum. Bidirektionale Wirkmodell-Wirkmodell-Relation wird angelegt.
> ↗ Querverweis: Konflikt- und Variantenrelationen – vgl. Kap. 7.6.5

OPTION D – VERBUND
> → Mehrere Wirkmodelle als Teilmodelle. Verbundstruktur: Abhängigkeits-, Input-Output- oder Zeitrelationen. Sofortige Schnittstellenkompatibilitätsprüfung.
> ↗ Querverweis: Wirkmodellverbünde – vgl. Kap. 7.6

OPTION E – ONTOLOGIE-IMPORT
> → Startet mit Import einer formalen Ontologie (OWL, RDF, RDFS, SKOS). Leitet in Kap. 21.4.5 weiter.

Schritt 2: View-Präferenz
Alle Views zeigen dasselbe Modell. Änderungen in einem View sofort in allen sichtbar.

GRAPH (VOREINSTELLUNG)
Netzwerkorientiert. Modellelemente als Knoten, Relationen als gerichtete Kanten. Fokusprinzip: aktives Element zentriert. Kanten sind selektierbar und editierbar – Kausalrelationen sind reich attributierte Objekte; Klick öffnet vollständiges Objekt.

TEXT
Strukturierter Texteditor. Ideal für natürliche Sprache und komplexe Attribute.

TIMELINE
Zeitachsenansicht nach Zeitscheiben und Geltungsperioden.

TABELLE
Elementtyp als Zeilen, Attribute als Spalten. Direkt editierbar.

BAUM
Hierarchische Teil-Ganzes-Ansicht. Primär Navigationswerkzeug.

Weitere Views möglich; MVC-Prinzip stellt sicher, dass sie das Modell nicht verändern.

Schritt 3: Systemverhalten
Identisch mit Kap. 20.1, Schritt 3: still / dezent / aktiv.
> ↗ Querverweis: Systemverhalten – vgl. Kap. 20.1, Schritt 3

## 20.2 Das UI-Modell
20.2.1 MVC-Prinzip
Eine einzige interne Repräsentation (Objektmodell aus Kap. 7.4). Views sind Fenster darauf. Text-View, Graph-View, Timeline-View – alle zeigen dasselbe Modell. Keine "Graph-Version" und "Text-Version".
> ↗ Querverweis: Objektmodell – vgl. Kap. 7.4
20.2.2 Fokusprinzip
Immer genau ein fokussiertes Element als Anker. Alle anderen Elemente ordnen sich nach semantischer Nähe (gemäß Relationensystem aus Kap. 7.4.4) um diesen Anker.
> ↗ Querverweis: Relationen zwischen Objektklassen – vgl. Kap. 7.4.4
20.2.3 Graph-View: Kanten als editierbare Objekte
Kausalrelationen sind im Objektmodell reich attributierte Klassen (Mechanismus, Polarität, Zeitverzögerung, Unsicherheit, Geltungsbereich). Im Graph-View sind daher Kanten selektierbar und editierbar:
> → Klick auf Kante: selektiert die Relationsinstanz.
> → Doppelklick: öffnet vollständiges Objekt zur Bearbeitung aller Attribute.
> → Neue Kante per Drag: System fragt nach Relationstyp und weiteren Attributen.
> → Konflikte: rote Kante. Lücken: gestrichelter Knoten. Prüfpflichtig: Indikator.
> ↗ Querverweis: Kausalrelation als Objektklasse – vgl. Kap. 7.3.5 und 7.4.3 D

## 20.3 Statusmodell für Wirkmodelle
Jedes Wirkmodell hat zu jedem Zeitpunkt genau einen Status.

PRIVAT
Nur für Hauptautor sichtbar. Standard nach Anlage.

GETEILT
Für explizit eingeladene Personen. Kollaboration möglich.

REVIEWFÄHIG
Bereit für strukturiertes Feedback. Reviewende können kommentieren.

INTERN SICHTBAR
Für alle Plattformnutzer. Noch nicht im öffentlichen Katalog.

KATALOGSICHTBAR
Öffentlicher Katalog. Literaten können als Grundlage nutzen. Benachrichtigungen bei Änderungen aktiv.

ARCHIVIERT
Nicht aktiv, bleibt zugänglich. Keine neuen Verknüpfungen.

ERSETZT
Nachfolger-Link hinterlegt. Bestehende Verknüpfungen werden hingewiesen.

ZURÜCKGEZOGEN
Aktiv zurückgezogen. Begründung Pflicht. Verknüpfungen werden benachrichtigt.

Statusübergänge: Privat → Geteilt → Reviewfähig → Intern sichtbar → Katalogsichtbar. Von dort: Archiviert, Ersetzt oder Zurückgezogen. Rückwärtstransitionen nur mit Begründung.
> ↗ Querverweis: Lebenszyklusmodell – vgl. Kap. 7.4.7

## 20.4 Import im Detail
Import ist vollwertiger, häufig genutzter Einstiegspfad. Generell gilt für alle Importpfade:
> → Urheberrechtshinweis: Das System erinnert beim Import auf mögliche urheberrechtliche Grenzen. Das System leistet keine Rechtsberatung. Die rechtliche Verantwortung verbleibt vollständig bei der modellierenden Person.
> → Automatische Quellenangabe: Bei jedem durch Import entstandenen Modellelement wird automatisch eine Quellenangabe hinterlegt (Titel, Autor, Jahr, DOI, Typ). Diese ist im Transparenzbericht sichtbar und kann nicht gelöscht, nur ergänzt werden.
20.4.1 JATS XML
Standardformat für wissenschaftliche Artikel (PubMed, PMC, CrossRef). Extraktion: Metadaten, Abstract, Volltext, Referenzliste. Das System extrahiert voräufige Claims, Kausalrelationen, Annahmen und Evidenzbezüge zur Bestätigung durch die modellierende Person. Mehrere Dokumente können nacheinander importiert werden; System erkennt übereinstimmende und widersprechende Claims.
> ↗ Querverweis: Evidenzobjekte – vgl. Kap. 7.3.9 und 7.4.3 C
20.4.2 BibTeX / RIS
Literaturverwaltung (Zotero, Mendeley, EndNote). Metadaten ohne Volltext. Je Referenz ein Evidenzobjekt. Manuelle Verknüpfung mit Claims. Volltext-Ergänzung nachträglich möglich.
20.4.3 PDF mit Textextraktion
Häufigstes Format; weniger zuverlässig als JATS. System extrahiert Text, behandelt ihn wie Freitext im Text-View. Gescannte PDFs ohne Maschinentext: Hinweis, keine Verarbeitung möglich.
20.4.4 OWL / RDF (Formale Ontologien)
Sonderfall: Quelldaten bereits formal strukturiert. System übersetzt: Klassen → Entitäten; Properties → Relationen; Axiome → Annahmen; Restrictions → Geltungsbedingungen. Übersetzung nie vollständig verlustfrei – mehrdeutige Stellen werden als Mehrdeutigkeitsmarkierungen gekennzeichnet. Einstiegspfad E leitet direkt hierher.
Hinweis zu lizenzierten Ontologien: Besonders relevant bei kommerziell lizenzierten Vokabularen (z.B. SNOMED CT, MeSH).
> ↗ Querverweis: Objektklassen – vgl. Kap. 7.4.3
> ↗ Querverweis: Mehrdeutigkeitsmarkierung – vgl. Kap. 7.4.3 F

## 20.5 Phase 1: Freies Modellieren
20.5.1 Systemverhalten im Hintergrund
Sobald ein Modellelement gespeichert wird:
> → Strukturprüfung: vollständig typisiert? Pflichtattribute vorhanden? Unverbundene Knoten?
> → Lokale Konsistenzprüfung: Widersprüche im selben Geltungsbereich?
> → Lückenprüfung: fehlender Wirkmechanismus? Kausalrelation ohne Quelle/Ziel? Claim ohne Evidenz?
> → Mehrdeutigkeitsprüfung: gleicher Begriff unterschiedlich verwendet?
> → Verbundprüfung (wenn Teil eines Verbunds): Schnittstellenkompatibilität bei Änderung von Inputs/Outputs.
> ↗ Querverweis: Prüfverfahren – vgl. Kap. 7.5
20.5.2 Modellrestrukturierung
Regelmäßiger Vorgang. System unterstützt: Neu-Situierung, Extraktion als eigenes Wirkmodell, Zusammenführung. Alle Operationen als Transformationsrelation protokolliert und rükgängig machbar.
> ↗ Querverweis: Modellrestrukturierung – vgl. Kap. 7.7

## 20.6 Phase 2: Veröffentlichungs-Gateway
Analog zu Kap. 20.3, mit wirkmodellspezifischen Prüfungen. Wirkmodelle können unabhängig von Narrativen veröffentlicht werden.
20.6.1 Rechtskonformitätsprüfung
Das System prüft auf Konformität mit dem deklarierten Rechtsraum. Das System leistet keine verbindliche Rechtsberatung. Verantwortung verbleibt bei der modellierenden Person.
20.6.2 Wirkmodellspezifische Prüfungen
> → Vollständigkeitsprüfung über Kompetenzfragen.
> → Schnittstellenprüfung: Inputs/Outputs definiert und typkompatibel?
> → Verbundprüfung: Modellverträge erfüllt, Abhängigkeiten auflösbar?
> → Versionierungsprüfung: Abhängige Artefakte werden über neue Version benachrichtigt.
> ↗ Querverweis: Prüfverfahren – vgl. Kap. 7.5
> ↗ Querverweis: Verbundprüfung – vgl. Kap. 7.8
20.6.3 Statusmodell im Gateway
Das Gateway überführt das Wirkmodell durch die Statuskette. Jeder Schritt erfordert erfüllte Voraussetzungen.
> ↗ Querverweis: Statusmodell – vgl. Kap. 21.3
20.6.4 Änderungen nach Veröffentlichung
Änderungen erzeugen neue Versionen. Abhängige Artefakte bleiben auf alter Version; werden über neue Version benachrichtigt.
⏸ Geparkt: Vollständiges Versionsmanagement – geparkt, vgl. 20.9

METADATEN FÜR DEN KATALOG
> → Analog zu Kap. 20, Schritt 2.5: Cover, Klappentext und Tags für Wirkmodelle. Beim Wirkmodell kann der Klappentext den Wirkraum, die zentrale Fragestellung und die wichtigsten Erklärungsansätze für Nicht-Fachleute beschreiben.

Recycling und Wirkmodell-Einzug: Wenn ein Literat ein Werk recycelt und dabei ein neues Wirkmodell einzieht, kann er direkt aus der Autorenumgebung auf den Wirkmodell-Katalog zugreifen. Das Refactoring-Tool nutzt die Wirkmodell-Repräsentation, um betroffene Textstellen zu identifizieren.
> ↗ Querverweis: Recycling und Refactoring-Tool – vgl. Kap. 20.9
> → Tags können sowohl domänenspezifisch (z.B. Klimapolitik, Gesundheitssystem) als auch methodisch (z.B. Kausalmodell, Szenarioanalyse) sein.
> ↗ Querverweis: Katalog und Entdeckung – vgl. Kap. 22.2

## 20.7 Kollaboration
Identisch mit Kap. 20.5: Hauptautor, Co-Autor, gleichberechtigter Autor, begrenzte Einladungen, Rechtsraum.
> ↗ Querverweis: Kollaboration – vgl. Kap. 20.5

## 20.8 Designprinzipien
EINE REPRÄSENTATION, VIELE VIEWS
Einzige Modellinstanz; Views sind Fenster darauf.

FOKUS STATT ÜBERSICHT
Zentriertes Element + semantische Umgebung. Komplexität durch Navigation beherrschbar.

IMPORT ALS GLEICHWERTIGER EINSTIEG
Mit automatischer Quellenangabe und Urheberrechtshinweis bei jedem Importpfad.

KANTEN SIND OBJEKTE
Kausalrelationen sind reich attributierte Objekte; Kanten im Graph-View sind selektierbar und vollständig editierbar.

STATUSMODELL ALS LEITFADEN
Explizites Statusmodell von privat bis katalogsichtbar; transparente Archivierung, Ersatz oder Rückzug.

MODELLRESTRUKTURIERUNG IST NORMAL
Explizit unterstützt, protokolliert, rükgängig machbar.

DAS SYSTEM FRAGT, ES URTEILT NICHT
Urheberrechtshinweise als Erinnerung, keine Verbote. Keine Rechtsberatung.

ERWEITERBARKEIT DER VIEWS
MVC ermöglicht neue Views ohne Modelländerung.

## 20.9 Geparkte Themen
VERSIONSMANAGEMENT
⏸ Geparkt: Abhängigkeitsgraph; Breaking-Change-Erkennung und -Kommunikation.

WEITERE VIEWS
⏸ Geparkt: Matrixansicht; Netzwerkkarte für Verbundstrukturen.

KI-EXTRAKTION
⏸ Geparkt: Qualitätsschwellen, Konfidenzwerte, widersprechände Extraktion aus mehreren Quellen.

KOLLABORATIVER REVIEW
⏸ Geparkt: Peer-Review-Verfahren analog zu wissenschaftlichen Zeitschriften.

DOMÄNENONTOLOGIEN
⏸ Geparkt: SNOMED, MeSH, ENVO als Standardreferenzrahmen.

VERBUND-GOVERNANCE
⏸ Geparkt: Rechte und Pflichten bei Verbund-Änderungen.

LOGGING
⏸ Geparkt: Protokollierung von Modellierungshandlungen.
