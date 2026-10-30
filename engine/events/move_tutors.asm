SECTION "Champion Move Tutors", ROMX

RefreshMoveTutorObjects::
	ld a, [wCurrentMapScriptFlags]
	bit 6, a
	ret z
	res 6, a
	ld [wCurrentMapScriptFlags], a
	ld a, [wGameplayModeCache]
	and a
	jr z, .hide
	ld a, [wNumHoFTeams]
	and a
	jr z, .hide
	ld a, HS_SS_ANNE_MOVE_DELETER
	ld [wMissableObjectIndex], a
	predef ShowObject
	ret
.hide
	ld a, HS_SS_ANNE_MOVE_DELETER
	ld [wMissableObjectIndex], a
	predef HideObject
	ret

MoveDeleterTalk::
	call TutorChampionWelcome
	ret c
	call SelectTutorPokemon
	ret c
	call GetTutorPartyMoves
	ld b, 0
.count
	ld a, [hli]
	and a
	jr z, .counted
	inc b
	ld a, b
	cp NUM_MOVES
	jr nz, .count
.counted
	ld a, b
	cp 2
	jr c, .lastMove
	ld hl, .question
	call PrintText
	ld a, 2
	ld [wMoveMenuType], a
	xor a
	ld [wPlayerMoveListIndex], a
	farcall MoveSelectionMenu
	ret nz
	ld a, [wPlayerMoveListIndex]
	ld [wTutorCandidate], a
	ld hl, .confirm
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	ret nz
	call DeleteTutorMove
	ld hl, .forgotten
	jp PrintText
.lastMove
	ld hl, .last
	jp PrintText
.question
	text "Welche Attacke soll"
	line "es vergessen?"
	prompt
.confirm
	text "Diese Attacke"
	line "wirklich vergessen?"
	prompt
.forgotten
	text "Die Attacke wurde"
	line "vergessen!"
	done
.last
	text "Die letzte Attacke"
	line "darf es behalten!"
	done

TutorChampionWelcome:
	ld a, [wGameplayModeCache]
	and a
	jr z, .unavailable
	ld a, [wNumHoFTeams]
	and a
	jr z, .unavailable
	ld hl, .welcome
	call PrintText
	and a
	ret
.unavailable
	ld hl, .voyage
	call PrintText
	scf
	ret
.welcome
	text "Wir kamen, um den"
	line "neuen CHAMPION"
	cont "kennenzulernen."
	para "Und nun bist Du"
	line "hier! Unsere Gabe"
	cont "hilft Dir gratis."
	prompt
.voyage
	text "Gute Fahrt!"
	done

SelectTutorPokemon:
	call SaveScreenTilesToBuffer2
	xor a
	ld [wUpdateSpritesEnabled], a
	ld [wPartyMenuTypeOrMessageID], a
	ld [wMenuItemToSwap], a
	call DisplayPartyMenu
	push af
	call GBPalWhiteOutWithDelay3
	call RestoreScreenTilesAndReloadTilePatterns
	call LoadGBPal
	pop af
	ret c
	ld a, [wWhichPokemon]
	ld [wTutorPartyIndex], a
	and a
	ret

GetTutorPartyMoves:
	ld hl, wPartyMon1Moves
	ld a, [wTutorPartyIndex]
	ld bc, wPartyMon2 - wPartyMon1
	jp AddNTimes

DeleteTutorMove:
	call GetTutorPartyMoves
	push hl
	ld a, [wTutorCandidate]
	ld e, a
	ld d, 0
	add hl, de
	call ShiftTutorMoveSlots
	pop hl
	ld bc, wPartyMon1PP - wPartyMon1Moves
	add hl, bc
	ld a, [wTutorCandidate]
	ld e, a
	ld d, 0
	add hl, de
ShiftTutorMoveSlots:
	ld d, h
	ld e, l
	inc hl
	ld a, [wTutorCandidate]
	ld b, a
	ld a, 3
	sub b
	jr z, .last
	ld b, a
.loop
	ld a, [hli]
	ld [de], a
	inc de
	dec b
	jr nz, .loop
.last
	xor a
	ld [de], a
	ret
