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
	call ClearScreen
	hlcoord 0, 0
	lb bc, 3, 18
	call TextBoxBorder
	hlcoord 1, 1
	ld de, .heading
	call PlaceString
	hlcoord 3, 3
	ld de, .male
	call PlaceString
	hlcoord 10, 3
	ld de, .female
	call PlaceString
	hlcoord 2, 16
	ld de, .back
	call PlaceString
.waitForRelease
	call DelayFrame
	call Joypad
	ldh a, [hJoyHeld]
	and SELECT
	jr nz, .waitForRelease
	xor a
	ld [wSpriteMenuCursorRow], a
	ld [wCurrentMenuItem], a
	ld a, [wPlayerGenderTag]
	cp $47
	jr nz, .input
	ld a, [wPlayerGender]
	cp 1
	jr nz, .input
	ld [wCurrentMenuItem], a
.input
	call .drawCursor
	call DelayFrame
	call JoypadLowSensitivity
	ldh a, [hJoy5]
	ld b, a
	and B_BUTTON | START
	jr nz, .done
	bit BIT_D_DOWN, b
	jr nz, .backRow
	bit BIT_D_UP, b
	jr nz, .genderRow
	ld a, [wSpriteMenuCursorRow]
	and a
	jr nz, .checkConfirm
	bit BIT_D_LEFT, b
	jr nz, .maleSelected
	bit BIT_D_RIGHT, b
	jr nz, .femaleSelected
.checkConfirm
	bit BIT_A_BUTTON, b
	jr z, .input
	ld a, [wSpriteMenuCursorRow]
	and a
	jr nz, .done
	ld a, [wCurrentMenuItem]
	ld [wPlayerGender], a
	ld a, $47
	ld [wPlayerGenderTag], a
	call ReloadSelectedPlayerSprite
	; Animation frames share VRAM with the font; restore menu graphics.
	call LoadFontTilePatterns
	call LoadTextBoxTilePatterns
.done
	ret
.backRow
	ld a, 1
	ld [wSpriteMenuCursorRow], a
	jr .input
.genderRow
	xor a
	ld [wSpriteMenuCursorRow], a
	jr .input
.maleSelected
	xor a
	ld [wCurrentMenuItem], a
	jr .input
.femaleSelected
	ld a, 1
	ld [wCurrentMenuItem], a
	jr .input
.drawCursor
	ld a, " "
	hlcoord 2, 3
	ld [hl], a
	hlcoord 9, 3
	ld [hl], a
	hlcoord 1, 16
	ld [hl], a
	ld a, [wSpriteMenuCursorRow]
	and a
	jr nz, .drawArrow
	ld a, [wCurrentMenuItem]
	and a
	hlcoord 2, 3
	jr z, .drawArrow
	hlcoord 9, 3
.drawArrow
	ld [hl], "▶"
	ret
.heading
	db "GESCHLECHT@"
.male
	db "♂@"
.female
	db "♀@"
.back
	db "ZURÜCK@"

ReloadSelectedPlayerSprite:
	ld a, [wWalkBikeSurfState]
	and a
	jp z, LoadWalkingPlayerSpriteGraphics
	dec a
	jp z, LoadBikePlayerSpriteGraphics
	jp LoadSurfingPlayerSpriteGraphics
