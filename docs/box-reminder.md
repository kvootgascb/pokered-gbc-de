# Hinweis auf die volle Pokémon-Box

Nur in Erweitert: Wenn ein erfolgreicher Wildfang bei vollem Team in die
aktuelle Box übertragen wird und diese damit ihre 20 Plätze belegt, denkt
der Protagonist nach der normalen Übertragungsmeldung:

> Ich sollte meine POKéMON-Box prüfen.
> Vielleicht ist sie schon voll ...

Es wird weder automatisch die Box gewechselt noch eine neue Fangmöglichkeit
geschaffen. Die ursprüngliche Sperre bei gleichzeitig vollem Team und voller
Box bleibt bestehen. Fänge ins Team, eine noch nicht volle Box und Classic
zeigen den zusätzlichen Text nicht. Beim späteren erneuten Füllen einer
geleerten oder anderen Box darf der Hinweis erneut erscheinen.

Ein neuer gespeicherter Zustand ist dafür nicht nötig: Der Hinweis wird nur
unmittelbar nach der Übertragung ausgelöst, die die Box füllt. Laden oder
Betreten eines Gebiets wiederholen ihn nicht. Das bereits reservierte Byte
`wFeatureBoxReminderState` bleibt unbenutzt; Saveformat und Version bleiben gleich.
