# 1. Executive Summary

klartext.jetzt ist eine epistemische Publikationsplattform. Sie verbindet narrative Texte mit formalen Wirkmodellen und macht die Annahmen, Kausalitäten und Weltbilder hinter öffentlichen Debatten sichtbar – für alle, nicht nur für Fachleute.

Das zentrale Problem ist nicht Informationsmangel, sondern epistemische Intransparenz. Menschen streiten nicht nur über Fakten, sondern über unterschiedliche Grundannahmen, die unsichtbar bleiben. Wer nicht weiß, was jemand voraussetzt, kann nicht verstehen warum er denkt wie er denkt. Das ist die Wurzel moderner Polarisierung.

klartext.jetzt adressiert dieses Problem durch drei miteinander verbundene Schichten:

→ Wissenschaftlich-kausale Ebene: Fachleute legen Wirkmodelle an – formale Repräsentationen von Axiomen, Kausalrelationen, Entitäten und Geltungsbereichen. Diese Modelle sind nicht Wahrheit, sondern explizite Setzungen. Wer ein anderes Modell hat, legt ein eigenes an.

→ Narrative Ebene: Literaten, Journalisten und andere schreibende Personen entwickeln Geschichten innerhalb eines gewählten Wirkmodells. Die Geschichte macht spürbar, was das Modell abstrakt beschreibt. Beide Ebenen sind bidirektional verbunden.

→ KI-gestützte Konsistenzschicht: Das System prüft fortlaufend ob die Geschichte konsistent mit dem Wirkmodell ist, extrahiert implizite Annahmen, markiert Lücken und erstellt einen epistemischen Transparenzbericht. Die KI ist kein Wahrheitsrichter – sie ist ein Konsistenz- und Transparenzwerkzeug.

Die Plattform kennt drei Nutzerrollen. Wirkmodell-Autoren legen formale Modelle an, importieren wissenschaftliche Literatur und pflegen Axiomräume. Literaten schreiben Geschichten, die auf Wirkmodellen aufbauen. Leser lesen Texte zusammen mit ihren Transparenzberichten, erkunden Wirkmodelle, geben strukturiertes Feedback und diskutieren in einem zensierten Raum, in dem nur über klar und unklar gestritten werden darf – nie über wahr und unwahr.

Die Plattform unterstützt drei Mechanismen für epistemischen Pluralismus: Gegenreden (ein Autor antwortet auf eine Geschichte mit einer eigenen, auf demselben oder einem anderen Wirkmodell), Recycling (ein Autor übernimmt eine Geschichte als Ausgangsmaterial und arbeitet sie mit einem anderen Wirkmodell um) und direkte Wirkmodell-Gegenentwürfe. Alle diese Relationen sind bidirektional transparent und dauerhaft sichtbar.

Die Gemeinschaft wird durch ein Trust Network aus Akzeptanz-Signalen strukturiert – nicht durch Bewertungen oder Follower-Zahlen, sondern durch die neutrale Anerkennung als ernsthafter Diskursteilnehmer. Ein Präsentationsmodus ermöglicht Live-Formate wie Podcasts und Streams, bei denen Wirkmodelle und Transparenzberichte direkt in den Diskurs eingebunden werden.

Technisch basiert die Plattform auf PostgreSQL (via Supabase), einer FastAPI-KI-Serviceschicht mit Claude API, und einem React-Frontend. Die Implementierung folgt einem Drei-Phasen-Modell mit TDD-Ansatz: technischer Durchstich (Phase 1), funktionsfähiger Prototyp (Phase 2), erste produktionsreife Version (Phase 3).

Die übergeordnete Vision: Komplexität soll nicht vereinfacht oder versteckt werden. Sie soll sichtbar, erzählbar und vergleichbar gemacht werden. Nicht Wahrheit soll zentralisiert werden – Verständlichkeit soll infrastrukturell ermöglicht werden.
