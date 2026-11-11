# Pokémon DX · Spielstand-Editor

**[ZIP herunterladen](Pokemon-DX-Saveeditor.zip), entpacken und die HTML-Datei im Browser öffnen.**
Alternativ direkt [Pokemon-DX-Saveeditor.html](Pokemon-DX-Saveeditor.html) herunterladen.
Die einzelne HTML-Datei enthält Oberfläche, Spieldaten und Pokémon-Bilder.
Es sind keine Installation, Internetverbindung oder ROM-Datei nötig. Der Editor
lädt keine Dateien hoch und stellt keine externen Verbindungen her.

## Benutzung

1. Im Spiel mit **SICHERN** speichern und den Emulator schließen.
2. Die normale `.sav`-Datei im Editor öffnen oder hineinziehen.
3. Unter **Team** Pokémon-Art, Level, Spitznamen, KP/Status und Attacken ändern.
   Teamplätze lassen sich hinzufügen, entfernen und verschieben. Unter
   **DVs & Trainingswerte** können auch die Werte der ersten Generation
   angepasst werden.
4. Unter **Beutel** Items und Mengen bearbeiten, hinzufügen, entfernen oder
   sortieren. Die Grenze beträgt 30 Plätze in DX und 99 Stück pro Item.
5. **Bearbeitete .sav speichern** lädt eine neue Datei mit dem Zusatz
   `-bearbeitet.sav` herunter. Die ursprüngliche Datei bleibt unverändert.
6. Die heruntergeladene Datei im Emulator als Spielstand verwenden, bei
   VBA-M also bei geschlossenem Emulator passend zur ROM benennen
   (z. B. `pokeblue.sav`). Das Spiel neu starten und **WEITER** wählen.
   Einen alten Emulator-Schnellspeicherstand dabei nicht laden.

Emulator-Schnellspeicherstände wie `.sgm` sind keine normalen Spielstände.
Unterstützt werden 32-KB-Dateien mit dem deutschen Basislayout: das aktuelle
DX-Format `I2`, das frühere `I1` und ursprüngliche 20-Platz-Beutel. Ältere
Formate werden beim Export beibehalten; die ROM übernimmt ihre Migration.
Unbekannte neuere Formate und ungültige Prüfsummen werden abgelehnt.

## Verhalten

- Team: 1–6 Pokémon, alle 151 Arten, Level 1–100, vier Attacken, AP und AP-Plus.
- Neue Pokémon erhalten die Trainer-ID und den OT-Namen des Spielers,
  Level 5, volle KP, DVs 15 und Trainingswerte 0. Ihre anfänglichen Attacken
  stammen aus den Basisdaten. Level und Attacken können anschließend frei
  geändert werden; der Editor erzwingt keine erlernbare Attackenliste.
- Bei Änderung von Art oder Level werden Erfahrung, Typen bzw. Statuswerte
  konsistent geschrieben. Bei geänderten DVs oder Trainingswerten werden
  die Statuswerte neu berechnet. Unveränderte gespeicherte Statuswerte
  bleiben erhalten; Gen 1 wendet hinzugekommene Stat-Erfahrung erst bei
  einer Neuberechnung an. KP können mit **Heilen & AP auffüllen** gefüllt werden.
- Neue Arten werden im Pokédex als gesehen und gefangen eingetragen.
- Beutelplätze und Mengen werden geprüft; doppelte Items sind nicht erlaubt.
- Die Basis-Prüfsumme wird aktualisiert. PC-Boxen, Geschichte und sämtliche
  512 Feature-Bytes einschließlich Reserven und ihrer Prüfsumme bleiben
  unverändert. Auch unbekannte gespeicherte Spitznamen bleiben unangetastet,
  sofern sie nicht bearbeitet werden.
- Ein Export ohne Änderungen ist bytegenau mit der Eingabedatei identisch.

## Entwicklung und Prüfung

Die HTML-Datei ist das fertige Programm. Zum Neubauen zuerst die ROMs gemäß
`INSTALL.md` bauen, dann vom Repository-Stamm aus:

```sh
python3 tools/save-editor/build.py
node tests/save_editor_test.cjs
```

`build.py` liest das tatsächliche SRAM-Layout aus den Symbolen und vergleicht
Rot/Blau. Namen, interne IDs, Basiswerte, Wachstumskurven, Attacken/AP und die
DX-Signatur stammen aus den gebauten ROM-Daten. Die Signatur `QOLS` ist im
Spielzeichensatz kodiert, nicht als ASCII. Die Bilder kommen aus den bereits
im Repository verwendeten Gold-/Silber-Frontgrafiken. Der Builder braucht nur
die Python-Standardbibliothek; die generierte HTML-Datei hat keine Laufzeitabhängigkeiten.

Die Codec-Tests prüfen Formate, Prüfsummen, Grenzen, Sortierung, geschützte
Bereiche, Gen-1-Statuswerte und AP-Plus. Mit Playwright und Chromium kann
zusätzlich die Oberfläche einschließlich Download und Mobilansicht geprüft werden:

```sh
node tests/save_editor_browser.cjs
```

Optional lässt sich eine echte Save-Kopie bearbeiten und mit PyBoy 2.8.1 in
beiden ROMs laden. Die Eingabedatei wird auch hier nicht überschrieben:

```sh
DX_TEST_SAVE=/pfad/zum/spielstand.sav node tests/save_editor_test.cjs
python tests/save_editor_native.py
```

Dabei liegt die Testkopie unter `/tmp/dx-editor-tests/real-edited.sav`. Die
ROM-Prüfung vergleicht geladenes Team, Beutel und Featureblock und berechnet
Statuswerte und AP mit den nativen Spielroutinen nach. Browser-Testbilder und
synthetische Testdateien liegen ebenfalls nur unter `/tmp/dx-editor-tests/`.
