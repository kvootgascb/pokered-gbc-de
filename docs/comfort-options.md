# Unabhängige Komfortoptionen

Im Geheimmenü wechselt **Select** zwischen den beiden Seiten. Ein Druck
wechselt genau eine Seite; Halten wiederholt den Wechsel nicht. Der lange
Öffnungsgriff blättert nicht zusätzlich. Unten rechts steht **S. 1/2** oder
**S. 2/2**. Die frühere Auswahl WEITER/SEITE 1 entfällt.

Seite 1 enthält Geschlecht, Spielmodus und VM-Animationen. Seite 2 enthält
schnelle Heilung und freien Platz für künftige Optionen. Auf beiden Seiten
steht **ZURÜCK** unten links. A auf ZURÜCK beendet das gesamte Geheimmenü;
B/Start beenden es ebenfalls. Links/Rechts übernimmt Einstellungen sofort.
Alle Änderungen beider Seiten bleiben beim Blättern und Verlassen erhalten.
Dauerhaft gesichert werden sie wie bisher durch normales Speichern im Spiel.
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

## Schnelle Heilung

**AUS** erhält den ursprünglichen Pokémon-Center-Dialog samt Animation und ist
voreingestellt. **AN** zeigt eine kurze Heilungsfrage und nach Zustimmung eine
kurze Bestätigung ohne Maschinenanimation und zusätzliche Verbeugungspause.
Die längeren Wiederholungstexte des Centers entfallen. Bei Nein wird nicht
geheilt und der Rückkehrort bei einer Niederlage nicht verändert.

HP, Status und AP einschließlich AP-Plus-Boni werden durch die ursprüngliche
Heilroutine wiederhergestellt. Der Rückkehrort wird wie bisher gesetzt;
Safari-Rasthäuser behalten ihre ursprüngliche Ausnahme. Die schnelle Variante
verändert weder Items noch Geld und führt keine neuen Heilungskosten ein.
Andere NPC-Gespräche und Storytexte werden von dieser Option nicht gekürzt.

Die Option gilt unabhängig vom Modus und verwendet Bit 0 desselben vorhandenen
Preference-Bytes. Die Menütests schalten beide Optionen auch in Classic sofort
um und prüfen dabei, dass die jeweils andere Option sowie reservierte Bits
nicht überschrieben werden.

Die Emulator-Tests sprechen die Schwester im echten Center an: schnelle Heilung
in Classic und Erweitert, ursprünglicher Ablauf bei ausgeschalteter Option und
Ablehnung. Sie prüfen den vollständigen Team-Datensatz, HP, Status, AP samt
AP-Plus, den Rückkehrort, das Ausbleiben beziehungsweise Vorhandensein der
Maschinenanimation und den kürzeren Ablauf.

Die Menütests prüfen auch Select von der ZURÜCK-Zeile, Halten ohne Wiederholung,
den Öffnungsgriff, beide sichtbaren Seitenzähler, beide ZURÜCK-Cursor und den
gemeinsamen Erhalt von Figur, Modus und Komfortoptionen beim Speichern/Laden.
