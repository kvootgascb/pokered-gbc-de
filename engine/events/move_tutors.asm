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
	ld a, HS_SS_ANNE_MOVE_REMINDER
	ld [wMissableObjectIndex], a
	predef ShowObject
	ld a, HS_SS_ANNE_MERCHANT
	ld [wMissableObjectIndex], a
	predef ShowObject
	ret
.hide
	ld a, HS_SS_ANNE_MOVE_DELETER
	ld [wMissableObjectIndex], a
	predef HideObject
	ld a, HS_SS_ANNE_MOVE_REMINDER
	ld [wMissableObjectIndex], a
	predef HideObject
	ld a, HS_SS_ANNE_MERCHANT
	ld [wMissableObjectIndex], a
	predef HideObject
	ret

MoveDeleterTalk::
	ld a, [wUpdateSpritesEnabled]
	push af
	call .talk
	pop af
	ld [wUpdateSpritesEnabled], a
	ret
.talk
	call TutorChampionWelcome
	ret c
	ld hl, .offer
	call ConfirmTutorService
	ret nz
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
	call ConfirmTutorService
	ret nz
	call DeleteTutorMove
	ld hl, .forgotten
	jp PrintText
.lastMove
	ld hl, .last
	jp PrintText
.offer
	text "Soll ein #MON"
	line "eine Attacke"
	cont "vergessen?"
	prompt
.question
	text "Welche Attacke"
	line "vergessen?"
	prompt
.confirm
	text "Attacke wirklich"
	line "vergessen?"
	prompt
.forgotten
	text "Die Attacke wurde"
	line "vergessen!"
	done
.last
	text "Die letzte Attacke"
	line "darf es behalten!"
	done

ConfirmTutorService:
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	ret z
	; The No/B choice already dismissed this dialogue; do not wait again.
	jp DisableWaitingAfterTextDisplay

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
	text "Wir sind Zwillinge"
	para "Wir kamen, um den"
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
	; The party menu restores map sprites. Keep them off the tutor's menus.
	xor a
	ld [wUpdateSpritesEnabled], a
	call HideSprites
	; A successful selection opens a dedicated move menu, not a partial map.
	pop af
	push af
	call nc, ClearScreen
	call LoadGBPal
	pop af
	jr nc, .selected
	; B already cancelled the party menu. Dismiss the enclosing NPC text too.
	call DisableWaitingAfterTextDisplay
	scf
	ret
.selected
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

MoveReminderTalk::
	ld a, [wUpdateSpritesEnabled]
	push af
	call .talk
	pop af
	ld [wUpdateSpritesEnabled], a
	ret
.talk
	call TutorChampionWelcome
	ret c
	ld hl, .offer
	call ConfirmTutorService
	ret nz
	call SelectTutorPokemon
	ret c
	call BuildTutorMoveList
	ld a, [wTutorMoveCount]
	and a
	jr z, .none
	ld hl, .choose
	call PrintText
	ld hl, wTutorMoveCount
	ld a, l
	ld [wListPointer], a
	ld a, h
	ld [wListPointer + 1], a
	ld a, MOVESLISTMENU
	ld [wListMenuID], a
	ld a, MOVE_NAME
	ld [wNameListType], a
	xor a
	ld [wPrintItemPrices], a
	ld [wListScrollOffset], a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem], a
	call DisplayListMenuID
	ret c
	ld a, [wcf91]
	ld [wTutorCandidate], a
	ld a, [wTutorPartyIndex]
	ld [wWhichPokemon], a
	ld a, [wTutorCandidate]
	ld [wMoveNum], a
	predef LearnMove
	ret
.none
	ld hl, .noMoves
	jp PrintText
.offer
	text "Soll ein #MON"
	line "sich an eine"
	cont "Attacke erinnern?"
	prompt
.choose
	text "Welche Attacke"
	line "wieder lernen?"
	prompt
.noMoves
	text "Es erinnert sich"
	line "an alle passenden"
	cont "Attacken bereits."
	done

BuildTutorMoveList:
	xor a
	ld [wTutorMoveCount], a
	ld a, $ff
	ld [wTutorMoves], a
	ld hl, wPartyMon1
	ld a, [wTutorPartyIndex]
	ld bc, wPartyMon2 - wPartyMon1
	call AddNTimes
	ld a, [hl]
	ld [wTutorSpecies], a
	ld hl, wPartyMon1Level
	ld a, [wTutorPartyIndex]
	ld bc, wPartyMon2 - wPartyMon1
	call AddNTimes
	ld a, [hl]
	ld [wTutorLevel], a
	ld a, 3
	ld [wTutorChainDepth], a
.chain
	call CollectTutorSpeciesMoves
	call FindTutorPreEvolution
	and a
	ret z
	ld [wTutorSpecies], a
	ld hl, wTutorChainDepth
	dec [hl]
	jr nz, .chain
	ret

CollectTutorSpeciesMoves:
	ld a, [wTutorSpecies]
	ld [wd0b5], a
	call GetMonHeader
	ld hl, wMonHMoves
	ld b, NUM_MOVES
.base
	push bc
	push hl
	ld a, [hl]
	call AddTutorMove
	pop hl
	pop bc
	inc hl
	dec b
	jr nz, .base
	ld a, [wTutorSpecies]
	call PointTutorRecord
.skipEvolutions
	call ReadTutorByte
	and a
	jr z, .learnset
	cp EVOLVE_ITEM
	call z, ReadTutorByte
	call ReadTutorByte
	call ReadTutorByte
	jr .skipEvolutions
.learnset
	call ReadTutorByte
	and a
	ret z
	ld [wTutorRecordLevel], a
	call ReadTutorByte
	ld c, a
	ld a, [wTutorRecordLevel]
	ld b, a
	ld a, [wTutorLevel]
	cp b
	jr c, .learnset
	ld a, c
	call AddTutorMove
	jr .learnset

AddTutorMove:
	and a
	ret z
	ld [wTutorCandidate], a
	call GetTutorPartyMoves
	ld b, NUM_MOVES
.known
	ld a, [wTutorCandidate]
	cp [hl]
	ret z
	inc hl
	dec b
	jr nz, .known
	ld a, [wTutorMoveCount]
	ld b, a
	ld hl, wTutorMoves
	and a
	jr z, .append
.duplicate
	ld a, [wTutorCandidate]
	cp [hl]
	ret z
	inc hl
	dec b
	jr nz, .duplicate
.append
	ld a, [wTutorMoveCount]
	cp 64
	ret nc
	inc a
	ld [wTutorMoveCount], a
	ld a, [wTutorCandidate]
	ld [hli], a
	ld [hl], $ff
	ret

PointTutorRecord:
	dec a
	ld b, 0
	add a
	rl b
	ld c, a
	ld hl, EvosMovesPointerTable
	add hl, bc
	ld de, wTutorRecordPtr
	ld bc, 2
	ld a, BANK(EvosMovesPointerTable)
	jp FarCopyData

ReadTutorByte:
	ld a, [wTutorRecordPtr]
	ld l, a
	ld a, [wTutorRecordPtr + 1]
	ld h, a
	ld de, wBuffer
	ld bc, 1
	ld a, BANK(EvosMovesPointerTable)
	call FarCopyData
	ld hl, wTutorRecordPtr
	inc [hl]
	jr nz, .noCarry
	inc hl
	inc [hl]
.noCarry
	ld a, [wBuffer]
	ret

FindTutorPreEvolution:
	ld a, 1
	ld [wTutorScanSpecies], a
.scan
	ld a, [wTutorScanSpecies]
	dec a
	ld c, a
	ld b, 0
	ld hl, PokedexOrder
	add hl, bc
	ld de, wBuffer
	ld bc, 1
	ld a, BANK(PokedexOrder)
	call FarCopyData
	ld a, [wBuffer]
	and a ; unused species indexes must not enter GetMonHeader
	jr z, .next
	ld a, [wTutorScanSpecies]
	call PointTutorRecord
.evolution
	call ReadTutorByte
	and a
	jr z, .next
	cp EVOLVE_ITEM
	call z, ReadTutorByte
	call ReadTutorByte
	call ReadTutorByte
	ld c, a
	ld a, [wTutorSpecies]
	cp c
	jr z, .found
	jr .evolution
.next
	ld hl, wTutorScanSpecies
	inc [hl]
	ld a, [hl]
	cp NUM_POKEMON_INDEXES + 1
	jr c, .scan
	xor a
	ret
.found
	ld a, [wTutorScanSpecies]
	ret
