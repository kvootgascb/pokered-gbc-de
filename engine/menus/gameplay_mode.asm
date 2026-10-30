SECTION "Gameplay Mode", ROMX

CommitGameplayMode:
	ld a, [wModeMenuChoice]
	ld c, a
	; fall through; no register arguments cross the farcall bank switch
SetGameplayMode:
	ld a, c
	ld [wGameplayModeCache], a
	ld a, 3
	ldh [rSVBK], a
	ld a, c
	ld [wFeatureMode], a
	xor a
	ldh [rSVBK], a
	xor a
	ld [wEXPBarKeepFullFlag], a
	ld [wEXPBarPixelLength], a
	ret

ChooseGameplayMode:
	call ClearScreen
	hlcoord 0, 0
	lb bc, 5, 18
	call TextBoxBorder
	hlcoord 1, 1
	ld de, .title
	call PlaceString
	hlcoord 3, 3
	ld de, .choices
	call PlaceString
	xor a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem], a
	ld [wMenuJoypadPollCount], a
	ld [wMenuWatchMovingOutOfBounds], a
	ldh [hUILayoutFlags], a
	ld a, 3
	ld [wTopMenuItemY], a
	ld a, 2
	ld [wTopMenuItemX], a
	ld a, 1
	ld [wMaxMenuItem], a
	ld a, A_BUTTON
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	ld a, [wCurrentMenuItem]
	ld c, a
	call SetGameplayMode
	jp ClearScreen
.title
	db "SPIELMODUS@"
.choices
	db "CLASSIC"
	next "ERWEITERT@"

; Called once per movement tick, before the ordinary sprite advancement.
ApplyPlayerSpeedup::
	ld a, [wd736]
	bit 6, a ; ledge / fishing
	ret nz
	ld a, [wWalkBikeSurfState]
	dec a
	jp z, DoBikeSpeedup
	inc a
	ret nz ; surfing
	ld a, [wGameplayModeCache]
	cp FEATURE_MODE_EXTENDED
	ret nz
	ldh a, [hJoyHeld]
	and B_BUTTON
	ret z
	ld a, [wd730]
	bit 7, a ; simulated movement
	ret nz
	ld a, [wNPCMovementScriptPointerTableNum]
	and a
	ret nz
	ld a, [wd736]
	bit 7, a ; spinning tiles
	ret nz
	ld a, [wWalkCounter]
	cp 2 ; B can be pressed/released halfway through a step
	ret c
	jp AdvancePlayerSprite
