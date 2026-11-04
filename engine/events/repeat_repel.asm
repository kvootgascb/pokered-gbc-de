SECTION "Repeat Repel", ROMX

RememberRepelType::
	ld a, [wcf91]
	ld c, a
	ld hl, wFeatureLastRepel
	write_feature_byte
	ret

OfferRepeatRepel::
	ld a, [wGameplayModeCache]
	and a
	ret z
	call FindLastRepelInBag
	ret nc
	ld hl, .question
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	ret nz
	jp RepeatLastRepel
.question
	text "Noch ein Exemplar"
	line "derselben Art"
	cont "benutzen?"
	prompt

; Re-find the actual bag position rather than using an old party/menu index.
RepeatLastRepel::
	ld a, [wGameplayModeCache]
	and a
	ret z
	call FindLastRepelInBag
	ret nc
	ld a, [wWhichPokemon]
	push af
	ld a, c
	ld [wWhichPokemon], a
	; The overworld can overwrite the shared name buffer after the first use.
	; Prepare the item-use text just as the bag menu does.
	ld a, [wcf91]
	ld [wd11e], a
	call GetItemName
	call CopyToStringBuffer
	call UseItem
	pop af
	ld [wWhichPokemon], a
	ret

FindLastRepelInBag:
	ld hl, wFeatureLastRepel
	read_feature_byte
	ld a, c
	cp REPEL
	jr z, .valid
	cp SUPER_REPEL
	jr z, .valid
	cp MAX_REPEL
	jr z, .valid
	and a ; old saves with an unknown active repel do not guess its type
	ret
.valid
	ld [wcf91], a
	ld d, a
	ld a, [wNumBagItems]
	and a
	ret z
	ld b, a
	ld c, 0
	ld hl, wBagItems
.scan
	ld a, [hli]
	cp d
	jr z, .found
	inc hl
	inc c
	dec b
	jr nz, .scan
	and a
	ret
.found
	ld a, [hl] ; also reject an invalid zero-quantity stack
	and a
	ret z
	scf
	ret
