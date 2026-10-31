# Rote Edition DX / Blaue Edition DX

Die Spielnamen sind **Pokémon: Rote Edition DX** und **Pokémon: Blaue Edition DX**.

Der Titelbildschirm behält den vorhandenen Schriftzug ROTE EDITION bzw.
BLAUE EDITION und ergänzt DX aus den bestehenden D-/X-Schriftzeichen. Die
gesamte Beschriftung wird als 13 Kacheln auf Zeile 8 zentriert. Logo,
Pokémon-Wechsel und Auswahl der gespeicherten Spielfigur bleiben erhalten.
Die ursprünglichen Titel-PNGs werden nicht verändert.

Die kurzen ROM-Headernamen lauten `POKEMON ROT DX` bzw. `POKEMON BLAU DX`.
Sie passen in das für CGB-ROMs verfügbare Titelfeld; RGBFIX erzeugt die
passenden Headerprüfsummen. Auch Debug- und VC-Buildregeln verwenden diese
Namen. Die bestehenden Ausgabedateinamen `pokered.gbc` und `pokeblue.gbc`
sowie Saveformat, SRAM-Offsets und Saveversion bleiben unverändert.

Die Emulator-Suite prüft Headernamen, Titel-Kacheldaten und die tatsächliche
Titelanzeige beim Kaltstart mit Green-Spielstand und ohne gültigen Spielstand.
Alle bisherigen Gameplay- und Spielstandtests laufen weiter mit. Rot, Blau
und Blau Debug werden gebaut; die Emulator-Suite läuft für Rot und Blau.

Die passenden Stickerentwürfe mit Green und Turtok bzw. Glurak sind unter
[artwork/README.md](../artwork/README.md) mit beiden PNGs dokumentiert.
