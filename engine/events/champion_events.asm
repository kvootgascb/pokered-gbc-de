SECTION "Champion Event State", ROMX

; Existing champions are initialized once when first visiting an expanded NPC
; or harbor. New victories always refresh one opportunity, never a stack.
EnsureChampionFeatures::
	ld hl, wFeatureSchemaFlags
	homecall GetFeatureByte
	bit 0, c
	ret nz
	set 0, c
	homecall SetFeatureByte
	ld a, [wNumHoFTeams]
	and a
	ret z
	jr RefreshChampionOpportunities

RegisterChampionVictory::
	ld hl, wFeatureSchemaFlags
	homecall GetFeatureByte
	set 0, c
	homecall SetFeatureByte
	ld a, 3
	ldh [rSVBK], a
	ld hl, wFeatureEliteFourWins
	inc [hl]
	jr nz, .counted
	inc hl
	inc [hl]
.counted
	xor a
	ldh [rSVBK], a
RefreshChampionOpportunities:
	ld hl, wFeatureOakPendingStarter
	homecall GetFeatureByte
	ld a, c
	and a
	jr nz, .ship
	ld hl, wFeatureOakBattleAvailable
	ld c, 1
	homecall SetFeatureByte
.ship
	ld hl, wFeatureAnneState
	ld c, 1
	homecall SetFeatureByte
	ret

PrepareAnneVisit::
	ld a, [wCurrentMapScriptFlags]
	bit 6, a
	ret z
	ld a, [wGameplayModeCache]
	and a
	jr nz, .expanded
	ld a, [wNumHoFTeams]
	and a
	ret z
	SetEvent EVENT_SS_ANNE_LEFT
	ret
.expanded
	call EnsureChampionFeatures
	ld hl, wFeatureAnneState
	homecall GetFeatureByte
	ld a, c
	cp 1
	ret nz
	ResetEvent EVENT_SS_ANNE_LEFT
	ResetEvent EVENT_STARTED_WALKING_OUT_OF_DOCK
	ResetEvent EVENT_WALKED_OUT_OF_DOCK
	ResetEvent EVENT_WALKED_PAST_GUARD_AFTER_SS_ANNE_LEFT
	ret

ConsumeAnneVisit::
	ld hl, wFeatureAnneState
	ld c, 0
	homecall SetFeatureByte
	ret
