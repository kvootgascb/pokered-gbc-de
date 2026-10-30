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
	hlcoord 5, 3
	ld de, .male
	call PlaceString
	hlcoord 14, 3
	ld de, .female
	call PlaceString
	hlcoord 0, 5
	lb bc, 3, 18
	call TextBoxBorder
	hlcoord 1, 6
	ld de, .modeHeading
	call PlaceString
	hlcoord 2, 8
	ld de, .classic
	call PlaceString
	hlcoord 10, 8
	ld de, .extended
	call PlaceString
	ld a, [wGameplayModeCache]
	ld [wModeMenuChoice], a
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
	cp 2
	jr z, .checkConfirm
	bit BIT_D_LEFT, b
	jr nz, .maleSelected
	bit BIT_D_RIGHT, b
	jr nz, .femaleSelected
.checkConfirm
	bit BIT_A_BUTTON, b
	jp z, .input
	ld a, [wSpriteMenuCursorRow]
	cp 2
	jr z, .done
	and a
	jr z, .confirmGender
	ld a, [wModeMenuChoice]
	ld c, a
	farcall CommitGameplayMode
	ret
.confirmGender
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
	ld a, [wSpriteMenuCursorRow]
	cp 2
	jp z, .input
	inc a
	ld [wSpriteMenuCursorRow], a
	jp .input
.genderRow
	ld a, [wSpriteMenuCursorRow]
	and a
	jp z, .input
	dec a
	ld [wSpriteMenuCursorRow], a
	jp .input
.maleSelected
	xor a
	jr .select
.femaleSelected
	ld a, 1
.select
	ld c, a
	ld a, [wSpriteMenuCursorRow]
	and a
	ld a, c
	jr nz, .selectMode
	ld [wCurrentMenuItem], a
	jp .input
.selectMode
	ld [wModeMenuChoice], a
	jp .input

.drawCursor
	ld a, " "
	hlcoord 4, 3
	ld [hl], a
	hlcoord 13, 3
	ld [hl], a
	hlcoord 1, 8
	ld [hl], a
	hlcoord 9, 8
	ld [hl], a
	hlcoord 1, 16
	ld [hl], a
	ld a, [wSpriteMenuCursorRow]
	cp 2
	jr z, .drawArrow
	and a
	jr z, .genderCursor
	ld a, [wModeMenuChoice]
	and a
	hlcoord 1, 8
	jr z, .drawArrow
	hlcoord 9, 8
	jr .drawArrow
.genderCursor
	ld a, [wCurrentMenuItem]
	and a
	hlcoord 4, 3
	jr z, .drawArrow
	hlcoord 13, 3
.drawArrow
	ld [hl], "▶"
	ret
.heading
	db "GESCHLECHT@"
.male
	db "♂@"
.female
	db "♀@"
.modeHeading
	db "SPIELMODUS@"
.classic
	db "CLASSIC@"
.extended
	db "ERWEITERT@"
.back
	db "ZURÜCK@"

ReloadSelectedPlayerSprite:
	ld a, [wWalkBikeSurfState]
	and a
	jp z, LoadWalkingPlayerSpriteGraphics
	dec a
	jp z, LoadBikePlayerSpriteGraphics
	jp LoadSurfingPlayerSpriteGraphics
