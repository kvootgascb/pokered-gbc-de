; Syntactic sugar macros

MACRO lb ; r, hi, lo
	ld \1, ((\2) & $ff) << 8 + ((\3) & $ff)
ENDM

MACRO ldpal
	ld \1, \2 << 6 | \3 << 4 | \4 << 2 | \5
ENDM

; Design patterns

MACRO dict
	IF \1 == 0
		and a
	ELSE
		cp \1
	ENDC
	jp z, \2
ENDM


; Select matching-bank player art, preserving all registers except DE.
MACRO player_graphics
	ASSERT BANK(\1) == BANK(\2)
	ld de, \1
	push hl
	ld hl, \2
	call SelectPlayerGraphics
	pop hl
ENDM

; Bank-safe feature access from any ROM bank. HL is the payload address;
; C is the output/input value. Restore HL/C after the farcall trampoline.
MACRO read_feature_byte
	ld a, l
	ld [wFeatureAccessLow], a
	ld a, h
	ld [wFeatureAccessHigh], a
	farcall ReadFeatureState
	ld a, [wFeatureAccessResult]
	ld c, a
	ld a, [wFeatureAccessLow]
	ld l, a
	ld a, [wFeatureAccessHigh]
	ld h, a
ENDM
MACRO write_feature_byte
	ld a, l
	ld [wFeatureAccessLow], a
	ld a, h
	ld [wFeatureAccessHigh], a
	ld a, c
	ld [wFeatureAccessValue], a
	farcall WriteFeatureState
	ld a, [wFeatureAccessValue]
	ld c, a
	ld a, [wFeatureAccessLow]
	ld l, a
	ld a, [wFeatureAccessHigh]
	ld h, a
ENDM
