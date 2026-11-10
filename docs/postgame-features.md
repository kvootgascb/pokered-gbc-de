# Umgesetzte Erweiterungen: Champion, Begegnungen und Spielhalle

Diese Inhalte gelten im Modus **Erweitert**. Classic behält die ursprünglichen
Zugänge und Dialoge. Bereits erhaltene Pokémon und gespeicherte Ereignisse
bleiben bei einem Moduswechsel erhalten. Änderungen an Karten/NPCs greifen
beim natürlichen Betreten; ein sofortiger Umbau beim Umschalten ist nicht nötig.

## Champion und M.S. Anne

Jeder Top-Vier-Sieg schaltet einen Eich-Kampf und einen Schiffsbesuch frei.
Gelegenheiten sammeln sich nicht an. Bestehende Champion-Spielstände erhalten
beim ersten erweiterten Besuch ebenfalls einmal diese Gelegenheiten.

Eich bietet im Labor einen nostalgischen Kampf an. Er verwendet seine bereits
vorhandenen Teams auf Level 66–70, passend zum ursprünglich gewählten Starter.
Die Kampfgelegenheit wird beim Annehmen verbraucht, auch bei einer Niederlage.
Nach einem Sieg setzt Eich automatisch mit dem Geschenkdialog fort und
übergibt einen zufälligen Starter auf Level 5; alle drei sind gleich
wahrscheinlich. Mit vollem Team weist er direkt auf den fehlenden Platz hin;
das Geschenk bleibt zur späteren Abholung
gespeichert. Solange es wartet, gibt es keinen weiteren Eich-Kampf, auch nach
einem weiteren Top-Vier-Sieg. Nach der Abholung ist ein neuer Sieg nötig.

Die Einladung wird seitenweise mit A/B bestätigt; nach der abschließenden
Kampffrage erscheint Ja/Nein ohne weiteren Tastendruck. Nein oder B schließt
den Dialog direkt. Die Kampftexte lassen eine eigene Zeile für den automatisch
vorangestellten Trainernamen frei. Beim Geschenk sagt Eich:
„Als Dank für den Kampf möchte ich Dir dieses Pokémon anvertrauen.“
Bei vollem Team wird jede Seite normal bestätigt und die letzte Seite mit
einem Tastendruck geschlossen.

Die M.S. Anne verwendet beim Verlassen über die Gangway ihren ursprünglichen
Abfahrtsablauf. Kabinen- oder Deckwechsel verbrauchen den Besuch nicht.
Classic verbirgt nach dem Champion-Sieg den erneuten Zugang, ohne die erweiterte
Gelegenheit zu löschen.

Die Abfahrt setzt das ursprüngliche Flag `EVENT_SS_ANNE_LEFT` nach dem
Verbrauchen der Besuchsfreigabe mit einer ausdrücklich neu geladenen
Event-Adresse. Der vorgeschaltete `farcall` erhält HL nicht. Ein Wiederverwenden
des alten Zeigers setzte das Flag deshalb nicht und startete die gesamte
Abfahrts-/Dampfsequenz im nächsten Karten-Skriptdurchlauf erneut.
Die Korrektur verändert weder Saveformat noch Animationsdauer oder Grafik.

## Begegnungen

| Pokémon | Ort | Bedingung / Rate | Level |
| --- | --- | --- | --- |
| Amonitas | Tiefste Ebene der Azuria-Höhle | Superangel, 1 % pro erfolgreichem Biss | 55 |
| Kabuto | Tiefste Ebene der Azuria-Höhle | Superangel, 1 % pro erfolgreichem Biss | 55 |
| Surfer-Pikachu | Kraftwerk | 1 % der regulären Zufallsbegegnungen | 23 |
| Mew | Lastwagen im Hafen | Versteckspiel | 30 |

Die ursprüngliche Chance auf „kein Biss“ bleibt bestehen. Fossil-Pokémon sind
lebende Begegnungen und brauchen keine Wiederbelebung. Surfer-Pikachu behält
Surfer auch beim Fang ins Team oder in die Box.

Beim Lastwagen flieht Mew beim ersten Versuch immer zur anderen Seite. Dieselbe
Seite erneut anzusprechen würfelt nicht. Auf der jeweils richtigen Seite gibt
es anschließend eine Chance von 1:4; bei Misserfolg wechselt Mew wieder die
Seite. Die Begegnung wird beim Erscheinen dauerhaft verbraucht. Flucht oder
Besiegen erzeugt keinen neuen Versuch. Mew nutzt die regulären Level-30-Attacken.

In Erweitert bleibt ein wildes Mew auch nach Wandler beim Fang ein Mew.
Die ursprüngliche Art liegt bereits in `wEnemyMonSpecies2`; nur die erzwungene
Gen-1-Zuweisung von Ditto wird für diese Kombination aus Modus und Art
übersprungen. Der originale Wandler-Effekt und die Fangberechnung bleiben
erhalten. Die native Fangroutine stellt Mews Art, Namen und reguläre
Level-30-Attacken einschließlich Wandler wieder her und übernimmt es korrekt
ins Team oder in die Box. Fangtext und Pokédex-Eintrag verwenden Mew.

Ditto, andere verwandelte wilde Arten und Classic behalten ihre ursprüngliche
Behandlung. Es gibt weder einen nachträglichen Pokémon-Austausch noch einen
neuen Save-Zustand. Die Ausnahme gilt beim Fang; sie verändert keine bereits
als Ditto gespeicherten Pokémon. Mews verbrauchtes Lastwagen-Ereignis wird
dadurch nicht zurückgesetzt.

## Spielhalle

- Münzkauf in Erweitert: 50 Münzen für ¥1000. Wenn beim Öffnen mindestens
  ¥10000 vorhanden sind, stehen 500 Münzen für ¥10000 an erster Stelle,
  danach 50 Münzen und Zurück. Sonst wird das große Paket ausgeblendet.
  Das kompakte Kaufmenü zeigt Geld und Münzen über der Spielhallenansicht.
  Spieler und NPCs bleiben während der Begrüßung sichtbar. Nur im Kaufmenü
  werden sie ausgeblendet, damit sie die Fenster nicht überdecken; vor
  Dankes-, Fehler- und Abschiedstext werden Karte und Figuren wiederhergestellt.
  Die Begrüßung
  „Willkommen in der ROCKET SPIELHALLE!“ bleibt erhalten; nach der Frage
  erscheint die Auswahl ohne zusätzliche Bestätigung. Zurück oder B führt
  zum ursprünglichen Abschied „Nein? Dann komm vorbei, wenn Du spielen
  möchtest!“. Nach einem Kauf bedankt sich der Verkäufer ohne Mengenangabe:
  „Danke! Hier sind Deine Münzen!“. Jede Textseite wird normal mit A/B
  bestätigt; zum Abschluss ist kein zusätzlicher Tastendruck nötig.
  Classic behält den ursprünglichen Münzkauf.
- Erstes reguläres Preisfenster in Erweitert: Evoli für 2500 Münzen,
  Kicklee und Nockchan für jeweils 4600, alle auf Level 25. Classic behält
  seine ursprünglichen Angebote; der NPC behält seinen ursprünglichen Dialog.
- Die zusätzlichen Preise orientieren sich an den Blau-Preisstufen.
- Fehlendes Geld oder zu wenig Platz im Münzkorb verbrauchen
  weder Münzen noch Geld. Pokémon-Preise nutzen die reguläre Vergabe an Team
  oder PC-Box; sind beide voll, werden keine Münzen abgezogen.

## Kostenlose Attacken-Helfer

Zwei neue Gäste stehen nach dem ersten Top-Vier-Sieg auf dem Deck der M.S. Anne.
Sie kamen, um den neuen Champion kennenzulernen, und helfen ihm mit ihren
besonderen Begabungen. Sie stellen sich als Zwillinge vor und verwenden
denselben Sprite und stehen direkt nebeneinander. Beide Dienste sind kostenlos. Vor der Pokémon-Auswahl wird
der gewünschte Dienst mit Ja/Nein bestätigt. Nein oder B schließt den Dialog
sofort ohne weiteren Tastendruck, auch beim B-Abbruch der Pokémon-Auswahl.
Die Attackenauswahl nutzt einen
sauberen Menühintergrund; beim Verlassen kehrt die Karte zurück.

Der Verlerner entfernt auch VMs, aber nie die letzte verbliebene Attacke.
Die AP und AP-Plus-Daten der übrigen Attacken bleiben erhalten.
Der Erinnerer bietet Start- und frühere Level-Attacken der aktuellen Art und
ihrer Vorentwicklungen bis zum aktuellen Level an. Bereits bekannte Attacken
und doppelte Einträge werden ausgefiltert. Das Erlernen nutzt den normalen
Attackenwechsel; zum Ersetzen einer VM ist vorher der Verlerner da.

Die Helfer verwenden inzwischen die gemeinsame Gelb-Lerndatengrundlage.
Details stehen in [yellow-learnsets.md](yellow-learnsets.md).

## Tausch-zurück-Trainer

Der rechte Assistent in Eichs Labor bietet in Erweitert nach der Starterwahl
einen kostenlosen Linkkabel-Test an. Nach Bestätigung wählt der Spieler ein
Team-Pokémon aus. Die originale Tauschanimation zeigt den Hin- und Rückweg
durch das Linkkabel; anschließend ist es wieder im Team. Kadabra, Maschock, Georok und
Alpollo entwickeln sich über die ursprüngliche Tauschentwicklungsroutine.
Andere Arten werden unverändert zurückgegeben; insbesondere werden keine
Level- oder Steinentwicklungen ausgelöst. Ein zweites Gerät ist nicht nötig.

Das Pokémon verlässt seine Teamposition nicht, wechselt weder Besitzer noch
Trainer-ID und erhält dadurch keinen Fremdtrainer-EP-Bonus. Spitzname, Erfahrung,
DVs, Stat-EP, Attacken und AP bleiben erhalten; normale Entwicklungsänderungen
an Art, Typen und Statuswerten gelten weiterhin. Beim aktuellen Level regulär
angebotene Entwicklungsattacken nutzt die ursprüngliche Lernroutine.
Classic behält den bisherigen Dialog des Assistenten. Es gibt keinen neuen
persistenten Zwischenzustand und keine Änderung am Saveformat.

Die Emulator-Tests prüfen alle vier Entwicklungen, unveränderte Pokémon-Daten,
ein nicht entwickelbares Pokémon, die Classic-Sperre sowie den echten Dialog
mit Teamauswahl, beiden Animationsrichtungen, Entwicklung und Rückkehr ins
Labor. Blumen- und Wasseranimationen der Karte pausieren während Tausch und
Entwicklung, damit sie keine Pokémon-Grafik überschreiben. Sie werden erst nach
der Wiederherstellung von Tileset-Grafik, LCD-/Fensterposition und Sprites
fortgesetzt. Die Dialogzeilen passen in den Textkasten; Nein und B in
der Teamauswahl schließen ohne weiteren Tastendruck.

## Speicher und Prüfung

Alle dauerhaften Zustände nutzen das bestehende Feature-Saveformat mit
unveränderten veröffentlichten Offsets und Schema 1. Kein neuer Spielstand
ist nötig. Details stehen in [save-format.md](save-format.md).

`tests/player_gender_smoke.py` prüft die Ereigniszustände, ausstehende Geschenke,
Begegnungsregeln, Münzgrenzen, Preisprüfungen und Attackenlisten sowie das
Speichern, Laden und Migrieren alter Spielstände. Diese automatisierten Checks
ersetzen keinen vollständigen manuellen Durchlauf der gesamten Handlung.

Mews Fangprüfung führt zuerst den tatsächlichen Wandler-Effekt gegen Mewtu
aus und fängt anschließend mit der echten Ball-Routine. Sie prüft Team und
Box, Fangtext, Standard-Spitznamen, Pokédex, Level, Attacken/AP, DVs, KP und
Status sowie den weiterhin verbrauchten Begegnungszustand. Gegenproben decken
unverwandeltes Mew, Classic, Ditto und eine andere verwandelte Art ab.

Die Suite führt außerdem die vollständige Abfahrt einschließlich acht
Dampfwolken, Entfernen des Schiffs, automatischem Verlassen des Hafens und
wieder verfügbarer Spielersteuerung aus. Sie prüft Classic/Erweitert beim
ersten Besuch und Erweitert beim erneuten Besuch nach einem Champion-Sieg.
Die Sequenz darf jeweils genau einmal beginnen; der Spieler muss sich danach
in Orania wieder normal bewegen können.

Ein externer Ingame-Spielstand kurz vor der Gangway auf Etage 1 kann zusätzlich
über die echten Titel-/Fortsetzen-Menüs geprüft werden:

```sh
python tests/ss_anne_departure_smoke.py pokeblue /pfad/zum/pokeblue.sav
```

Dieser Test lädt das Save nur in den Emulator-Speicher und überprüft, dass die
Datei unverändert bleibt. Persönliche Test-Spielstände gehören nicht ins Repository.

## Weitere Champion-Inhalte

Die acht Arenaleiter bieten nun unabhängige Rückkämpfe mit ihren Originalteams
auf Level 60–65 an: [gym-rematches.md](gym-rematches.md).
Der zusätzliche Händler auf dem Schiffsdeck verkauft seltene Vorräte:
[ship-merchant.md](ship-merchant.md). Beide Inhalte gelten nur in Erweitert.
