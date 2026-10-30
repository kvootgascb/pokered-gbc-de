# Basis-Item auf Select

Nur in Erweitert: Im Beutel ein geeignetes Basis-Item auswählen, dann
**REGISTRIEREN** wählen. Außerhalb der Menüs benutzt ein kurzer Druck auf
**Select** das registrierte Item. Es gibt einen gemeinsamen Platz.

Unterstützt werden Fahrrad, Angel, Profiangel, Superangel, Detektor,
Pokéflöte und Karte. Verbrauchsitems und andere Schlüsselitems sind nicht
registrierbar. Das zusätzliche Item-Menü enthält **BENUTZEN**,
**REGISTRIEREN** und **ZURÜCK**. Bei dem schon registrierten Item steht
stattdessen **ABMELDEN**. Ein anderes Item zu registrieren ersetzt die Auswahl.

Die Auswahl wird beim normalen Speichern gesichert und bleibt beim Wechsel
auf Classic erhalten, ist dort aber inaktiv. Ein in den PC gelegtes Item kann
nicht über Select benutzt werden; eine Meldung weist darauf hin. Die
Registrierung bleibt für die spätere Rücknahme aus dem PC erhalten.

Der Effekt nutzt die ursprünglichen Item-Routinen. Fahrradverbote,
Angelvoraussetzungen und die Pflicht zum Radfahren auf dem Radweg gelten
weiterhin. Skriptbewegungen, Linkräume und Kämpfe aktivieren den Shortcut nicht.
Select innerhalb von Menüs behält seine dortige Bedeutung, insbesondere den
Zugang zum Geheimmenü unter OPTION. Außerhalb von Menüs zählt Select allein.

## Speicher und Tests

Der bestehende Payload-Eintrag an Offset 2 wird verwendet; neue Felder oder ein
neuer Spielstand sind nicht nötig. `tests/player_gender_smoke.py` prüft die
Registrierung aller unterstützten Items, Ersatz/Abmeldung, Ablehnung von
Verbrauchsitems und Classic sowie Speichern/Laden. Der Test registriert das
Fahrrad durch den echten Beutel-Dialog und steigt anschließend mit Select auf
und ab. Fehlendes Item und die Radweg-Sperre werden ebenfalls geprüft.
