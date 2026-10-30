SECTION "Local Trade Back Trainer", ROMX

TradeBackTrainerTalk::
	ld a, [wGameplayModeCache]
	and a
	ret z
	CheckEvent EVENT_GOT_STARTER
	ret z
	ld hl, .offer
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	jr nz, .done
	farcall SelectTutorPokemon
	jr c, .done
	ld a, [wTutorPartyIndex]
	ld [wWhichPokemon], a
	call SaveScreenTilesToBuffer2
	call RunLocalTradeEvolution
	call GBPalWhiteOutWithDelay3
	call RestoreScreenTilesAndReloadTilePatterns
	call LoadGBPal
	ld hl, .returned
	call PrintText
.done
	scf
	ret
.offer
	text "Mein Linkkabel hat"
	line "wieder Kontakt!"
	para "Es war wohl ein"
	line "Wackelkontakt."
	para "Testen wir es? Dein"
	line "#MON bekommst Du"
	cont "sofort zurück!"
	prompt
.returned
	text "Es funktioniert!"
	line "Dein #MON ist"
	cont "wieder bei Dir."
	done

; Use the original evolution engine in local trade mode. No party removal,
; ownership changes or serial communication; only the selected mon may evolve.
RunLocalTradeEvolution::
	xor a
	ld [wEvolutionOccurred], a
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wWhichPokemon]
	ld b, a
	ld a, [wPartyCount]
	cp b
	ret z
	ret c
	ld a, [wLinkState]
	push af
	ld a, [wForceEvolution]
	push af
	ld a, 1
	ld [wForceEvolution], a
	ld a, LINK_STATE_TRADING
	ld [wLinkState], a
	callfar TryEvolvingMon
	pop af
	ld [wForceEvolution], a
	pop af
	ld [wLinkState], a
	xor a
	ld [wCanEvolveFlags], a
	jp PlayDefaultMusic
