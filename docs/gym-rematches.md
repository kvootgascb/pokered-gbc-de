# Arena-Rückkämpfe nach dem Champion-Sieg

Nur in Erweitert: Jeder Top-Vier-Sieg schaltet jeden der acht Arenaleiter
einmal erneut frei. Die Gelegenheiten sind unabhängig und sammeln sich nicht
an. Bestehende Champion-Spielstände erhalten bei der ersten Nutzung ebenfalls
einmal die acht Gelegenheiten. Ein neuer Spielstand ist nicht nötig.

Nach der ursprünglichen Orden-/TM-Übergabe bietet der Leiter beim Ansprechen
eine persönliche Revanche an. Nein lässt die Gelegenheit erhalten. Bei Ja
wird nur die Gelegenheit dieses Leiters verbraucht, auch bei einer Niederlage.
Erst ein weiterer Top-Vier-Sieg schaltet sie wieder frei. Moduswechsel sowie
Speichern/Laden erzeugen keine zusätzlichen Kämpfe.

## Teams

Arten, Reihenfolge und Teamgröße bleiben wie im ursprünglichen Arenakampf.
Es werden ausdrücklich keine Vorentwicklungen ersetzt und keine weiteren
Pokémon hinzugefügt. Nur die Level sind höher:

| Leiter | Team in ursprünglicher Reihenfolge |
| --- | --- |
| Rocko | Kleinstein 60, Onix 65 |
| Misty | Sterndu 60, Starmie 65 |
| Major Bob | Voltobal 60, Pikachu 62, Raichu 65 |
| Erika | Sarzenia 60, Tangela 62, Giflor 65 |
| Koga | Smogon 60, Sleimok 62, Smogon 60, Smogmog 65 |
| Sabrina | Kadabra 60, Pantimos 62, Omot 62, Simsala 65 |
| Pyro | Fukano 60, Ponita 60, Gallopa 62, Arkani 65 |
| Giovanni | Rihorn 60, Digdri 61, Nidoqueen 62, Nidoking 63, Rizeros 65 |

Attacken entstehen weiterhin durch die normale Trainer-Routine mit den
gemeinsamen Gelb-Lerndaten. Die ursprünglichen Signaturattacken wie Geduld,
Donnerblitz und Geofissur bleiben erhalten. Kampfregeln, KI und Preisgeld
verwenden den ursprünglichen Ablauf. Es gibt keine erneuten Orden oder Arena-TMs.
Die ersten Arenakämpfe behalten ihre ursprünglichen Teams und Level.

## Giovanni und Dialoge

Giovanni kehrt nach dem Champion-Sieg in Erweitert in seine Arena zurück.
Er erklärt, dass er sich zurückgezogen, trainiert und aus seiner Niederlage
gelernt hat. Sein ursprünglicher Story-Abgang vor dem Champion-Sieg bleibt
erhalten. In Classic bleibt der erweiterte Zugang verborgen. Die Anpassung
greift beim natürlichen Betreten beziehungsweise Neuladen der Arena.

Solange seine neue Gelegenheit verbraucht ist, wartet Giovanni auf den nächsten
Ligasieg; er führt seinen alten Abschiedsablauf nicht erneut aus. Die anderen
Leiter geben ohne verfügbare Revanche weiterhin ihren ursprünglichen Rat.
Noch ausstehende ursprüngliche TMs werden zuerst über den bisherigen Dialog
übergeben. Arenatrainer und Rätsel werden nicht zurückgesetzt.

Alle Leiter haben eigene Einladungen: Rocko möchte den Fortschritt sehen,
Misty die Stärke des Champions prüfen, Major Bob seine Niederlage verarbeiten,
Erika das gewachsene Können erleben, Koga das Training vergleichen, Sabrina
den diesmal unklaren Ausgang erfahren und Pyro die Feuerprobe wiederholen.

## Speicher und Prüfung

Payload-Offset 16 enthält acht Verfügbarkeitsbits in Orden-Reihenfolge.
Bit 1 der Initialisierungsflags an Offset 3 verhindert erneutes Freischalten
beim Laden bestehender Spielstände. Alle veröffentlichten Offsets und
Schema 1 bleiben erhalten; die übrigen reservierten Bytes bleiben unberührt.

Die Emulator-Tests prüfen die acht Original- und Rückkampfteams einschließlich
Leveln und Signaturattacken über die tatsächliche Trainer-Routine. Sie prüfen
die einzelnen Chancen, E4-Reset, Nichtansammeln, Speichern/Laden, Classic- und
Orden-Sperren, alle Nein-Dialoge sowie die separaten Rückkehrskripte.
Ein kompletter Rocko-Rückkampf wird vom NPC-Dialog bis zum Sieg und der Rückkehr
gespielt, einschließlich normalem Preisgeld und ohne doppelte TM-/Orden-Ereignisse.
Giovannis Sichtbarkeit und sein Dialog bei verbrauchter Chance werden auf der
echten Karte geprüft. Das ist kein vollständiger manueller Durchlauf aller Arenen.
