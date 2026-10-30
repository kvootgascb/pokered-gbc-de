SECTION "Independent Comfort Options", ROMX

; Returns NZ when VM animations should be skipped, in either game mode.
SkipVMAnimationsEnabled::
	ld hl, wFeaturePreferences
	read_feature_byte
	bit 1, c
	ret

FastHealingEnabled::
	ld hl, wFeaturePreferences
	read_feature_byte
	bit 0, c
	ret

; Carry means the original nurse conversation has been handled. This preference
; is independent of Classic/Extended and keeps the ordinary Yes/No choice.
TryFastPokemonCenter::
	call FastHealingEnabled
	jr nz, .enabled
	and a
	ret
.enabled
	call SaveScreenTilesToBuffer1
	ld hl, wd72e
	set 1, [hl]
	set 2, [hl]
	ld hl, .offer
	call PrintText
	call YesNoChoicePokeCenter
	ld a, [wCurrentMenuItem]
	and a
	jr nz, .declined
	farcall SetLastBlackoutMap
	predef HealParty
	call LoadScreenTilesFromBuffer1
	ld hl, .healed
	jr .finish
.declined
	call LoadScreenTilesFromBuffer1
	ld hl, .farewell
.finish
	call PrintText
	call UpdateSprites
	scf
	ret
.offer
	text "Deine #MON"
	line "heilen?"
	prompt
.healed
	text "Alle wieder fit!"
	line "Bis bald!"
	done
.farewell
	text "Bis bald!"
	done
