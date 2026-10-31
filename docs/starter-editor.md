# Temporärer Starter-Editor

Im Geheimmenü auf **Seite 2** steht unter der schnellen Heilung der
**STARTER-EDITOR**. Er ist in **Classic und Erweitert** verfügbar, solange
der Spieler in Eichs Labor steht und noch keinen Starter gewählt hat.
Andernfalls zeigt das Feld „NICHT MÖGLICH“ und Links/Rechts ändern nichts.

Mit Hoch/Runter die Zeile auswählen. Links/Rechts blättert durch **ORIGINAL**
und die **151 Arten in Pokédex-Reihenfolge**, mit Umlauf an beiden Enden.
A übernimmt keinen zusätzlichen Schritt und verlässt das Menü hier nicht.
Select wechselt wie bisher die Seite; Zurück, B oder Start verlassen das
Menü und behalten die temporäre Auswahl.

Danach wählt man ganz normal eine Starter-Kugel. Die Kugel bestimmt weiterhin
Erhalt-Dialog, verschwundene Kugeln, Story-Starter, Rivalen-Starter und spätere
Trainerteams. Nur das tatsächlich erhaltene Pokémon wird ersetzt. Beispiel:
**SIMSALA wählen → Schiggy-Kugel nehmen → Simsala erhalten; Rivale nimmt Bisasam.**
Der Spitznamendialog gehört zum tatsächlich erzeugten Pokémon.

Das Pokémon entsteht über die ursprüngliche Erzeugungsroutine auf **Level 5**,
mit den zur Art und diesem Level passenden **Gelb-Attacken**, normalen PP,
Werten, Spieler-OT und Pokédex-Eintrag. ORIGINAL erhält das normale Verhalten.
Das Feature verändert keine Kampfregeln und ersetzt keine bereits vorhandenen
Teammitglieder.

Die Voreinstellung verwendet genau ein Byte außerhalb aller gespeicherten
Datenblöcke. Sie wird bei der Übergabe verbraucht sowie bei New Game und jedem
Ladeversuch gelöscht. Sie wird nicht in SRAM geschrieben; Format, Version und
Offsets bestehender Spielstände bleiben gleich. Ein bereits erhaltenes
Ersatz-Pokémon wird als normales Teammitglied gespeichert und bleibt erhalten.

## Prüfung

Die Emulator-Suite `tests/player_gender_smoke.py` prüft in Rot und Blau:

- Tatsächliche Auswahl aller drei Labor-Kugeln mit Simsala als Ersatz,
  anschließende Rivalenwahl, Story-Starter, Level und Speichern/Laden.
- Erzeugung verschiedener Arten einschließlich Mew in beiden Modi, mit
  ursprünglicher OT-ID und denselben Level-5-Attacken/PP wie native Erzeugung.
- ORIGINAL, falscher Ort, abgeschlossene Starterwahl und ungültige Art.
- Menübedienung, Namensanzeige, Umlauf zwischen ORIGINAL und Mew,
  A ohne Schließen, Seitenwechsel und Erreichbarkeit von Zurück.
- Verwerfen der Voreinstellung beim Laden und beim neuen Spiel.
