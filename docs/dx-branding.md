# Rote Edition DX / Blaue Edition DX

Die Spielnamen sind **Pokémon: Rote Edition DX** und **Pokémon: Blaue Edition DX**.

Der Titelbildschirm behält den vorhandenen Schriftzug ROTE EDITION bzw.
BLAUE EDITION und ergänzt DX in derselben fetten, fünf Pixel hohen Schrift
auf derselben Grundlinie. Das D entspricht dem D in EDITION; das X ist
passend dazu gezeichnet, beide Buchstaben sind platzsparend gepackt. Die
gesamte Beschriftung wird als 12 Kacheln auf Zeile 8 zentriert. Die leere
Endkachel der ursprünglichen Editionsgrafik wird beim Laden ausgelassen;
zwischen EDITION und DX steht genau eine normale Leer-Kachel (acht Pixel).
Dadurch bleibt ein normaler Wortabstand ohne den überflüssigen alten Rand
und ohne sichtbare Schriftpixel zu entfernen. Logo,
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
