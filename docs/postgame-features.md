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
Nach einem Sieg hält er einen zufälligen Starter auf Level 5 bereit; alle drei
sind gleich wahrscheinlich. Mit vollem Team bleibt das Geschenk zur Abholung
gespeichert. Solange es wartet, gibt es keinen weiteren Eich-Kampf, auch nach
einem weiteren Top-Vier-Sieg. Nach der Abholung ist ein neuer Sieg nötig.

Die M.S. Anne verwendet beim Verlassen über die Gangway ihren ursprünglichen
Abfahrtsablauf. Kabinen- oder Deckwechsel verbrauchen den Besuch nicht.
Classic verbirgt nach dem Champion-Sieg den erneuten Zugang, ohne die erweiterte
Gelegenheit zu löschen.

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

## Spielhalle

- Münzkauf: weiterhin 50 für 1000, zusätzlich 500 für 10000.
- Zusätzlicher Preishändler im Preisgebäude: Evoli für 2500 Münzen,
  Kicklee und Nockchan für jeweils 4600, alle auf Level 25.
- Die zusätzlichen Preise orientieren sich an den Blau-Preisstufen.
- Volles Team, fehlendes Geld oder zu wenig Platz im Münzkorb verbrauchen
  weder Münzen noch Geld. Für Pokémon-Preise muss ein Teamplatz frei sein.

## Kostenlose Attacken-Helfer

Zwei neue Gäste stehen nach dem ersten Top-Vier-Sieg auf dem Deck der M.S. Anne.
Sie kamen, um den neuen Champion kennenzulernen, und helfen ihm mit ihren
besonderen Begabungen. Beide Dienste sind kostenlos.

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
Team-Pokémon aus und bekommt es sofort zurück. Kadabra, Maschock, Georok und
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
mit Teamauswahl, Entwicklung und Rückkehr ins Labor.

## Speicher und Prüfung

Alle dauerhaften Zustände nutzen das bestehende Feature-Saveformat mit
unveränderten veröffentlichten Offsets und Schema 1. Kein neuer Spielstand
ist nötig. Details stehen in [save-format.md](save-format.md).

`tests/player_gender_smoke.py` prüft die Ereigniszustände, ausstehende Geschenke,
Begegnungsregeln, Münzgrenzen, Preisprüfungen und Attackenlisten sowie das
Speichern, Laden und Migrieren alter Spielstände. Diese automatisierten Checks
ersetzen keinen vollständigen manuellen Durchlauf der gesamten Handlung.

## Weitere Champion-Inhalte

Die acht Arenaleiter bieten nun unabhängige Rückkämpfe mit ihren Originalteams
auf Level 60–65 an: [gym-rematches.md](gym-rematches.md).
Der zusätzliche Händler auf dem Schiffsdeck verkauft seltene Vorräte:
[ship-merchant.md](ship-merchant.md). Beide Inhalte gelten nur in Erweitert.
