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
	xor a
	ld [wHiddenMenuPage], a
	ld [wSpriteMenuCursorRow], a
	ld a, [wGameplayModeCache]
	ld [wModeMenuChoice], a
	ld hl, wFeaturePreferences
	read_feature_byte
	ld a, c
	ld [wHiddenMenuPreferences], a
	xor a
	ld [wCurrentMenuItem], a
	ld a, [wPlayerGenderTag]
	cp $47
	jr nz, .redraw
	ld a, [wPlayerGender]
	cp 1
	jr nz, .redraw
	ld [wCurrentMenuItem], a
.redraw
	call ClearScreen
	hlcoord 0, 0
	lb bc, 3, 18
	call TextBoxBorder
	ld a, [wHiddenMenuPage]
	and a
	jp nz, .comfortPage
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
	hlcoord 2, 13
	ld de, .nextPage
	jr .pageLinks
.comfortPage
	hlcoord 1, 1
	ld de, .animationHeading
	call PlaceString
	hlcoord 5, 3
	ld de, .on
	call PlaceString
	hlcoord 14, 3
	ld de, .off
	call PlaceString
	hlcoord 2, 13
	ld de, .previousPage
.pageLinks
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
.input
	call .drawCursor
	call DelayFrame
	call JoypadLowSensitivity
	ldh a, [hJoy5]
	ld b, a
	and B_BUTTON | START
	jp nz, .done
	bit BIT_D_DOWN, b
	jp nz, .down
	bit BIT_D_UP, b
	jp nz, .up
	ld a, [wHiddenMenuPage]
	and a
	ld a, [wSpriteMenuCursorRow]
	jr nz, .comfortInput
	cp 2
	jr nc, .checkConfirm
	jr .checkLeftRight
.comfortInput
	and a
	jr nz, .checkConfirm
.checkLeftRight
	bit BIT_D_LEFT, b
	jr nz, .left
	bit BIT_D_RIGHT, b
	jr nz, .right
.checkConfirm
	bit BIT_A_BUTTON, b
	jp z, .input
	ld a, [wHiddenMenuPage]
	and a
	ld a, [wSpriteMenuCursorRow]
	jr nz, .comfortConfirm
	cp 3
	jr z, .done
	cp 2
	jp nz, .input
	ld a, 1
	ld [wHiddenMenuPage], a
	xor a
	ld [wSpriteMenuCursorRow], a
	jp .redraw
.comfortConfirm
	cp 2
	jr z, .done
	cp 1
	jp nz, .input
	xor a
	ld [wHiddenMenuPage], a
	ld a, 2
	ld [wSpriteMenuCursorRow], a
	jp .redraw
.done
	ret
.down
	call .lastRow
	ld c, a
	ld a, [wSpriteMenuCursorRow]
	cp c
	jp z, .input
	inc a
	ld [wSpriteMenuCursorRow], a
	jp .input
.up
	ld a, [wSpriteMenuCursorRow]
	and a
	jp z, .input
	dec a
	ld [wSpriteMenuCursorRow], a
	jp .input
.lastRow
	ld a, [wHiddenMenuPage]
	and a
	ld a, 3
	ret z
	dec a
	ret
.left
	xor a
	jr .select
.right
	ld a, 1
.select
	ld c, a
	ld a, [wHiddenMenuPage]
	and a
	jr nz, .selectAnimation
	ld a, [wSpriteMenuCursorRow]
	and a
	ld a, c
	jr nz, .selectMode
	ld [wCurrentMenuItem], a
	ld a, [wPlayerGenderTag]
	cp $47
	jr nz, .applyGender
	ld a, [wPlayerGender]
	cp c
	jp z, .input
.applyGender
	ld a, c
	ld [wPlayerGender], a
	ld a, $47
	ld [wPlayerGenderTag], a
	call ReloadSelectedPlayerSprite
	; Restore only the 12 font tiles overwritten by the animation frames.
	ld de, FontGraphics
	ld hl, vFont
	lb bc, BANK(FontGraphics), 12
	call CopyVideoDataDouble
	jp .input
.selectMode
	ld [wModeMenuChoice], a
	ld a, [wGameplayModeCache]
	cp c
	jp z, .input
	farcall CommitGameplayMode
	jp .input
.selectAnimation
	ld a, [wHiddenMenuPreferences]
	res 1, a
	bit 0, c
	jr z, .storePreference
	set 1, a
.storePreference
	ld [wHiddenMenuPreferences], a
	ld c, a
	ld hl, wFeaturePreferences
	write_feature_byte
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
	hlcoord 1, 13
	ld [hl], a
	hlcoord 1, 16
	ld [hl], a
	ld a, [wHiddenMenuPage]
	and a
	jr nz, .comfortCursors
	hlcoord 4, 3
	ld a, [wPlayerGenderTag]
	cp $47
	jr nz, .savedGender
	ld a, [wPlayerGender]
	cp 1
	jr nz, .savedGender
	hlcoord 13, 3
.savedGender
	ld [hl], "▷"
	hlcoord 1, 8
	ld a, [wGameplayModeCache]
	and a
	jr z, .savedMode
	hlcoord 9, 8
.savedMode
	ld [hl], "▷"
	ld a, [wSpriteMenuCursorRow]
	cp 3
	jr z, .backCursor
	cp 2
	jr z, .pageCursor
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
	jr .drawArrow
.comfortCursors
	hlcoord 4, 3
	ld a, [wHiddenMenuPreferences]
	bit 1, a
	jr z, .animationCursor
	hlcoord 13, 3
.animationCursor
	ld [hl], "▷"
	ld a, [wSpriteMenuCursorRow]
	cp 2
	jr z, .backCursor
	cp 1
	jr z, .pageCursor
	jr .drawArrow
.pageCursor
	hlcoord 1, 13
	jr .drawArrow
.backCursor
	hlcoord 1, 16
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
.animationHeading
	db "VM-ANIMATIONEN@"
.on
	db "AN@"
.off
	db "AUS@"
.nextPage
	db "WEITER@"
.previousPage
	db "SEITE 1@"
.back
	db "ZURÜCK@"

ReloadSelectedPlayerSprite:
	ld a, [wWalkBikeSurfState]
	and a
	jp z, LoadWalkingPlayerSpriteGraphics
	dec a
	jp z, LoadBikePlayerSpriteGraphics
	jp LoadSurfingPlayerSpriteGraphics
