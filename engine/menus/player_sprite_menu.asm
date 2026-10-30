; Kept outside fixed legacy bank sections to avoid moving existing entry points.
SECTION "Hidden Player Sprite Menu", ROMX

DEF PLAYER_SPRITE_MENU_HOLD_FRAMES EQU 180 ; approximately three seconds

; Called exactly once per options input frame. Only SELECT on its own counts.
; Carry indicates that the hidden menu should open.
CheckOptionsSpriteShortcut:
	ld a, [wOptionsSpriteMenuEnabled]
	and a
	ret z ; AND also clears carry in title-screen options
	ldh a, [hJoyHeld]
	cp SELECT
	jr nz, .reset
	ld hl, wOptionsSelectHoldFrames
	inc [hl]
	ld a, [hl]
	cp PLAYER_SPRITE_MENU_HOLD_FRAMES
	jr z, .open
	and a ; clear carry while still counting
	ret
.reset
	xor a
	ld [wOptionsSelectHoldFrames], a
	ret
.open
	xor a
	ld [hl], a
	scf
	ret

ShowPlayerSpriteMenu:
	ldh a, [hUILayoutFlags]
	push af
	res 1, a ; menu cursor uses two rows
	res 2, a ; PlaceString uses two rows
	ldh [hUILayoutFlags], a
	call ClearScreen
	hlcoord 0, 0
	lb bc, 16, 18
	call TextBoxBorder
	hlcoord 2, 2
	ld de, .heading
	call PlaceString
	hlcoord 2, 4
	lb bc, 7, 14
	call TextBoxBorder
	hlcoord 4, 4
	ld de, .sectionTitle
	call PlaceString
	hlcoord 2, 14
	ld de, .controls
	call PlaceString
	hlcoord 4, 6
	ld de, .choices
	call PlaceString
	; Do not let the opening SELECT hold repeat or confirm anything.
.waitForRelease
	call DelayFrame
	call Joypad
	ldh a, [hJoyHeld]
	and SELECT
	jr nz, .waitForRelease
	xor a
	ld [wMenuWatchMovingOutOfBounds], a
	ld [wMenuWrappingEnabled], a
	ld [wMenuJoypadPollCount], a
	ld [wCurrentMenuItem], a
	ld a, [wPlayerGenderTag]
	cp $47
	jr nz, .selectionReady
	ld a, [wPlayerGender]
	cp 1
	jr nz, .selectionReady
	ld [wCurrentMenuItem], a
.selectionReady
	ld a, [wCurrentMenuItem]
	ld [wLastMenuItem], a
	ld a, 6
	ld [wTopMenuItemY], a
	ld a, 3
	ld [wTopMenuItemX], a
	ld a, 2
	ld [wMaxMenuItem], a
	ld a, A_BUTTON | B_BUTTON | START
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	and B_BUTTON | START
	jr nz, .done
	ld a, [wCurrentMenuItem]
	cp 2 ; ZURÜCK
	jr z, .done
	ld [wPlayerGender], a
	ld a, $47
	ld [wPlayerGenderTag], a
	call ReloadSelectedPlayerSprite
	; Walking frames share $8800 with the menu font. Restore the font before
	; redrawing Options; closing the Start menu reloads the walking frames.
	call LoadFontTilePatterns
	call LoadTextBoxTilePatterns
.done
	pop af
	ldh [hUILayoutFlags], a
	ret

.heading
	db "GEHEIMMENÜ@"
.sectionTitle
	db "FIGUR@"
.controls
	db "A:OK  B:ZURÜCK@"
.choices
	db "JUNGE"
	next "GREEN"
	next "ZURÜCK@"

; Reload immediately, preserving location, facing and walking/bike/surf state.
ReloadSelectedPlayerSprite:
	ld a, [wWalkBikeSurfState]
	and a
	jp z, LoadWalkingPlayerSpriteGraphics
	dec a
	jp z, LoadBikePlayerSpriteGraphics
	jp LoadSurfingPlayerSpriteGraphics
