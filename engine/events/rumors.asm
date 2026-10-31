SECTION "Rumor NPCs", ROMX

; LoadMapHeader calls this before sprites are drawn. Append only the new
; objects, so no existing hide/show ID or saved flag changes its meaning.
PrepareRumorObjects::
	ld a, [wCurMap]
	ld hl, .pallet
	cp PALLET_TOWN
	jr z, .selected
	ld hl, .rockTunnel
	cp ROCK_TUNNEL_POKECENTER
	jr z, .selected
	ld hl, .cinnabar
	cp CINNABAR_ISLAND
	jr z, .selected
	ld hl, .shore
	cp VERMILION_CITY
	ret nz
.selected
	push hl
	call RumorObjectsVisible
	ld b, FLAG_SET ; hidden
	jr nc, .visibility
	ld b, FLAG_RESET
.visibility
	pop hl
	ld de, wMissableObjectList
.findEnd
	ld a, [de]
	cp -1
	jr z, .append
	inc de
	inc de
	jr .findEnd
.append
	ld a, [hli]
	cp -1
	jr z, .done
	ld [de], a
	inc de
	ld a, [hli]
	ld [de], a
	inc de
	ld c, a
	push hl
	ld hl, wMissableObjectFlags
	predef FlagActionPredef
	pop hl
	jr .append
.done
	ld [de], a
	ret
.pallet
	db PALLETTOWN_RUMOR_TRAINER, HS_PALLET_RUMOR_TRAINER, -1
.rockTunnel
	db ROCKTUNNELPOKECENTER_RUMOR_HIKER, HS_ROCK_TUNNEL_RUMOR_HIKER, -1
.cinnabar
	db CINNABARISLAND_RUMOR_FISHER, HS_CINNABAR_RUMOR_FISHER, -1
.shore
	db VERMILIONCITY_SHORE_SAILOR1, HS_VERMILION_SHORE_SAILOR1
	db VERMILIONCITY_SHORE_SAILOR2, HS_VERMILION_SHORE_SAILOR2
	db VERMILIONCITY_SHORE_SAILOR3, HS_VERMILION_SHORE_SAILOR3
	db VERMILIONCITY_SHORE_SAILOR4, HS_VERMILION_SHORE_SAILOR4, -1

; Carry = show this map's new NPCs. No new persistent state is required.
RumorObjectsVisible:
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wCurMap]
	cp VERMILION_CITY
	jr z, .shore
	cp PALLET_TOWN
	jr nz, .show
	ld a, [wNumHoFTeams]
	and a
	ret z
.show
	scf
	ret
.shore
	ld a, [wNumHoFTeams]
	and a
	ret z
	; Derive the same single opportunity as the existing harbor access. This
	; also initializes old champion saves once, without stacking visits.
	farcall EnsureChampionFeatures
	ld hl, wFeatureAnneState
	read_feature_byte
	ld a, c
	cp 1
	jr z, .show
	and a
	ret

; D/E are the intended Y/X tile deltas. Only listed new NPCs are limited to
; one tile left/right of their starting position. The original NPCs keep
; the native movement rules, including their original wandering behavior.
RumorNPCWalkBlocked::
	ld hl, RumorWalkBounds
.find
	ld a, [hli]
	cp -1
	jr z, .allowed
	ld c, a
	ld a, [wCurMap]
	cp c
	jr nz, .skip3
	ld c, [hl]
	inc hl
	ldh a, [hCurrentSpriteOffset]
	swap a
	cp c
	jr nz, .skip2
	ld a, [hli]
	add 3 ; map coordinates store +4; lower bound = anchor - 1 + 4
	ld c, a
	push hl
	ld h, HIGH(wSpriteStateData2)
	ldh a, [hCurrentSpriteOffset]
	add SPRITESTATEDATA2_MAPY
	ld l, a
	ld a, [hl]
	add d
	sub c
	cp 1 ; keep the original row; all new patrols are horizontal
	pop hl
	jr nz, .blocked
	ld a, [hl]
	add 3
	ld c, a
	ld h, HIGH(wSpriteStateData2)
	ldh a, [hCurrentSpriteOffset]
	add SPRITESTATEDATA2_MAPX
	ld l, a
	ld a, [hl]
	add e
	sub c
	cp 3
	jr nc, .blocked
.allowed
	and a
	ret
.blocked
	scf
	ret
.skip3
	inc hl
.skip2
	inc hl
	inc hl
	jr .find

RumorWalkBounds:
	; map, object, anchor Y, anchor X
	db PALLET_TOWN, PALLETTOWN_RUMOR_TRAINER, 10, 17
	db ROCK_TUNNEL_POKECENTER, ROCKTUNNELPOKECENTER_RUMOR_HIKER, 5, 8
	db CINNABAR_ISLAND, CINNABARISLAND_RUMOR_FISHER, 13, 8
	db VERMILION_CITY, VERMILIONCITY_SHORE_SAILOR1, 5, 13
	db VERMILION_CITY, VERMILIONCITY_SHORE_SAILOR2, 14, 7
	db VERMILION_CITY, VERMILIONCITY_SHORE_SAILOR3, 14, 25
	db -1

OakRumorTalk::
	ld hl, .text
	jp PrintText
.text
	text "Hast du schon"
	line "gehört?"
	para "Professor EICH war"
	line "früher ein starker"
	cont "Trainer."
	para "Neulich habe ich"
	line "ihn wieder seine"
	cont "alten #BÄLLE"
	cont "polieren sehen ..."
	done

MewRumorTalk::
	ld hl, .text
	jp PrintText
.text
	text "Hast du schon"
	line "gehört?"
	para "Letztes Jahr bin"
	line "ich mit der"
	cont "M.S. ANNE"
	cont "gefahren."
	para "Beim Einsteigen"
	line "sah ich einen"
	cont "Schatten unter dem"
	cont "Lastwagen huschen."
	para "Keine Ahnung, was"
	line "das war. Von der"
	cont "Farbe her hätte es"
	cont "ein FLEGMON sein"
	cont "können ..."
	done

FossilRumorTalk::
	ld hl, .text
	jp PrintText
.text
	text "Hast du schon"
	line "gehört?"
	para "Ein Forscher aus"
	line "dem Labor meint,"
	para "tief in einer"
	line "Höhle würden noch"
	cont "lebende Fossil-"
	cont "#MON anbeißen!"
	para "Warum suchen die"
	line "dann hier in"
	cont "alten Steinen?"
	done

SurfPikachuRumorTalk::
	ld hl, .text
	jp PrintText
.text
	text "Hast du schon"
	line "gehört?"
	para "Vom Deck aus habe"
	line "ich eine ganze"
	cont "Gruppe PIKACHU"
	cont "zum KRAFTWERK"
	cont "schwimmen sehen!"
	para "Ich konnte meinen"
	line "Augen nicht"
	cont "trauen!"
	para "Die anderen"
	line "glauben mir bis"
	cont "heute kein Wort!"
	done

ShoreSailorFeetTalk::
	ld hl, .text
	jp PrintText
.text
	text "Endlich wieder"
	line "festen Boden unter"
	cont "den Füßen!"
	done

ShoreSailorSuppliesTalk::
	ld hl, .text
	jp PrintText
.text
	text "Vor der Abfahrt"
	line "muss ich noch"
	cont "Proviant besorgen."
	para "Auf See gibt es"
	line "keinen Laden!"
	done

ShoreSailorHarborTalk::
	ld hl, .text
	jp PrintText
.text
	text "Ein bisschen"
	line "Landgang tut gut!"
	para "Danach geht es"
	line "zurück an Bord."
	done
