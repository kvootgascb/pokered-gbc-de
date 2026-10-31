SECTION "Temporary Starter Editor", ROMX

; Both modes allow the editor, but only before the original starter choice.
; Carry = available. No changes to the ball choice or rival's starter.
StarterEditorAvailable::
	ld a, [wCurMap]
	cp OAKS_LAB
	jr nz, .unavailable
	CheckEvent EVENT_GOT_STARTER
	jr nz, .unavailable
	scf
	ret
.unavailable
	and a
	ret

; Read the current menu direction after farcall (which clobbers BC).
; Cycle in Pokédex order, with zero as ORIGINAL.
CycleStarterEditor::
	call StarterEditorAvailable
	ret nc
	ldh a, [hJoy5]
	and D_RIGHT
	ld c, a
	ld a, [wStarterEditorChoice]
	bit BIT_D_RIGHT, c
	jr z, .left
	inc a
	cp NUM_POKEMON + 1
	jr c, .store
	xor a
	jr .store
.left
	and a
	jr nz, .decrement
	ld a, NUM_POKEMON + 1
.decrement
	dec a
.store
	ld [wStarterEditorChoice], a
	ret

DrawStarterEditorChoice::
	hlcoord 1, 8
	ld de, .blank
	call PlaceString
	call StarterEditorAvailable
	jr nc, .unavailable
	hlcoord 5, 8
	ld de, .original
	ld a, [wStarterEditorChoice]
	and a
	jp z, PlaceString
	cp NUM_POKEMON + 1
	jp nc, PlaceString
	ld [wd11e], a
	farcall PokedexToIndex
	call GetMonName
	hlcoord 5, 8
	jp PlaceString
.unavailable
	hlcoord 5, 8
	ld de, .locked
	jp PlaceString
.blank
	db "                  @"
.original
	db "ORIGINAL@"
.locked
	db "NICHT MÖGLICH@"

; Called in place of AddPartyMon after the original ball/story fields were
; assigned. Use native generation, naming, ownership and Pokédex updates.
; The lab sets level 5 and player-party location exactly as before.
GiveEditedStarter::
	call StarterEditorAvailable
	jr nc, .give
	ld a, [wStarterEditorChoice]
	and a
	jr z, .give
	cp NUM_POKEMON + 1
	jr nc, .give
	ld a, [wPartyCount]
	cp PARTY_LENGTH
	ret nc
	ld a, [wStarterEditorChoice]
	ld [wd11e], a
	farcall PokedexToIndex
	ld a, [wd11e]
	ld [wcf91], a
.give
	call AddPartyMon
	xor a
	ld [wStarterEditorChoice], a
	ret
