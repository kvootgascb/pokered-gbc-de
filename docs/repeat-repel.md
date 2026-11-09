# Schutz nach Ablauf erneut verwenden

In Erweitert folgt auf die normale Ablaufmeldung eine Ja/Nein-Frage, wenn
ein weiteres Exemplar derselben Schutzart im Beutel liegt. Zuerst bestätigt
der Spieler die Ablaufmeldung mit A/B. Danach erscheint die zweizeilige Frage
„Gleiche Schutzart erneut verwenden?“ mit direkter Ja/Nein-Auswahl, ohne
weiteren Bestätigungsdruck oder Text-Scroll. Bei Ja wird genau
ein Exemplar verwendet, bei Nein bleibt der Beutel unverändert. Nein oder B
schließt die Nachfrage sofort; die Ablaufmeldung muss nicht zusätzlich
weggeklickt werden.

- Schutz: 100 Schritte.
- Superschutz: 200 Schritte.
- Top-Schutz: 250 Schritte.

Andere Schutzarten werden nicht als Ersatz verwendet. Ohne passenden Vorrat
oder in Classic gibt es nur die ursprüngliche Ablaufmeldung. Das normale
Verhalten des Schutzes gegenüber dem Level des führenden Pokémon bleibt gleich.

Die zuletzt benutzte Schutzart wird an Payload-Offset 15 gespeichert, auch beim
normalen Einsatz in Classic. Dadurch ist ein späterer Moduswechsel möglich.
Das bestehende Schema bleibt Version 1, veröffentlichte Felder werden nicht
verschoben. Bei älteren Spielständen mit bereits aktivem Schutz und noch
unbekannter Schutzart erscheint beim ersten Ablauf keine zusätzliche Frage.
Ab dem nächsten normalen Einsatz ist die Art bekannt.

Die Emulator-Tests prüfen alle drei Dauern, die Entnahme aus dem richtigen
Beutelplatz, Speichern/Laden, Ablehnung, fehlenden Vorrat und Classic. Außerdem
wird der ursprüngliche letzte-Schritt-Handler mit Ablaufmeldung, Ja/Nein-Menü
und anschließendem erneuten Einsatz vollständig ausgeführt. Für jede Schutzart
wird auch geprüft, dass einmal Nein oder B ohne weitere Eingabe schließt.
