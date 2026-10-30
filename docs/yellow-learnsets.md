# Gemeinsame Attacken-Lerndaten aus Pokémon Gelb

Startattacken, Level-up-Lernlisten und TM-/VM-Kompatibilität aller 151 Arten
entsprechen jetzt Pokémon Gelb, in Classic und Erweitert gleichermaßen.
Es gibt keinen zusätzlichen Schalter und keine Änderung am Saveformat.

Quelle ist die Disassembly [pret/pokeyellow](https://github.com/pret/pokeyellow/tree/91d503bffacef97de879da60afc13e5ca3450b02),
festgehalten auf Commit `91d503bffacef97de879da60afc13e5ca3450b02`:

- `data/pokemon/evos_moves.asm`: ausschließlich die Level-up-Listen.
- `data/pokemon/base_stats/*.asm`: ausschließlich Startattacken und TM-/VM-Bits.

Entwicklungsbedingungen, Basiswerte, Typen, Fangraten, Basis-EP und
Wachstumskurven bleiben unverändert. Grafikdaten und Kampfmechanik werden
ebenfalls nicht aus Gelb übernommen. Insbesondere gibt es kein Starter-Pikachu
mit Gelbs besonderen Entwicklungsregeln.

## Unterschiede zur bisherigen Datengrundlage

23 Arten erhalten andere Level-up-Listen, 13 andere Startattacken.
Bei acht Arten ändert sich die nutzbare TM-/VM-Kompatibilität:

| Pokémon | Änderung |
| --- | --- |
| Smettbo, Bluzuk, Omot | Können Blitz lernen. |
| Glurak | Kann Fliegen lernen. |
| Digda, Digdri, Kabutops | Können Zerschneider lernen. |
| Mewtu | Kann Zahltag nicht mehr per TM lernen. |

Bei Mew wird zusätzlich das unbenutzte achte Bit des letzten TM-/VM-Bytes
gelöscht; alle 55 regulären TMs/VMs bleiben verfügbar.
Ein Beispiel für die neuen Level-Listen ist Pikachus Donnerblitz auf Level 26.

## Bestehende Pokémon und besondere Begegnungen

Bereits vorhandene Pokémon behalten ihre Attacken und AP beim Laden des
Spielstands. Sie werden weder neu erzeugt noch rückwirkend umgeschrieben.
Die neuen Daten gelten beim Erzeugen neuer Pokémon, beim künftigen Levelaufstieg,
beim TM-/VM-Einsatz und beim Attacken-Erinnerer. Verpasste frühere Level-Attacken
können beim Erinnerer nachgeholt werden.

Surfer beim seltenen Kraftwerk-Pikachu bleibt als besondere Begegnungsattacke
erhalten. Eine bestehende Attacke wird auch dann nicht entfernt, wenn die Art
sie nach den neuen Kompatibilitätsdaten nicht mehr per TM lernen könnte.

## Prüfung

`tests/fixtures/yellow_learnsets.json` enthält die Referenzwerte aller 151 Arten
mit Quellenstand sowie die bisherigen Entwicklungs- und übrigen Basisdaten.
`tests/yellow_learnsets_check.py` liest die tatsächlich gebauten ROM-Tabellen
und prüft sämtliche Startattacken, Level-Attacken und TM-/VM-Bits dagegen.
Zusätzlich prüft es, dass Entwicklungsbedingungen und die übrigen Basisdaten
erhalten bleiben, einschließlich des separat gespeicherten Mew-Datensatzes.

`tests/player_gender_smoke.py` erzeugt in beiden Modi ein Pikachu auf Level 26
und prüft Donnerblitz sowohl beim Erzeugen als auch über die echte
Level-up-Lernroutine. Die bestehenden Prüfungen für Tauschentwicklungen,
TMs, besondere Begegnungsattacken, Erinnerer und alte Spielstände laufen mit.
