SECTION "Champion Ship Merchant", ROMX

ShipMerchantTalk::
	ld a, [wUpdateSpritesEnabled]
	push af
	call .talk
	pop af
	ld [wUpdateSpritesEnabled], a
	ret
.talk
	call ShipMerchantAvailable
	jp nc, .unavailable
	ld hl, .welcome
	call PrintText
	ld hl, .inventory
	call LoadItemList
	ld a, PRICEDITEMLISTMENU
	ld [wListMenuID], a
	xor a
	ldh [hUILayoutFlags], a
	ld [wUpdateSpritesEnabled], a
	call HideSprites
	ld a, 1
	ld [wShipMerchantActive], a
	; Unlike script_mart, this shop runs inside a text_asm command. Suspend
	; its outer letter delay so quantity/price redraws are not typed out.
	ld a, [wLetterPrintingDelayFlags]
	push af
	res 1, a
	ld [wLetterPrintingDelayFlags], a
	farcall DisplayPokemartDialogue_
	pop af
	ld [wLetterPrintingDelayFlags], a
	xor a
	ld [wShipMerchantActive], a
	ret
.inventory
	db NUM_SHIP_MERCHANT_ITEMS
	db PP_UP, MAX_ETHER, ELIXER, MAX_ELIXER, MOON_STONE, MAX_REVIVE
	db -1
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

; Only the native buying list uses these prices. Selling and other shops
; continue to use ItemPrices, including the normal resale value of these items.
GetShipMerchantPrice::
	ld a, [wShipMerchantActive]
	and a
	ret z
	ld a, [wListMenuID]
	cp PRICEDITEMLISTMENU
	jr nz, .normalPrice
	ld a, [wcf91]
	ld c, a
	ld hl, ShipMerchantStock
	ld b, NUM_SHIP_MERCHANT_ITEMS
.loop
	ld a, [hli]
	cp c
	jr z, .found
	inc hl
	inc hl
	inc hl
	dec b
	jr nz, .loop
.normalPrice
	and a
	ret
.found
	ld de, hItemPrice
	ld bc, 3
	call CopyData
	ld de, hItemPrice
	scf
	ret

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
	db MAX_REVIVE
	bcd3 10000
.end
DEF NUM_SHIP_MERCHANT_ITEMS EQU (ShipMerchantStock.end - ShipMerchantStock) / 4
