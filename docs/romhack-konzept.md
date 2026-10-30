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
  Kartenbezogene Änderungen dürfen erst beim nächsten natürlichen Laden oder
  Gebietswechsel greifen; ein sofortiger Umbau des laufenden Gebiets ist nicht nötig.
- Unabhängig vom Modus gewählte Komfortoptionen bleiben beim Moduswechsel erhalten.
- Persistente Änderungen werden über das normale Speichern im Spielstand gesichert. Die temporäre Auswahl des Starter-Editors ist davon ausdrücklich ausgenommen.

Der vorhandene Zugang zum Geheimmenü bleibt die Grundlage:
**Start → OPTION → Select ungefähr drei Sekunden halten, dann loslassen.**

Geplante Menüpunkte:

| Menüpunkt | Auswahl | Gültigkeit |
| --- | --- | --- |
| Spielmodus | Classic / Erweitert | Im laufenden Spiel wechselbar |
| Spielfigur | Junge / Green | Unabhängig vom Modus |
| Schnelle Heilung und kürzere Wiederholungstexte | An / Aus | Unabhängig vom Modus |
| VM-Animationen überspringen | An / Aus | Unabhängig vom Modus |
| Starter-Editor (z. B. Seite 2) | Ersatz-Pokémon wählen / deaktivieren | Nur bei der ersten Starterwahl in Eichs Labor; Auswahl temporär, Modusverfügbarkeit noch offen |
| Zurück | Menü schließen | — |

Standardwerte der neuen Schalter und die endgültige Menügestaltung sind offen.

## Vereinbarte Features

| Feature | Classic | Erweitert | Festgelegtes Verhalten |
| --- | --- | --- | --- |
| Junge-/Green-Auswahl | Ja | Ja | Vorhandene Auswahl und laufender Sprite-Wechsel bleiben erhalten. |
| Größerer Beutel | Ja | Ja | 30 Plätze (umgesetzt). |
| Größeres PC-Item-Lager | Ja | Ja | 70 Plätze (umgesetzt). |
| Laufschuhe | Nein | Ja | Umgesetzt: B halten für doppeltes normales Gehtempo, auch in Innenräumen. Kein Extra-Tempo beim Surfen, Fahrrad, Springen oder geskripteten Bewegungen. |
| Kampf gegen Professor Eich | Nein | Ja | Nach jedem Top-Vier-Sieg einmal verfügbar, danach bis zum nächsten Top-Vier-Sieg gesperrt. Ein Sieg über Eich gibt einen zufälligen Starter als Preis. |
| Arena-Rückkämpfe | Nein | Ja | Geplant: nach jedem Top-Vier-Sieg jeder Leiter einmal erneut herausforderbar; Gelegenheiten sammeln sich nicht an. Teams und Level noch offen. |
| Tausch-zurück-Trainer | Nein | Ja | Umgesetzt: rechter Assistent in Eichs Labor, nach der Starterwahl. Testet das zuvor wackelige Linkkabel; Pokémon wird sofort zurückgegeben und kann sich durch Tausch entwickeln. |
| Alle 151 Pokémon erhältlich | Nein | Ja | Jede Art soll ohne externen Tausch in einem Spielstand erhältlich sein. Einmal pro Art genügt; keine Fanggarantie. |
| Wiederverwendbare TMs | Nein | Ja | TMs werden beim Einsatz nicht verbraucht. |
| Rückkehr der M.S. Anne | Nein | Ja | Kehrt nach jedem Top-Vier-Sieg zurück. Nach dem Verlassen fährt sie wieder ab; für die nächste Rückkehr sind die Top Vier erneut zu besiegen. |
| Attacken-Helfer | Nein | Ja | Zwei neue NPCs: einer verlernt VMs, einer erinnert Attacken. Umgesetzt: kostenlos auf dem Deck der M.S. Anne nach dem ersten Top-Vier-Sieg. |
| Spezialhändler auf der M.S. Anne | Nein | Ja | Geplant: erscheint nach dem ersten Top-Vier-Sieg wie die Attacken-Helfer; verkauft sonst nicht kaufbare Items. Sortiment und Preise noch abzustimmen. |
| Kontextabhängige VMs | Nein | Ja | Zerschneider, Stärke und Surfer per A am passenden Hindernis aktivieren, wenn ein Team-Pokémon die VM beherrscht. Ordenvoraussetzungen bleiben erhalten. |
| Größere Münzkäufe | Nein | Ja | In der Spielhalle mehr Münzen auf einmal kaufen. Umgesetzt: zusätzlich 500 Münzen für 10000 Geld. |
| Fangsymbol bei wilden Pokémon | Nein | Ja | Anzeigen, ob die Art bereits gefangen wurde. |
| Attacken-Lernlisten aus Pokémon Gelb | Ja | Ja | Gelb als gemeinsame Moveset-Grundlage; bisher nur geplant. Gen-1-Kampfmechanik unverändert. |
| EP-Leiste | Nein | Ja | Umgesetzt: EP-Leiste in Erweitert anzeigen; in Classic nur die blaue Füllung ausblenden, HUD und leere Leiste erhalten. EP-Gewinn bleibt unverändert. |
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

## Geplanter Starter-Editor im Geheimmenü

Ein zusätzlicher Editor, beispielsweise auf **Seite 2** des Geheimmenüs, soll
vor der ersten Starterwahl in **Professor Eichs Labor** ein Ersatz-Pokémon
festlegen können. Die Auswahl soll jederzeit in dieser Phase direkt im Spiel
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

Noch offen: endgültige Seitengestaltung und Artenauswahl, Verfügbarkeit in
Classic/Erweitert sowie die genauen Erzeugungswerte (Level, Startattacken nach
der geplanten Gelb-Grundlage usw.). Der bisher gewünschte Umfang ist die Wahl
der Pokémon-Art, kein allgemeiner Editor für Level, Werte, Items oder Teams.
Dieses Feature ist **nur geplant, noch nicht implementiert**.

## Geplant: Rückkämpfe gegen die Arenaleiter

Nur im erweiterten Modus. Nach jedem Top-Vier-Sieg kann jeder der acht
Arenaleiter erneut herausgefordert werden. Jeder Leiter hat seine eigene
Verfügbarkeit; ein Rückkampf bei Rocko verbraucht beispielsweise nicht Mistys
Gelegenheit. Mehrere Top-Vier-Siege sammeln keine zusätzlichen Kämpfe an.
Classic pausiert die zusätzlichen Angebote, ohne die Zustände zurückzusetzen.
Die Verfügbarkeit soll gespeichert werden und vorhandene Spielstände weiter
unterstützen. Die ursprünglichen ersten Arenakämpfe bleiben erhalten.

Dialogideen vor der Herausforderung, noch keine endgültigen Bildschirmtexte:

| Leiter | Motivation / Dialogidee |
| --- | --- |
| Rocko | „Seit unserem ersten Kampf ist viel passiert. Zeig mir, wie stark Du geworden bist!“ |
| Misty | „Du bist jetzt CHAMPION? Dann will ich sehen, ob Du auch gegen meine Strömung bestehst!“ |
| Major Bob | „Diese Niederlage lässt mir keine Ruhe, Soldat! Zeit für eine Revanche!“ |
| Erika | „Dein Können ist seit unserem letzten Treffen aufgeblüht. Darf ich es noch einmal erleben?“ |
| Koga | „Ein wahrer Ninja hört nie auf zu trainieren. Prüfen wir, was wir beide gelernt haben!“ |
| Sabrina | „Ich habe vorausgesehen, dass Du zurückkommst. Den Ausgang unseres Kampfes sehe ich diesmal nicht klar.“ |
| Pyro | „Neue Frage: Wie schlägt sich ein CHAMPION gegen mein Feuer? Finden wir es heraus!“ |
| Giovanni | Vorschlag bei einer möglichen Rückkehr: „Ich habe mich zurückgezogen, um meine Schwäche zu verstehen. Zeig mir, ob ich daraus gelernt habe.“ |

Noch zu entscheiden:

- Teams und Level der Rückkämpfe; verstärkte Teams sind ein Vorschlag.
- Wird die Gelegenheit beim Kampfbeginn oder erst bei einem Sieg verbraucht?
- Preisgeld und weitere Belohnungen. Vorschlag: keine erneuten Orden oder
  ursprünglichen Arena-TMs.
- Giovanni verschwindet im Original nach seiner Niederlage. Für den achten
  Rückkampf braucht es eine ausdrücklich festgelegte Rückkehr oder einen
  anderen Austragungsort; sein normaler Story-Abgang soll nicht versehentlich
  rückgängig gemacht werden.

Dieses Feature ist **nur geplant, noch nicht implementiert**.

## Geplant: Spezialhändler auf der M.S. Anne

Ein weiterer NPC erscheint im erweiterten Modus nach dem ersten Top-Vier-Sieg
auf der M.S. Anne, unter denselben Freischaltbedingungen wie die beiden
Attacken-Helfer. Er ist bei den wiederkehrenden Schiffsbesuchen erreichbar.
In Classic erscheint sein zusätzliches Angebot nicht.

Er verkauft nützliche Items, die im Original nicht regulär gekauft werden
können. Gewünscht sind AP-Plus und der beste Äther, also Top-Äther.
Ergänzende Sortimentsideen:

| Item | Status / Nutzen |
| --- | --- |
| AP-Plus | Gewünscht; erhöht dauerhaft die maximalen AP einer Attacke. |
| Top-Äther | Gewünscht; füllt die AP einer Attacke vollständig auf. |
| Elixier | Vorschlag; stellt AP aller Attacken wieder her. |
| Top-Elixier | Vorschlag; füllt die AP aller Attacken vollständig auf. |
| Entwicklungssteine | Optional, noch nicht beschlossen; besonders Mondstein als sonst nicht regulär kaufbarer Stein. Die anderen Steine sind bereits im Kaufhaus erhältlich. |

Hintergrundidee: Ein weit gereister Händler bringt seltene Vorräte von seinen
Reisen mit. Dialogvorschlag: „Für einen CHAMPION habe ich etwas Besonderes an
Bord. Solche Vorräte findest Du in keinem normalen Laden!“

Noch offen sind genaue Preise, das endgültige Sortiment, der Platz an Bord
und mögliche Kaufbegrenzungen. Unbegrenzter Vorrat ist bisher nicht festgelegt;
insbesondere AP-Plus soll bewusst bepreist werden. Die Gen-1-Itemwirkungen
bleiben unverändert.

Dieses Feature ist **nur geplant, noch nicht implementiert**.

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
- Genaue Auslösung und Wiederholungssperre des Box-Hinweises.
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
Ein Neustart ist für den Wechsel zu Erweitert nicht erforderlich. Weitere
geplante QoL-Funktionen, einschließlich wiederverwendbarer TMs, sind damit noch
nicht aktiviert. Details: [gameplay-modes.md](gameplay-modes.md).


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
