SECTION "Extra Pokemon Prizes", ROMX

ExtraPokemonPrizeShop::
	ld a, [wGameplayModeCache]
	and a
	ret z
	call ClearScreen
	hlcoord 0, 0
	lb bc, 10, 18
	call TextBoxBorder
	hlcoord 1, 1
	ld de, .title
	call PlaceString
	hlcoord 3, 3
	ld de, .choices
	call PlaceString
	xor a
	ldh [hUILayoutFlags], a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem], a
	ld [wMenuJoypadPollCount], a
	ld [wMenuWatchMovingOutOfBounds], a
	ld a, 3
	ld [wTopMenuItemY], a
	ld [wMaxMenuItem], a
	ld a, 2
	ld [wTopMenuItemX], a
	ld a, A_BUTTON | B_BUTTON
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	and B_BUTTON
	jr nz, .done
	ld a, [wCurrentMenuItem]
	cp 3
	jr z, .done
	ld [wPostgameAction], a
	call ValidateExtraPrizePurchase
	ld a, [wPostgameAction]
	cp 4
	ld hl, .notEnough
	jr z, .print
	cp 5
	ld hl, .full
	jr z, .print
	ld hl, .species
	ld a, [wPostgameAction]
	ld e, a
	ld d, 0
	add hl, de
	ld b, [hl]
	ld c, 25
	call GivePokemon
	jr nc, .done
	call LoadExtraPrizeCost
	ld hl, hCoins + 1
	ld de, wPlayerCoins + 1
	ld c, 2
	predef SubBCDPredef
	jr .done
.print
	call PrintText
.done
	scf
	ret
.title
	db "BESONDERE PREISE@"
.choices
	db "EVOLI     2500"
	next "KICKLEE   4600"
	next "NOCKCHAN  4600"
	next "ZURÜCK@"
.species
	db EEVEE, HITMONLEE, HITMONCHAN
.notEnough
	text "Du hast nicht"
	line "genug Münzen."
	done
.full
	text "Mach bitte einen"
	line "Platz im Team frei."
	done

ValidateExtraPrizePurchase:
	ld a, [wPartyCount]
	cp PARTY_LENGTH
	jr nc, .full
	call LoadExtraPrizeCost
	call HasEnoughCoins
	ret nc
	ld a, 4
	jr .result
.full
	ld a, 5
.result
	ld [wPostgameAction], a
	ret

LoadExtraPrizeCost:
	ld a, [wPostgameAction]
	and a
	ld a, $25
	jr z, .cost
	ld a, $46
.cost
	ldh [hCoins], a
	xor a
	ldh [hCoins + 1], a
	ret
