SECTION "Merged Edition Encounters", ROMX

; Terrain (0 grass/indoor, 1 water) and byte slot offset were selected by the
; original encounter code. Only differing Red/Blue slots make an extra RNG draw.
ChooseMergedWildMon::
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld hl, ExtendedWildOverrides
.scan
	ld a, [hli]
	cp $ff
	ret z
	ld b, a
	ld a, [wCurMap]
	cp b
	jr nz, .skipFour
	ld a, [wTutorMode]
	cp [hl]
	jr nz, .skipFour
	inc hl
	ld a, [wTutorCandidate]
	cp [hl]
	jr nz, .skipThree
	inc hl
	push hl
	call Random
	pop hl
	and 1
	ret z
	ld a, [hli]
	ld [wCurEnemyLVL], a
	ld a, [hl]
	ld [wcf91], a
	ld [wEnemyMonSpecies2], a
	ret
.skipFour
	inc hl
.skipThree
	inc hl
	inc hl
	inc hl
	jr .scan

INCLUDE "data/wild/extended_overrides.asm"
