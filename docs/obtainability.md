# Alle 151 Arten in Erweitert

In Erweitert stehen die Gras-, Höhlen- und Surf-Begegnungen aus Rot und Blau
gemeinsam zur Verfügung. Bei einem unterschiedlichen Begegnungsslot wird
gleich wahrscheinlich dessen Rot- oder Blau-Fassung gewählt, mit dem jeweiligen
Originallevel. Gleiche Slots und die allgemeinen Begegnungsraten bleiben gleich.
Damit behalten beispielsweise Magmar und Elektek ihre jeweiligen Lebensräume.
Die zusätzlichen 1-%-Begegnungen bleiben davon unabhängig erhalten.

Classic verwendet ausschließlich seine ursprünglichen Tabellen. Der neue Modus
gilt bei der nächsten Begegnung, auch ohne die Karte erneut zu betreten.

## Vollständigkeit

Die Kombination umfasst folgende Beschaffungswege:

- Gemeinsame Wildtabellen und die ursprünglichen Angeln.
- Normale Level- und Steinentwicklungen; die vorhandenen Mondsteine reichen
  für die vier benötigten Mondstein-Entwicklungen. Andere Steine sind kaufbar.
- Tauschentwicklungen über den Tausch-zurück-Trainer im Labor.
- Die ursprünglichen NPC-Tauschangebote, insbesondere Pantimos, Porenta,
  Schlurp und Rossana, mit im selben Spielstand beschaffbaren Tauschpartnern.
- Evoli, Kicklee und Nockchan als zusätzliche Spielhallenpreise; Porygon als
  ursprünglicher Preis. Evoli ist erneut erhältlich, sodass alle drei
  Entwicklungen möglich bleiben.
- Starter-Belohnungen bei Eich, ohne Beschränkung auf den ursprünglichen Starter.
- Amonitas und Kabuto als lebende Angelbegegnungen in der Azuria-Höhle.
- Aerodactyl aus dem ursprünglichen Altbernstein, Lapras als ursprüngliches
  Geschenk sowie die normalen stationären Pokémon und Mew am Lastwagen.

Es gibt damit für jede der 151 Arten einen Beschaffungsweg ohne externen Tausch.
Das ist keine Fanggarantie: einmalige Begegnungen bleiben bei Flucht/Besiegen
verbraucht. Zufällige Starter-Belohnungen können Wiederholungen liefern.

## Datenpflege und Tests

`tools/expanded_wild.py` erzeugt die zusätzlichen Slots direkt aus den beiden
Fassungen der bestehenden Map-Dateien. Nach einer Tabellenänderung mit
`python tools/expanded_wild.py` aktualisieren; `--check` prüft den Stand.

`tests/obtainability_check.py` prüft die tatsächlich gebauten Originaltabellen
und Zusatzslots in Rot und Blau. Ein Beschaffungsgraph verknüpft Wildfänge,
Geschenke, Preise, NPC-Tausch und Entwicklungen und muss alle 151 Arten erreichen.
Er bildet nicht den vollständigen Story-Durchlauf oder alle Verbrauchsentscheidungen ab.
Die Emulator-Tests prüfen zusätzlich die Wahl beider Versionen eines Slots
und die Classic-Sperre. Bestehende Tests für seltene Begegnungen und
Tauschentwicklungen laufen weiterhin mit.
