SECTION "Expanded Rare Encounters", ROMX

; Uniform 0..99: reject the last 56 outcomes, then fold the upper half.
RareEncounterPercent:
	call Random
	cp 200
	jr nc, RareEncounterPercent
	cp 100
	ret c
	sub 100
	ret

TryFossilFishing:
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wSpecialSuperRod]
	and a
	ret z
	ld a, [wRodResponse]
	cp 1
	ret nz
	ld a, [wCurMap]
	cp CERULEAN_CAVE_B1F
	ret nz
	call RareEncounterPercent
FossilFishingRoll:
	cp 2
	ret nc
	ld b, OMANYTE
	and a
	jr z, .chosen
	ld b, KABUTO
.chosen
	ld a, b
	ld [wCurOpponent], a
	ld a, 55
	ld [wCurEnemyLVL], a
	ret

TrySurfPikachu:
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wCurMap]
	cp POWER_PLANT
	ret nz
	call RareEncounterPercent
SurfPikachuRoll:
	and a
	ret nz
	ld a, PIKACHU
	ld [wcf91], a
	ld [wEnemyMonSpecies2], a
	ld a, 23
	ld [wCurEnemyLVL], a
	ld a, 1
	ld [wRareSurfPikachu], a
	ret

ApplySurfPikachuMove:
	ld a, [wIsInBattle]
	cp 1
	ret nz
	ld a, [wRareSurfPikachu]
	and a
	ret z
	ld a, [wEnemyMonSpecies2]
	cp PIKACHU
	ret nz
	ld a, SURF
	ld [wEnemyMonMoves], a
	ret

CheckCaughtSurfPikachu:
	ld a, [wRareSurfPikachu]
	and a
	ret z
	ld a, [wcf91]
	cp PIKACHU
	ret

PreserveSurfPikachuInParty:
	call CheckCaughtSurfPikachu
	ret nz
	ld a, [wRareSurfPikachu]
	and a
	ret z
	ld hl, wPartyMon1Moves
	ld a, [wPartyCount]
	dec a
	ld bc, wPartyMon2 - wPartyMon1
	call AddNTimes
	ld [hl], SURF
	ld bc, wPartyMon1PP - wPartyMon1Moves
	add hl, bc
	ld [hl], 15
	ret

PreserveSurfPikachuInBox:
	call CheckCaughtSurfPikachu
	ret nz
	ld a, [wRareSurfPikachu]
	and a
	ret z
	ld a, SURF
	ld [wBoxMon1Moves], a
	ld a, 15
	ld [wBoxMon1PP], a
	ret
