# VMs per Ansprechen

Nur in Erweitert: A vor einem zerschneidbaren Busch oder am Wasser bietet
eine Ja/Nein-Frage an. Der normale Fels-Dialog bietet entsprechend Stärke an.
Das erste passende Team-Pokémon wird gewählt; die VM muss tatsächlich zu seinen
vier Attacken gehören. Wie im ursprünglichen VM-Menü werden keine AP verbraucht.

| Aktion | Voraussetzung |
| --- | --- |
| Zerschneider | Quellorden, Team-Pokémon mit Zerschneider, echter Busch im Freien oder in Erikas Arena |
| Surfer | Seelenorden, Team-Pokémon mit Surfer, passende Wasser-/Uferkachel |
| Stärke | Farborden, Team-Pokémon mit Stärke, ansprechbarer Schiebefels |

NPCs, Schilder und versteckte Ereignisse behalten Vorrang vor der zusätzlichen
Kachelprüfung. Normales Gras löst keinen Zerschneider-Dialog aus. Beim Surfen
bleibt der normale Ausstieg per Bewegung erhalten; A aktiviert dort nicht erneut
Surfer. Alle drei ursprünglichen Menüeinträge bleiben nutzbar.

Bereits eingesammelte versteckte Items verbrauchen in Erweitert keinen weiteren
A-Tastendruck. Dadurch wird nach dem Einsammeln wieder die normale Prüfung auf
Bücherregale, Schilder, NPCs und Feld-VMs erreicht. Noch vorhandene Items behalten
ihren Vorrang; ein voller Beutel darf nicht als eingesammeltes Item gelten.
Classic behält die ursprüngliche Behandlung der versteckten Fundstelle.
Der konkrete Fall ist der Busch mit dem versteckten Trank in Vertania bei (14,4):
zuerst den Trank nehmen, beim nächsten A Zerschneider anbieten.

Die Ausführung verwendet die ursprünglichen Routinen: Zerschneider ersetzt den
Kartenblock, Surfer prüft weiterhin Radweg, Strömung und Kachel-Kollisionen und
setzt den normalen Einstiegsschritt, Stärke aktiviert den normalen Schiebeablauf.
Stärke gilt weiterhin nur bis zum natürlichen Zurücksetzen beim Kartenwechsel.
Classic erhält keine zusätzlichen Angebote. Es sind keine neuen Save-Felder nötig.

Beim direkten Ansprechen eines Buschs wird nach Ja die Karte ohne Weißblende
wiederhergestellt. Dieser Weg steigt direkt in den gemeinsamen Schnittablauf
ein: Der Kartenblock, der Einsatztext und die optionale Schnittanimation
bleiben erhalten. Der ursprüngliche Einstieg über das Pokémon-Menü behält
seinen bisherigen Ausblend-/Grafik-Wiederherstellungsablauf; er wird für die
direkte A-Interaktion nicht mehr unnötig wiederverwendet.

`tests/player_gender_smoke.py` prüft Modus, Orden, Kachel und Attackenbesitz,
einschließlich eines passenden Pokémon an zweiter Teamposition. Auf echten
Karten wird ein Busch auf Route 2 entfernt, in Alabastia Surfer benutzt und auf
den Seeschauminseln Stärke aktiviert und ein Fels geschoben. Weitere Checks
prüfen den Vorrang von Schild/NPC sowie Ablehnung und gesperrte Stärke-Nutzung.
Für Zerschneider läuft die echte A-/Ja-Interaktion mit VM-Animationen an und
aus sowie die Ablehnung mit Nein. Die Prüfung erfasst jeden gerenderten Frame
im oberen Kartenbereich und Aufrufe der Weißblende: Bei der direkten
Interaktion dürfen weder eine Weißblende noch weiße Kartenframes auftreten.
Der ursprüngliche Menü-Einstieg wird weiterhin separat mit seinem bisherigen
Übergang und unverändertem Schnitteffekt geprüft.
Für den Vertania-Busch wird zusätzlich die echte Item-Aufnahme vor dem Schnitt
ausgeführt sowie der Fall eines bereits gesetzten Fundflags. Das Item wird
nicht doppelt vergeben; Classic bietet weiterhin keine Kontext-VM an.
