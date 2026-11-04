SECTION "Expanded Coin Purchases", ROMX

ExpandedCoinShop::
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wUpdateSpritesEnabled]
	push af
	call .shop
	pop af
	ld [wUpdateSpritesEnabled], a
	scf
	ret
.shop
	ld hl, wd730
	set 6, [hl] ; menu entries are not scrolling dialogue
	xor a
	ldh [hUILayoutFlags], a
	ld [wUpdateSpritesEnabled], a
	call HideSprites
	call ClearScreen
	hlcoord 0, 0
	lb bc, 8, 18
	call TextBoxBorder
	hlcoord 1, 1
	ld de, .title
	call PlaceString
	hlcoord 3, 3
	ld de, .choices
	call PlaceString
	ld hl, wd730
	res 6, [hl]
	xor a
	ldh [hUILayoutFlags], a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem], a
	ld [wMenuWatchMovingOutOfBounds], a
	ld [wMenuJoypadPollCount], a
	ld a, 3
	ld [wTopMenuItemY], a
	ld a, 2
	ld [wTopMenuItemX], a
	ld [wMaxMenuItem], a
	ld a, A_BUTTON | B_BUTTON
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	and B_BUTTON
	jr nz, .handled
	ld a, [wCurrentMenuItem]
	cp 2
	jr z, .handled
	ld [wPostgameAction], a
	call BuyExpandedCoins
	ld a, [wPostgameAction]
	ld hl, .success
	cp 2
	jr z, .print
	ld hl, .money
	cp 3
	jr z, .print
	ld hl, .full
	cp 4
	jr z, .print
	ld hl, .case
.print
	call PrintText
.handled
	scf
	ret
.title
	db "MÜNZEN / GELD@"
.choices
	db "50 FÜR 1000"
	next "500 FÜR 10000"
	next "ZURÜCK@"
.success
	text "Hier sind die"
	line "gekauften Münzen!"
	done
.money
	text "Das Geld reicht"
	line "leider nicht aus."
	done
.full
	text "Dein Münzkorb hat"
	line "zu wenig Platz."
	done
.case
	text "Du brauchst einen"
	line "MÜNZKORB!"
	done

; Action 0: 50/1000; 1: 500/10000. Returns result 2..5 in action.
BuyExpandedCoins:
	ld b, COIN_CASE
	call IsItemInBag
	jr z, .noCase
	ld a, [wPostgameAction]
	and a
	ld a, $99
	jr z, .smallLimit
	ld a, $95
.smallLimit
	ldh [hCoins], a
	ld a, [wPostgameAction]
	and a
	ld a, $50
	jr z, .limit
	xor a
.limit
	ldh [hCoins + 1], a
	call HasEnoughCoins
	jr nc, .noRoom
	call .setMoney
	call HasEnoughMoney
	jr c, .noMoney
	call .setMoney
	ld hl, hMoney + 2
	ld de, wPlayerMoney + 2
	ld c, 3
	predef SubBCDPredef
	ld a, [wPostgameAction]
	and a
	ld a, 5
	jr nz, .large
	xor a
.large
	ldh [hCoins], a
	ld a, [wPostgameAction]
	and a
	ld a, $50
	jr z, .amount
	xor a
.amount
	ldh [hCoins + 1], a
	ld de, wPlayerCoins + 1
	ld hl, hCoins + 1
	ld c, 2
	predef AddBCDPredef
	ld a, 2
	jr .result
.noMoney
	ld a, 3
	jr .result
.noRoom
	ld a, 4
	jr .result
.noCase
	ld a, 5
.result
	ld [wPostgameAction], a
	ret
.setMoney
	xor a
	ldh [hMoney], a
	ldh [hMoney + 1], a
	ldh [hMoney + 2], a
	ld a, [wPostgameAction]
	and a
	jr z, .thousand
	ld a, 1
	ldh [hMoney], a
	ret
.thousand
	ld a, $10
	ldh [hMoney + 1], a
	ret
