# Konzept: Original mit optionalen QoL-Erweiterungen

Stand: 30. Oktober 2026. Arbeitskonzept, kein Implementierungsauftrag.
Ein endgültiger Name für den Hack ist noch nicht festgelegt.

## Leitidee

Die deutsche Pokémon-Rot-/Blau-GBC-Fassung bleibt in Welt, Handlung,
Atmosphäre und Kampfmechanik dem Original treu. Vor einem neuen Spiel wird
zwischen **Classic** und **Erweitert (QoL)** gewählt. Es gibt keine neue Region
und keine neue Hauptgeschichte als Bestandteil dieses Konzepts.

**An der Gen-1-Kampfmechanik wird nichts geändert.** Dazu gehören auch die
bekannten Kampfeigenheiten und Fehler. Moderne Typen, Fähigkeiten und eine
neue physisch/spezielle Schadensaufteilung sind nicht vorgesehen.

**Die Pokémon-Movesets beziehungsweise Attacken-Lernlisten sollen aus Pokémon
Gelb übernommen werden – in Classic und Erweitert gleichermaßen.** Das ist eine
bewusste Ausnahme von der Rot-/Blau-Originaltreue in Classic und verändert die
Lerndaten, nicht die Gen-1-Kampfregeln oder deren Eigenheiten. Diese Änderung
ist vorerst nur geplant, nicht implementiert. Bei der Umsetzung sind
Startattacken, Level-up-Lernlisten und TM-/VM-Kompatibilität mit Gelb
abzugleichen; besondere Begegnungsattacken wie Surfer bei dem seltenen
Kraftwerk-Pikachu bleiben als eigener Konzeptpunkt erhalten.

Weniger umständliche Bedienung und zusätzliche Beschaffungswege sollen die
ursprünglichen Konsequenzen verpasster Chancen nicht aufheben.

## Modi und Geheimmenü

- Classic spielt weitestgehend wie das Original, mit Junge-/Green-Auswahl.
- Größerer Beutel, größeres PC-Item-Lager und die Movesets aus Pokémon Gelb gelten ausdrücklich in beiden Modi.
- Vor dem Spielstart wird der Modus gewählt und im Spielstand gespeichert.
- Der Modus soll jederzeit über das Geheimmenü wechselbar sein.
- Bereits erhaltene Pokémon, Items und Fortschritte bleiben beim Wechsel erhalten.
  Beispielsweise verschwindet ein in Erweitert gefangenes Mew nicht in Classic.
- Erweiterte Inhalte werden in Classic deaktiviert beziehungsweise pausiert.
  Übergänge müssen sicher bleiben, etwa beim Umschalten an Bord der M.S. Anne.
- Unabhängig vom Modus gewählte Komfortoptionen bleiben beim Moduswechsel erhalten.
- Änderungen werden über das normale Speichern im Spielstand gesichert.

Der vorhandene Zugang zum Geheimmenü bleibt die Grundlage:
**Start → OPTION → Select ungefähr drei Sekunden halten, dann loslassen.**

Geplante Menüpunkte:

| Menüpunkt | Auswahl | Gültigkeit |
| --- | --- | --- |
| Spielmodus | Classic / Erweitert | Im laufenden Spiel wechselbar |
| Spielfigur | Junge / Green | Unabhängig vom Modus |
| Schnelle Heilung und kürzere Wiederholungstexte | An / Aus | Unabhängig vom Modus |
| VM-Animationen überspringen | An / Aus | Unabhängig vom Modus |
| Zurück | Menü schließen | — |

Standardwerte der neuen Schalter und die endgültige Menügestaltung sind offen.

## Vereinbarte Features

| Feature | Classic | Erweitert | Festgelegtes Verhalten |
| --- | --- | --- | --- |
| Junge-/Green-Auswahl | Ja | Ja | Vorhandene Auswahl und laufender Sprite-Wechsel bleiben erhalten. |
| Größerer Beutel | Ja | Ja | 30 Plätze (umgesetzt). |
| Größeres PC-Item-Lager | Ja | Ja | 60 Plätze (umgesetzt). |
| Laufschuhe | Nein | Ja | Laufen ermöglichen; Taste, Freischaltung und erlaubte Orte noch festlegen. |
| Kampf gegen Professor Eich | Nein | Ja | Nach jedem Top-Vier-Sieg einmal verfügbar, danach bis zum nächsten Top-Vier-Sieg gesperrt. Ein Sieg über Eich gibt einen zufälligen Starter als Preis. |
| Tausch-zurück-Trainer | Nein | Ja | In Eichs Labor: testet ein zuvor wackeliges Linkkabel. Tauscht ein Pokémon und gibt es sofort zurück; ermöglicht Tauschentwicklungen ohne externen Tauschpartner. |
| Alle 151 Pokémon erhältlich | Nein | Ja | Jede Art soll ohne externen Tausch in einem Spielstand erhältlich sein. Einmal pro Art genügt; keine Fanggarantie. |
| Wiederverwendbare TMs | Nein | Ja | TMs werden beim Einsatz nicht verbraucht. |
| Rückkehr der M.S. Anne | Nein | Ja | Kehrt nach jedem Top-Vier-Sieg zurück. Nach dem Verlassen fährt sie wieder ab; für die nächste Rückkehr sind die Top Vier erneut zu besiegen. |
| Attacken-Helfer | Nein | Ja | Zwei neue NPCs: einer verlernt VMs, einer erinnert Attacken. Standorte und Bedingungen offen. |
| Kontextabhängige VMs | Nein | Ja | Zerschneider, Stärke und Surfer per A am passenden Hindernis aktivieren, wenn ein Team-Pokémon die VM beherrscht. Ordenvoraussetzungen bleiben erhalten. |
| Größere Münzkäufe | Nein | Ja | In der Spielhalle mehr Münzen auf einmal kaufen. Mengen und Preise offen. |
| Fangsymbol bei wilden Pokémon | Nein | Ja | Anzeigen, ob die Art bereits gefangen wurde. |
| Attacken-Lernlisten aus Pokémon Gelb | Ja | Ja | Gelb als gemeinsame Moveset-Grundlage; bisher nur geplant. Gen-1-Kampfmechanik unverändert. |
| EP-Leiste | Nein | Ja | Vorhandene EP-Leiste in Erweitert beibehalten, in Classic ausblenden. |
| Hinweis auf volle Box | Nein | Ja | Nur ein Hinweis; kein automatischer Boxwechsel. |
| Registrierbares Basis-Item | Nein | Ja | Ein Basis-Item auf Select legen, z. B. Fahrrad oder Angel. Außerhalb des Optionsmenüs direkt verwendbar. |
| Schutz erneut verwenden | Nein | Ja | Nach Ablauf anbieten, ein weiteres vorhandenes Exemplar einzusetzen. |
| Schnelle Heilung / kürzere Wiederholungstexte | Optional | Optional | Separater Schalter im Geheimmenü, unabhängig vom Modus. |
| VM-Animationen überspringen | Optional | Optional | Separater Schalter im Geheimmenü, unabhängig vom Modus. |
| Kleine Gerüchte über Geheimnisse | Nein | Ja | Wenige passende NPC-Hinweise, ohne die Lösung ausdrücklich zu verraten. Ausgestaltung später. |

Die vorgeschlagene Auslösung des Box-Hinweises ist noch zu bestätigen:
Nach dem Fang, der die aktuelle Box füllt, einmalig einen Gedanken anzeigen,
z. B. „Ich sollte meine Pokémon-Box prüfen. Vielleicht ist sie schon voll …“.
Die ursprüngliche Beschränkung bei gleichzeitig vollem Team und voller Box bleibt.

## Beschaffungswege für alle 151 Pokémon

Es reicht, jede Art einmal erhalten zu können. Wiederholbare Quellen sind kein
zusätzliches Ziel; die folgenden ausdrücklich vorgesehenen Quellen bleiben
Bestandteil des Konzepts.

| Gruppe | Vorgesehener Weg |
| --- | --- |
| Editionsexklusive Pokémon | Begegnungstabellen und Fundorte von Rot und Blau zusammenführen, möglichst unter Erhalt der gewohnten Fundorte. Raten und Verteilung später festlegen. |
| Tauschentwicklungen | Tausch-zurück-Trainer in Eichs Labor. |
| Amonitas und Kabuto | Auf der tiefsten Ebene der Azuria-Höhle **lebend angeln**. Keine zusätzliche Wiederbelebung nötig. Angel und Begegnungsraten offen. |
| Aerodactyl | Einmalig über den ursprünglichen Altbernstein und die Wiederbelebung auf der Zinnoberinsel. Kein zusätzlicher Fundort erforderlich. |
| Evoli sowie die Kampf-Pokémon aus dem Karate-Dojo | Als Preise in der Spielhalle erhältlich. Preise und genaue Angebotsgestaltung offen. |
| Starter | Zufälliger Preis nach einem Sieg über Eich. Genaue Zufallsverteilung offen. |
| Entwicklungssteine | Ausreichend, aber nicht unnötig großzügig verfügbar: Einkaufszentrum und gegebenenfalls zusätzliche Fundorte. Den tatsächlichen Bedarf prüfen. |
| Mew | Einmaliges Geheimnis beim Lastwagen im Hafen; Ablauf siehe unten. |
| Surfer-Pikachu | Sehr seltene wilde Begegnung **im Kraftwerk**, nicht im Wasser davor. Es gehört zu den Elektro-Pokémon dort; Surfer erklärt augenzwinkernd, wie es hingelangt ist. |

**Keine Wiederbegegnungen für verpasste einmalige Pokémon.** Insbesondere
legendäre Pokémon erscheinen nach Besiegen oder Verpassen nicht erneut.
Weitere Top-Vier-Siege setzen diese Begegnungen nicht zurück.
„Alle erhältlich“ bedeutet, dass alle nötigen Wege vorhanden sind, nicht,
dass Fehlentscheidungen oder Pech rückgängig gemacht werden.

## Mew unter dem Lastwagen

### Zugang

Wenn die M.S. Anne nach einem Top-Vier-Sieg zurückkehrt, soll der Hafen wieder
regulär zugänglich sein. Mit Surfer gelangt man zum Lastwagen. Glitches sind
für diesen Weg nicht vorgesehen.

Vorderseite und Heck sind die beiden untersuchbaren Versteckpunkte.
Die tatsächliche Tile-Anordnung und die Interaktionsflächen sind bei der
späteren Umsetzung zu prüfen; „zwei Kacheln“ ist bisher eine Vermutung.

### Versteckspiel

1. **Erste Untersuchung:** Egal welche Seite angesprochen wird, der erste
   Versuch scheitert garantiert. Etwas flüchtet zur gegenüberliegenden Seite.
2. **Dieselbe Seite erneut:** Nur ein Hinweis, dass es noch am anderen Ende
   sitzt. Kein neuer Zufallsversuch.
3. **Gegenüberliegende Seite untersuchen:** Ab jetzt hat jeder gültige
   Seitenwechsel eine **Chance von 1:4**, Mew hervorzulocken.
4. **Fehlschlag:** Mew flüchtet wieder zur gegenüberliegenden Seite.
5. **Erfolg:** Mew kommt hervor und der einmalige Kampf beginnt.

Die erste garantierte Flucht sowie die aktuelle Versteckseite werden über
Gebietswechsel und Speichern hinweg erhalten. Weggehen setzt das Rätsel
nicht zurück. Nach einem Fang, Besiegen oder der Flucht des Spielers ist die
Begegnung verbraucht. Es gibt keinen erneuten Versuch nach dem Kampf.

Vorläufige Texte, noch redaktionell abzustimmen:

- Erste Flucht: „Etwas huscht unter dem Wagen zur anderen Seite!“
- Gleiche Seite: „Es scheint sich noch immer am anderen Ende zu verstecken …“
- Erfolg: „Ein Pokémon kommt unter dem Wagen hervor!“

Level und Attacken von Mew sind noch offen.

## Gerüchte und neue Dialoge

Die Idee ist beschlossen; Sprecher, Standorte und endgültige Texte bleiben offen.
Hinweise sollen neugierig machen und Entdeckungen belohnen, keine Questmarker
oder ausdrückliche Schritt-für-Schritt-Lösungen liefern.

Unverbindliche Textideen:

- Surfer-Pikachu, eventuell im Pokémon-Center bei der Felshöhle:
  „Im Kraftwerk soll ein PIKACHU leben, das keine Angst vor Wasser hat.
  Seltsam, oder?“
- Lastwagen:
  „Am Hafen habe ich etwas unter einem alten Wagen verschwinden sehen.
  Als ich nachschauen wollte, war es plötzlich auf der anderen Seite …“
- Der Assistent in Eichs Labor erzählt von seinem reparierten Linkkabel und
  möchte mit einem sofortigen Rücktausch dessen Funktion testen.

## Noch nicht beschlossene Vorschläge

Die folgenden Ideen wurden genannt, aber bisher **nicht angenommen** und
gehören daher noch nicht zum vereinbarten Umfang:

- Beutel sortieren, zusätzliche Item-Kategorien und veränderte Stapelregeln.
- Freie Mengenwahl bei weiteren Käufen sowie beim Einlagern/Abheben im PC.
- Attackentyp, Stärke und Genauigkeit beim Erlernen anzeigen.
- Geeignete Pokémon beim Einsatz von Entwicklungssteinen hervorheben.
- Pokédex-Fundortanzeige um neue Begegnungsorte ergänzen, Geheimnisse ausgenommen.
- Eichs Dialog vor dem Kampf an den Pokédex-Fortschritt anpassen.

Bereits abgelehnt: automatischer Boxwechsel und erneutes Erscheinen besiegter
legendärer Pokémon. Änderungen an der Gen-1-Kampfmechanik sind ausgeschlossen.

## Offene Konzeptfragen vor der Umsetzung

- Namen und Beschreibungen der Modi, Standardwerte und genaue Menüführung.
- Sicherer Moduswechsel bei erweiterten Orten, Ereignissen und laufenden Zuständen,
  insbesondere auf der M.S. Anne; kein Löschen erworbener Inhalte.
- Abgleich weiterer vorhandener GBC-Erweiterungen mit dem Classic-Ziel.
- Weitere Anforderungen an Beutel und PC über die umgesetzten 30/60 Plätze hinaus.
- Laufschuhe: Bedienung, Freischaltung und Orte.
- Eich: Team, Level, Voraussetzungen, Dialog und Starter-Belohnungsverteilung.
- Neue Begegnungsraten, Surfer-Pikachu-Level und -Attacken, Preise in der Spielhalle.
- Welche Entwicklungssteine zusätzlich nötig sind und wo sie erhältlich werden.
- Attacken-Erinnerer: angebotene Attacken, Kosten und Standort; VM-Verlerner-Standort.
- Genaue Auslösung und Wiederholungssperre des Box-Hinweises.
- Mew-Level, Texte, technische Interaktionsflächen und sichere Hafen-Zugänglichkeit.
- Endgültige Gerüchte, Sprecher und Platzierung.

## Bestehende technische Grundlage

Junge-/Green-Auswahl, gespeicherte Figur und das versteckte Sprite-Menü sind
bereits umgesetzt. Beutel und PC-Item-Lager sind auf 30 beziehungsweise 60 Plätze
erweitert; alte 20/50-Spielstände werden beim Laden übernommen. Greens bisheriger Look mit brauner Palette bleibt erhalten;
der experimentelle grüne-Kleid-Commit wurde auf Wunsch zurückgenommen.
Details und Herkunft der Grafiken stehen in [green-sprites.md](green-sprites.md).

Die übrigen Punkte dieses Dokuments sind Planung und dürfen nicht als bereits
implementierte Funktionen verstanden werden. Die Implementierung der Inventarkapazitäten ist in [inventory-storage.md](inventory-storage.md) beschrieben.
