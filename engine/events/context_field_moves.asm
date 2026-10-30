SECTION "Context Field Moves", ROMX

; Called only after hidden objects, signs and NPCs have declined A.
CheckContextFieldMove::
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wWalkBikeSurfState]
	cp 2
	jr z, .unavailable
	predef GetTileAndCoordsInFrontOfPlayer
	ld a, [wCurMapTileset]
	and a ; OVERWORLD
	jr z, .outdoors
	cp GYM
	jr nz, .water
	ld a, [wTileInFrontOfPlayer]
	cp $50
	jr z, .cut
	jr .water
.outdoors
	ld a, [wTileInFrontOfPlayer]
	cp $3d ; tree, not ordinary grass
	jr nz, .water
.cut
	ld a, [wObtainedBadges]
	bit BIT_CASCADEBADGE, a
	jr z, .unavailable
	ld a, 1
	ld [wPostgameAction], a
	ld a, CUT
	jr .find
.water
	ld a, [wObtainedBadges]
	bit BIT_SOULBADGE, a
	jr z, .unavailable
	farcall IsNextTileShoreOrWater
	jr c, .unavailable
	ld a, 2
	ld [wPostgameAction], a
	ld a, SURF
.find
	ld [wTutorCandidate], a
	call FindPartyFieldMove
	ret nc
	call SaveScreenTilesToBuffer2
	scf
	ret
.unavailable
	and a
	ret

FindPartyFieldMove::
	ld a, [wPartyCount]
	and a
	ret z
	ld b, a
	ld c, 0
	ld hl, wPartyMon1Moves
.mon
	push hl
	ld d, NUM_MOVES
.move
	ld a, [wTutorCandidate]
	cp [hl]
	jr z, .found
	inc hl
	dec d
	jr nz, .move
	pop hl
	ld de, wPartyMon2 - wPartyMon1
	add hl, de
	inc c
	dec b
	jr nz, .mon
	and a
	ret
.found
	pop hl
	ld a, c
	ld [wTutorPartyIndex], a
	scf
	ret

ContextBoulderText::
	text_asm
	call TryContextStrength
	jp c, TextScriptEnd
	ld hl, .original
	call PrintText
	jp TextScriptEnd
.original
	text_far _BoulderText
	text_end

TryContextStrength::
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wd728]
	bit 0, a
	jr nz, .active
	ld a, [wObtainedBadges]
	bit BIT_RAINBOWBADGE, a
	jr z, .unavailable
	ld a, STRENGTH
	ld [wTutorCandidate], a
	call FindPartyFieldMove
	ret nc
	ld a, 3
	ld [wPostgameAction], a
	call ContextFieldMoveDialogue
	scf
	ret
.active
	ld hl, .activeText
	call PrintText
	scf
	ret
.unavailable
	and a
	ret
.activeText
	text "Die Felsen lassen"
	line "sich nun bewegen."
	done

ContextFieldMoveDialogue::
	ld a, [wPostgameAction]
	ld hl, .cutQuestion
	dec a
	jr z, .ask
	ld hl, .surfQuestion
	dec a
	jr z, .ask
	ld hl, .strengthQuestion
.ask
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	ret nz
	call PrepareContextPokemon
	ld a, [wPostgameAction]
	dec a
	jr z, .cut
	dec a
	jr z, .surf
	predef PrintStrengthTxt
	ret
.cut
	predef UsedCut
	ret
.surf
	farcall IsSurfingAllowed
	ld hl, wd728
	bit 1, [hl]
	res 1, [hl]
	ret z
	; The native boarding routine takes its simulated step from this direction.
	ld a, [wSpritePlayerStateData1FacingDirection]
	srl a
	srl a
	ld e, a
	ld d, 0
	ld hl, .directions
	add hl, de
	ld a, [hl]
	ld [wPlayerDirection], a
	ld a, SURFBOARD
	ld [wcf91], a
	ld [wPseudoItemID], a
	jp UseItem
.directions
	db PLAYER_DIR_DOWN, PLAYER_DIR_UP, PLAYER_DIR_LEFT, PLAYER_DIR_RIGHT
.cutQuestion
	text "Diesen Busch"
	line "zerschneiden?"
	prompt
.surfQuestion
	text "Möchtest Du hier"
	line "SURFER einsetzen?"
	prompt
.strengthQuestion
	text "Möchtest Du"
	line "STÄRKE einsetzen?"
	prompt

PrepareContextPokemon:
	ld a, [wTutorPartyIndex]
	ld [wWhichPokemon], a
	ld c, a
	ld b, 0
	ld hl, wPartySpecies
	add hl, bc
	ld a, [hl]
	ld [wcf91], a
	ld a, c
	ld hl, wPartyMonNicks
	jp GetPartyMonName

PUSHS
SECTION "Context Field Move Text Entry", ROM0
DisplayContextFieldMove::
	farcall ContextFieldMoveDialogue
	jp HoldTextDisplayOpen
POPS
