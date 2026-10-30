; Helper functions for oak intro

GetNidorinoPalID:
	call ClearScreen
IF GEN_2_GRAPHICS
	ld a, PAL_NIDORINO
ELSE
	ld a, PAL_PURPLEMON
ENDC
	jr GotPalID

GetRedPalID:
	call ClearScreen
IF GEN_2_GRAPHICS
	ld a, PAL_HERO
ELSE
	ld a, PAL_REDMON
ENDC
	push af
	ld a, [wPlayerGenderTag]
	cp $47
	jr nz, .keepPalette
	ld a, [wPlayerGender]
	dec a
	jr nz, .keepPalette
	pop af
	ld a, PAL_BROWNMON
	jr GotPalID
.keepPalette
	pop af
	jr GotPalID

GetRivalPalID:
	call ClearScreen
IF GEN_2_GRAPHICS
	ld a, PAL_GARY1
ELSE
	ld a, PAL_MEWMON
ENDC
	jr GotPalID

GotPalID:
	ld e, 0
	ld d, a

	ld a, 2
	ldh [rSVBK], a
	CALL_INDIRECT LoadSGBPalette
	xor a
	ldh [rSVBK], a
	ret

