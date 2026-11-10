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
	xor a
	ldh [hUILayoutFlags], a
	ld [wUpdateSpritesEnabled], a
	call HideSprites
	; Snapshot affordability once when opening the dialogue. Menu index 0
	; is the large bundle only when it is offered; purchase actions stay 0/1.
	ld a, 1
	ld [wPostgameAction], a
	call BuyExpandedCoins.setMoney
	call HasEnoughMoney
	ld a, 1 ; small bundle + Back
	jr c, .optionsReady
	inc a ; large bundle + small bundle + Back
.optionsReady
	push af
	ld hl, .question
	call PrintText
	callfar GameCornerDrawCoinBox
	pop af
	ld [wMaxMenuItem], a
	add a
	add 3
	ld b, a ; five/seven interior rows, matching two-row bundle entries
	ld c, 9
	hlcoord 0, 0
	call TextBoxBorder
	ld hl, wd730
	set 6, [hl]
	hlcoord 1, 1
	ld de, .title
	call PlaceString
	ld a, [wMaxMenuItem]
	cp 2
	ld de, .smallChoices
	jr nz, .drawChoices
	ld de, .largeChoices
.drawChoices
	; Amount, price below it; cursor advances two rows like a normal mart.
	ldh a, [hUILayoutFlags]
	set 2, a
	ldh [hUILayoutFlags], a
	hlcoord 2, 2
	call PlaceString
	ld hl, wd730
	res 6, [hl]
	xor a
	ldh [hUILayoutFlags], a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem], a
	ld [wMenuWatchMovingOutOfBounds], a
	ld [wMenuJoypadPollCount], a
	ld a, 2
	ld [wTopMenuItemY], a
	ld a, 1
	ld [wTopMenuItemX], a
	ld a, A_BUTTON | B_BUTTON
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	and B_BUTTON
	jr nz, .cancel
	ld a, [wCurrentMenuItem]
	ld hl, wMaxMenuItem
	cp [hl]
	jr z, .cancel
	ld a, [hl]
	cp 2
	ld a, 0
	jr nz, .buy
	ld a, [wCurrentMenuItem]
	xor 1 ; first row = 500, second row = 50
.buy
	ld [wPostgameAction], a
	call BuyExpandedCoins
	callfar GameCornerDrawCoinBox
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
	scf
	ret
.cancel
	ld hl, .farewell
	jr .print
.title
	db "KAUF@"
.largeChoices
	db "500"
	next " ¥10000"
	next "50"
	next " ¥1000"
	next "ZURÜCK@"
.smallChoices
	db "50"
	next " ¥1000"
	next "ZURÜCK@"
.question
	text "Willkommen"
	line "in der ROCKET"
	cont "SPIELHALLE!"
	para "Benötigst Du"
	line "Spiel-Münzen?"
	done
.success
	text "Danke! Hier sind"
	line "Deine Münzen!"
	done
.farewell
	text_far _GameCornerClerk1PleaseComePlaySometimeText
	text_end
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
