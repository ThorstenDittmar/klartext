# 7. Formale Wirkmodelle und modellinterne Prüfverfahren

## 7.1 Abgrenzung: Import eines Wirkmodells und Prüfung eines Wirkmodells

Für die Plattform ist zwischen zwei Aufgabenbereichen zu unterscheiden:

Import, Extraktion und Anlage eines Wirkmodells: Dieser Bereich betrifft die Frage, wie aus natürlicher Sprache, wissenschaftlichen Texten, Debattenbeiträgen, Datensätzen oder bestehenden Modellen ein formalisiertes Wirkmodell erzeugt wird. Hier wären Verfahren wie Argumentation Mining, Natural Language Processing, Terminologie-Extraktion, Ontologie-Mapping oder manuell geführte Modellierungsdialoge relevant.
Prüfung eines bereits angelegten Wirkmodells: Dieser Bereich betrifft die Frage, ob ein vorhandenes Wirkmodell intern konsistent, explizit, strukturell vollständig, semantisch eindeutig, argumentativ nachvollziehbar und formal prüfbar ist. Die Plattform bewertet dabei nicht, ob die Aussagen empirisch wahr sind oder ob bestimmte normative Setzungen richtig sind. Sie prüft vielmehr, ob das Modell seine eigenen Voraussetzungen, Relationen, Schlussregeln, Geltungsbereiche, Evidenzstandards, Konsequenzen und offenen Stellen transparent macht.

Im Folgenden wird ausschließlich der zweite Bereich behandelt: die Prüfung bereits angelegter Wirkmodelle.

## 7.2 Grundbegriff: Wirkmodell

Ein Wirkmodell ist eine formale, versionierte und prüfbare Repräsentation von Annahmen darüber, welche Entitäten, Zustände, Prozesse, Bedingungen, Ursachen, Wirkungen, Argumente und Evidenzbezüge innerhalb eines abgegrenzten Wirkraums relevant sind.

Ein Wirkmodell beschreibt nicht notwendig die empirische Wirklichkeit selbst. Es beschreibt vielmehr, wie ein bestimmter Autor, eine Gruppe, eine Theorie oder ein hypothetisches Szenario einen Ausschnitt von Wirklichkeit modelliert. Dadurch können auch konkurrierende, spekulative, kontrafaktische, fiktionale oder fachlich randständige Wirkmodelle nebeneinander bestehen, sofern ihre jeweiligen Annahmen explizit und ihre internen Strukturen prüfbar sind.

Die Plattform ist daher keine Wahrheitsmaschine. Sie entscheidet nicht, welches Wirkmodell die Welt korrekt abbildet. Sie dient der Klarheit über Wirkannahmen. Ihre Aufgabe besteht darin, Voraussetzungen, Begriffe, Relationen, Kausalannahmen, Schlussregeln, Geltungsbereiche, Evidenzstandards, Konflikte, Lücken und Konsequenzen sichtbar zu machen.

Ein Wirkmodell ist nicht primär ein Text, sondern eine formale Struktur. Natürliche Sprache dient der Eingabe, Erläuterung und Darstellung; die interne Repräsentation besteht aus typisierten Modellobjekten.

Für das Wirkmodell gilt dabei ein zentrales Prinzip: Interpretative Entscheidungen dürfen bei der Modellbildung getroffen werden, dürfen aber im fertigen Wirkmodell nicht als unaufgelöste Mehrdeutigkeit verbleiben.

Ein Wirkmodell kann also auf Deutungen, Annahmen, normativen Setzungen oder hypothetischen Entscheidungen beruhen. Diese müssen jedoch als formale Modellbestandteile ausgewiesen werden: als Definition, Annahme, Axiom, Variante, Geltungsbereich, Prioritätsregel, Unsicherheit, Konflikt oder offene Lücke.

Die Modellsemantik muss eindeutig auswertbar sein. Das bedeutet nicht, dass die modellierte Welt deterministisch sein muss. Ein Wirkmodell kann Wahrscheinlichkeiten, Unsicherheiten, Szenarien oder alternative Verläufe enthalten. Entscheidend ist jedoch, dass eindeutig bestimmbar ist, wie diese Unsicherheiten, Varianten oder Alternativen im Modell formal behandelt werden.

Nicht zulässig als fertiger Modellzustand wäre:

Begriff X kann irgendwie A oder B bedeuten.

Zulässig wäre:

Definition 1: X = A.
Definition 2: X = B.
Modellvariante M1 verwendet Definition 1.
Modellvariante M2 verwendet Definition 2.

Nicht zulässig wäre:

Modell A und Modell B liefern widersprüchliche Ergebnisse, aber beide gelten irgendwie.

Zulässig wäre:

Output A und Output B stehen in Konflikt.
Status: unresolved_conflict.
Erforderliche Auflösung: Prioritätsregel, Variantenbildung, zeitliche Trennung oder explizite Konfliktmarkierung.

Damit wird das Wirkmodell nicht zu einer Wahrheitsmaschine, sondern zu einem formal auswertbaren Klarheitsmodell.

## 7.3 Bestandteile eines Wirkmodells

### 7.3.1 Wirkraum

Der Wirkraum bezeichnet den abgegrenzten Bereich, für den ein Wirkmodell gelten soll.

Er enthält mindestens:

thematischen Geltungsbereich,
zeitlichen Geltungsbereich,
räumlichen Geltungsbereich,
Abstraktionsebene,
beteiligte Domäne oder Disziplin,
Zweck des Modells,
Modellgrenzen.

Beispiel:

Wirkraum:
Globale Klimadynamik von 1850 bis 2100 unter besonderer Berücksichtigung anthropogener und natürlicher Einflussfaktoren.

Der Wirkraum legt nicht fest, was wahr ist. Er legt fest, worüber das Modell Aussagen macht und innerhalb welcher Grenzen diese Aussagen gelten sollen.

### 7.3.2 Entitäten

Entitäten sind die grundlegenden Gegenstände des Modells. Dazu können physische Objekte, Akteure, Institutionen, Größen, Prozesse oder abstrakte Konzepte gehören.

Beispiele:

Atmosphäre
CO₂-Konzentration
globale Mitteltemperatur
Sonnenaktivität
Industrieemissionen
Klimapolitik

Jede Entität sollte typisiert sein, etwa als physikalische Größe, Akteur, Prozess, Institution, Norm, Messgröße oder Modellvariable.

### 7.3.3 Zustände und Eigenschaften

Entitäten können Zustände oder Eigenschaften besitzen.

Beispiele:

CO₂-Konzentration: steigt
globale Mitteltemperatur: steigt
Sonnenaktivität: stabil
Emissionsniveau: hoch

Zustände sollten möglichst Angaben zu Einheit, Richtung, Messgröße, Skala und Zeitraum enthalten.

### 7.3.4 Relationen

Relationen beschreiben Beziehungen zwischen Entitäten, Zuständen oder Aussagen.

Zu unterscheiden sind insbesondere:

definitorische Relationen,
Teil-Ganzes-Relationen,
Zugehörigkeitsrelationen,
Vergleichsrelationen,
kausale Relationen,
argumentative Relationen,
normative Relationen,
Evidenzrelationen.

Beispiel:

CO₂ ist ein Treibhausgas.
CO₂-Konzentration beeinflusst Strahlungsantrieb.
Strahlungsantrieb beeinflusst globale Mitteltemperatur.

Die Plattform prüft hier nicht, ob diese Relationen empirisch zutreffen, sondern ob sie formal eindeutig, typologisch passend und innerhalb des Modells nachvollziehbar eingebunden sind.

### 7.3.5 Kausalrelationen

Kausalrelationen sind gerichtete Wirkbeziehungen. Sie sollten nicht nur Quelle und Ziel enthalten, sondern auch Mechanismus, Polarität, Stärke, Verzögerung, Geltungsbedingungen und Unsicherheit.

Beispiel:

Quelle: steigende CO₂-Konzentration
Ziel: steigender Strahlungsantrieb
Mechanismus: Absorption infraroter Strahlung
Polarität: positiv
Bedingung: atmosphärischer Kontext
Status: empirische Kausalannahme

Auch kontrafaktische oder hypothetische Kausalrelationen können modelliert werden. Entscheidend ist, dass sie im Wirkmodell explizit dargestellt werden.

Eine Kausalrelation darf nicht bloß interpretativ offen bleiben. Wenn mehrere Mechanismen möglich sind, müssen sie als Varianten, konkurrierende Hypothesen, offene Lücken oder bedingte Relationen modelliert werden.

### 7.3.6 Claims

Ein Claim ist eine im Modell behauptete Aussage.

Claims sollten typisiert werden:

empirischer Claim,
kausaler Claim,
definitorischer Claim,
normativer Claim,
prognostischer Claim,
kontrafaktischer Claim,
methodischer Claim,
Unsicherheitsclaim.

Beispiel:

Der Temperaturanstieg seit Mitte des 20. Jahrhunderts ist überwiegend anthropogen verursacht.

Ein Claim wird nicht dadurch für die Plattform relevant, dass er wahr ist, sondern dadurch, dass er im Wirkmodell eine Rolle spielt und mit anderen Modellbestandteilen verbunden ist.

> → Voräufige Claims aus Narrativen: Claims können auch aus narrativem Text extrahiert werden. Zunächst nicht verbindlich; werden zur Bestätigung, Verwerfung oder Reformulierung vorgelegt.
> ↗ Querverweis: Claim-Extraktion – vgl. Kap. 20.2.2
### 7.3.7 Annahmen und Axiome

Annahmen oder Axiome sind Voraussetzungen, die innerhalb des Modells gesetzt werden. Sie können empirisch, theoretisch, methodisch, definitorisch oder normativ sein.

Beispiel:

Messreihen globaler Mitteltemperaturen sind hinreichend zuverlässig, um langfristige Trends zu bestimmen.

Solche Annahmen müssen nicht innerhalb des Modells endgültig bewiesen werden. Sie müssen aber explizit sein. Ein Wirkmodell darf auch Annahmen setzen, die außerhalb des Modells umstritten oder fachlich randständig sind. Die Plattform prüft dann nicht deren Wahrheit, sondern deren Rolle, Konsistenz und Konsequenzen innerhalb des Modells.

### 7.3.8 Schlussregeln

Schlussregeln legen fest, unter welchen Bedingungen aus bestimmten Aussagen andere Aussagen folgen.

Beispiel:

Wenn X die wichtigste Ursache von Y ist und Y ein relevantes Risiko erzeugt, dann ist X ein zentraler Interventionspunkt.

Hier ist erkennbar: Diese Regel enthält nicht nur empirische, sondern auch handlungsbezogene und gegebenenfalls normative Bestandteile. Die Plattform prüft, ob solche Bestandteile getrennt und explizit modelliert sind.

Schlussregeln müssen eindeutig anwendbar sein. Wenn mehrere Regeln zu unterschiedlichen Ergebnissen führen, muss das Modell klären, ob eine Prioritätsregel gilt, ob Varianten entstehen, ob die Regeln unterschiedliche Geltungsbereiche haben oder ob ein ungelöster Konflikt vorliegt.

### 7.3.9 Evidenzobjekte

Evidenzobjekte beschreiben, worauf sich Claims innerhalb eines Wirkmodells stützen. Das können Messdaten, Studien, Modellrechnungen, Expertisen, theoretische Ableitungen, Simulationen, narrative Setzungen oder interne Modellannahmen sein.

Für die Prüfung eines Wirkmodells ist zunächst nicht entscheidend, ob die Evidenz außerhalb des Modells abschließend als richtig gilt. Entscheidend ist, ob sichtbar ist, welche Aussage auf welcher Evidenz oder welchem Evidenzstandard beruht.

### 7.3.10 Gegenclaims und Konfliktrelationen

Ein Wirkmodell sollte auch Einwände, konkurrierende Erklärungen und Gegenclaims darstellen können.

Beispiel:

Claim A: Der aktuelle Temperaturanstieg ist überwiegend anthropogen.
Claim B: Der aktuelle Temperaturanstieg ist überwiegend durch natürliche Variabilität erklärbar.
Relation: Konflikt / gegenseitige Inkompatibilität unter gleichem Geltungsbereich.

Die Plattform entscheidet nicht automatisch, welcher Claim wahr ist. Sie macht sichtbar, worin der Konflikt besteht: in Begriffen, Geltungsbereichen, Kausalannahmen, Evidenzstandards, Schlussregeln oder normativen Setzungen.

Konflikte dürfen nicht verdeckt bleiben. Wenn zwei Claims im selben Geltungsbereich miteinander unvereinbar sind, muss dies als Konfliktrelation, Variantenbildung, Prioritätsregel oder offene Lücke formal ausgewiesen werden.

### 7.3.11 Geltungsbereiche

Jede relevante Aussage sollte einen Geltungsbereich besitzen:

zeitlich,
räumlich,
sachlich,
disziplinär,
methodisch,
epistemisch.

Viele Scheinkonflikte entstehen, weil Aussagen unterschiedliche Geltungsbereiche haben.

Beispiel:

„Klima verändert sich immer“ bezieht sich auf geologische Zeiträume.
„Der aktuelle Klimawandel ist anthropogen“ bezieht sich auf die jüngere historische Periode.

Diese Aussagen widersprechen sich nicht notwendig, wenn ihre Geltungsbereiche sauber unterschieden werden.

### 7.3.12 Unsicherheiten und Statusangaben

Ein Wirkmodell sollte angeben, welchen epistemischen Status eine Aussage hat.

Mögliche Statuswerte:

gesetzt,
abgeleitet,
hypothetisch,
empirisch gestützt,
modellabhängig,
umstritten,
offen,
widerlegt innerhalb des Modells,
normativ gesetzt.

Unsicherheit ist nicht dasselbe wie Mehrdeutigkeit. Eine unsichere Aussage kann formal eindeutig modelliert sein, wenn ihr Status, ihre Bedingungen und ihre möglichen Folgen klar angegeben sind.

Beispiel:

Kausalrelation R gilt mit Wahrscheinlichkeit 0,35.
Wenn Wahrscheinlichkeit > 0,30, wird Szenario S2 aktiviert.

Das Modell enthält Unsicherheit, bleibt aber formal auswertbar.

### 7.3.13 Lückenobjekte

Eine erkannte Lücke sollte als eigenes Modellobjekt gespeichert werden.

Beispiel:

Lücke:
Zwischen natürlicher Klimavariabilität und beobachtetem Temperaturanstieg fehlt ein expliziter Mechanismus für den Zeitraum seit 1950.

Lücken sind keine bloßen Kommentare, sondern prüfbare Hinweise auf unvollständige Modellstellen.

Eine Lücke ist eine zulässige Form nicht aufgelöster Modellierung, sofern sie ausdrücklich markiert ist. Unzulässig ist dagegen eine verdeckte Mehrdeutigkeit, die weder als Lücke noch als Variante, Konflikt, Unsicherheit oder offene Frage gekennzeichnet ist.

## 7.4 Formales Objekt- und Lebenszyklusmodell
### 7.4.1 Zweck des Objekt- und Lebenszyklusmodells
Das formale Objekt- und Lebenszyklusmodell beschreibt, welche Einheiten innerhalb eines Wirkmodells als eigenständige, adressierbare und prüfbare Objekte behandelt werden. Es bildet die fachliche Zwischenschicht zwischen der konzeptionellen Beschreibung eines Wirkmodells und späteren technischen Umsetzungen wie Datenmodell, Autorenumgebung, Prüfverfahren oder Workflows.
Ziel dieses Modells ist nicht die vollständige technische Implementierung. Vielmehr wird festgelegt, welche Klassen von Modellelementen unterschieden werden, welche Relationen zwischen ihnen bestehen, welche Zustände sie annehmen können und welche Änderungen an ihnen zulässig oder prüfpflichtig sind.
Damit erfüllt das Objekt- und Lebenszyklusmodell vier Funktionen:
Es macht die Bestandteile eines Wirkmodells eindeutig referenzierbar.
Es beschreibt die Beziehungen zwischen diesen Bestandteilen.
Es legt fest, welche Änderungen an Modellelementen fachlich relevant sind.
Es definiert, wann Konsistenz-, Integritäts- oder Plausibilitätsprüfungen ausgelöst werden.
Das Kapitel dient damit als Grundlage für die später zu beschreibenden Workflows. Workflows beschreiben, wie Autorinnen, Autoren, Leserinnen, Leser oder Systeme mit den Objekten interagieren. Das Objekt- und Lebenszyklusmodell beschreibt dagegen zunächst, welche Objekte überhaupt existieren und welchen formalen Bedingungen sie unterliegen.
### 7.4.2 Grundprinzip: Modellelemente als adressierbare Einheiten
Ein Wirkmodell besteht nicht nur aus Text, sondern aus unterscheidbaren Modellelementen. Ein Modellelement ist jede Einheit, die innerhalb eines Wirkmodells eine fachliche Bedeutung trägt und auf die andere Elemente Bezug nehmen können.
Dazu gehören insbesondere Entitäten, Zustände, Relationen, Wirkungen, Annahmen, axiomatisch markierte Elemente, Evidenzobjekte, Schlussregeln, zeitliche Marker sowie narrative Verknüpfungen.
Jedes Modellelement sollte mindestens drei Eigenschaften besitzen:
eine eindeutige Identität,
eine fachliche Typisierung,
eine definierte Position innerhalb des Wirkmodells.
Die eindeutige Identität erlaubt es, Modellelemente unabhängig von ihrer sprachlichen Darstellung zu referenzieren. Die Typisierung legt fest, welche Rolle das Element im Wirkmodell spielt. Die Position innerhalb des Wirkmodells beschreibt, in welchem Wirkraum, in welcher Zeitscheibe, in welchem Modellverbund oder in welchem argumentativen Zusammenhang das Element verwendet wird.
Diese Adressierbarkeit ist eine Voraussetzung für Konsistenzprüfung, Modellrestrukturierung, Rückverfolgbarkeit und transparente KI-Unterstützung.
### 7.4.3 Objektklassen von Wirkmodell, Narrativ und Prüfschicht
Die Modellierungsumgebung umfasst nicht nur Objektklassen des Wirkmodells im engeren Sinn. Für die spätere Konsistenzprüfung, Modellrestrukturierung, narrative Rückbindung und Transparenzdokumentation müssen mindestens drei Ebenen unterschieden werden: wirkmodellinterne Objektklassen, narrative Objektklassen sowie Prüf- und Transparenzobjekte. Einige dieser Klassen bilden Domänenphänomene ab; andere beschreiben Aussagen, Relationen, Bedingungen, Statusinformationen oder abgeleitete Prüfartefakte.
Die folgende Systematik ist keine technische Datenbankspezifikation. Sie legt fest, welche fachlichen Einheiten als eigenständige, adressierbare und prüfbare Objekte behandelt werden sollten. Ob eine Einheit später als eigene Tabelle, Dokumentstruktur, Graphknoten, Attribut oder abgeleitetes Artefakt umgesetzt wird, bleibt eine Implementierungsfrage.
#### A. Modell- und Verbundobjekte
#### Wirkmodell
Das Wirkmodell ist die oberste fachliche Einheit der wissenschaftlich-kausalen Ebene. Es beschreibt einen abgegrenzten Wirkraum, innerhalb dessen Entitäten, Zustände, Relationen, Kausalrelationen, Claims, Annahmen, Bedingungen und Evidenzbezüge modelliert werden. Ein Wirkmodell kann eigenständig bestehen oder Teil eines Wirkmodellverbundes sein.
#### Wirkmodellverbund und Teilmodell
Ein Wirkmodellverbund ist eine strukturierte Menge mehrerer Wirkmodelle, die über Schnittstellen, Input-Output-Beziehungen, gemeinsame Geltungsbereiche oder Modellverträge verbunden sind. Ein Teilmodell beschreibt einen fachlich abgegrenzten Ausschnitt innerhalb eines größeren Wirkmodells oder Verbundes.
#### Wirkraum
Der Wirkraum bezeichnet den sachlichen, sozialen, politischen, ökologischen, technischen oder kulturellen Bereich, auf den sich ein Wirkmodell bezieht. Er legt fest, welche Phänomene innerhalb des Modells betrachtet werden und welche außerhalb des Modells liegen.
#### Geltungsbereich
Der Geltungsbereich beschreibt, unter welchen sachlichen, räumlichen, zeitlichen, sozialen, methodischen oder normativen Bedingungen ein Modellelement gültig sein soll. Er ist besonders wichtig, um Scheinkonflikte zu vermeiden: Zwei Aussagen können nur dann als widersprüchlich gelten, wenn sich ihre Geltungsbereiche tatsächlich überschneiden.
#### Zeitscheibe, Geltungsperiode und Übergang
Eine Zeitscheibe oder Geltungsperiode ordnet Modellelemente zeitlich. Ein Übergang beschreibt den Wechsel von einem Modellzustand, einer Zeitscheibe oder einem Szenariostand zu einem anderen. Diese Objektklassen sind insbesondere für Zukunftsnarrative, Langzeitprozesse und rückwärts konstruierte Entwicklungspfade relevant.
#### Szenario, Szenariopfad und Modellvariante
Ein Szenario beschreibt eine mögliche Entwicklung innerhalb eines definierten Wirkraums. Ein Szenariopfad verbindet mehrere zeitlich geordnete Modellzustände. Eine Modellvariante bezeichnet eine alternative, aber formal explizite Ausprägung eines Wirkmodells, etwa bei konkurrierenden Deutungen, abweichenden Annahmen oder alternativen Zukunftspfaden.
#### B. Domänen- und Strukturierungsobjekte
#### Entität
Eine Entität ist ein im Modell unterscheidbarer Akteur, Gegenstand, Prozess, Institution, Systembestandteil oder abstrakter Träger von Eigenschaften. Beispiele sind Personen, Gruppen, Organisationen, Ressourcen, Technologien, Staaten, Ökosysteme, Normen oder Infrastrukturen.
#### Zustand und Eigenschaft
Ein Zustand beschreibt eine Eigenschaft, Lage oder Ausprägung einer Entität zu einem bestimmten Zeitpunkt oder innerhalb einer bestimmten Zeitscheibe. Eigenschaften können qualitativ, quantitativ oder relational beschrieben werden.
#### Prozess
Ein Prozess beschreibt eine zeitlich ausgedehnte Veränderungsstruktur. Er kann mehrere Zustände, Bedingungen, Zwischenzustände und Wirkungen verbinden. Prozesse sind besonders relevant, wenn Wirkungen nicht sofort eintreten, sondern über längere Zeiträume stabilisiert oder fortgeführt werden müssen.
#### Variable, Input, Output, Einheit, Datentyp und Wertebereich
Variablen bezeichnen veränderliche Größen oder kategoriale Ausprägungen innerhalb eines Wirkmodells. Inputs sind Werte, Zustände oder Claims, die ein Wirkmodell aus einem anderen Modell oder aus einer externen Quelle übernimmt. Outputs sind Ergebnisse, Zustände oder Claims, die ein Wirkmodell erzeugt und an andere Modelle, Narrative oder Prüfverfahren weitergeben kann. Einheit, Datentyp und Wertebereich bestimmen, wie eine Variable interpretiert und verglichen werden darf.
#### Schnittstelle
Eine Schnittstelle beschreibt, welche Inputs, Outputs, Bedingungen und Bedeutungsannahmen zwischen Wirkmodellen ausgetauscht werden. Sie ist nicht nur eine technische Verbindung, sondern eine semantische Kopplung zwischen Modellbereichen.
#### C. Aussage- und Begründungsobjekte
#### Claim
Ein Claim ist eine im Wirkmodell behauptete Aussage. Er kann empirischer, kausaler, definitorischer, normativer, prognostischer, kontrafaktischer, methodischer oder unsicherheitsbezogener Art sein. Claims sind zentrale Träger von Begründungs-, Evidenz-, Konflikt-, Ableitungs-, Geltungsbereichs- und Statusbeziehungen. Ein Claim ist nicht deshalb relevant, weil er als wahr gilt, sondern weil er innerhalb des Wirkmodells eine explizite Rolle spielt.
#### Gegenclaim
Ein Gegenclaim ist ein Claim, der einem anderen Claim widerspricht, ihn einschränkt, relativiert oder eine konkurrierende Erklärung anbietet. Gegenclaims erlauben es, Dissens, Alternativerklärungen und strittige Modellbereiche explizit zu modellieren, ohne den Konflikt vorschnell aufzulösen.
#### Annahme
Eine Annahme ist eine Aussage oder Voraussetzung, die im Wirkmodell verwendet wird, ohne dass sie innerhalb desselben Modells vollständig hergeleitet wird. Annahmen können empirisch gestützt, theoretisch begründet, hypothetisch gesetzt oder narrativ erforderlich sein. Sie sind nicht automatisch Axiome.
#### Axiomatisch markiertes Element und Axiomsraum
Ein axiomatisch markiertes Element ist ein Modellelement, das innerhalb eines Wirkmodells als nicht weiter intern begründet behandelt wird und für weitere Ableitungen als gesetzt gilt. Grundsätzlich können nicht nur Claims oder Annahmen, sondern auch Entitäten, Variablen, Relationen, Kausalrelationen, Geltungsbereiche oder andere Modellelemente axiomatisch markiert werden. Der Axiomsraum ist die Menge aller innerhalb eines Wirkmodells axiomatisch markierten Elemente.
#### Schlussregel und Prioritätsregel
Eine Schlussregel beschreibt, nach welchem Prinzip aus bestimmten Modellelementen andere Aussagen, Zustände oder Prüfhinweise abgeleitet werden dürfen. Eine Prioritätsregel legt fest, welche Regel, Annahme, Evidenzform oder Modellvariante bei konkurrierenden Ableitungen Vorrang erhält oder wie ein Konflikt vorläufig geordnet wird.
#### Evidenzobjekt und Evidenzstandard
Ein Evidenzobjekt ist ein Verweis auf Daten, Quellen, Studien, Beobachtungen, Argumente oder andere Begründungsformen, die ein Modellelement stützen, schwächen oder kontextualisieren. Ein Evidenzstandard beschreibt, welche Art und Qualität von Evidenz für einen bestimmten Claim, eine Annahme oder eine Relation als hinreichend gilt.
#### Kompetenzfrage
Eine Kompetenzfrage beschreibt eine Frage, die ein Wirkmodell beantworten können soll. Sie dient der Vollständigkeitsprüfung und der semantikerhaltenden Modellrestrukturierung: Wird ein Modell umgebaut, sollte es die relevanten Kompetenzfragen weiterhin beantworten können, sofern diese zum beibehaltenen Geltungsbereich gehören.
#### D. Relations- und Wirkobjekte
#### Relation
Eine Relation beschreibt eine Beziehung zwischen mindestens zwei Modellelementen. Relationen können strukturell, semantisch, kausal, normativ, temporär, argumentativ, evidenziell oder narrativ sein. Nicht jede Relation ist eine Kausalrelation.
#### Kausalrelation und Wirkmechanismus
Eine Kausalrelation beschreibt einen gerichteten Wirkzusammenhang zwischen Quelle und Ziel. Sie kann Mechanismus, Bedingungen, Polarität, Stärke, Verzögerung und Unsicherheit enthalten. Der Wirkmechanismus beschreibt, warum oder über welchen Vermittlungsweg eine Ursache eine Wirkung hervorbringen soll.
#### Konfliktrelation
Eine Konfliktrelation beschreibt, dass zwei oder mehrere Claims, Annahmen, Axiome, Relationen, Geltungsbereiche oder narrative Aussagen nicht ohne Weiteres miteinander vereinbar sind. Sie ist die formale Grundlage für Widerspruchs-, Dissens- und Alternativenprüfungen.
#### Abhängigkeits-, Evidenz-, Referenz-, Varianten- und Transformationsrelation
Abhängigkeitsrelationen zeigen, dass ein Modellelement ein anderes voraussetzt. Evidenzrelationen verbinden Evidenzobjekte mit Claims, Annahmen oder Relationen. Referenzrelationen verbinden narrative Einheiten mit Modellelementen. Variantenrelationen ordnen alternative Modellfassungen. Transformationsrelationen beschreiben Verschiebung, Teilung, Zusammenführung oder Neu-Situierung von Modellelementen im Rahmen der Modellrestrukturierung.
#### E. Vertrags- und Bedingungsobjekte
#### Wirkmodell-Vertrag
Ein Wirkmodell-Vertrag beschreibt, unter welchen Bedingungen ein Wirkmodell mit anderen Wirkmodellen verbunden werden darf. Er bündelt insbesondere Inputs, Outputs, Preconditions, Postconditions, Invarianten und semantische Schnittstellenannahmen.
#### Precondition
Eine Precondition ist eine Bedingung, die erfüllt sein muss, damit ein Prozess, ein Modellschritt, eine Kausalrelation, ein Output oder ein Übergang gültig angewendet werden kann.
#### Postcondition
Eine Postcondition beschreibt einen Zustand, Claim oder Output, der nach Anwendung eines Prozesses, einer Relation, eines Übergangs oder eines Wirkmodells erwartet wird.
#### Invariante, Aktivierungsbedingung und Übergangsbedingung
Eine Invariante ist eine Bedingung, die während einer Veränderung, Modellrestrukturierung oder Kopplung erhalten bleiben muss. Eine Aktivierungsbedingung legt fest, wann eine Relation, Regel oder Prozessstruktur wirksam wird. Eine Übergangsbedingung beschreibt, unter welchen Voraussetzungen ein Wechsel zwischen Modellzuständen oder Zeitscheiben zulässig ist.
#### F. Status-, Unsicherheits- und Lückenobjekte
#### Statusangabe und Unsicherheitsangabe
Statusangaben beschreiben, ob ein Modellelement etwa gesetzt, abgeleitet, hypothetisch, empirisch gestützt, normativ gesetzt, umstritten, offen, veraltet oder prüfpflichtig ist. Unsicherheitsangaben beschreiben Grad, Art oder Quelle von Unsicherheit. Beide Objektarten steuern, wie Elemente geprüft, verglichen und narrativ verwendet werden dürfen.
#### Lückenobjekt, offene Frage und Mehrdeutigkeitsmarkierung
Ein Lückenobjekt markiert eine bekannte Leerstelle im Wirkmodell. Eine offene Frage bezeichnet einen ungeklärten Sachverhalt, der für das Modell relevant sein kann. Eine Mehrdeutigkeitsmarkierung zeigt an, dass ein Begriff, Claim, narrativer Bezug oder Geltungsbereich noch nicht eindeutig genug bestimmt ist.
#### Prüfpflicht
Eine Prüfpflicht ist eine formale Markierung, dass ein Modellelement oder eine Änderung daran ein Prüfverfahren auslösen muss. Sie kann aus Typ, Status, Abhängigkeit, Konflikt, Geltungsbereich oder Restrukturierung entstehen.
#### G. Narrative Objekte
#### Narratives Artefakt und narrative Einheit
Ein narratives Artefakt ist ein erzählerisches Werk oder Teilwerk, das auf ein Wirkmodell bezogen ist. Narrative Einheiten sind seine strukturierten Bestandteile. Die Textstruktur folgt dem in Kap. 6.2.1 beschriebenen Dokumentmodell: DocumentNode-Instanzen bilden den Composite-Baum (Work → Part → Chapter → Section → Paragraph → Sentence → String → Character), DocumentAsset-Instanzen leben außerhalb des Baums und werden über DocumentLink referenziert. Figur, Handlung und narrativer Konflikt sind keine Strukturelemente des Textmodells, sondern inhaltliche Konzepte die im narrativen Text ausgedrückt werden. Sie werden nicht selbst zu kausalen Modellen, können aber auf Modellelemente verweisen und durch diese geprüft werden.
#### Narrativer Bezug und Referenzobjekt
Ein narrativer Bezug verbindet ein Modellelement mit einer Passage, Figur, Handlung, Szene oder Entwicklung innerhalb einer Geschichte. Ein Referenzobjekt hält diese Verbindung formal fest und ermöglicht bidirektionale Rückverfolgbarkeit zwischen Narrativ und Wirkmodell.
#### Narrative Abweichung
Eine narrative Abweichung beschreibt eine Stelle, an der eine Geschichte von einem zugrunde gelegten Wirkmodell abweicht, eine zusätzliche Annahme einführt oder einen modellinternen Konflikt narrativ verdeckt. Eine solche Abweichung muss nicht unzulässig sein, sollte aber markiert und begründet werden.
#### H. Prüf- und Transparenzobjekte
#### Prüfverfahren, Prüfprofil und Prüfergebnis
Ein Prüfverfahren beschreibt eine definierte Art der Modell-, Narrativ- oder Verbundprüfung. Ein Prüfprofil legt fest, welche Prüfungen in welchem Kontext anzuwenden sind. Ein Prüfergebnis dokumentiert Ergebnis, Reichweite, Unsicherheit und betroffene Modellelemente einer Prüfung.
#### Prüfhinweis, Konfliktmarkierung und Konsistenzwarnung
Ein Prüfhinweis ist ein durch das System oder eine prüfende Instanz erzeugtes Artefakt, das auf eine mögliche Inkonsistenz, Lücke, Mehrdeutigkeit, abweichende Annahme oder offene Frage hinweist. Konfliktmarkierungen und Konsistenzwarnungen sind spezialisierte Prüfhinweise.
#### Transparenzbericht
Ein Transparenzbericht ist ein abgeleitetes Artefakt, das zentrale Annahmen, axiomatisch markierte Elemente, Claims, Evidenzbezüge, offene Konflikte, narrative Abweichungen und Prüfhinweise zusammenführt. Er dient der epistemischen Nachvollziehbarkeit für Autorinnen, Autoren, Leserinnen, Leser oder externe Prüfinstanzen.
> → Der Transparenzbericht ist ein eigenständiges, versioniertes Transparenzartefakt mit drei Referenzen: Werkfassung, Wirkmodellfassung und Prüfstand zum Zeitpunkt der Veröffentlichung. Ändert sich Text oder Wirkmodell, entsteht eine neue Version; alte bleiben erhalten.
> ↗ Querverweis: Transparenzbericht als versioniertes Artefakt – vgl. Kap. 20.4.1 und 20.6
#### Abgeleitete implizite Annahme, Kausalitätslücke und Referenzintegritätsproblem
Eine abgeleitete implizite Annahme ist eine Voraussetzung, die nicht explizit modelliert wurde, aber aus Narrativ, Claimstruktur oder Wirkzusammenhang hervorgeht. Eine Kausalitätslücke bezeichnet einen fehlenden oder unzureichend bestimmten Wirkmechanismus. Ein Referenzintegritätsproblem entsteht, wenn narrative und formale Ebene nicht mehr eindeutig aufeinander bezogen sind.
### 7.4.4 Relationen zwischen Objektklassen
Die Objektklassen von Wirkmodell, Narrativ und Prüfschicht stehen nicht isoliert nebeneinander. Ihre fachliche Bedeutung entsteht durch Relationen. Relationen können selbst einfache Verweise sein oder als eigenständige Relationsobjekte auftreten, wenn sie Status, Geltungsbereich, Evidenz, Unsicherheit oder Versionierung besitzen müssen.
#### Enthaltensein
Ein Modellelement kann Teil eines Wirkmodells, eines Wirkraums, eines Modellverbundes, einer Zeitscheibe, eines Szenariopfads oder eines narrativen Artefakts sein. Beispiele sind: Entität X ist Bestandteil von Wirkmodell M; Szene S ist Bestandteil von Kapitel K; Zustand Z gehört zu Entität X.
#### Referenz und Rückverfolgbarkeit
Ein Modellelement kann auf ein anderes Element verweisen, ohne es logisch oder kausal abzuleiten. Referenzrelationen sind besonders wichtig zwischen narrativen Einheiten und formalen Modellelementen. Sie sichern die bidirektionale Rückverfolgbarkeit zwischen Text, Modell und Transparenzbericht.
#### Claim- und Evidenzrelationen
Claims können durch Evidenzobjekte gestützt, geschwächt, relativiert oder kontextualisiert werden. Ein Claim kann einen anderen Claim voraussetzen, aus ihm abgeleitet sein, ihn begründen, einschränken oder mit ihm konkurrieren. Evidenzrelationen sollten deshalb nicht nur das Vorhandensein einer Quelle, sondern auch Art, Richtung, Geltungsbereich und Evidenzstandard der Stützung erfassen.
#### Konflikt- und Gegenclaimrelationen
Ein Gegenclaim steht nicht bloß neben einem Claim, sondern in einer expliziten Konflikt-, Einschränkungs- oder Alternativrelation zu ihm. Eine Konfliktrelation sollte angeben, ob es sich um einen logischen Widerspruch, einen empirischen Dissens, eine normative Spannung, eine Geltungsbereichskollision oder eine konkurrierende Erklärung handelt.
#### Kausale Abhängigkeit
Eine kausale Abhängigkeit beschreibt, dass die Veränderung eines Elements als Ursache, Bedingung oder Einflussgröße für die Veränderung eines anderen Elements modelliert wird. Kausalrelationen sollten Quelle, Ziel, Mechanismus, Bedingungen, Verzögerung, Stärke, Polarität und Unsicherheit erfassen, sofern diese Angaben für das Modell relevant sind.
#### Logische und argumentative Abhängigkeit
Eine logische oder argumentative Abhängigkeit liegt vor, wenn ein Modellelement für die Begründung, Ableitung oder Plausibilisierung eines anderen Elements erforderlich ist. Beispiele sind: Claim C setzt Annahme A voraus; Schlussfolgerung F wird aus A und B abgeleitet; Prioritätsregel P ordnet zwei konkurrierende Regeln.
#### Temporale Relation
Temporale Relationen ordnen Modellelemente zeitlich. Sie beschreiben Vorher-Nachher-Verhältnisse, Dauer, Verzögerung, Gleichzeitigkeit, Periodizität oder Übergänge zwischen Zeitscheiben. Sie sind für Langzeitprozesse und Zukunftspfade unverzichtbar.
#### Input-Output- und Schnittstellenrelation
Eine Input-Output-Relation beschreibt, dass ein Ergebnis eines Wirkmodells als Eingabe eines anderen Wirkmodells verwendet wird. Eine Schnittstellenrelation spezifiziert zusätzlich Geltungsbereich, Datentyp, Einheit, Wertebereich, Preconditions, Postconditions und Invarianten.
#### Konsistenzrelation
Eine Konsistenzrelation beschreibt, ob zwei Modellelemente miteinander vereinbar, widersprüchlich, spannungsreich, unabhängig oder prüfbedürftig sind. Widersprüche müssen nicht automatisch gelöscht werden; sie können auch als offene Konflikte, Varianten oder bewusste Spannungen markiert werden.
#### Transformationsrelation
Eine Transformationsrelation beschreibt, dass ein Modellelement durch Modellrestrukturierung verschoben, geteilt, zusammengeführt, ersetzt oder neu situiert wird. Dabei muss geprüft werden, ob die semantische Identität des Elements erhalten bleibt und ob Kompetenzfragen weiterhin beantwortbar sind.
### 7.4.5 Axiomatische Markierung und Axiomsraum
Innerhalb eines Wirkmodells kann jedes Modellelement als axiomatisch markiert werden, sofern es im Modell als grundlegende Setzung fungiert. Diese Markierung bedeutet nicht, dass das Element wahr, endgültig oder unangreifbar ist. Sie bedeutet lediglich, dass das Wirkmodell dieses Element an der betreffenden Stelle nicht weiter intern herleitet.
Die axiomatische Markierung ist daher eine funktionale Eigenschaft eines Modellelements. Sie beschreibt die Rolle, die ein Element im Modell spielt. Ein und dasselbe Element kann in unterschiedlichen Wirkmodellen unterschiedlich behandelt werden. In einem Modell kann es axiomatisch gesetzt sein, während es in einem anderen Modell selbst Gegenstand einer Herleitung oder Prüfung ist.
Der Axiomsraum eines Wirkmodells ergibt sich aus der Menge aller axiomatisch markierten Elemente. Er ist für die Konsistenzprüfung besonders relevant, weil Änderungen an axiomatisch markierten Elementen Auswirkungen auf nachgelagerte Ableitungen, narrative Plausibilitäten und andere Modellelemente haben können.
Wird ein axiomatisch markiertes Element verändert, entfernt oder durch ein anderes Element ersetzt, muss das System prüfen, welche weiteren Elemente von dieser Änderung abhängen. Dies betrifft insbesondere:
abgeleitete Claims,
Schlussfolgerungen,
Kausalrelationen,
narrative Szenen,
Evidenzzuordnungen,
Precondition- und Postcondition-Strukturen,
andere axiomatisch markierte Elemente.
Die axiomatische Markierung macht ein Element somit nicht unveränderlich. Sie macht seine Änderung jedoch prüfpflichtig.

Ein zentraler konzeptioneller Punkt: Axiome sind innerhalb des Systems nicht anfechtbar – nicht weil sie geschützt werden, sondern weil Anfechtung kategorial falsch ist. Wer ein Axiom ablehnt, stellt nicht eine Frage, auf die das System antworten könnte. Er setzt eine andere Grundannahme. Die angemessene Reaktion auf ein abgelehntes Axiom ist daher kein Gegenargument, sondern ein Gegenentwurf – ein eigenes Wirkmodell mit anderem Axiomraum.
Das hat direkte Konsequenzen für den Community-Diskurs: Kritik an einem Axiom ist keine strukturelle Kritik (klar/unklar), sondern eine Wahrheitsaussage über die Grundannahme. Solche Aussagen gehören nicht in den Diskussionsbereich eines Werks – nicht weil sie verboten wären, sondern weil sie die falsche Frage stellen. Die Plattform bietet mit dem Gegenentwurf-Mechanismus die richtige Antwort auf inhaltliche Ablehnung.
> ↗ Querverweis: Gegenentwurf als Antwort auf abgelehnten Axiomraum – vgl. Kap. 20.1 Option C und 20.1 Option C
> ↗ Querverweis: Community-Diskurs und Zensur-Logik – vgl. Kap. 23.1
### 7.4.6 Lebenszyklus zentraler Modellelemente
Modellelemente durchlaufen innerhalb eines Wirkmodells einen fachlichen Lebenszyklus. Dieser Lebenszyklus beschreibt nicht die konkrete Benutzeroberfläche, sondern die möglichen Zustände eines Modellelements. Ein typischer Lebenszyklus umfasst folgende Zustände:
#### Entwurf
Das Modellelement wurde angelegt, ist aber noch nicht vollständig spezifiziert. In diesem Zustand kann es unvollständig, mehrdeutig oder vorläufig sein.
#### Spezifiziert
Das Modellelement besitzt eine ausreichende fachliche Beschreibung, um innerhalb des Wirkmodells verwendet zu werden.
#### Verknüpft
Das Modellelement steht in Relationen zu anderen Modellelementen. Es kann nun Teil von Ableitungen, Prüfungen oder narrativen Bezügen sein.
#### Prüfpflichtig
Das Modellelement oder eine Änderung daran löst eine Prüfung aus. Dies kann durch neue Relationen, geänderte Annahmen, Konflikte oder Modellrestrukturierungen geschehen.
#### Geprüft
Das Modellelement wurde im Rahmen der definierten Prüfverfahren bewertet. Das Ergebnis kann konsistent, inkonsistent, unvollständig, spannungsreich oder nicht entscheidbar sein.
#### Stabilisiert
Das Modellelement gilt innerhalb des aktuellen Modellstands als hinreichend stabil, um als Grundlage weiterer Modellierungen oder narrativer Ableitungen zu dienen.
#### Überarbeitet
Das Modellelement wurde verändert. Dadurch können frühere Prüfungen ungültig werden. Abhängige Elemente müssen erneut betrachtet werden.
#### Verworfen oder archiviert
Das Modellelement wird nicht mehr aktiv verwendet, bleibt aber aus Gründen der Nachvollziehbarkeit erhalten. Dies ist insbesondere wichtig, wenn frühere narrative Versionen oder Prüfentscheidungen darauf Bezug genommen haben.
Dieser Lebenszyklus ist nicht zwingend linear. Ein Modellelement kann mehrfach zwischen Entwurf, Überarbeitung, Prüfung und Stabilisierung wechseln.
### 7.4.7 Änderungsoperationen
Ein Wirkmodell muss veränderbar bleiben. Änderungen sind jedoch nicht beliebig, da sie bestehende Relationen, Ableitungen und narrative Bezüge beeinflussen können. Die wichtigsten Änderungsoperationen sind:
#### Anlegen
Ein neues Modellelement wird erstellt und einem Wirkmodell, Wirkraum oder Modellverbund zugeordnet.
#### Spezifizieren
Ein bestehendes Modellelement wird fachlich genauer beschrieben. Dies kann Eigenschaften, Geltungsbereich, zeitliche Einordnung oder Relationstypen betreffen.
#### Markieren
Ein Modellelement erhält eine zusätzliche fachliche Markierung, etwa als axiomatisch, hypothetisch, empirisch gestützt, prüfpflichtig oder narrativ verwendet.
#### Verknüpfen
Ein Modellelement wird mit einem anderen Modellelement in Beziehung gesetzt. Dadurch entstehen neue Abhängigkeiten und potenziell neue Prüfpflichten.
#### Ändern
Ein bestehendes Modellelement wird inhaltlich verändert. Je nach Typ und Vernetzung des Elements kann dies lokale oder weitreichende Folgen haben.
#### Entfernen
Ein Modellelement wird aus dem aktiven Modell entfernt. Ist es bereits referenziert, darf es nicht folgenlos gelöscht werden. Stattdessen muss geprüft werden, welche Relationen, Ableitungen oder narrativen Bezüge betroffen sind.
#### Verschieben
Ein Modellelement wird aus einem Wirkmodell, Wirkraum oder Kontext in einen anderen verschoben. Diese Operation gehört zur Modellrestrukturierung. Dabei muss geprüft werden, ob die semantische Identität des Elements erhalten bleibt.
#### Teilen
Ein Modellelement wird in mehrere Elemente aufgespalten, etwa wenn eine Annahme mehrere unterscheidbare Teilannahmen enthält.
#### Zusammenführen
Mehrere Modellelemente werden zu einem gemeinsamen Element zusammengeführt. Dies ist nur zulässig, wenn keine relevanten Bedeutungsunterschiede verloren gehen.
#### Versionieren
Ein Modellelement erhält eine neue Fassung, während frühere Fassungen erhalten bleiben. Versionierung ist insbesondere dann erforderlich, wenn Änderungen Auswirkungen auf Ableitungen, Prüfungen oder narrative Fassungen haben.
### 7.4.8 Konsistenz- und Integritätsbedingungen
Das Objekt- und Lebenszyklusmodell benötigt Integritätsbedingungen. Diese legen fest, wann ein Wirkmodell, ein narrativer Bezug oder ein Prüfartefakt formal zulässig, unvollständig, widersprüchlich oder prüfbedürftig ist. Zu unterscheiden sind mindestens die folgenden Bedingungstypen.
#### Identitätsbedingungen
Jedes aktive Modellelement muss eindeutig identifizierbar sein. Es darf keine ununterscheidbaren Dubletten geben, wenn diese unterschiedliche fachliche Rollen spielen. Dies gilt auch für Claims, Gegenclaims, narrative Referenzen, Prüfhinweise und Modellvarianten.
#### Typbedingungen
Jedes Modellelement muss einem fachlichen Typ zugeordnet sein. Der Typ bestimmt, welche Relationen und Operationen zulässig sind. Ein Evidenzobjekt kann einen Claim, eine Annahme oder Relation stützen, ist aber nicht selbst eine Kausalrelation. Ein Gegenclaim benötigt eine Konflikt- oder Einschränkungsrelation zu mindestens einem Claim.
#### Geltungsbereichsbedingungen
Für prüfrelevante Claims, Annahmen, Axiome, Kausalrelationen, Modellverträge und narrative Referenzen muss ein Geltungsbereich angegeben oder eine bewusste Offenmarkierung gesetzt werden. Ohne Geltungsbereich kann häufig nicht entschieden werden, ob zwei Elemente tatsächlich widersprüchlich sind oder nur unterschiedliche Kontexte betreffen.
#### Status- und Unsicherheitsbedingungen
Claims, Annahmen, Axiome, Evidenzobjekte, Kausalrelationen und Prüfhinweise sollten einen Status besitzen. Dieser kann beispielsweise gesetzt, abgeleitet, hypothetisch, empirisch gestützt, normativ gesetzt, umstritten, offen, veraltet oder prüfpflichtig sein. Unsicherheit darf nicht mit Inkonsistenz gleichgesetzt werden, muss aber explizit werden, wenn sie für Ableitungen relevant ist.
#### Relationsbedingungen
Relationen müssen typkompatibel sein. Eine Kausalrelation benötigt mindestens ein Ausgangselement und ein Zielelement. Eine Evidenzrelation benötigt ein Evidenzobjekt und ein gestütztes, geschwächtes oder kontextualisiertes Modellelement. Eine Referenzrelation benötigt eine narrative Einheit und ein formales Zielelement.
#### Claim-spezifische Bedingungen
Ein Claim sollte mindestens Typ, Status und Geltungsbereich besitzen oder ausdrücklich als unvollständig markiert sein. Wird ein Claim als abgeleitet behandelt, muss die Ableitungsbasis referenzierbar sein. Wird ein Claim durch Evidenz gestützt, muss die Art der Evidenzrelation erkennbar sein. Wird ein Claim bestritten, muss der Gegenclaim oder die Konfliktrelation ausgewiesen werden.
#### Vertrags- und Schnittstellenbedingungen
Ein Wirkmodell-Vertrag muss die relevanten Inputs, Outputs, Preconditions, Postconditions und Invarianten hinreichend beschreiben. Inputs und Outputs sollten hinsichtlich Bedeutung, Einheit, Datentyp, Wertebereich und Geltungsbereich kompatibel sein.
#### Abhängigkeitsbedingungen
Wenn ein Modellelement von einem anderen abhängig ist, darf dieses andere Element nicht ohne Prüfung entfernt oder wesentlich verändert werden. Wird ein axiomatisch markiertes Element verändert, müssen alle davon abhängigen Claims, Kausalrelationen, Schlussregeln, narrativen Einheiten und Prüfartefakte erneut betrachtet werden.
#### Referenzintegritätsbedingungen
Narrative Referenzen müssen auf existierende und hinreichend bestimmte Modellelemente verweisen. Wird ein Modellelement verschoben, geteilt, gelöscht oder ersetzt, müssen alle betroffenen narrativen Einheiten und Transparenzartefakte aktualisiert oder als veraltet markiert werden.
#### Konsistenzbedingungen
Modellelemente dürfen nicht in einem ungeklärten Widerspruch zueinander stehen, sofern sie im selben Geltungsbereich verwendet werden. Ein Widerspruch muss nicht automatisch zur Löschung eines Elements führen. Er kann als Spannung, offene Frage, Gegenclaim oder alternative Modellvariante markiert werden. Entscheidend ist, dass er nicht unsichtbar bleibt.
### 7.4.9 Auslösung von Prüfverfahren
Prüfverfahren werden nicht nur manuell gestartet, sondern können durch bestimmte Änderungen am Wirkmodell, am Narrativ oder an Prüfartefakten ausgelöst werden. Das Objekt- und Lebenszyklusmodell definiert daher Triggerpunkte.
Eine Prüfung sollte insbesondere ausgelöst werden, wenn:
ein neues axiomatisch markiertes Element angelegt oder verändert wird,
ein Claim neu angelegt, verändert, abgeleitet, bestritten oder als unvollständig markiert wird,
ein Gegenclaim oder eine Konfliktrelation eingeführt wird,
der Geltungsbereich eines Claims, einer Annahme, eines Axioms, einer Kausalrelation oder eines Modellvertrags verändert wird,
ein Claim ohne Evidenzbezug, ohne Status oder ohne Geltungsbereich in einem prüfrelevanten Kontext verwendet wird,
eine neue Kausalrelation eingefügt oder eine bestehende Kausalrelation verändert wird,
ein Wirkmechanismus, eine Verzögerung, eine Bedingung oder eine Unsicherheitsangabe einer Kausalrelation fehlt oder geändert wird,
ein Input, Output, eine Schnittstelle oder ein Wirkmodell-Vertrag verändert wird,
Preconditions, Postconditions, Invarianten, Aktivierungsbedingungen oder Übergangsbedingungen verändert werden,
ein Modellelement mit vielen Abhängigkeiten geändert, entfernt, geteilt, zusammengeführt oder verschoben wird,
zwei Wirkmodelle zusammengeführt oder ein Wirkmodell geteilt wird,
ein Element zwischen Wirkmodellen verschoben wird,
eine Kompetenzfrage nach einer Modellrestrukturierung nicht mehr beantwortbar ist,
eine narrative Passage einem Modellelement neu zugeordnet oder von ihm gelöst wird,
eine narrative Passage eine implizite Annahme, einen zusätzlichen Claim oder eine vom Wirkmodell abweichende Kausalität einführt,
eine narrative Passage im Widerspruch zu einem Modellelement steht,
ein Transparenzbericht, ein Prüfhinweis oder eine Konfliktmarkierung durch Modelländerungen veraltet sein könnte,
ein langfristiger Prozess über mehrere Zeitscheiben modelliert oder verändert wird.
Die ausgelösten Prüfungen können unterschiedlicher Art sein. Dazu gehören formale Konsistenzprüfungen, Plausibilitätsprüfungen, Abhängigkeitsanalysen, Geltungsbereichsprüfungen, Evidenzprüfungen, Claim-Konflikt-Prüfungen, Schnittstellenprüfungen, narrative Kohärenzprüfungen und Prüfungen von Modellverbünden.
Dabei ist methodisch zu unterscheiden zwischen Fehlern, Widersprüchen, offenen Annahmen, unvollständigen Modellierungen, alternativen Deutungen, bewussten Spannungen und methodisch nicht entscheidbaren Fragen. Nicht jede Auffälligkeit ist ein Fehler. Das System sollte deshalb nicht nur blockieren, sondern qualifizierte Hinweise geben.
### 7.4.10 Abgrenzung zu Workflows
Das Objekt- und Lebenszyklusmodell beschreibt die formalen Einheiten, Zustände und Operationen eines Wirkmodells. Es beschreibt noch nicht, wie eine Benutzerin oder ein Benutzer konkret durch einen Arbeitsprozess geführt wird.
Ein Workflow beantwortet Fragen wie:
Wie legt eine Autorin ein neues Wirkmodell an?
Wie wird ein Axiom im Autorenwerkzeug geändert?
Wie reagiert das System auf eine erkannte Inkonsistenz?
Wie wird eine alternative Modellvariante erzeugt?
Wie untersucht ein Leser die Annahmen hinter einer Geschichte?
Das Objekt- und Lebenszyklusmodell beantwortet dagegen vorgelagerte Fragen:
Welche Art von Objekt wird bearbeitet?
Welche Relationen bestehen zu anderen Objekten?
Welche Änderung ist fachlich relevant?
Welche Prüfpflicht entsteht?
Welche Zustände kann das Objekt einnehmen?
Damit bildet das Objekt- und Lebenszyklusmodell die formale Grundlage für spätere Workflows. Ohne diese Zwischenschicht würden Workflows Gefahr laufen, implizite Modellannahmen zu enthalten, die nicht ausdrücklich definiert sind.

> → Der erste vollständig beschriebene Workflow ist der Literaten-Workflow (Kap. 20), gefolgt vom Wirkmodell-Autor-Workflow (Kap. 21).
> ↗ Querverweis: Literaten-Workflow – vgl. Kap. 20
> ↗ Querverweis: Wirkmodell-Autor-Workflow – vgl. Kap. 21
### 7.4.11 Zwischenfazit
Das formale Objekt- und Lebenszyklusmodell präzisiert die interne Struktur eines Wirkmodells. Es beschreibt Wirkmodelle nicht mehr nur als konzeptionelle Gebilde, sondern als Mengen adressierbarer, typisierter und relational verbundener Modellelemente.
Diese Präzisierung ist notwendig, weil Konsistenzprüfung, Modellrestrukturierung, narrative Rückbindung und transparente KI-Unterstützung nur funktionieren können, wenn klar ist, welche Elemente verändert, geprüft, abgeleitet oder referenziert werden.
Das Kapitel schafft damit die Grundlage für drei nachfolgende Ausarbeitungsschritte:
die genauere Beschreibung der Prüfverfahren,
die spätere Modellierung zentraler Workflows,
die spätere technische Spezifikation eines Daten- und Interaktionsmodells.
## 7.5 Prüfungen eines bereits angelegten Wirkmodells

Die Prüfung eines Wirkmodells sollte nicht als einzelne Gesamtprüfung verstanden werden. Sinnvoller ist ein mehrdimensionales Prüfprofil. Jede Prüfung untersucht eine bestimmte Eigenschaft des Modells und hat eigene Stärken und Grenzen.

Alle Prüfungen erfolgen modellintern. Sie prüfen nicht, ob das Wirkmodell als Ganzes wahr ist. Sie prüfen, ob das Modell klar, explizit, konsistent, ableitbar, semantisch eindeutig, kausal ausgearbeitet und in seinen Grenzen transparent ist.

Zusätzlich gilt: Ein Wirkmodell muss formal eindeutig auswertbar sein. Mehrdeutigkeiten müssen entweder aufgelöst oder als Varianten, Konflikte, Unsicherheiten, Prioritätsregeln oder Lücken markiert werden.

### 7.5.1 Strukturprüfung

Die Strukturprüfung untersucht, ob das Wirkmodell formal vollständig angelegt ist: Gibt es alle notwendigen Objekttypen? Sind sie typisiert? Sind sie miteinander verbunden?

Geprüft werden unter anderem fehlende IDs, fehlende Typen, fehlende Relationen, nicht verbundene Knoten, Claims ohne Begründung, Kausalrelationen ohne Quelle oder Ziel, Evidenzobjekte ohne referenzierten Claim, Lückenobjekte ohne Zielobjekt, unmarkierte Mehrdeutigkeiten und Konflikte ohne Konfliktrelation.

Findbare Modellprobleme sind isolierte Modellbestandteile, untypisierte Aussagen, Relationen ohne Ziel, Claims ohne Status, Entitäten ohne Definition, Evidenz ohne Bezug, nicht modellierte Abhängigkeiten, nicht markierte Mehrdeutigkeiten und nicht aufgelöste Strukturkonflikte.

Die Strukturprüfung erkennt formale Unvollständigkeit. Sie erkennt nicht, ob eine modellierte Relation gut begründet, semantisch eindeutig oder kausal ausgearbeitet ist. Ausgleichend wirken semantische Prüfung, kausale Prüfung, logische Prüfung und argumentative Prüfung.

### 7.5.2 Typen- und Ontologieprüfung

Diese Prüfung untersucht, ob die verwendeten Objekte und Relationen zu den im Modell definierten Klassen, Kategorien und erlaubten Verbindungstypen passen.

Das Modell wird gegen eine Ontologie oder ein Typensystem geprüft. Dabei wird festgestellt, ob bestimmte Relationstypen nur zwischen geeigneten Objekttypen auftreten.

Beispiel:

Eine physikalische Größe kann eine andere physikalische Größe beeinflussen.
Eine normative Forderung kann aber nicht ohne Zwischenschritt als physikalische Ursache wirken.

Findbare Modellprobleme sind Kategorienfehler, unzulässige Relationen, Vermischung empirischer und normativer Ebenen, unklare Begriffsklassen, falsche Zuordnung von Entitäten und unvereinbare Typen.

Eine Ontologie ist selbst modellabhängig. Sie kann zu eng, zu grob oder domänenspezifisch verzerrt sein. Ausgleichend wirken manuelle Review-Verfahren, Versionierung alternativer Ontologien, semantische Prüfung und Nutzerhinweise auf neue oder fehlende Kategorien.

### 7.5.3 Logische Konsistenzprüfung

Die logische Konsistenzprüfung untersucht, ob die im Wirkmodell enthaltenen Aussagen unter den im Modell gesetzten Annahmen gemeinsam widerspruchsfrei sein können.

Sie prüft nicht, ob die Aussagen empirisch zutreffen. Diese Einschränkung ist keine Schwäche des Verfahrens, sondern eine bewusste methodische Festlegung der Plattform. Ein Wirkmodell darf auch kontrafaktische, spekulative oder fachlich randständige Annahmen enthalten, sofern diese als Annahmen explizit gemacht und in ihren Konsequenzen konsistent weitergeführt werden.

Claims, Annahmen und Regeln werden in eine logische Repräsentation überführt. Anschließend wird geprüft, ob sich direkte oder indirekte Widersprüche innerhalb des Modells ergeben. Mögliche Verfahren sind Aussagenlogik, Prädikatenlogik, SAT-Solving, SMT-Solving, Description Logic und regelbasierte Konsistenzprüfung.

Findbare Modellprobleme sind direkte Widersprüche, indirekte Widersprüche, unvereinbare Annahmen, unerfüllbare Bedingungskombinationen, Konklusionen, die den eigenen Prämissen widersprechen, unmarkierte Wechsel des Geltungsbereichs, widersprüchliche Definitionen und konkurrierende Regeln ohne Priorisierung oder Variantenbildung.

Beispiel: Ein Nutzer legt einen Wirkraum an, in dem die Erde als Scheibe modelliert wird. Die Plattform verwirft diesen Wirkraum nicht aufgrund des etablierten wissenschaftlichen Wissens. Sie prüft vielmehr, ob die Annahmen, Folgerungen und Nebenannahmen intern konsistent modelliert sind.

A1: Die Erde ist eine Scheibe.
A2: Die Sonne bewegt sich über dieser Scheibe.
A3: Tag und Nacht entstehen durch die Bewegung der Sonne über verschiedenen Bereichen der Scheibe.

Die logische Prüfung sagt nicht: „A1 ist empirisch falsch.“ Sondern sie fragt, ob die Erklärung von Tag und Nacht aus A1, A2 und A3 folgt, ob Jahreszeiten erklärbar sind, ob unterschiedliche Sternbilder vorgesehen sind und ob Aussagen im Modell zugleich eine kugelförmige Erde voraussetzen.

Die logische Konsistenzprüfung ist abhängig von der Formalisierungstiefe des Wirkmodells. Nicht modellierte Voraussetzungen oder unausgesprochene Begriffe können unentdeckt bleiben. Ausgleichend wirken Ableitungsprüfung, Kompetenzfragenprüfung, Kausalitätsprüfung, Geltungsbereichsprüfung, nutzerbasierte Lückenprüfung und Vergleichsprüfung.

### 7.5.4 Ableitungsprüfung

Die Ableitungsprüfung untersucht, ob Claims und Schlussfolgerungen tatsächlich aus den angegebenen Prämissen, Annahmen und Regeln folgen.

Für jede abgeleitete Aussage wird geprüft, ob eine vollständige Ableitungskette existiert:

Prämisse A
Prämisse B
Regel R
> → Schlussfolgerung C

Findbare Modellprobleme sind unbegründete Konklusionen, fehlende Zwischenschritte, fehlende Schlussregeln, zu starke Schlussfolgerungen, normative Schlussfolgerungen aus rein deskriptiven Prämissen, empirische Schlussfolgerungen aus bloßen Definitionen, unklare Abhängigkeit zwischen Prämisse und Konklusion und mehrere mögliche Ableitungswege ohne Priorisierung oder Variantenmarkierung.

Beispiel:

Prämisse: Die globale Temperatur steigt.
Konklusion: Deshalb muss Maßnahme X umgesetzt werden.

Hier fehlt mindestens eine normative oder entscheidungstheoretische Brückenannahme.

Die Ableitungsprüfung entscheidet nicht, ob eine normative Brückenannahme richtig ist. Sie prüft nur, ob eine solche Brücke vorhanden, explizit und konsistent verwendet wird. Ausgleichend wirken semantische Prüfung, argumentative Prüfung, nutzerbasierte Lückendetektion und Kompetenzfragenprüfung.

### 7.5.5 Kausalitätsprüfung

Die Kausalitätsprüfung untersucht, ob kausale Aussagen innerhalb eines Wirkmodells vollständig und nachvollziehbar modelliert sind. Sie prüft, ob Ursache, Wirkung, Wirkmechanismus, Richtung, Bedingungen, Zeitstruktur, mögliche Gegenmechanismen und Konsequenzen explizit angegeben sind.

Sie entscheidet nicht, ob die behauptete Kausalität empirisch zutrifft. Diese Nicht-Prüfung ist keine Schwäche, sondern eine bewusste methodische Begrenzung des Systems. Auch ein kontrafaktisches, spekulatives oder fachlich randständiges Wirkmodell kann kausale Relationen enthalten, sofern diese innerhalb des Modells explizit und konsistent ausgearbeitet werden.

Findbare Modellprobleme sind Kausalrelationen ohne Ursache, ohne Wirkung oder ohne Wirkmechanismus, unklare Kausalrichtung, fehlende Zeitstruktur, fehlende Geltungsbedingungen, fehlende Polarität, fehlende Wirkstärke, fehlende Gegenmechanismen, unmodellierte Rückkopplung, unbehandelte Alternativerklärung, unbegründete Dominanz einer Ursache, fehlende Zwischenschritte und konkurrierende Kausalpfade ohne Varianten-, Prioritäts- oder Konfliktmarkierung.

Beispiel: Ein Nutzer legt einen Wirkraum an, in dem die Erde als Scheibe modelliert wird. Eine kausale Aussage lautet:

Die Sonne bewegt sich kreisförmig über der Erdscheibe und verursacht dadurch Tag und Nacht.

Die Plattform prüft nicht, ob diese Aussage empirisch richtig ist. Sie fragt stattdessen, was Ursache und Wirkung sind, wie unterschiedliche Helligkeitszonen entstehen, welche Zeitstruktur den 24-Stunden-Rhythmus erklärt, wie Tageslängen, Jahreszeiten und Zeitzonen erklärt werden und welche Zusatzannahmen nötig sind.

Die Kausalitätsprüfung ist abhängig von der formalen Tiefe des Wirkmodells. Ausgleichend wirken Strukturprüfung, Ontologieprüfung, Ableitungsprüfung, Geltungsbereichsprüfung, Kompetenzfragenprüfung, nutzerbasierte Lückenprüfung und Vergleichsprüfung.

### 7.5.6 Semantische Prüfung

Die semantische Prüfung untersucht, ob zentrale Begriffe eindeutig, konsistent und im selben Sinn verwendet werden.

Begriffe, Definitionen und Verwendungsstellen werden verglichen. Die Prüfung markiert Mehrdeutigkeiten, Bedeutungswechsel und unklare Fachbegriffe.

Findbare Modellprobleme sind mehrdeutige Begriffe, nicht definierte Schlüsselbegriffe, Bedeutungswechsel innerhalb einer Argumentation, Synonyme ohne Zusammenführung, Homonyme ohne Trennung, Vermischung von Alltags- und Fachsprache und konkurrierende Definitionen ohne Varianten- oder Geltungsbereichsmarkierung.

Der Begriff „Klimawandel“ kann beispielsweise jede langfristige Klimaänderung, den aktuellen globalen Temperaturanstieg, anthropogenen Klimawandel, politisch relevanten Klimawandel oder gefährlichen Klimawandel bedeuten. Ein Wirkmodell ist semantisch unvollständig, wenn nicht klar ist, welche Bedeutung verwendet wird.

Die semantische Prüfung entscheidet nicht, welche Begriffsdefinition die richtige ist. Sie verlangt nur, dass Begriffe explizit definiert und konsistent verwendet werden. Mehrere Definitionen können zulässig sein, wenn sie formal getrennt werden: als Varianten, domänenspezifische Begriffe, zeitlich getrennte Definitionen oder konkurrierende Modellannahmen.

### 7.5.7 Argumentative Prüfung

Die argumentative Prüfung untersucht, ob die Begründungsstruktur eines Wirkmodells vollständig und nachvollziehbar ist.

Claims werden mit Prämissen, Evidenz, Gegenclaims, Rebuttals und Schlussregeln verbunden. Das Modell wird darauf geprüft, ob eine Aussage gestützt, angegriffen, widerlegt, verteidigt oder offen ist.

Findbare Modellprobleme sind Claims ohne Begründung, Gegenclaims ohne Bearbeitung, Einwände ohne Antwort, Begründungen ohne Bezug, argumentative Zirkularität, fehlende Schlussregel, unklare Beweislast, Vermischung von Evidenz und Behauptung und mehrere konkurrierende argumentative Deutungen ohne Auflösung.

Beispiel:

Claim: Klimamodelle sind unzuverlässig.
Konklusion: Daher ist anthropogener Klimawandel nicht nachgewiesen.

Eine argumentative Prüfung kann markieren, dass eine Schlussregel fehlt, warum Modellunsicherheit den gesamten Attributionsclaim entkräftet, dass eine Unterscheidung zwischen Modellunsicherheit und Messdaten fehlt und dass nicht dargestellt wird, welche Evidenztypen betroffen sind.

### 7.5.8 Evidenzprüfung

Die Evidenzprüfung untersucht, ob Claims mit geeigneten Evidenzobjekten verbunden sind und ob diese Evidenzobjekte typologisch zum Claim passen.

Die Evidenzprüfung ist dabei nicht mit einer externen Wahrheitsprüfung gleichzusetzen. Sie prüft zunächst, ob ein Claim innerhalb des Wirkmodells eine erkennbare Evidenzgrundlage besitzt und ob der verwendete Evidenztyp zum Claimtyp passt.

Findbare Modellprobleme sind unbelegte Claims, falscher Evidenztyp, Evidenz ohne Bezug, Evidenz außerhalb des Geltungsbereichs, Überdehnung einer Quelle, fehlende Gegenbelege innerhalb des Modells, unklarer Evidenzstandard, nicht explizierte Ablehnung bestimmter Evidenztypen und mehrere Evidenzstandards ohne Prioritäts- oder Variantenmarkierung.

Beispiel:

Claim: Der aktuelle Temperaturanstieg ist natürlich.
Evidenz: Es gab Eiszeiten und Warmzeiten in der Erdgeschichte.

Die Evidenzprüfung kann markieren, dass die Evidenz innerhalb des Modells langfristige natürliche Klimavariabilität belegt, aber offen bleibt, durch welche Schlussregel daraus die Ursache des aktuellen Temperaturanstiegs abgeleitet wird.

### 7.5.9 Geltungsbereichsprüfung

Die Geltungsbereichsprüfung untersucht, ob Aussagen nur innerhalb der Bereiche verwendet werden, für die sie definiert sind.

Claims, Evidenzen, Relationen und Schlussregeln werden hinsichtlich Zeit, Raum, Skala, Domäne und Abstraktionsebene verglichen.

Findbare Modellprobleme sind Übertragungen von lokaler Evidenz auf globale Aussagen, Übertragungen geologischer Zeiträume auf aktuelle Entwicklungen, Vermischungen kurzfristiger Wetterereignisse mit langfristigem Klima, Verallgemeinerungen aus Spezialfällen, unmarkierte Skalenwechsel, Übertragungen in nicht definierte Kontexte und überlappende Geltungsbereiche ohne Prioritätsregel.

Beispiel:

In einer Region war ein Winter besonders kalt.
Daraus folgt: Es gibt keine globale Erwärmung.

Die Prüfung markiert einen Geltungsbereichsfehler zwischen regionaler Wetterbeobachtung und globalem Klimatrend. Sie entscheidet damit nicht über die Wahrheit der Endthese, sondern über die Reichweite der verwendeten Aussage.

### 7.5.10 Unsicherheits- und Modalitätsprüfung

Diese Prüfung untersucht, ob das Wirkmodell Unsicherheiten, Wahrscheinlichkeiten, Hypothesen und epistemische Statusangaben angemessen kennzeichnet.

Dabei wird unterschieden zwischen sicher, wahrscheinlich, möglich, hypothetisch, umstritten, modellabhängig, normativ gesetzt, empirisch gestützt und offen.

Findbare Modellprobleme sind absolute Formulierungen trotz unsicherer Modelllage, fehlende Unsicherheitsangaben, Verwechslung von Möglichkeit und Wahrscheinlichkeit, hypothetische Annahmen als gesicherte Modellbestandteile, fehlende Sensitivität gegenüber Modellannahmen, unklarer Status einer Aussage und Unsicherheit ohne definierte Auswertungsregel.

Unsicherheit darf nicht als Ersatz für unaufgelöste Mehrdeutigkeit dienen. Wenn verschiedene Bedeutungen, Varianten oder Konflikte vorliegen, müssen sie als solche modelliert werden.

### 7.5.11 Vollständigkeitsprüfung über Kompetenzfragen

Diese Prüfung untersucht, ob das Wirkmodell die Fragen beantworten kann, die es aufgrund seines eigenen Geltungsbereichs beantworten können sollte.

Für jeden Wirkraum wird ein Satz von Kompetenzfragen definiert. Das Modell wird darauf geprüft, ob seine Struktur Antworten auf diese Fragen ermöglicht.

Beispielhafte Kompetenzfragen für ein Klimawandel-Wirkmodell:

Welche Ursachen des Temperaturanstiegs werden modelliert?
Welche Ursachen werden ausgeschlossen?
Welche Zeiträume sind gemeint?
Welche Messgrößen werden verwendet?
Welche Wirkmechanismen werden angenommen?
Welche Alternativerklärungen werden behandelt?
Welche Unsicherheiten werden anerkannt?
Welche Beobachtung würde das Modell schwächen?

Findbare Modellprobleme sind fehlende Alternativerklärungen, fehlende Mechanismen, fehlende Abgrenzungen, fehlende Falsifikationsbedingungen innerhalb des Modells, unzureichende Operationalisierung und nicht aufgelöste Varianten bei zentralen Modellfragen.

### 7.5.12 Vergleichsprüfung zwischen Wirkmodellen

Die Vergleichsprüfung untersucht nicht nur ein einzelnes Modell, sondern Unterschiede, Überschneidungen und Konfliktpunkte zwischen mehreren Wirkmodellen.

Zwei oder mehr Wirkmodelle werden auf gemeinsame Entitäten, gegensätzliche Claims, unterschiedliche Kausalpfade, abweichende Geltungsbereiche und unterschiedliche Evidenzstandards verglichen.

Findbare Modellprobleme oder Konfliktpunkte sind Scheinwidersprüche durch unterschiedliche Begriffe, echte Widersprüche bei gleichem Geltungsbereich, fehlende Behandlung relevanter Gegenpositionen, asymmetrische Modellierung, unterschiedliche Evidenzstandards, versteckte normative Differenzen, unaufgelöste Modellvarianten und konkurrierende Outputs ohne Auflösungsregel.

Die Plattform entscheidet nicht automatisch, welches Modell wahr ist. Sie zeigt, wo sich die Modelle unterscheiden und welche Annahmen, Begriffe, Evidenzstandards oder Kausalrelationen für den Dissens verantwortlich sind.

### 7.5.13 Nutzerbasierte Lückenprüfung

Die nutzerbasierte Lückenprüfung ergänzt automatische Verfahren durch strukturierte menschliche Prüfung.

Nutzer können Lücken nicht nur kommentieren, sondern als formale Lückenobjekte anlegen. Diese Lücken werden typisiert, auf Modellbestandteile bezogen und mit Bearbeitungsstatus versehen.

Mögliche Lückentypen sind fehlende Entität, fehlende Relation, fehlender Mechanismus, fehlende Evidenz, fehlende Definition, fehlende Schlussregel, fehlender Geltungsbereich, fehlende Alternativerklärung, fehlende Unsicherheitsangabe, Kategorienfehler, Skalenfehler, unaufgelöste Mehrdeutigkeit, fehlende Prioritätsregel und unklare Variantenbeziehung.

Nutzerbasierte Prüfung kann verzerrt, interessengeleitet oder unsystematisch sein. Ausgleichend wirken standardisierte Lückentypen, rollenbasierte Reviews, Begründungspflicht, Bewertung der Relevanz, Versionierung, Moderation und automatische Vorprüfung.

## 7.6 Wirkmodellverbünde und Beziehungen zwischen Wirkmodellen

### 7.6.1 Grundbegriff: Wirkmodellverbund

Ein einzelnes Wirkmodell reicht für größere narrative, wissenschaftliche oder hypothetische Welten in der Regel nicht aus. Ein längerer literarischer Entwurf, eine Eutopie, eine Zukunftssimulation oder ein komplexes Szenario enthält typischerweise eine Vielzahl von Wirkmodellen aus unterschiedlichen Bereichen.

Beispiel:

Gesamtwelt 2100
├── Klimamodell
├── Finanzmodell
│   ├── Fiskalpolitik
│   ├── Haushaltspolitik
│   ├── Handelspolitik
│   └── Geldpolitik
├── Technologiemodell
├── Demografiemodell
├── Institutionenmodell
└── Konfliktmodell

Ein Wirkmodellverbund ist eine formal beschriebene Menge von Wirkmodellen, die durch Kompositions-, Abhängigkeits-, Input-Output-, Konflikt-, Varianten- oder Zeitrelationsbeziehungen miteinander verbunden sind.

Auch der Wirkmodellverbund ist keine Wahrheitsmaschine. Er prüft nicht, ob die modellierte Welt realistisch oder empirisch korrekt ist. Er prüft, ob die beteiligten Wirkmodelle formal kompatibel, zeitlich anschlussfähig, semantisch eindeutig und in ihren wechselseitigen Abhängigkeiten transparent sind.

### 7.6.2 Wirkmodelle als modulare Systeme

Für Wirkmodellverbünde lassen sich Prinzipien aus Softwareentwicklung und Programmiersprachendesign adaptieren. Ein Wirkmodell kann als formales Modul verstanden werden.

Ein solches Modul besitzt Zweck, Geltungsbereich, Inputs, Outputs, Vorbedingungen, Nachbedingungen, Invarianten, interne Entitäten, interne Relationen, interne Claims, interne Kausalannahmen, Evidenzstandards, Abhängigkeiten und Version.

Die Analogie zur Softwareentwicklung ist hilfreich, aber nicht vollständig. Ein Wirkmodell ist kein Programm. Es enthält auch normative Annahmen, hypothetische Setzungen, Unsicherheiten, Varianten und narrative Zwecke. Dennoch kann es wie ein Modul mit Schnittstellen, Verträgen, Abhängigkeiten und Gültigkeitsbedingungen beschrieben werden.

### 7.6.3 Schnittstellen von Wirkmodellen

Jedes Wirkmodell sollte eine explizite Schnittstelle besitzen.

Diese Schnittstelle beschreibt:

Welche Inputs erwartet das Wirkmodell?
Welche Outputs liefert es?
Welche Einheiten und Datentypen werden verwendet?
Welche zeitlichen und räumlichen Geltungsbereiche gelten?
Welche Definitionen werden vorausgesetzt?
Welche Wertebereiche sind zulässig?
Welche anderen Wirkmodelle werden benötigt?

Beispiel:

Wirkmodell: Agrarmodell
Inputs: Temperaturänderung, Niederschlagsänderung, Bodenqualität, Arbeitskräfteverfügbarkeit
Outputs: Ernteertrag, Nahrungsmittelpreis, Importbedarf

Dadurch wird prüfbar, ob ein anderes Modell die benötigten Inputs liefert, ob Einheiten kompatibel sind, ob Zeiträume zusammenpassen und ob ein Output außerhalb seines Geltungsbereichs verwendet wird.

### 7.6.4 Wirkmodell-Verträge: Vorbedingungen, Nachbedingungen und Invarianten

In Anlehnung an Design by Contract können Wirkmodelle über formale Verträge beschrieben werden.

Ein Wirkmodell-Vertrag enthält:

Preconditions: Welche Bedingungen müssen gelten, damit das Modell anwendbar ist?
Postconditions: Welche Zustände, Claims oder Outputs liefert das Modell nach Anwendung?
Invariants: Welche Bedingungen müssen während der Geltung des Modells erhalten bleiben?

Beispiel:

Wirkmodell: Fiskalpolitisches Investitionsmodell
Preconditions: Staat besitzt Steuerhoheit; Kapitalmarktzugang ist gegeben; Schuldenquote liegt unter Schwelle X.
Postconditions: öffentliche Investitionen steigen; Staatsverschuldung steigt kurzfristig; Produktivität steigt unter Bedingung Y.
Invariants: Zahlungsfähigkeit des Staates bleibt erhalten; institutionelle Handlungsfähigkeit bleibt über Schwelle Z.

Diese Verträge sind keine Wahrheitsbehauptungen über die Welt. Sie legen offen, unter welchen Annahmen ein Wirkmodell angewendet wird und welche Konsequenzen es innerhalb des Modellverbunds erzeugt.

Vorbedingungen, Nachbedingungen und Invarianten sind selbst Modellbestandteile. Sie können daher ebenfalls Claims, Annahmen, Geltungsbereiche, Unsicherheiten oder normative Setzungen enthalten.

### 7.6.5 Beziehungstypen zwischen Wirkmodellen

Zwischen Wirkmodellen können unterschiedliche formale Beziehungen bestehen:

Komposition: Ein Wirkmodell ist Teil eines größeren Wirkmodells, etwa part_of(Haushaltspolitikmodell, Finanzmodell).
Abhängigkeit: Ein Wirkmodell benötigt Annahmen, Variablen oder Outputs eines anderen Wirkmodells, etwa depends_on(Sozialmodell, Arbeitsmarktmodell).
Input-Output-Beziehung: Ein Modell erzeugt Größen, die ein anderes Modell weiterverwendet, etwa output_of(Temperaturänderung, Klimamodell) und input_to(Temperaturänderung, Agrarmodell).
Zeitliche Abfolge: Ein Wirkmodell gilt für einen Zeitraum und wird danach durch ein anderes ersetzt.
Bedingte Aktivierung: Ein Wirkmodell gilt nur, wenn bestimmte Bedingungen erfüllt sind.
Konflikt oder Inkompatibilität: Zwei Wirkmodelle können nicht gleichzeitig unter denselben Bedingungen gelten.
Variantenbeziehung: Mehrere Modelle können alternative Szenarien desselben Bereichs darstellen.
Verfeinerung: Ein Modell kann ein anderes detaillieren.
Ersetzung: Ein Modell kann ein anderes ab einem bestimmten Zeitpunkt oder unter bestimmten Bedingungen ersetzen.

### 7.6.6 Ambiguitätsauflösung im Wirkmodellverbund

Bei der Komposition mehrerer Wirkmodelle können Mehrdeutigkeiten entstehen:

Zwei Modelle liefern dieselbe Variable mit unterschiedlicher Definition.
Zwei Modelle gelten im selben Zeitraum, haben aber widersprüchliche Preconditions.
Ein Modell erwartet einen Input, der von mehreren anderen Modellen geliefert wird.
Ein Output wird außerhalb seines Geltungsbereichs verwendet.
Zwei Varianten werden gleichzeitig aktiviert.

Solche Mehrdeutigkeiten dürfen nicht implizit bleiben. Der Wirkmodellverbund muss sie auflösen oder formal markieren.

Mögliche Auflösungsformen sind Prioritätsregel, Geltungsbereichstrennung, zeitliche Trennung, Variantenbildung, Aggregation, explizite Konfliktmarkierung und offene Lücke.

Beispiel:

Modell A liefert Arbeitslosenquote für 2050.
Modell B liefert ebenfalls Arbeitslosenquote für 2050.
Das Sozialmodell verwendet Arbeitslosenquote als Input.

Nicht zulässig wäre: Das Sozialmodell verwendet irgendwie beide Werte.

Zulässig wären Variantenbildung, eine Prioritätsregel, eine Aggregationsregel oder eine explizite Konfliktmarkierung mit dem Status unresolved_conflict.

### 7.6.7 Zeitliche Gültigkeit und Modellwechsel

Wirkmodelle können zeitlich begrenzt gelten. In längeren narrativen oder spekulativen Entwürfen ist dies zentral.

Beispiel:

Finanzmodell_A gilt von 2030 bis 2050.
Finanzmodell_B gilt von 2050 bis 2100.

Die Plattform muss prüfen, ob es Lücken zwischen Geltungszeiträumen gibt, ob sich Modelle überlappen, ob der Übergang definiert ist, ob Outputs korrekt übergeben werden, ob Invarianten verletzt werden und ob sich zentrale Definitionen ändern.

Beispielproblem:

Modell A: 2030–2050 gilt starke staatliche Investitionspolitik.
Modell B: 2040–2070 gilt strikte Schuldenbremse.

Das ist nicht automatisch falsch. Aber es erzeugt eine Prüfanforderung: Wie können beide Modelle zwischen 2040 und 2050 zugleich gelten? Gibt es eine Prioritätsregel? Gilt eines nur für bestimmte Staaten? Wird die Schuldenbremse durch Sondervermögen umgangen? Wird das Investitionsmodell ab 2040 abgeschwächt?

### 7.6.8 Versionierung und Abwärtskompatibilität

Wirkmodelle können in mehreren Versionen vorliegen.

Beispiel:

Finanzmodell v1.0: gilt 2030–2050; nutzt Zinssatzmodell A; setzt freie Kapitalmärkte voraus.
Finanzmodell v2.0: gilt 2050–2100; nutzt Zinssatzmodell B; setzt Kapitalverkehrskontrollen voraus.

Prüfbar ist, welche Modelle von welcher Version abhängen, ob eine alte Modellversion noch verwendet wird, ob eine Änderung Auswirkungen auf abhängige Modelle hat, ob ein Übergang zwischen Versionen definiert ist und ob ein Breaking Change entsteht.

Ein Breaking Change im Wirkmodellverbund liegt vor, wenn eine Änderung an einem Modell dazu führt, dass abhängige Modelle ihre Preconditions nicht mehr erfüllen, Outputs nicht mehr typkompatibel sind oder Geltungsbereiche nicht mehr zusammenpassen.

## 7.7 Modellrestrukturierung
Da Wirkmodellverbünde im Arbeitsprozess wachsen und ihre angemessene Struktur häufig erst nachträglich sichtbar wird, benötigt die Plattform Verfahren zur Modellrestrukturierung. Modellrestrukturierung bezeichnet strukturverändernde Operationen an einem Wirkmodell oder Wirkmodellverbund, bei denen die modellinterne Semantik erhalten bleiben soll. Sie dient dazu, gewachsene oder unübersichtliche Modellstrukturen nachträglich klarer, modularer, konsistenter und besser prüfbar zu machen.
Der Begriff ist an das Refactoring in der Softwareentwicklung anschlussfähig, wird im Projekt jedoch als Modellrestrukturierung gefasst, um den Vorgang auch für Nutzer ohne technischen Hintergrund verständlich zu machen. Entscheidend ist nicht die Herkunft des Begriffs, sondern das Prinzip: Die Struktur darf verändert werden, die modellinterne Bedeutung soll erhalten bleiben.
### 7.7.1 Abgrenzung: Modellrestrukturierung, Modellklärung und Modellrevision
Die Plattform unterscheidet drei Änderungsarten:
Modellrestrukturierung: Die Struktur wird verändert, während die modellinterne Semantik erhalten bleiben soll.
Modellklärung: Eine implizite, unklare oder mehrdeutige Stelle wird explizit gemacht. Dabei kann ein semantisches Risiko entstehen, wenn mehrere Deutungen möglich waren.
Modellrevision: Claims, Ableitungen, Geltungsbereiche, Schnittstellenwirkungen oder Konsequenzen verändern sich. In diesem Fall liegt keine reine Restrukturierung mehr vor.
Nach jeder Modellrestrukturierung muss geprüft werden, ob Claims, Ableitungen, Schnittstellen, Geltungsbereiche, Invarianten, Outputs und Kompetenzfragen weiterhin erhalten bleiben.
### 7.7.2 Neu-Situierung einzelner Modellbestandteile
Bei der Neu-Situierung werden einzelne Elemente innerhalb eines Wirkmodells oder zwischen Wirkmodellen verschoben. Dies betrifft etwa Claims, Annahmen, Relationen, Kausalverbindungen, Evidenzobjekte, Vorbedingungen, Invarianten oder Outputs.
Beispiel: Ein Claim liegt zunächst im Finanzmodell, wird später aber in das Handelspolitikmodell verschoben, weil dort sein sachlicher Ort präziser ist.
Die Semantikerhaltungsprüfung fragt, ob der Claim inhaltlich identisch bleibt, ob seine Abhängigkeiten erhalten bleiben, ob Geltungsbereich und Status unverändert sind, ob alle Ableitungen weiterhin funktionieren und ob abhängige Modelle weiterhin Zugriff auf den Claim haben.
Der typische Nutzen liegt in einer fachlich passenderen Zuordnung, besserer Modularität und klarerer Verantwortlichkeit einzelner Teilmodelle.
### 7.7.3 Extraktion und Einbettung von Teilmodellen
Diese Restrukturierungen verändern die Granularität eines Wirkmodells. Bei einer Extraktion wird ein Teilbereich aus einem bestehenden Modell herausgelöst und als eigenes Wirkmodell modelliert. Bei einer Einbettung wird ein bisher eigenständiges Modell in ein anderes Modell aufgenommen.
Beispiel für Extraktion: Ein Finanzmodell enthält zunächst handelspolitische Annahmen. Später wird daraus ein eigenes Handelspolitikmodell, von dem das Finanzmodell abhängig ist.
Beispiel für Einbettung: Ein separates Zollmodell wird in ein übergeordnetes Handelspolitikmodell integriert.
Zu prüfen ist, ob alle internen Claims erhalten bleiben, ob frühere interne Relationen nun als Schnittstellen korrekt abgebildet werden, ob Inputs und Outputs verfügbar bleiben, ob neue Abhängigkeiten entstehen und ob Kompetenzfragen unverändert beantwortbar bleiben.
### 7.7.4 Aufteilung und Zusammenführung von Modellen und Modellverbünden
Diese Operationen betreffen ganze Wirkmodelle oder Wirkmodellverbünde. Ein großes Modell kann in mehrere Modelle zerlegt werden; mehrere Modelle können zu einem größeren Modell zusammengeführt werden. Entsprechend können auch ganze Modellverbünde geteilt oder verschmolzen werden.
Beispiel für Aufteilung: Ein monolithisches Finanzmodell wird in Fiskalpolitikmodell, Haushaltspolitikmodell, Geldpolitikmodell und Handelspolitikmodell gegliedert.
Beispiel für Zusammenführung: Ein Fiskalpolitikmodell und ein Haushaltspolitikmodell werden zu einem Staatsfinanzmodell verbunden.
Zu prüfen ist, ob alle Claims, Relationen und Kausalpfade erhalten bleiben, ob bisherige Schnittstellen verfügbar bleiben, ob unmarkierte Konflikte entstehen, ob Geltungsbereiche verändert werden, ob Invarianten erhalten bleiben und ob Kompetenzfragen gleich beantwortbar bleiben.
Der typische Nutzen liegt in der besseren Gliederung großer narrativer Welten, der Auflösung monolithischer Modelle und der Reduktion von Doppelstrukturen.
### 7.7.5 Schnittstellen- und Abhängigkeitsrestrukturierung
Diese Restrukturierungen verändern nicht primär den Inhalt eines Modells, sondern die Art, wie Modelle miteinander gekoppelt sind. Dazu gehören das Einführen oder Herauslösen von Schnittstellen, das Ersetzen von Abhängigkeiten, das Sichtbarmachen bisher interner Outputs oder das Einführen von Adaptern zwischen inkompatiblen Modellen.
Beispiel: Ein Agrarmodell nutzt zunächst informell Klimadaten. Nach der Restrukturierung liefert das Klimamodell explizit Temperatur- und Niederschlagsänderungen, die vom Agrarmodell als Inputs erwartet werden.
Ein Adapter kann erforderlich werden, wenn ein Modell regionale Werte liefert, ein anderes Modell aber globale Durchschnittswerte erwartet. Die Umrechnung muss dann als eigene Regel oder Schnittstellenkomponente modelliert werden.
Zu prüfen ist, ob Inputs und Outputs typkompatibel sind, ob Einheiten und Wertebereiche erhalten bleiben, ob Outputs weiterhin an alle abhängigen Modelle geliefert werden, ob neue zirkuläre Abhängigkeiten entstehen und ob frühere implizite Abhängigkeiten korrekt explizit gemacht wurden.
### 7.7.6 Zeitliche Restrukturierung
Zeitliche Restrukturierungen betreffen die Gültigkeit von Wirkmodellen über Zeit. Sie sind besonders relevant für längere narrative oder spekulative Entwürfe, in denen sich politische, ökonomische, technische oder ökologische Wirkzusammenhänge über Jahrzehnte verändern.
Mögliche Operationen sind das Aufteilen eines Geltungszeitraums, das Zusammenführen von Zeitabschnitten, das Einführen eines Übergangsmodells, das Verschieben eines Modells in einen früheren oder späteren Zeitraum, das Definieren eines Nachfolgemodells oder das Festlegen einer Überlappungsregel.
Beispiel: Ein Finanzmodell gilt zunächst von 2030 bis 2100. Später wird es in Finanzmodell A für 2030 bis 2050 und Finanzmodell B für 2050 bis 2100 aufgeteilt.
Zu prüfen ist, ob zeitliche Lücken entstehen, ob unmarkierte Überlappungen vorliegen, ob Übergänge definiert sind, ob Outputs eines Zeitabschnitts korrekt an den nächsten übergeben werden und ob Invarianten über den Übergang hinweg verletzt werden.
### 7.7.7 Begriffs- und Typrestrukturierung
Diese Restrukturierungen betreffen Definitionen, Typen und Namensräume. Sie dienen dazu, Begriffe präziser zu fassen, Mehrdeutigkeiten aufzulösen und die Ontologie des Wirkmodellverbunds klarer zu machen.
Mögliche Operationen sind das Umbenennen einer Entität oder Variable, das Aufteilen eines Begriffs, das Zusammenführen von Begriffen, das Einführen eines Namensraums, das Ändern einer Typzuordnung oder das Herausziehen einer Definition.
Beispiel: Der Begriff „Wachstum“ wird in „BIP-Wachstum“, „Bevölkerungswachstum“ und „Produktivitätswachstum“ aufgeteilt.
Eine solche Änderung ist nur dann reine Modellrestrukturierung, wenn die Bedeutung erhalten bleibt oder bereits implizit so gemeint war. Wenn dadurch eine von mehreren möglichen Bedeutungen ausgewählt wird, handelt es sich eher um Modellklärung oder Modellrevision.
Zu prüfen ist, ob alte Referenzen korrekt übertragen werden, ob Bedeutungen identisch bleiben, ob neue oder gelöste Mehrdeutigkeiten entstehen und ob Kompetenzfragen anders beantwortet werden.
### 7.7.8 Vertragsrestrukturierung
Diese Restrukturierungen betreffen Vorbedingungen, Nachbedingungen und Invarianten eines Wirkmodells. Sie machen sichtbar, unter welchen Bedingungen ein Modell angewendet werden darf, welche Outputs oder Zustände es erzeugt und welche Bedingungen während seiner Geltung erhalten bleiben müssen.
Beispiel: Ein Investitionsmodell setzt implizit Kapitalmarktzugang voraus. Nach der Restrukturierung wird diese Voraussetzung als explizite Precondition modelliert.
Zu prüfen ist, ob die Bedingung vorher bereits implizit im Modell enthalten war, ob durch die neue Precondition der Geltungsbereich verändert wird, ob abhängige Modelle dadurch eingeschränkt werden, ob sich ableitbare Konsequenzen ändern und ob Kompetenzfragen gleich beantwortbar bleiben.
Vertragsrestrukturierungen erhöhen die Explizitheit, können aber semantisch riskant sein, wenn sie bislang nur vermutete Voraussetzungen nachträglich als verbindlich setzen.
### 7.7.9 Varianten- und Konfliktrestrukturierung
Diese Restrukturierungen betreffen konkurrierende Deutungen, Modellvarianten und Konflikte. Sie sind besonders wichtig, weil die Plattform keine unmarkierten Interpretationsspielräume zulässt.
Mögliche Operationen sind das Herauslösen einer Variante, das Zusammenführen von Varianten, das Einführen einer Prioritätsregel, das Einführen einer Konfliktrelation, das Aufteilen eines Konflikts nach Geltungsbereichen, die Umwandlung einer Mehrdeutigkeit in Varianten oder die Umwandlung eines Konflikts in eine bedingte Regel.
Beispiel: Der Begriff „Stabilität“ kann demokratische oder autoritäre Stabilität bedeuten. Nach der Restrukturierung werden daraus zwei explizite Varianten mit unterschiedlichen Annahmen und Konsequenzen.
Viele dieser Operationen sind eher Modellklärung als reine Modellrestrukturierung. Zu prüfen ist daher, ob eine bisher implizite Mehrdeutigkeit nur sichtbar gemacht wird oder ob eine Bedeutung neu ausgewählt wird.
### 7.7.10 Prüfung nach Modellrestrukturierungen
Nach jeder Modellrestrukturierung sollte ein Standardprüfset ausgeführt werden. Dieses Prüfset soll klären, ob sich nur die Struktur geändert hat oder ob auch die Modellsemantik verändert wurde.
Mindestens relevant sind Strukturprüfung, semantische Prüfung, Ableitungsprüfung, Schnittstellenprüfung, Dependency-Prüfung, Geltungsbereichsprüfung, Invariantenprüfung, Kompetenzfragenprüfung, Konfliktprüfung und Versionsprüfung.
Die Plattform kann vier Ergebnisse unterscheiden:
Semantikerhaltende Modellrestrukturierung: Die Struktur wurde verändert, die Modellsemantik bleibt erhalten.
Modellklärung: Eine implizite oder mehrdeutige Stelle wurde explizit gemacht; das semantische Risiko wird als niedrig, mittel oder hoch ausgewiesen.
Modellrevision: Die Änderung verändert Claims, Ableitungen, Geltungsbereiche, Schnittstellenwirkungen oder Konsequenzen.
Nicht vollständig prüfbar: Die Plattform kann nicht feststellen, ob die Semantik erhalten bleibt; Nutzerreview ist erforderlich.
Damit wird Modellrestrukturierung zu einem kontrollierten Verfahren: Die Plattform erlaubt strukturelle Weiterentwicklung, verhindert aber, dass semantische Änderungen unbemerkt als bloße Strukturänderungen erscheinen.
## 7.8 Prüfung von Wirkmodellverbünden

Neben der Prüfung einzelner Wirkmodelle braucht die Plattform eine Prüfung von Wirkmodellverbünden.

Diese untersucht:

Passen die Geltungsbereiche der Modelle zusammen?
Werden Outputs eines Modells korrekt als Inputs eines anderen verwendet?
Gibt es Widersprüche zwischen Axiomen verschiedener Modelle?
Sind zeitliche Übergänge definiert?
Gibt es Lücken zwischen aufeinanderfolgenden Modellen?
Werden Variablen in verschiedenen Modellen gleich definiert?
Sind Abhängigkeiten zyklisch, beabsichtigt oder problematisch?
Wird ein Modell außerhalb seines Geltungsbereichs verwendet?
Werden Invarianten verletzt?
Gibt es konkurrierende Outputs ohne Auflösungsregel?

Auch diese Prüfung ist keine Wahrheitsprüfung. Sie erzeugt ein Klarheits- und Kompatibilitätsprofil des Modellverbunds.

Beispielausgabe:

Wirkmodellverbund: Gesellschaft 2100
Kompositionsstruktur: vollständig
Schnittstellenkompatibilität: mittel
Zeitliche Anschlussfähigkeit: niedrig
Offene Modellübergänge: 3
Konflikte zwischen Preconditions: 2
Unaufgelöste Output-Konflikte: 1
Verletzte Invarianten: 1
Nicht erfüllte Dependencies: 4

## 7.9 Zusammenspiel der Prüfverfahren

Keines der genannten Verfahren reicht allein aus. Die Stärke des Ansatzes liegt in der Kombination.

Beispiel: Eine Kausalrelation ist formal korrekt angelegt. Die Strukturprüfung findet keinen Fehler. Die Ontologieprüfung erkennt aber, dass eine normative Entität als physikalische Ursache verwendet wird.

Ein anderes Beispiel: Ein Wirkmodell ist für sich genommen konsistent. Die Verbundprüfung zeigt aber, dass sein Output eine Invariante eines abhängigen Modells verletzt.

Deshalb sollte die Plattform nicht ein einziges Urteil ausgeben, sondern ein Prüfprofil:

Strukturelle Vollständigkeit: hoch
Ontologische Konsistenz: mittel
Logische Konsistenz: hoch
Kausale Explizitheit: niedrig
Evidenzabdeckung: mittel
Semantische Eindeutigkeit: niedrig
Argumentative Abdeckung: mittel
Geltungsbereichsklarheit: hoch
Schnittstellenkompatibilität: mittel
Zeitliche Anschlussfähigkeit: niedrig
Offene Lücken: 14
Kritische Lücken: 3
Unaufgelöste Mehrdeutigkeiten: 2

Ein solches Prüfprofil ist kein Wahrheitsurteil. Es ist ein Klarheitsprofil. Es beschreibt, wie gut ein Wirkmodell oder Wirkmodellverbund seine eigenen Voraussetzungen, Relationen, Schlussregeln, Evidenzstandards, Geltungsbereiche, Schnittstellen und Konsequenzen expliziert.

## 7.10 Methodische Grenzen und bewusste Nicht-Ziele

Die Plattform ist nicht darauf ausgelegt, Wirkmodelle abschließend nach wahr oder falsch zu klassifizieren. Sie ist auch nicht darauf ausgelegt, normative Konflikte oder Evidenzkonflikte automatisch zu entscheiden. Ihr Ziel ist die formale, semantische und argumentative Klärung von Wirkannahmen.

### 7.10.1 Keine Wahrheitsprüfung, sondern Klarheitsprüfung

Die Plattform verfolgt nicht das Ziel, Wirkmodelle automatisch nach wahr oder falsch zu klassifizieren. Sie dient nicht als Wahrheitsinstanz, sondern als Instrument zur Offenlegung der internen Struktur eines Wirkraums.

Ein Wirkmodell kann daher auch kontrafaktisch, hypothetisch, spekulativ, fiktional oder fachlich randständig sein. Entscheidend ist nicht, ob es mit einem externen empirischen Wahrheitsstandard übereinstimmt, sondern ob seine Voraussetzungen, Begriffe, Relationen, Kausalannahmen, Schlussregeln, Geltungsbereiche und Konsequenzen explizit gemacht werden.

Die leitende Prüffrage lautet daher nicht: Ist dieses Wirkmodell wahr? Sondern: Ist dieses Wirkmodell klar genug formuliert, um seine Annahmen, Folgerungen, Konflikte, Lücken und Konsequenzen nachvollziehen zu können?

### 7.10.2 Keine unmarkierte Mehrdeutigkeit

Die Plattform muss zwischen zulässiger Offenheit und unzulässiger Mehrdeutigkeit unterscheiden.

Zulässig sind explizite Unsicherheit, explizite Varianten, explizite Konflikte, explizite offene Lücken, explizite Prioritätsregeln und explizite Geltungsbereichstrennung.

Nicht zulässig als fertiger Modellzustand sind unmarkierte Begriffsmehrdeutigkeiten, konkurrierende Outputs ohne Auflösung, widersprüchliche Regeln ohne Konfliktmarkierung und Interpretationsspielräume ohne formale Repräsentation.

Die Plattform muss ein Wirkmodell daher ähnlich wie ein Compiler prüfen: Nicht ob es wahr ist, sondern ob es eindeutig auswertbar ist. Ist dies nicht der Fall, wird das Modell nicht als falsch, sondern als nicht vollständig auswertbar markiert.

### 7.10.3 Abhängigkeit von formaler Modellierung

Die Prüfqualität hängt davon ab, wie gut das Wirkmodell formal angelegt wurde. Wenn zentrale Annahmen nicht modelliert werden, können sie auch nicht zuverlässig geprüft werden. Dieses Problem kann durch Kompetenzfragen, Nutzerreviews und Lückenhinweise reduziert, aber nicht vollständig beseitigt werden.

### 7.10.4 Implizites Hintergrundwissen

Viele wissenschaftliche, kulturelle oder alltägliche Aussagen setzen Hintergrundwissen voraus. Nicht jedes Hintergrundwissen kann explizit modelliert werden. Die Plattform muss daher unterscheiden zwischen notwendiger expliziter Annahme, domänenspezifischem Standardwissen und irrelevantem Hintergrundwissen. Diese Unterscheidung ist schwierig und oft kontextabhängig.

### 7.10.5 Ontologische Vorentscheidungen

Jedes formale Modell setzt voraus, welche Arten von Dingen und Relationen überhaupt zugelassen werden. Damit enthält das System bereits ontologische Vorentscheidungen. Solche Entscheidungen sind nicht rein technisch, sondern konzeptionell und wissenschaftstheoretisch relevant. Sie sollten daher explizit dokumentiert, versioniert und gegebenenfalls durch alternative Ontologien ergänzbar sein.

### 7.10.6 Normative Setzungen als explizite Modellbestandteile

Normative Aussagen und Wertannahmen werden im Wirkmodell nicht als Störfaktoren behandelt, sondern als eigene, explizit zu modellierende Bestandteile. Die Plattform entscheidet nicht, welche normative Setzung richtig ist. Sie macht sichtbar, wo normative Setzungen auftreten, welche Rolle sie im Modell spielen und welche Konsequenzen aus ihnen folgen.

### 7.10.7 Strategische Modellierung

Nutzer können ein Modell absichtlich so formulieren, dass kritische Punkte ausgelassen, abgeschwächt oder formal schwer angreifbar gemacht werden. Automatische Prüfungen können solche Strategien teilweise sichtbar machen, etwa durch fehlende Gegenclaims, unklare Geltungsbereiche, nicht ausgearbeitete Kausalmechanismen, fehlende Kompetenzfragen oder unmarkierte Mehrdeutigkeiten. Vollständig verhindern lassen sie sich nicht.

### 7.10.8 Komplexität realer und hypothetischer Systeme

Viele Wirkzusammenhänge sind nicht linear, sondern dynamisch, rekursiv, probabilistisch und kontextabhängig. Ein formales Wirkmodell muss diese Komplexität reduzieren. Diese Reduktion ist notwendig, erzeugt aber immer einen Verlust. Daher sollte jedes Wirkmodell seine Modellgrenzen explizit ausweisen.

Die Forderung nach eindeutiger Modellsemantik hebt Komplexität nicht auf. Sie verlangt nur, dass Komplexität formal repräsentiert wird: als Rückkopplung, Wahrscheinlichkeit, Szenario, Variante, offene Lücke oder Abhängigkeitsstruktur.

### 7.10.9 Dissens über Evidenzstandards

Konflikte entstehen nicht nur über einzelne Aussagen, sondern auch über die Frage, welche Formen von Evidenz innerhalb eines Wirkmodells als zulässig, relevant oder hinreichend gelten.

Beispiel: Ein Nutzer akzeptiert Klimamodelle als Evidenz. Ein anderer Nutzer lehnt Klimamodelle grundsätzlich als Evidenz ab.

Die Plattform kann diesen Dissens sichtbar machen, indem sie die jeweiligen Evidenzstandards als explizite Modellbestandteile ausweist. Sie entscheidet jedoch nicht automatisch, welcher Evidenzstandard vorzuziehen ist. Stattdessen zeigt sie, welche Claims von welchen Evidenzstandards abhängen und welche Folgerungen sich daraus ergeben.

An dieser Stelle wird eine ergänzende nutzerbasierte Prüfung relevant: Nutzer können auf problematische, unklare oder unzureichend begründete Evidenzstandards hinweisen und diese als prüfbedürftige Modellstellen markieren. Die konkrete Ausgestaltung dieser nutzerbasierten Prüfung wird separat behandelt.

## 7.11 Zusammenfassung

Ein Wirkmodell ist eine formale Repräsentation eines abgegrenzten Wirkraums. Es besteht aus typisierten Entitäten, Zuständen, Relationen, Kausalannahmen, Claims, Evidenzen, Schlussregeln, Geltungsbereichen, Unsicherheiten, Gegenclaims und Lückenobjekten.

Die Prüfung eines Wirkmodells zielt nicht auf eine automatische Wahrheitsentscheidung. Sie zielt auf interne Konsistenz, Explizitheit, semantische Eindeutigkeit, argumentative Nachvollziehbarkeit, kausale Ausarbeitung, transparente Modellgrenzen und sichtbare Konsequenzen.

Ein Wirkmodell darf auf interpretativen, normativen, hypothetischen oder kontrafaktischen Vorentscheidungen beruhen. Diese dürfen jedoch nicht als unaufgelöste Mehrdeutigkeiten im Modell verbleiben. Wo mehrere Deutungen, Begriffe, Kausalpfade, Evidenzstandards oder normative Setzungen möglich sind, müssen sie als Varianten, Konflikte, Unsicherheiten, Prioritätsregeln, Geltungsbereichsunterscheidungen oder offene Lücken formalisiert werden.

Für größere narrative oder wissenschaftliche Entwürfe genügt ein einzelnes Wirkmodell nicht. Es braucht Wirkmodellverbünde, in denen mehrere Wirkmodelle über Kompositions-, Abhängigkeits-, Input-Output-, Konflikt-, Varianten- und Zeitrelationsbeziehungen miteinander verbunden sind. Solche Verbünde können nach Prinzipien modularer Systeme beschrieben werden: mit Schnittstellen, Vorbedingungen, Nachbedingungen, Invarianten, Versionen und Abhängigkeitsgraphen.

Da Wirkmodellverbünde im Arbeitsprozess wachsen, benötigt die Plattform darüber hinaus Verfahren zur Modellrestrukturierung. Diese erlauben es, Modellbestandteile neu zu situieren, Teilmodelle auszulagern oder einzubetten, Modelle und Modellverbünde zu teilen oder zusammenzuführen, Schnittstellen einzuführen, Geltungsbereiche zu präzisieren und Verträge offenzulegen. Ziel ist eine klarere Struktur bei erhaltener Modellsemantik. Änderungen, die die modellinterne Bedeutung verändern, werden als Modellrevision behandelt.

Dazu werden verschiedene Prüfverfahren kombiniert: Strukturprüfung, Ontologieprüfung, logische Konsistenzprüfung, Ableitungsprüfung, Kausalitätsprüfung, semantische Prüfung, argumentative Prüfung, Evidenzprüfung, Geltungsbereichsprüfung, Unsicherheitsprüfung, Kompetenzfragenprüfung, Vergleichsprüfung, Verbundprüfung und nutzerbasierte Lückenprüfung. Jedes Verfahren deckt bestimmte Modellprobleme auf, besitzt aber eigene Grenzen. Erst das Zusammenspiel der Verfahren erzeugt ein belastbares Klarheitsprofil.

Die Plattform entscheidet damit nicht, welcher Wirkraum wahr ist. Sie macht sichtbar, wie ein Wirkraum konstruiert ist, wo seine Annahmen liegen, welche Schlüsse er erlaubt, welche Lücken bestehen, welche Alternativen nicht behandelt werden, welche Modellbeziehungen bestehen und wo Dissens auf Begriffe, Evidenzstandards, Kausalannahmen oder normative Setzungen zurückgeht.
