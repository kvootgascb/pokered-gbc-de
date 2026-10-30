SECTION "Mew Truck Secret", ROMX

InvestigateMewTruck::
	call DetermineMewTruckAction
	ld a, [wPostgameAction]
	and a
	ld hl, MewTruckOrdinaryText
	jp z, PrintText
	dec a
	ld hl, MewTruckEscapedText
	jp z, PrintText
	dec a
	ld hl, MewTruckHidingText
	jp z, PrintText
	ld hl, MewTruckEmergesText
	call PrintText
SetupMewTruckBattle:
	xor a
	ld [wRareSurfPikachu], a
	ld [wBattleType], a
	ld a, MEW
	ld [wCurOpponent], a
	ld a, 30
	ld [wCurEnemyLVL], a
	ret ; normal overworld battle dispatch starts the encounter

DetermineMewTruckAction:
	xor a
	ld [wPostgameAction], a
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld hl, wFeatureMewState
	read_feature_byte
	ld a, c
	cp 3
	ret z
	and a
	jr z, MoveMewToOtherSide ; first attempt always fails, no RNG call
	ld a, [wSpecialSuperRod]
	cp c
	jr nz, MewTruckSameSide
	call Random
	and 3
MewTruckRoll:
	and a
	jr nz, MoveMewToOtherSide
	ld hl, wFeatureMewState
	ld c, 3
	write_feature_byte
	ld a, 3
	ld [wPostgameAction], a
	ret
MewTruckSameSide:
	ld a, 2
	ld [wPostgameAction], a
	ret

MoveMewToOtherSide:
	ld a, [wSpecialSuperRod]
	xor 3
	ld c, a
	ld hl, wFeatureMewState
	write_feature_byte
	ld a, 1
	ld [wPostgameAction], a
	ret

MewTruckOrdinaryText:
	text "Ein alter Wagen."
	done
MewTruckEscapedText:
	text "Etwas huscht zur"
	line "anderen Seite!"
	done
MewTruckHidingText:
	text "Es versteckt sich"
	line "noch am anderen"
	cont "Ende des Wagens."
	done
MewTruckEmergesText:
	text "Ein #MON kommt"
	line "unter dem Wagen"
	cont "hervor!"
	done
