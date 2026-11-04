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
	call AddPartyMon
	jr nc, .done
	; Append to the existing PC inventory: never recreate a withdrawn Potion.
	ld a, [wcf91]
	push af
	ld a, [wItemQuantity]
	push af
	ld a, RARE_CANDY
	ld [wcf91], a
	ld a, 99
	ld [wItemQuantity], a
	ld hl, wNumBoxItems
	call AddItemToInventory
	pop af
	ld [wItemQuantity], a
	pop af
	ld [wcf91], a
	jr .done
.give
	call AddPartyMon
.done
	xor a
	ld [wStarterEditorChoice], a
	ret
