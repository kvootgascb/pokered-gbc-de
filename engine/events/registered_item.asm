SECTION "Registered Basis Item", ROMX

IsRegisterableItem:
	ld a, [wcf91]
	ld hl, .items
	ld de, 1
	jp IsInArray ; carry means eligible
.items
	db BICYCLE, OLD_ROD, GOOD_ROD, SUPER_ROD, ITEMFINDER, POKE_FLUTE, TOWN_MAP
	db -1

RegisteredItemMenu::
	ld a, [wGameplayModeCache]
	and a
	ret z
	call IsRegisterableItem
	ret nc
	hlcoord 0, 9
	lb bc, 6, 18
	call TextBoxBorder
	hlcoord 2, 10
	ld de, .choices
	call PlaceString
	ld hl, wFeatureRegisteredItem
	read_feature_byte
	ld a, [wcf91]
	cp c
	jr nz, .input
	hlcoord 2, 12
	ld de, .unregister
	call PlaceString
.input
	xor a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem], a
	ld [wMenuJoypadPollCount], a
	ld [wMenuWatchMovingOutOfBounds], a
	ldh [hUILayoutFlags], a
	ld a, 10
	ld [wTopMenuItemY], a
	ld a, 1
	ld [wTopMenuItemX], a
	ld a, 2
	ld [wMaxMenuItem], a
	ld a, A_BUTTON | B_BUTTON
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	and B_BUTTON
	ld a, 2
	jr nz, .chosen
	ld a, [wCurrentMenuItem]
.chosen
	ld [wPostgameAction], a
	cp 1
	jr nz, .done
	call ToggleRegisteredItem
.done
	scf ; caller uses action 0 to use normally, otherwise returns to the bag
	ret
.choices
	db "BENUTZEN"
	next "REGISTRIEREN"
	next "ZURÜCK@"
.unregister
	db "ABMELDEN    @"

ToggleRegisteredItem::
	ld a, [wGameplayModeCache]
	and a
	ret z
	call IsRegisterableItem
	ret nc
	ld hl, wFeatureRegisteredItem
	read_feature_byte
	ld a, [wcf91]
	cp c
	jr nz, .store
	xor a
.store
	ld c, a
	write_feature_byte
	scf
	ret

CheckRegisteredItemShortcut::
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wLinkState]
	and a
	ret nz
	ld a, [wIsInBattle]
	and a
	ret nz
	call IsPlayerCharacterBeingControlledByGame
	and a
	ret nz
	ld hl, wFeatureRegisteredItem
	read_feature_byte
	ld a, c
	ld [wcf91], a
	jp IsRegisterableItem

UseRegisteredItem::
	ld hl, wFeatureRegisteredItem
	read_feature_byte
	ld a, c
	ld [wcf91], a
	call IsRegisterableItem
	ret nc
	ld a, [wcf91]
	ld b, a
	call IsItemInBag
	jr z, .missing
	ld a, [wcf91]
	ld [wd11e], a
	call GetItemName
	call CopyToStringBuffer
	xor a
	ld [wPseudoItemID], a
	; Cycling Road still forbids getting off the bike.
	ld a, [wcf91]
	cp BICYCLE
	jr nz, .use
	ld a, [wd732]
	bit 5, a
	jr nz, .blocked
.use
	jp UseItem ; native restrictions and effects, including fishing battle setup
.missing
	ld hl, .missingText
	jp PrintText
.blocked
	ld hl, .blockedText
	jp PrintText
.missingText
	text "Das registrierte"
	line "Item ist nicht"
	cont "in Deinem Beutel."
	done
.blockedText
	text "Hier musst Du auf"
	line "dem Rad bleiben!"
	done

PUSHS
SECTION "Registered Item Text Entry", ROM0
DisplayRegisteredItem::
	farcall UseRegisteredItem
	jp HoldTextDisplayOpen
POPS
