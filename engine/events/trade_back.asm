SECTION "Local Trade Back Trainer", ROMX

TradeBackTrainerTalk::
	ld a, [wGameplayModeCache]
	and a
	ret z
	CheckEvent EVENT_GOT_STARTER
	ret z
	ld a, [wUpdateSpritesEnabled]
	push af
	call .talk
	pop af
	ld [wUpdateSpritesEnabled], a
	scf
	ret
.talk
	ld hl, .offer
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	jr z, .select
	call DisableWaitingAfterTextDisplay
	jr .done
.select
	farcall SelectTutorPokemon
	jr c, .done
	ld a, [wTutorPartyIndex]
	ld [wWhichPokemon], a
	; Flower/water updates share VRAM with the traded mon's front picture.
	; Resume them only after the overworld graphics have been restored.
	ldh a, [hTileAnimations]
	push af
	xor a
	ldh [hTileAnimations], a
	; Trading changes the LCD layout/window position as well as tile graphics.
	ldh a, [hSCX]
	push af
	ldh a, [hSCY]
	push af
	ldh a, [rLCDC]
	push af
	ldh a, [rWX]
	push af
	ldh a, [hWY]
	push af
	call PlayLocalTradeBackAnimation
	call RunLocalTradeEvolution
	call GBPalWhiteOutWithDelay3
	pop af
	ldh [hWY], a
	ldh [rWY], a
	pop af
	ldh [rWX], a
	pop af
	ldh [rLCDC], a
	pop af
	ldh [hSCY], a
	pop af
	ldh [hSCX], a
	; The native in-game trade reloads tilesets and encounters after evolution.
	farcall InGameTrade_RestoreScreen
	farcall RedrawMapView
	pop af
	ldh [hTileAnimations], a
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
	para "Testen wir es?"
	line "Du bekommst Dein"
	cont "#MON zurück!"
	prompt
.returned
	text "Es funktioniert!"
	line "Dein #MON ist"
	cont "wieder bei Dir."
	done

; The native animation already shows both cable directions. Both displayed
; Pokemon are the selected mon: it goes to the scientist and comes straight
; back. Only animation metadata is copied; party/ownership data stays intact.
PlayLocalTradeBackAnimation:
	ld a, [wWhichPokemon]
	push af
	ld hl, wLinkEnemyTrainerName
	ld b, NAME_LENGTH
.saveName
	ld a, [hli]
	push af
	dec b
	jr nz, .saveName
	ld hl, .scientist
	ld de, wLinkEnemyTrainerName
	ld bc, NAME_LENGTH
	call CopyData
	ld a, [wWhichPokemon]
	ld hl, wPartySpecies
	ld b, 0
	ld c, a
	add hl, bc
	ld a, [hl]
	ld [wTradedPlayerMonSpecies], a
	ld [wTradedEnemyMonSpecies], a
	ld hl, wPartyMonOT
	ld bc, NAME_LENGTH
	ld a, [wWhichPokemon]
	call AddNTimes
	push hl
	ld de, wTradedPlayerMonOT
	ld bc, NAME_LENGTH
	call CopyData
	pop hl
	ld de, wTradedEnemyMonOT
	ld bc, NAME_LENGTH
	call CopyData
	ld hl, wPartyMon1OTID
	ld bc, wPartyMon2 - wPartyMon1
	ld a, [wWhichPokemon]
	call AddNTimes
	push hl
	ld de, wTradedPlayerMonOTID
	ld bc, 2
	call CopyData
	pop hl
	ld de, wTradedEnemyMonOTID
	ld bc, 2
	call CopyData
	call LoadHpBarAndStatusTilePatterns
	predef InternalClockTradeAnim
	ld hl, wLinkEnemyTrainerName + NAME_LENGTH - 1
	ld b, NAME_LENGTH
.restoreName
	pop af
	ld [hld], a
	dec b
	jr nz, .restoreName
	pop af
	ld [wWhichPokemon], a
	ret
.scientist
	db "FORSCHER@@@"
	ASSERT @ - .scientist == NAME_LENGTH

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
