# 6. Systemarchitektur: Drei Schichten

Die Plattform lässt sich in drei zentrale Schichten gliedern.

## 6.1 Wissenschaftlich-kausale Ebene: Wirkmodell und Axiomraum

Das Wirkmodell bildet die formale Gesamtstruktur der wissenschaftlich-kausalen Ebene. Es beschreibt Entitäten, Zustände, Relationen, Kausalbeziehungen, Geltungsbereiche, Unsicherheiten und Evidenzbezüge. Der Axiomsraum bezeichnet die Menge aller innerhalb eines Wirkmodells als axiomatisch markierten Elemente. Grundsätzlich kann jede Instanz eines beliebigen Elementtyps eines Wirkmodells axiomatisch gesetzt werden. Ob eine Entität, Variable, Relation, Kausalität oder andere Struktur axiomatisch ist, hängt nicht vom Typ des Elements ab, sondern von seiner Rolle im Modell.

Ein Axiom ist dabei nicht zwingend eine absolute Wahrheit. Im Kontext dieses Projekts bezeichnet ein Axiom eine gesetzte Grundannahme innerhalb eines Modells, die als expliziter Ausgangspunkt dient und innerhalb des betrachteten Wirkmodells zunächst nicht weiter kausal hinterfragt wird. Entscheidend ist nicht ihr Wahrheitsstatus, sondern ihre Funktion als gesetzte Modellannahme. Ein Axiom kann empirisch gut belegt, kontrovers, hypothetisch oder normativ geprägt sein.

**Beispiele für Axiome könnten sein:**

Höhere Zinsen reduzieren unter bestimmten Bedingungen Investitionstätigkeit.

CO₂-Konzentrationen beeinflussen langfristige Temperaturentwicklung.

Soziale Ungleichheit erhöht unter bestimmten Bedingungen politische Polarisierung.

Politische Instabilität senkt Investitionsbereitschaft.

Mediennutzung beeinflusst Wahrnehmung gesellschaftlicher Risiken.

Neben einzelnen Axiomen werden Kausalbeziehungen definiert. Diese beschreiben, wie Elemente miteinander interagieren. Dabei können Bedingungen, Schwellenwerte, Unsicherheiten oder konkurrierende Gewichtungen angegeben werden.

**Die wissenschaftliche Ebene erfüllt somit mehrere Funktionen:**

Sie macht Annahmen explizit.

Sie definiert die Grenzen des Modells.

Sie beschreibt Kausalitäten.

Sie legt fest, welche Aussagen innerhalb dieses Modells zulässig sind.

Sie ermöglicht späteren Vergleich mit alternativen Axiomräumen.

## 6.2 Narrative Ebene und Referenzstruktur

Die narrative Ebene ist der Ort literarischer, journalistischer oder essayistischer Gestaltung. Autorinnen und Autoren entwickeln Figuren, Konflikte, Szenen, Dialoge, Perspektiven, Spannungsbögen und emotionale Dynamiken. Sie übersetzen abstrakte Kausalität in menschliche Erfahrung und machen modellierte Zusammenhänge erzählerisch erfahrbar.

Die narrative Ebene ist nicht bloße Verpackung. Sie ist ein eigenständiger Erkenntnismodus: Eine Geschichte kann zeigen, wie sich ein abstraktes Modell im Leben von Menschen auswirkt, Zielkonflikte sichtbar machen und Kausalität in konkreten Situationen veranschaulichen. Gleichzeitig bleibt die narrative Freiheit an das gewählte Wirkmodell und dessen Axiomraum gebunden. Eine Geschichte darf kreativ, literarisch und emotional sein; sie darf jedoch nicht ohne Markierung gegen die Grundannahmen und Kausalbeziehungen verstoßen, auf denen sie beruht.

Der naheliegende Vergleich ist Hard Science Fiction. In diesem Genre entstehen fiktionale Welten innerhalb konsistenter wissenschaftlicher oder technischer Regeln. Das Projekt überträgt dieses Prinzip auf gesellschaftliche, politische und wissenschaftliche Wirkmodelle im weiteren Sinne.

### 6.2.1 Narrative Artefakte als strukturierte Dokumente

Narrative Texte sind eigenständige Artefakte. Sie interpretieren, konkretisieren oder veranschaulichen Wirkmodelle, ersetzen diese jedoch nicht. Figuren, Konflikte, Szenen, Dialoge, Perspektiven und emotionale Dynamiken dürfen frei gestaltet werden, solange modellierte Bestandteile der Welt referenziert und nachvollziehbar eingebunden werden.

Die narrative Ebene wird als strukturierte Dokumenthierarchie verstanden. Narrative Artefakte können aus Werk, Teil, Kapitel, Szene und Fragment bestehen. Narrative Texte werden nicht als unstrukturierter Fließtext modelliert, sondern als strukturierte Dokumente mit referenzierbaren Bestandteilen.

### 6.2.2 Referenzen zwischen Narrativ und Wirkmodell

Sobald narrative Elemente auf modellierte Bestandteile der Welt Bezug nehmen, müssen formale Referenzen erzeugt werden. Referenzen sollen grundsätzlich auf die kleinstmögliche semantisch sinnvolle Einheit eines Wirkmodells verweisen. Referenzen auf größere Wirkmodellverbünde oder Modellaggregate sind zulässig, wenn eine Aussage bewusst mehrere Wirkzusammenhänge adressiert oder keine präzisere Zuordnung möglich ist.

Referenztypen können insbesondere sein:

Entitätsreferenzen: Verweise auf modellierte Organisationen, Institutionen, Orte, Technologien, Infrastrukturen oder andere Entitäten.

Policy-Referenzen: Verweise auf modellierte Regeln, Programme, politische Maßnahmen oder institutionelle Arrangements.

Zustandsreferenzen: Verweise auf modellierte gesellschaftliche, ökologische, ökonomische oder technische Zustände.

Kausalreferenzen: Verweise auf modellierte Ursache-Wirkungs-Beziehungen.

Zeitreferenzen: Verknüpfungen mit modellierten Zeitschichten oder Geltungsperioden.

Alternativitätsreferenzen: Verweise auf Variantenräume, Szenariopfade oder konkurrierende Modellvarianten.

Wirkverbund-Referenzen: Verweise auf mehrere miteinander verknüpfte Wirkmodelle.

### 6.2.3 Narrative Konkretisierung

Narrative Texte dürfen modellierte Zusammenhänge konkretisieren, ohne selbst Bestandteil des Wirkmodells zu werden. Narrative Szenen können modellierte Zustände, Regeln oder Kausalitäten exemplarisch verkörpern, ohne deren formale Repräsentation zu ersetzen.

### 6.2.4 Versionierung und bidirektionale Referenzintegrität

Narrative Texte sollen versionierbar sein. Unterschiedliche Fassungen, Zielgruppenvarianten, Perspektiven oder Überarbeitungen bleiben nachvollziehbar. Änderungen an referenzierten Wirkmodellen können Konsistenzwarnungen erzeugen, wenn narrative Texte auf veraltete Modellstände verweisen.

Wirkmodelle und ihre Bestandteile sollen Rückreferenzen auf narrative Verwendungen speichern. Modellobjekte können dadurch nachvollziehen, in welchen narrativen Artefakten sie erwähnt, kausal erklärt, konkretisiert oder kritisch reflektiert werden. Dies ermöglicht Transparenz, Änderungsfolgenanalyse und Nachvollziehbarkeit.

→ Narrativ-Narrativ-Relationen (Gegenrede): Eine „Gegenrede“-Relation verbindet zwei narrative Artefakte bidirektional. Drei Varianten: A (gleicher Axiomraum, andere Perspektive), B (gleicher Wirkraum, abweichender Axiomraum), C (anderes Wirkmodell). Das Original weiß, dass es Gegenreden gibt. Die Gegenrede weiß, auf welches Original sie antwortet.

↗ Querverweis: Gegenrede-Varianten – vgl. Kap. 20.1 und 20.1

## 6.3 KI-gestützte Konsistenz- und Transparenzschicht

Die dritte Schicht verbindet Wirkmodell, Axiomraum und Narrativ. Sie ist das operative Zentrum des Systems. Hier kommt ein Large Language Model oder eine Kombination mehrerer KI-Modelle zum Einsatz, um den entstehenden Text fortlaufend zu analysieren.

Die KI ist dabei nicht primär als kreativer Generator gedacht. Ihre zentrale Funktion ist epistemisch und analytisch. Sie prüft, ob die Geschichte innerhalb des gewählten Wirkmodells und seines Axiomraums bleibt, ob implizite Annahmen entstehen und ob die erzählten Ereignisse mit den definierten Kausalitäten vereinbar sind.

Die Konsistenz- und Transparenzschicht ist primär eine funktionale Schicht. Sie besitzt kein eigenständiges fachliches Domänenmodell neben Wirkmodell und Narrativ. Sie operiert auf den Daten der wissenschaftlich-kausalen Ebene und der narrativen Ebene. Ihre Ergebnisse bestehen in abgeleiteten Prüf-, Referenz- und Transparenzartefakten, etwa Konfliktmarkierungen, impliziten Annahmen, Kausalitätslücken und epistemischen Transparenzberichten.

### 6.3.1 Aufgaben der Konsistenzschicht

Diese Schicht übernimmt insbesondere folgende Aufgaben:

Abgleich narrativer Aussagen mit expliziten Axiomen.

Erkennung möglicher Widersprüche zwischen Geschichte, Wirkmodell und Axiomraum.

Identifikation impliziter, nicht genannter Voraussetzungen.

Markierung fehlender Kausalglieder.

Vorschläge zur Explizierung verdeckter Annahmen.

Erstellung eines epistemischen Transparenzberichts.

Die KI fungiert damit nicht als Wahrheitsrichter, sondern als Konsistenz- und Transparenzinstrument.

→ Voräufige Claim-Extraktion aus narrativem Text: Das System extrahiert beim Speichern einer Szene voräufige Claims als mögliche Aussagekerne. Nicht verbindlich. Die schreibende Person kann bestätigen, verwerfen, umformulieren oder offen lassen.

↗ Querverweis: Claim-Extraktion im Schreibprozess – vgl. Kap. 20.2.2

### 6.3.2 Konsistenzprüfung zwischen Wirkmodell und Narrativ

Ziel der Konsistenzprüfung ist die Sicherstellung epistemischer Nachvollziehbarkeit bei gleichzeitiger Wahrung narrativer Freiheit. Die Prüfung soll nicht literarische Gestaltung normieren, sondern sichtbar machen, an welchen Stellen ein Narrativ modellkonform ist, implizite Voraussetzungen erzeugt oder bewusst markierte Abweichungen enthält.

Vorläufige Prüfklassen sind:

Referenzintegritätsprüfung

Modellkonsistenzprüfung

Zeitkonsistenzprüfung

Kausalkonsistenzprüfung

Alternativpfad-Konsistenz

Granularitätsprüfung

### 6.3.3 Spätere Spezifikation

Zu einem späteren Zeitpunkt sollen Referenzauflösungsebenen (harte, weiche und symbolische Referenzen) sowie der Umgang mit akzeptierten narrativen Abweichungen näher spezifiziert werden.

**6.4 Community, Trust Network und Leseumgebung**

Neben den drei technischen Schichten bildet die Community-Schicht das soziale Fundament der Plattform.

→ Leseumgebung: Eine eigenständige Umgebung mit drei integrierten Bereichen: Textansicht, Transparenzbericht und Wirkmodell-Exploration (read-only). Drei Lesemodis: Fokus, Split-View, Annotiert. Entdeckung über Katalog, Wirkmodell-Einstieg, Gegenrede-Ketten und konfigurierbare Heatmap.

→ Community-Diskurs: Zensierter Diskussionsbereich für jedes veröffentlichte Werk. Zensiert bedeutet: Es darf nur über klar und unklar gestritten werden, nie über wahr und unwahr. Axiome sind innerhalb des Systems nicht anfechtbar – die richtige Antwort auf ein abgelehntes Axiom ist ein Gegenentwurf, kein Gegenargument.

→ Trust Network: Akzeptanz-basiertes Vertrauenssystem analog zu EigenTrust+. Akzeptanz ist keine Zustimmung, sondern die neutrale Anerkennung als ernsthafter Diskursteilnehmer. Drei Profilwerte: persönliche Akzeptanz, Peer-Group-Akzeptanz, Systemakzeptanz.

↗ Querverweis: Leser-Workflow – vgl. Kap. 22

↗ Querverweis: Community, Trust Network und Nutzerprofil – vgl. Kap. 23
