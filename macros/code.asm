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
