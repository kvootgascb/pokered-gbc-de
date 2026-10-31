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

## Vier Matrosen auf Landgang in Orania

Nur in Erweitert, nach dem ersten Champion-Sieg und während ein erneuter
M.S.-Anne-Besuch verfügbar ist. Ihre Anwesenheit ist der sichtbare Hinweis
auf die Rückkehr des Schiffs; ein zusätzlicher Ankündigungsdialog ist unnötig.

| Neuer Matrose | Ausgangspunkt | Bewegung | Gespräch |
| --- | --- | --- | --- |
| Beim Pokémon-Center | (13, 5) | Je ein Feld links/rechts | Surfer-Pikachu-Gerücht |
| Beim Pokémon-Fanclub | (7, 14) | Je ein Feld links/rechts | Endlich wieder festen Boden unter den Füßen |
| Beim Laden | (25, 14) | Je ein Feld links/rechts | Proviant vor der Abfahrt besorgen |
| Auf dem breiten Platz vor dem Hafengebiet | (21, 14) | Steht mit Blick nach Süden | Landgang, danach zurück an Bord |

Der erste Matrose erzählt:

> Hast du schon gehört?
> Vom Deck aus habe ich eine ganze Gruppe PIKACHU zum KRAFTWERK schwimmen sehen!
> Ich konnte meinen Augen nicht trauen!
> Die anderen glauben mir bis heute kein Wort!

Die übrigen drei führen normale Alltagsgespräche und verwenden deshalb nicht
die Einleitung eines Gerüchts. Die ursprünglichen Stadtbewohner und Matrosen
bleiben erhalten. Die Stadt hat damit zehn Objekte; die neuen Standorte und
kurzen Laufwege liegen außerhalb von Türen und des Kontrollpunkts am Hafen.
Der stehende Matrose steht ausdrücklich nicht auf dem zweifeldbreiten Steg.
So bleibt auch dann eine Spur frei, wenn der ursprüngliche laufende Matrose
auf dem Steg stehen bleibt. Der Weg zwischen Hafen und Stadt wird im Emulator
in beide Richtungen mit jeweils einer absichtlich blockierten Spur geprüft.

Es gibt keinen eigenen Landgang-Zähler. Alle vier verwenden dieselbe gespeicherte
Besuchsfreigabe `wFeatureAnneState` wie das Schiff. Nach dessen ursprünglichem
Abreiseablauf sind sie beim nächsten Laden Oranias verschwunden. Ein weiterer
Top-Vier-Sieg bringt sie mit dem Schiff zurück; Besuche sammeln sich nicht an.
Gespräche verbrauchen keinen Besuch. Bestehende Champion-Spielstände erhalten
dieselbe einmalige Initialisierung wie der bestehende Hafenzugang.

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
die Textzeiger der geladenen Karten. Für die vier Matrosen werden zusätzlich
verfügbare/verbrauchte Schiffsbesuche, die einmalige Übernahme alter
Champion-Spielstände, Speichern/Laden in beiden Zuständen, erneute
Champion-Siege und Moduswechsel beim Kartenladen geprüft. Drei laufen
sichtbar auf ihrer kurzen Strecke; der vierte bleibt stehen. Alle vier
Kartendialoge werden ausgeführt. Die Abreiseprüfung nutzt die vorhandene
Verbrauchsroutine des Schiffs; die komplette Abfahrtsanimation wird dabei
nicht erneut durchgespielt. Die bisherigen Gameplay-Tests laufen mit.
