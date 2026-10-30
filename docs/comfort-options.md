# Unabhängige Komfortoptionen

Im Geheimmenü führt **WEITER** auf Seite 2; **SEITE 1** führt zurück.
**ZURÜCK** beendet das Geheimmenü auf beiden Seiten. Links/Rechts übernimmt
Einstellungen sofort. A bestätigt nur die Seitenwahl oder ZURÜCK.
Leere Pfeile markieren die aktiven Werte außerhalb der Cursorzeile.

## VM-Animationen

**AN** ist der ursprüngliche Ablauf und die Voreinstellung. **AUS** überspringt
die Zerschneider-Animation und die Vogel-Flugsequenzen bei Abflug und Ankunft.
Die zusätzliche Rufpause beim Aktivieren von Stärke entfällt ebenfalls.

Karteneffekte und Voraussetzungen bleiben gleich: Busch entfernen, Flugziel,
Kartenwechsel, Spielerposition und Stärke-Aktivierung werden weiterhin durch
die ursprünglichen Routinen behandelt. Der Einstiegsschritt beim Surfen und
das eigentliche Schieben der Felsen sind keine entbehrlichen Animationen und
bleiben erhalten. Surfer und Blitz besitzen hier keine zusätzliche separate
Pokémon-Animationssequenz. Teleport, Schaufler und normale Kartenereignisse
werden von der VM-Option nicht verändert.

Die Option gilt unabhängig vom Modus auch bei Benutzung über das ursprüngliche
Pokémon-Menü. Sie wird in Bit 1 des vorhandenen Preference-Bytes gespeichert;
alle anderen Bits bleiben beim Umschalten erhalten.

Die Emulator-Tests prüfen die Seiten-/Cursorbedienung und sofortige Übernahme
auch in Classic. Native Zerschneider- und Flugroutinen werden mit und ohne
Animation ausgeführt: Kartenänderung, wiederhergestellte Spielerposition und
Flugzustand bleiben erhalten. Die vorhandenen Save-/Migrationstests prüfen
weiterhin das ganze Preference-Byte und den vollständigen Feature-Payload.
