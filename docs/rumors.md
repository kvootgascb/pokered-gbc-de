# Gerüchte und neue Bewohner

Die Gerüchte gehören zum Modus **Erweitert**. Alle Gerüchte beginnen mit
**„Hast du schon gehört?“**. Sie nennen weder Fangraten noch genaue
Freischaltbedingungen oder Lösungen. Die zusätzlichen Figuren benutzen
vorhandene Sprites und laufen auf einer kurzen horizontalen Strecke:
Startposition und je ein Feld links/rechts. Normale Hindernisse und andere
Figuren begrenzen die Bewegung zusätzlich. Original-NPCs behalten ihre
ursprünglichen Bewegungsregeln.

## Älterer Trainer in Alabastia

Nach dem ersten Champion-Sieg rechts neben Eichs Labor, Ausgangspunkt (17, 10).
Ein neuer älterer Trainer mit dem Gambler-Sprite erzählt:

> Hast du schon gehört?
> Professor EICH war früher ein starker Trainer.
> Neulich habe ich ihn wieder seine alten POKéBÄLLE polieren sehen ...

## Wanderer bei der Felshöhle

Ein neuer Wanderer geht im Pokémon-Center bei der Felshöhle auf und ab,
Ausgangspunkt (8, 5). Er ist unabhängig vom Champion-Sieg vorhanden.

> Hast du schon gehört?
> Letztes Jahr bin ich mit der M.S. ANNE gefahren.
> Beim Einsteigen sah ich einen Schatten unter dem Lastwagen huschen.
> Keine Ahnung, was das war. Von der Farbe her hätte es ein FLEGMON sein können ...

Mew und sein Versteckspiel werden nicht ausdrücklich verraten.

## Angler auf der Zinnoberinsel

Ein neuer Angler läuft am südlichen Ufer, Ausgangspunkt (8, 13).
Er ist unabhängig vom Champion-Sieg vorhanden.

> Hast du schon gehört?
> Ein Forscher aus dem Labor meint, tief in einer Höhle würden noch lebende
> Fossil-POKéMON anbeißen!
> Warum suchen die dann hier in alten Steinen?

Der Text nennt ausdrücklich keine bestimmte Höhle, Ebene oder Angel.
Die tatsächlichen Textboxen teilen diese Sätze in kurze Zeilen und Seiten.

## Sichtbarkeit und Speicherstand

Die neuen Hide/Show-Einträge werden hinten angehängt. Alle bisherigen globalen
Objekt-IDs, gespeicherten Flags und SRAM-Offsets behalten ihre Bedeutung.
Beim Laden einer betroffenen Karte werden die neuen Objekte an deren
Hide/Show-Liste angehängt und ihre Sichtbarkeit vor dem Zeichnen aus Modus
und Champion-Status abgeleitet. Das gilt auch für bestehende Spielstände.
Es braucht weder einen neuen Spielstand noch einen neuen Saveformatstand.
Ein Moduswechsel darf wie vereinbart erst beim natürlichen Kartenladen greifen.

Die Emulator-Suite prüft in Rot und Blau die Classic-/Champion-Freischaltung,
die Hide/Show-Zuordnung einschließlich des ursprünglichen Eich-Eintrags,
sichtbare Bewegung auf der kurzen Strecke und die tatsächlichen Dialoge über
die Textzeiger der geladenen Karten. Die bisherigen Gameplay-Tests laufen mit.

Die vereinbarten vier Matrosen auf Landgang und ihr Pikachu-Gerücht folgen
als eigener Feature-Commit.
