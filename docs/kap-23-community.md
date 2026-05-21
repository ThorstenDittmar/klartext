# 23. Community, Trust Network und Nutzerprofil

Dieses Kapitel beschreibt das Community-System der Plattform in drei Teilen: die Regeln für den Diskursbereich (Zensur-Logik), das Trust Network (Akzeptanz-System nach EigenTrust+-Analogie) und das Nutzerprofil als Knotenpunkt beider Systeme.
Diese Elemente sind untrennbar miteinander verbunden. Das Trust Network gibt Community-Beiträgen Kontext. Das Nutzerprofil macht beide Systeme für andere lesbar. Und die Zensur-Logik definiert den Rahmen, innerhalb dessen Community stattfindet.
> ↗ Querverweis: Leserperspektive und Community-Grundlagen – vgl. Kap. 11
> ↗ Querverweis: Zensierter Diskussionsbereich in der Leseumgebung – vgl. Kap. 22.5

## 22.1 Zensur-Logik und Diskursrahmen
Die Plattform kennt eine bewusste, transparente Zensur. Sie richtet sich nicht gegen Meinungen, sondern gegen Aussagetypen, die im Diskursraum der Plattform strukturell fehl am Platz sind. Zensur ist hier kein Werturteil über den Inhalt, sondern eine epistemische Einschränkung des Rahmens.
Die Zensur gilt für alle Bereiche der Plattform, in denen direkte Kommunikation zwischen Nutzern stattfindet: Diskussionsbereiche unter Werken und Wirkmodellen, Feedback-Bereiche und Community-Kanäle.
22.1.1 Drei Kategorien ausgegrauterInhalte

KATEGORIE 1: WAHRHEITSDEBATTEN (GRAU)
Beiträge, die Wahrheitsanspüche über Axiome, Claims oder Wirkmodelle stellen, werden ausgegraut. Der Grund: Axiome sind innerhalb des Systems nicht anfechtbar. Die richtige Antwort auf ein abgelehntes Axiom ist ein Gegenentwurf, kein Gegenargument.
> → Beispiele für Wahrheitsdebatten: „Dein Axiom ist falsch.“ / „Das stimmt nicht.“ / „Das widerspricht dem wissenschaftlichen Konsens.“
> → Keine Wahrheitsdebatten: „Diese Stelle ist mehrdeutig.“ / „Hier fehlt eine Begründungsebene.“ / „Diese Kausalrelation ist empirisch nicht gestützt.“ – das sind strukturelle Aussagen über Klarheit, keine Wahrheitsurteile.
> → Ausgegraut heißt: im Normalfall nicht angezeigt. Ein Button „Ausgegrauükte anzeigen“ macht sie für den Leser sichtbar, der das explizit möchte.

KATEGORIE 2: RECHTSWIDRIGE INHALTE (ANDERE FARBE)
Beiträge, die rechtlich problematisch sind (Volksverhetzung, Beleidigung im Rechtssinne, urheberrechtliche Verstöße usw.), werden in einer anderen Farbe ausgegraut als Wahrheitsdebatten. Die farbliche Unterscheidung macht den Grund der Zensurentscheidung transparent.
> → Separat schaltbar: Ein eigener Button macht diese Kategorie sichtbar. Standard: nicht angezeigt.
> → Das System leistet keine Rechtsberatung. Die Klassifikation als rechtswidrig ist eine systemseitige Einschätzung, keine rechtlich bindende Feststellung.

KATEGORIE 3: PERSÖNLICHE BESCHIMPFUNGEN (DRITTE FARBE)
Beiträge, die persönliche Angriffe auf Nutzer enthalten, werden in einer dritten Farbe ausgegraut. Auch diese Kategorie ist separat schaltbar.

22.1.2 Widerspruchsmechanismus
Wer mit einer Zensurentscheidung nicht einverstanden ist, kann sich an einen Administrator (Gutachter) wenden. Der Administrator kann die Entscheidung aufheben. Die Entscheidung des Administrators ist final und wird im Beitrag protokolliert.
> → Aufgehobene Zensuren bleiben als solche sichtbar markiert – die Moderationshistorie ist transparent.
> ↗ Querverweis: Gutachter als Systemrolle – vgl. Kap. 23.3
> ↗ Querverweis: Temporäre Flags im Präsentationsmodus – vgl. Kap. 22.9.2
Hinweis: Im Präsentationsmodus können temporäre Flags auch auf Beiträge im Community-Diskussionsbereich gesetzt werden. Diese Flags sind nur während der Präsentation sichtbar und werden danach gelöscht. Sie verändern den Beitrag selbst nicht.

22.1.3 Verstoß-Tracking
Die Anzahl bestehender Verstöße pro Kategorie wird beim Profil jedes Nutzers systemseitig gezählt. Drei Werte: Wahrheitsdebatten, Rechtsverstöße, Beschimpfungen.
> → Jeder Nutzer entscheidet selbst, ob diese drei Werte in seinem öffentlichen Profil angezeigt werden. Zeigt er sie nicht an, fehlt der Abschnitt im Profil – er erscheint nicht als null, um keine False-Positive-Signale zu senden.
> → Aufgehobene Verstöße werden aus dem Zähler entfernt.

## 22.2 Trust Network: Akzeptanz-System
Das Trust Network basiert auf einem Akzeptanz-Mechanismus, der konzeptionell an EigenTrust+ angelehnt ist. Akzeptanz ist bewusst kein Vertrauen, kein Mögen und keine inhaltliche Zustimmung. Es ist eine neutrale Aussage: Ich anerkenne diesen Menschen als ernsthaften Teilnehmer des Diskurses.
Das Naming ist konzeptionell wichtig. Akzeptanz hat keine inhaltliche Konnotation. Zwei Personen mit entgegengesetzten Axiomräumen können sich gegenseitig Akzeptanz aussprechen.
22.2.1 Akzeptanz aussprechen
> → Jeder registrierte Nutzer kann anderen Nutzern Akzeptanz aussprechen.
> → Akzeptanz ist binär: vorhanden oder nicht vorhanden. Es gibt keine Grade.
> → Der Mindestwert ist 0 (kein Akzeptanz-Signal erhalten). Es gibt keine negative Markierung. Kein Blame-Game.
> → Wer jemanden akzeptiert hat, sieht das in seiner eigenen Übersicht. Der akzeptierte Nutzer sieht nicht, wer ihn akzeptiert hat.
> → Akzeptanz kann jederzeit still zurückgezogen werden. Keine Benachrichtigung an den betroffenen Nutzer.
22.2.2 Akzeptanzmuster
Die Gesamtheit aller Akzeptanz-Aussprachen eines Nutzers ist sein Akzeptanzmuster. Es ist per Default privat.
> → Veröffentlichen: Der Nutzer kann sein Muster vollständig öffentlich machen. Dann kann es von anderen abonniert werden.
> → Keine mittlere Stufe: Es gibt kein „nur für Akzeptierte sichtbar“. Das würde soziale Schulden erzeugen und die Neutralität der Akzeptanz unterlaufen.
> → Abonnieren: Wer ein öffentliches Muster abonniert, nutzt es als Grundlage für seine Peer-Group-Akzeptanz. Asymmetrisch: Man kann ein Muster abonnieren ohne selbst eins zu veröffentlichen, ohne dass der Musterinhaber das Abonnement sieht.
> → Änderungen am Muster sind stilles Recht des Nutzers. Wer aus einem Muster entfernt wird, erhält keine Benachrichtigung.
22.2.3 Die drei Akzeptanz-Werte im Profil
Auf jedem Nutzerprofil werden drei Werte als farblich unterschiedliche Balken unter dem Nutzernamen angezeigt.

PERSÖNLICHE AKZEPTANZ
> → Habe ich diesem Nutzer persönlich Akzeptanz ausgesprochen? Binär: ja oder nein. Nur für mich selbst sichtbar in dieser Form – andere sehen nur den Balken, nicht die Quelle.

PEER-GROUP-AKZEPTANZ
> → Der Mittelwert aller Akzeptanzmuster, die ich abonniert habe. Wie sehen die Menschen, deren Muster ich verfolge, diesen Nutzer? Wird nur angezeigt wenn ich mindestens ein Muster abonniert habe.

SYSTEMAKZEPTANZ
> → Ein Kompositwert aus drei Quellen: erstens ob der Nutzer im nicht-öffentlichen Profil Klarname und Kontaktinformationen hinterlegt hat; zweitens Betriebsdauer ohne Zensur-Verstöße; drittens der gemittelte Wert aller persönlichen Akzeptanz-Aussprachen auf der Plattform – also wie viel Prozent der Nutzer diesem Nutzer Akzeptanz ausgesprochen haben.
> → Die Systemakzeptanz ist für alle sichtbar, auch ohne Login. Sie ist der einzige der drei Werte, der öffentlich ohne Personalisierung berechnet werden kann.

## 22.3 Nutzerprofil
Das Nutzerprofil ist der öffentliche Knotenpunkt eines Nutzers auf der Plattform. Es verbindet seine Aktivitäten, sein Trust-Signal und seinen Beitrag zur Community.
22.3.1 Öffentlicher Teil

IDENTITÄT
> → Nutzername (kein Profilbild).
> → Kurze Bio – sehr kurz, kein langer Steckbrief.
> → Systemrollen-Abzeichen wenn vorhanden: Admin, Gutachter oder andere systemvergebene Funktionsrollen. Keine community-vergebenen Abzeichen.

AKZEPTANZ-BALKEN
> → Drei farblich unterschiedliche Balken direkt unter dem Nutzernamen: Systemakzeptanz (immer sichtbar), persönliche Akzeptanz (nur für eingeloggte Nutzer), Peer-Group-Akzeptanz (nur wenn ich Muster abonniert habe).

VERSTOSS-ZÄHLER
> → Drei Werte (Wahrheitsdebatten, Rechtsverstöße, Beschimpfungen). Nur sichtbar wenn der Nutzer das selbst aktiviert hat. Fehlt der Abschnitt, wird er nicht als null angezeigt.

WERKE UND AKTIVITÄT
> → Veröffentlichte narrative Werke mit Cover, Klappentext und Tags.
> → Veröffentlichte Wirkmodelle.
> → Gegenreden (als Autor und als Ziel).
> → Recyclings (als Basis genutzt / selbst recycelt).

AKZEPTANZMUSTER
> → Nur sichtbar wenn der Nutzer es veröffentlicht hat. Dann abonnierbar.

LESEHISTORIE UND ABONNIERTE MUSTER
> → Nutzer entscheidet selbst ob sichtbar. Default: privat.

22.3.2 Nicht-öffentlicher Teil (nur System und Admins)
> → Klarname und Kontaktinformationen – fließt in Systemakzeptanz ein.
> → Vollständige Moderationshistorie.
> → Vollständige Verstoß-Historie inkl. aufgehobener Verstöße.

22.3.3 Profilansicht eines anderen Nutzers
Wenn ein Nutzer das Profil einer anderen Person betrachtet, sieht er zusätzlich zwei private Elemente die nur er selbst sieht:
> → Persönliches Notizfeld: Freier Text, nur für den Betrachter selbst sichtbar. Kein Datenaustausch. Kein Einfluss auf andere Systemwerte. Zum Beispiel: Warum habe ich diese Person akzeptiert? Was weiß ich über ihre Arbeit?
> → Interaktionshistorie: Eine Zusammenfassung aller Berührungspunkte zwischen dem Betrachter und dem betrachteten Nutzer: Feedback-Aussprachen, Community-Diskussionen, Recycling-Verbindungen, Gegenreden.

## 22.4 Designprinzipien des Community-Systems

KLAR/UNKLAR STATT WAHR/UNWAHR
Der Diskursrahmen ist epistemisch fokussiert. Wahrheitsfragen werden nicht moderiert – sie werden als falsche Fragen behandelt und ausgegraut. Die richtige Antwort auf ein abgelehntes Axiom ist ein Gegenentwurf.

AKZEPTANZ STATT VERTRAUEN
Akzeptanz hat keine inhaltliche Konnotation. Sie beschreibt die Anerkennung als ernsthafter Diskursteilnehmer, unabhängig von inhaltlicher Übereinstimmung.

KEIN BLAME-GAME
Es gibt keine negative Markierung. Der Mindestwert ist null. Akzeptanz kann still zurückgezogen werden ohne Benachrichtigung.

ASYMMETRISCHE TRANSPARENZ
Wer akzeptiert wird, sieht nicht wer ihn akzeptiert. Wer aus einem Muster entfernt wird, erhält keine Benachrichtigung. Das verhindert soziale Schulden und koordinierte Akzeptanz-Kampagnen.

SYSTEMROLLEN STATT COMMUNITY-ABZEICHEN
Abzeichen beschreiben nur systemvergebene Funktionen (Admin, Gutachter). Keine community-vergebenen Status-Symbole.

DREISTUFIGE FARBKODIERUNG
Zensierte Inhalte sind farblich nach Kategorie unterschieden. Der Grund der Zensurentscheidung ist transparent. Jede Kategorie ist separat schaltbar.

TRANSPARENZ GILT AUCH FÜR DAS SYSTEM
Moderationsentscheidungen und ihre Aufhebung sind protokolliert und sichtbar.

## 22.5 Geparkte Themen
MODERATIONSREGELN IM DETAIL
⏸ Geparkt: Präzise Abgrenzung zwischen struktureller Kritik (klar/unklar) und Wahrheitsdebatte für Moderatoren. Grenzfälle und Präzedenzfälle.

SYSTEMAKZEPTANZ-GEWICHTUNG
⏸ Geparkt: Wie werden die drei Quellen der Systemakzeptanz gewichtet? Gleich oder unterschiedlich?

KONSEQUENZEN HOHER/NIEDRIGER SYSTEMAKZEPTANZ
⏸ Geparkt: Aktuell rein informativ. Soll sich das ändern?

SPAM- UND BOT-SCHUTZ
⏸ Geparkt: Wie werden automatisierte Akzeptanz-Kampagnen erkannt und verhindert?

MODERATION BEI GUTACHTER-AUSFALL
⏸ Geparkt: Was passiert wenn kein Gutachter verfügbar ist?

PROFILDEAKTIVIERUNG UND -LÖSCHUNG
⏸ Geparkt: Was passiert mit Werken, Wirkmodellen und Community-Beiträgen wenn ein Nutzer seinen Account löscht?
