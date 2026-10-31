# Konzept: Original mit optionalen QoL-Erweiterungen

Stand: 31. Oktober 2026. Konzept und dokumentierter Umsetzungsstand.
Ein endgültiger Name für den Hack ist noch nicht festgelegt.

## Leitidee

Die deutsche Pokémon-Rot-/Blau-GBC-Fassung bleibt in Welt, Handlung,
Atmosphäre und Kampfmechanik dem Original treu. Vor einem neuen Spiel wird
zwischen **Classic** und **Erweitert (QoL)** gewählt. Es gibt keine neue Region
und keine neue Hauptgeschichte als Bestandteil dieses Konzepts.

**An der Gen-1-Kampfmechanik wird nichts geändert.** Dazu gehören auch die
bekannten Kampfeigenheiten und Fehler. Moderne Typen, Fähigkeiten und eine
neue physisch/spezielle Schadensaufteilung sind nicht vorgesehen.

**Die Pokémon-Movesets beziehungsweise Attacken-Lernlisten stammen jetzt aus
Pokémon Gelb – in Classic und Erweitert gleichermaßen.** Das ist eine
bewusste Ausnahme von der Rot-/Blau-Originaltreue in Classic und verändert die
Lerndaten, nicht die Gen-1-Kampfregeln oder deren Eigenheiten. Startattacken, Level-up-Lernlisten und TM-/VM-Kompatibilität sind umgesetzt
und mit Gelb abgeglichen; besondere Begegnungsattacken wie Surfer bei dem
seltenen Kraftwerk-Pikachu bleiben erhalten. Details: [yellow-learnsets.md](yellow-learnsets.md).

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
  Kartenbezogene Änderungen dürfen erst beim nächsten natürlichen Laden oder
  Gebietswechsel greifen; ein sofortiger Umbau des laufenden Gebiets ist nicht nötig.
- Unabhängig vom Modus gewählte Komfortoptionen bleiben beim Moduswechsel erhalten.
- Persistente Änderungen werden über das normale Speichern im Spielstand gesichert. Die temporäre Auswahl des Starter-Editors ist davon ausdrücklich ausgenommen.

Der vorhandene Zugang zum Geheimmenü bleibt die Grundlage:
**Start → OPTION → Select ungefähr drei Sekunden halten, dann loslassen.**

Menüpunkte:

| Menüpunkt | Auswahl | Gültigkeit |
| --- | --- | --- |
| Spielmodus | Classic / Erweitert | Im laufenden Spiel wechselbar |
| Spielfigur | Junge / Green | Unabhängig vom Modus |
| Schnelle Heilung und kürzere Wiederholungstexte | An / Aus | Unabhängig vom Modus |
| VM-Animationen überspringen | An / Aus | Unabhängig vom Modus |
| Starter-Editor (Seite 2) | ORIGINAL / 151 Pokémon-Arten | Umgesetzt: vor der ersten Starterwahl in Eichs Labor; temporär, in beiden Modi |
| Zurück | Menü schließen | — |

Select blättert im Geheimmenü zwischen zwei Seiten; unten rechts steht
S. 1/2 beziehungsweise S. 2/2. Seite 1 enthält Figur, Modus und VM-Animationen;
Seite 2 die schnelle Heilung und den Starter-Editor. ZURÜCK verlässt das gesamte Menü und behält
Änderungen beider Seiten. Voreinstellung:
VM-Animationen AN, schnelle Heilung AUS. Links/Rechts übernimmt sofort.
Der Starter-Editor nutzt Level 5 und die passenden Gelb-Attacken; Details:
[starter-editor.md](starter-editor.md).

## Vereinbarte Features

| Feature | Classic | Erweitert | Festgelegtes Verhalten |
| --- | --- | --- | --- |
| Junge-/Green-Auswahl | Ja | Ja | Vorhandene Auswahl und laufender Sprite-Wechsel bleiben erhalten. |
| Größerer Beutel | Ja | Ja | 30 Plätze (umgesetzt). |
| Größeres PC-Item-Lager | Ja | Ja | 70 Plätze (umgesetzt). |
| Laufschuhe | Nein | Ja | Umgesetzt: B halten für doppeltes normales Gehtempo, auch in Innenräumen. Kein Extra-Tempo beim Surfen, Fahrrad, Springen oder geskripteten Bewegungen. |
| Kampf gegen Professor Eich | Nein | Ja | Nach jedem Top-Vier-Sieg einmal verfügbar, danach bis zum nächsten Top-Vier-Sieg gesperrt. Ein Sieg über Eich gibt einen zufälligen Starter als Preis. |
| Arena-Rückkämpfe | Nein | Ja | Umgesetzt: nach jedem Top-Vier-Sieg jeder Leiter einmal; Originalteams auf Level 60–65, Giovanni zurück in seiner Arena. Details: [gym-rematches.md](gym-rematches.md). |
| Tausch-zurück-Trainer | Nein | Ja | Umgesetzt: rechter Assistent in Eichs Labor, nach der Starterwahl. Testet das zuvor wackelige Linkkabel; Pokémon wird sofort zurückgegeben und kann sich durch Tausch entwickeln. |
| Alle 151 Pokémon erhältlich | Nein | Ja | Umgesetzt und als Beschaffungsgraph geprüft: jede Art ohne externen Tausch in einem Spielstand erhältlich. Einmal pro Art genügt; keine Fanggarantie. Details: [obtainability.md](obtainability.md). |
| Wiederverwendbare TMs | Nein | Ja | Umgesetzt: TMs werden nach erfolgreichem Erlernen nicht verbraucht. Classic verbraucht sie weiterhin. |
| Rückkehr der M.S. Anne | Nein | Ja | Kehrt nach jedem Top-Vier-Sieg zurück. Nach dem Verlassen fährt sie wieder ab; für die nächste Rückkehr sind die Top Vier erneut zu besiegen. |
| Attacken-Helfer | Nein | Ja | Zwei neue NPCs: einer verlernt VMs, einer erinnert Attacken. Umgesetzt: kostenlos auf dem Deck der M.S. Anne nach dem ersten Top-Vier-Sieg. |
| Spezialhändler auf der M.S. Anne | Nein | Ja | Umgesetzt: erscheint nach dem ersten Top-Vier-Sieg wie die Attacken-Helfer; eigene Preise und unbegrenzter Vorrat. Details: [ship-merchant.md](ship-merchant.md). |
| Kontextabhängige VMs | Nein | Ja | Umgesetzt: Zerschneider, Stärke und Surfer per A und Ja/Nein am Hindernis aktivieren. Team-Attacke und ursprünglicher Orden nötig. Details: [context-field-moves.md](context-field-moves.md). |
| Größere Münzkäufe | Nein | Ja | In der Spielhalle mehr Münzen auf einmal kaufen. Umgesetzt: zusätzlich 500 Münzen für 10000 Geld. |
| Fangsymbol bei wilden Pokémon | Nein | Ja | Umgesetzt: vorhandenes Pokéball-Zeichen im Gegner-HUD nur in Erweitert, bei bereits gefangenen wilden Arten. Keine Anzeige bei Trainer-Pokémon oder unbekannten Geistern. |
| Attacken-Lernlisten aus Pokémon Gelb | Ja | Ja | Umgesetzt: Gelb als gemeinsame Moveset-Grundlage. Gen-1-Kampfmechanik unverändert. |
| EP-Leiste | Nein | Ja | Umgesetzt: EP-Leiste in Erweitert anzeigen; in Classic nur die blaue Füllung ausblenden, HUD und leere Leiste erhalten. EP-Gewinn bleibt unverändert. |
| Hinweis auf volle Box | Nein | Ja | Umgesetzt: Gedanke nach dem Fang, der die aktuelle Box füllt; kein automatischer Boxwechsel. Details: [box-reminder.md](box-reminder.md). |
| Registrierbares Basis-Item | Nein | Ja | Umgesetzt: im Beutel registrieren, außerhalb der Menüs per Select benutzen. Details: [registered-item.md](registered-item.md). |
| Schutz erneut verwenden | Nein | Ja | Umgesetzt: nach Ablauf bei vorhandenem Vorrat dieselbe Schutzart erneut anbieten; Ja/Nein. Details: [repeat-repel.md](repeat-repel.md). |
| Schnelle Heilung / kürzere Wiederholungstexte | Optional | Optional | Umgesetzt: Seite 2, schnelle Heilung mit kurzen Pokémon-Center-Texten; unabhängig vom Modus. |
| VM-Animationen überspringen | Optional | Optional | Umgesetzt: auf Seite 1 des Geheimmenüs „VM-Animationen“ auf Aus stellen; unabhängig vom Modus. |
| Kleine Gerüchte über Geheimnisse | Nein | Ja | Wenige passende NPC-Hinweise, ohne die Lösung ausdrücklich zu verraten. Ausgestaltung später. |

Der Box-Hinweis erscheint nach dem Fang, der die aktuelle Box füllt, als Gedanke,
z. B. „Ich sollte meine Pokémon-Box prüfen. Vielleicht ist sie schon voll …“.
Die ursprüngliche Beschränkung bei gleichzeitig vollem Team und voller Box bleibt.

## Präzisierte Regeln für Moduswechsel und wiederkehrende Ereignisse

### Moduswechsel als Power-User-/Debug-Funktion

Der Wechsel im Geheimmenü muss nicht alle laufenden Zustände sofort anpassen.
Die Moduswahl wird gespeichert; einfache Regeln wie TM-Verbrauch können beim
nächsten Einsatz gelten. Karten, NPCs und Begegnungstabellen dürfen den neuen
Modus beim nächsten natürlichen Laden beziehungsweise Gebietswechsel übernehmen.
Laufende Dialoge und Ereignisse dürfen unter ihren bisherigen Bedingungen enden.
Ein Wechsel auf der M.S. Anne muss das Schiff daher nicht sofort entfernen oder
den Spieler versetzen. Der reguläre Ausgang bleibt nutzbar; der Zugang wird beim
nächsten regulären Betreten geprüft.

Ein Moduswechsel **setzt keine Ereignisse oder Belohnungen zurück**. Classic
pausiert beziehungsweise verbirgt die erweiterten Zugänge. Beim Zurückwechseln
bleiben Verfügbarkeit, verbrauchte Begegnungen und ausstehende Belohnungen erhalten.

### Eich: Verfügbarkeit und spätere Abholung

- Nach einem Top-Vier-Sieg ist höchstens **ein Eich-Kampf** verfügbar.
- Mehrere Top-Vier-Siege ohne zwischenzeitlichen Eich-Kampf sammeln keine
  zusätzlichen Kämpfe an. Die Verfügbarkeit bleibt eine einzelne Gelegenheit.
- Nach dem abgeschlossenen Eich-Kampf ist diese Gelegenheit verbraucht; ein
  weiterer Top-Vier-Sieg kann wieder einen Kampf freischalten.
- Der zufällige Starter als Belohnung wird **beim Sieg über Eich bestimmt**.
- Ist das Team voll, weist Eich in einem passenden Kommentar darauf hin und
  hält die Belohnung zur späteren Abholung bereit. Der Sieg geht nicht verloren.
- Die ausstehende Pokémon-Art wird gespeichert. Erneutes Ansprechen, Laden oder
  späteres Abholen würfelt den Preis nicht neu aus.
- Ein weiterer Top-Vier-Sieg überschreibt keine ausstehende Belohnung.

Für die spätere Umsetzung werden daher Kampf-Verfügbarkeit und ausstehende
Belohnungs-Art getrennt gespeichert; dafür ist im Feature-Speicher Reserve
vorhanden. Die genaue Art, wie ein erneut verfügbarer Kampf mit einer noch nicht
abgeholten Belohnung zusammenspielt, ist noch festzulegen. Eine offene Belohnung
darf dabei weder verloren gehen noch überschrieben werden.

### M.S. Anne: ursprünglichen Abreiseablauf wiederverwenden

- Nach einem Top-Vier-Sieg ist höchstens **ein erneuter Schiffsbesuch** verfügbar.
- Mehrere Top-Vier-Siege ohne Besuch sammeln keine zusätzlichen Besuche an.
- Es wird der ursprüngliche Abreiseablauf wiederverwendet:
  **Spieler verlässt das Schiff → Schiff fährt aus dem Hafen → Spieler verlässt
  den Hafen.**
- Wechsel zwischen Kabinen, Decks und anderen Innenbereichen verbrauchen keinen
  Besuch. Maßgeblich ist das Verlassen des Schiffs im ursprünglichen Ablauf.
- Nach der Abreise ist der Besuch verbraucht. Ein weiterer Top-Vier-Sieg kann die
  Rückkehr freischalten.
- Bei der Umsetzung ist zu prüfen, welche vorhandenen Zugangs-/Abreiseflags
  gezielt zurückgesetzt werden müssen, damit das alte Ereignis erneut funktioniert.

Mew bleibt davon unabhängig einmalig: Weder ein erneuter Schiffsbesuch noch ein
Top-Vier-Sieg oder Moduswechsel setzt eine verbrauchte Mew-Begegnung zurück.
Sein Versteckspiel behält den gespeicherten Zustand über Gebietswechsel und Laden.

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

## Umgesetzt: Starter-Editor im Geheimmenü

Der Editor auf **Seite 2** des Geheimmenüs kann
vor der ersten Starterwahl in **Professor Eichs Labor** ein Ersatz-Pokémon
festlegen. Die Auswahl soll jederzeit in dieser Phase direkt im Spiel
möglich sein, ohne vorab eine ROM zu konfigurieren. Nach abgeschlossener
Starterwahl ist keine nachträgliche Team-Ersetzung durch diesen Editor vorgesehen.

### Verhalten

- Der Spieler wählt im Editor eine Pokémon-Art als temporären Ersatz, z. B. Simsala.
- Danach wird ganz normal eine der ursprünglichen Starter-Kugeln gewählt.
- **Die Kugelwahl bestimmt weiterhin den ursprünglichen Spielverlauf:**
  Dialoge, Starter-Flags, Rivalenwahl und nachfolgende Skripte laufen so,
  als hätte der Spieler dieses ursprüngliche Starter-Pokémon genommen.
- Nur das tatsächlich erhaltene Team-Pokémon wird durch die Editor-Art ersetzt.
  Es ist ein echtes Pokémon dieser Art mit dazu passenden Pokémon-Daten,
  nicht lediglich ein anderer Name oder Sprite für den ursprünglichen Starter.
- Beispiel: **Editor auf Simsala → Schiggy-Kugel wählen → Simsala im Team**;
  die Story behandelt die Wahl weiterhin als Schiggy und der Rivale erhält
  entsprechend der normalen Rot-/Blau-Auswahl Bisasam.
- Ohne aktivierte Ersatz-Auswahl funktioniert die Starterwahl unverändert.

### Lebensdauer der Auswahl

Die **Editor-Voreinstellung wird nicht im Spielstand gespeichert** und braucht
keinen Platz im persistenten Feature-Speicher. Sie muss nach einem Neustart
oder erneuten Laden wieder gewählt werden. Nach der einmaligen Übergabe des
Ersatz-Starters gilt die temporäre Auswahl als verbraucht.

Das bereits erhaltene Simsala bleibt selbstverständlich ein normales Mitglied
des Teams und wird regulär gespeichert. Nur die noch nicht angewendete
Editor-Voreinstellung ist flüchtig; beim Laden wird kein vorhandenes Pokémon
wieder gegen den ursprünglichen Starter ausgetauscht.

Umgesetzt in Classic und Erweitert: Links/Rechts wählt ORIGINAL oder eine der
151 Arten in Pokédex-Reihenfolge. Das Ersatz-Pokémon wird regulär auf Level 5
mit den zur Art und zum Level passenden Gelb-Attacken erzeugt. Es gibt keine
Editorfelder für Level, Werte, Items oder Teams. Details und Tests:
[starter-editor.md](starter-editor.md).

## Umgesetzt: Rückkämpfe gegen die Arenaleiter

Nur in Erweitert: Nach jedem Top-Vier-Sieg ist jeder Leiter einmal erneut
herausforderbar. Die Gelegenheiten sammeln sich nicht an. Nein behält die
Gelegenheit, Ja verbraucht sie beim Annehmen, auch bei einer Niederlage.
Originale Arten, Reihenfolge und Teamgröße bleiben gleich; nur die Level
werden auf 60–65 angehoben. Die ursprünglichen Signaturattacken bleiben erhalten.
Es gibt normales Preisgeld, aber keine erneuten Orden oder Arena-TMs.

Giovanni kehrt nach dem Champion-Sieg in seine Arena zurück und erklärt seine
Zeit im Rückzug und Training. Der ursprüngliche erste Story-Ablauf bleibt
bestehen. Alle Leiter haben eine eigene Einladung beziehungsweise Motivation.
Teams, Dialogkonzept, Speicherregeln und Testumfang:
[gym-rematches.md](gym-rematches.md).

## Umgesetzt: Spezialhändler auf der M.S. Anne

Der zusätzliche Händler erscheint in Erweitert nach dem ersten Top-Vier-Sieg
auf dem Deck wie die beiden Attacken-Helfer. Er verkauft bei jedem erneuten
Besuch AP-Plus (20000), Top-Äther (3000), Elixier (5000), Top-Elixier (10000)
und Mondstein (5000). Der Vorrat ist unbegrenzt; jeder Kauf wird bestätigt.
Andere Entwicklungssteine bleiben im ursprünglichen Kaufhaus erhältlich.
Itemwirkungen und normale Ladenpreise bleiben unverändert.
Details und Testumfang: [ship-merchant.md](ship-merchant.md).

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
- Geeignete natürliche Ladepunkte für Modusänderungen; kein sofortiger Umbau
  laufender Karten nötig und kein Löschen erworbener Inhalte.
- Abgleich weiterer vorhandener GBC-Erweiterungen mit dem Classic-Ziel.
- Weitere Anforderungen an Beutel und PC über die umgesetzten 30/70 Plätze hinaus.
- Gegebenenfalls später gewünschte Einschränkungen oder Freischaltung der bereits umgesetzten Laufschuhe.
- Welche Entwicklungssteine zusätzlich nötig sind und wo sie erhältlich werden.
- Endgültige Gerüchte, Sprecher und Platzierung.

## Bestehende technische Grundlage

Junge-/Green-Auswahl, gespeicherte Figur und das versteckte Sprite-Menü sind
bereits umgesetzt. Beutel und PC-Item-Lager sind auf 30 beziehungsweise 70 Plätze
erweitert; alte 20/50- und 30/60-Spielstände werden beim Laden übernommen. Greens bisheriger Look mit brauner Palette bleibt erhalten;
der experimentelle grüne-Kleid-Commit wurde auf Wunsch zurückgenommen.
Details und Herkunft der Grafiken stehen in [green-sprites.md](green-sprites.md).

Der Umsetzungsstand der Champion-Ereignisse, seltenen Begegnungen, Spielhalle
und Attacken-Helfer steht in [postgame-features.md](postgame-features.md).
Weitere Konzeptpunkte bleiben geplant. Die Inventarkapazitäten sind in
[inventory-storage.md](inventory-storage.md) beschrieben.


Für künftige Features ist bereits ein versionierter Speicherbereich mit 512 Bytes
und eigener Prüfsumme vorbereitet. Er reserviert Modus, Komfortoptionen,
registriertes Item sowie Zustände/Zähler für Eich, M.S. Anne, Mew, Box-Hinweis
und weitere Ereignisse. Das aktiviert die geplanten Features noch nicht.
Neue Features sollen vorhandene Spielstände migrieren beziehungsweise ihre
Startzustände aus dem bisherigen Fortschritt ableiten. Details: [save-format.md](save-format.md).


Moduswahl beim neuen Spiel und im Geheimmenü, modusabhängige EP-Leiste und
Laufschuhe sind inzwischen umgesetzt. Bestehende Spielstände übernehmen den
gespeicherten Modus; frühere Spielstände ohne Auswahl starten in Classic.
Ein Neustart ist für den Wechsel zu Erweitert nicht erforderlich. Tausch-zurück-Trainer und wiederverwendbare TMs sind ebenfalls umgesetzt.
Weitere Konzeptpunkte bleiben geplant. Details: [gameplay-modes.md](gameplay-modes.md).


## Ergänzte Festlegungen: Eich, Begegnungen und Attacken-Helfer

- Eich kämpft im Labor aus Erinnerung an seine Zeit als junger Trainer. Team
  und Level stammen aus seinen bereits vorhandenen Trainerdaten. Die drei
  Starter-Belohnungen sind gleich wahrscheinlich. Solange ein Geschenk offen
  ist, kämpft er nicht erneut und ein Top-Vier-Sieg schaltet ihn nicht wieder
  frei. Das Geschenk kann später mit einem passenden Kommentar abgeholt werden.
- Seltene Amonitas, Kabuto und Surfer-Pikachu: je 1 % pro Art,
  Level passend zum Gebiet. Fossil-Pokémon nur mit der besten Angel (Superangel).
- Mew: Level 30, reguläre bis dahin erlernte Attacken.
- Spielhallenpreise orientieren sich an Blau; die größte Münzkaufmenge wird
  verzehnfacht, bei gleichem Preis pro Münze.
- Beide Attacken-Helfer stehen auf dem Deck der M.S. Anne und arbeiten kostenlos.
  Sie kamen, um den neuen Champion kennenzulernen. Nun helfen sie ihm mit ihren
  besonderen Begabungen. Der Erinnerer berücksichtigt auch frühere Level-Attacken
  der Vorentwicklungen.
- Im Geheimmenü markieren leere Pfeile die gespeicherten Werte, der volle Pfeil
  zeigt den aktuellen Auswahlcursor.

Die zuletzt präzisierten Features sind umgesetzt; genaue Level, Preise,
Freischaltungen und Testumfang: [postgame-features.md](postgame-features.md).
