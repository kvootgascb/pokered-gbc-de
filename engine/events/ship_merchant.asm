SECTION "Champion Ship Merchant", ROMX

ShipMerchantTalk::
	call ShipMerchantAvailable
	jp nc, .unavailable
	ld hl, .welcome
	call PrintText
	xor a
	ld [wTutorCandidate], a
.menu
	call ClearScreen
	hlcoord 0, 0
	lb bc, 14, 18
	call TextBoxBorder
	hlcoord 1, 1
	ld de, .title
	call PlaceString
	hlcoord 2, 3
	ld de, .choices
	call PlaceString
	hlcoord 2, 17
	ld de, .moneyLabel
	call PlaceString
	hlcoord 11, 17
	ld de, wPlayerMoney
	ld c, MONEY_SIGN | 3
	call PrintBCDNumber
	xor a
	ldh [hUILayoutFlags], a
	ld [wLastMenuItem], a
	ld [wMenuJoypadPollCount], a
	ld [wMenuWatchMovingOutOfBounds], a
	ld a, [wTutorCandidate]
	ld [wCurrentMenuItem], a
	ld a, 3
	ld [wTopMenuItemY], a
	ld a, 1
	ld [wTopMenuItemX], a
	ld a, 5
	ld [wMaxMenuItem], a
	ld a, A_BUTTON | B_BUTTON
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	and B_BUTTON
	ret nz
	ld a, [wCurrentMenuItem]
	cp 5
	ret z
	ld [wTutorCandidate], a
	call PlaceUnfilledArrowMenuCursor
	ld hl, .confirm
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	jr nz, .menu
	call BuyShipMerchantItem
	ld a, [wPostgameAction]
	ld hl, .success
	cp 1
	jr z, .message
	ld hl, .poor
	cp 2
	jr z, .message
	ld hl, .full
.message
	call PrintText
	call WaitForTextScrollButtonPress
	jp .menu
.unavailable
	ld hl, .voyage
	jp PrintText
.welcome
	text "Von meinen Reisen"
	line "bringe ich seltene"
	cont "Vorräte mit."
	para "Für einen CHAMPION"
	line "nur das Beste!"
	prompt
.title
	db "REISEVORRÄTE@"
.choices
	db "AP-PLUS     20000"
	next "TOP-ÄTHER    3000"
	next "ELIXIER      5000"
	next "TOP-ELIXIER 10000"
	next "MONDSTEIN    5000"
	next "ZURÜCK@"
.moneyLabel
	db "GELD@"
.confirm
	text "Ein Exemplar"
	line "davon kaufen?"
	prompt
.success
	text "Bitte sehr!"
	line "Gute Reise!"
	done
.poor
	text "Dafür reicht Dein"
	line "Geld nicht aus."
	done
.full
	text "In Deinem Beutel"
	line "ist kein Platz."
	done
.voyage
	text "Gute Reise!"
	done

ShipMerchantAvailable:
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wNumHoFTeams]
	and a
	ret z
	scf
	ret

; Selected stock entry is wTutorCandidate. Result: 1 bought, 2 insufficient
; funds, 3 no inventory room, 4 not available. Never charge on a failed add.
BuyShipMerchantItem::
	call ShipMerchantAvailable
	jr nc, .locked
	ld a, [wTutorCandidate]
	cp 5
	jr nc, .locked
	call LoadShipMerchantCost
	call HasEnoughMoney
	jr c, .poor
	ld a, [wTutorCandidate]
	ld hl, ShipMerchantStock
	ld bc, 4
	call AddNTimes
	ld a, [hl]
	ld [wcf91], a
	ld a, 1
	ld [wItemQuantity], a
	ld hl, wNumBagItems
	call AddItemToInventory
	jr nc, .full
	call LoadShipMerchantCost
	ld hl, hMoney + 2
	ld de, wPlayerMoney + 2
	ld c, 3
	predef SubBCDPredef
	ld a, 1
	jr .result
.poor
	ld a, 2
	jr .result
.full
	ld a, 3
	jr .result
.locked
	ld a, 4
.result
	ld [wPostgameAction], a
	ret

LoadShipMerchantCost:
	ld a, [wTutorCandidate]
	ld hl, ShipMerchantStock + 1
	ld bc, 4
	call AddNTimes
	ld de, hMoney
	ld bc, 3
	jp CopyData

ShipMerchantStock::
	db PP_UP
	bcd3 20000
	db MAX_ETHER
	bcd3 3000
	db ELIXER
	bcd3 5000
	db MAX_ELIXER
	bcd3 10000
	db MOON_STONE
	bcd3 5000
