SECTION "Independent Comfort Options", ROMX

; Returns NZ when VM animations should be skipped, in either game mode.
SkipVMAnimationsEnabled::
	ld hl, wFeaturePreferences
	read_feature_byte
	bit 1, c
	ret
