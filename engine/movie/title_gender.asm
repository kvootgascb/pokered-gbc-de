SECTION "Saved Title Character", ROMX

; Called with the LCD off. Leave the title's existing OAM and palette intact.
LoadTitlePlayerGraphics::
	call ReadTitlePlayerGender
	ld hl, PlayerCharacterTitleGraphics
	ld a, [wTitlePlayerGender]
	and a
	ld a, BANK(PlayerCharacterTitleGraphics)
	jr z, .copy
	ld hl, GreenPlayerCharacterTitleGraphics
	ld a, BANK(GreenPlayerCharacterTitleGraphics)
.copy
	ld de, vSprites
	ld bc, 35 tiles
	jp FarCopyData2

; Read only: do not load/migrate saves, initialize feature data, or change
; the current player's gender. Invalid/missing saves display the original boy.
ReadTitlePlayerGender::
	xor a
	ld [wTitlePlayerGender], a
	ld a, SRAM_ENABLE
	ld [MBC1SRamEnable], a
	ld a, 1
	ld [MBC1SRamBankingMode], a
	ld [MBC1SRamBank], a
	ld a, [sMainData + wPlayerGenderTag - wMainDataStart]
	cp $47
	jr nz, .close
	ld a, [sMainData + wPlayerGender - wMainDataStart]
	cp 1
	jr nz, .close
	ld hl, sPlayerName
	ld b, NAME_LENGTH
.name
	ld a, [hli]
	cp "@"
	jr z, .check
	dec b
	jr nz, .name
	jr .close
.check
	ld hl, sGameData
	ld bc, sGameDataEnd - sGameData
	call .checksum
	ld b, a
	ld a, [sMainDataCheckSum]
	cp b
	jr nz, .close
	call .feature
	jr c, .close
	ld a, 1
	ld [wTitlePlayerGender], a
.close
	xor a
	ld [MBC1SRamBankingMode], a
	ld [MBC1SRamEnable], a
	ret

; Match LoadFeatureSaveData's format checks, without loading its payload.
.feature
	ld a, [sMainData + wInventoryFormat - wMainDataStart]
	cp $49
	jr nz, .valid
	ld a, [sMainData + wInventoryFormat + 1 - wMainDataStart]
	cp $31
	jr z, .valid
	cp $32
	jr nz, .invalid
	ld hl, sFeatureSaveMagic
	ld de, .magic
	ld b, 4
.magicLoop
	ld a, [de]
	inc de
	cp [hl]
	jr nz, .invalid
	inc hl
	dec b
	jr nz, .magicLoop
	ld a, [sFeatureSaveVersion]
	cp FEATURE_SAVE_VERSION
	jr nz, .invalid
	ld a, [sFeatureSaveSize]
	cp LOW(FEATURE_DATA_SIZE)
	jr nz, .invalid
	ld a, [sFeatureSaveSize + 1]
	cp HIGH(FEATURE_DATA_SIZE)
	jr nz, .invalid
	ld hl, sFeatureSaveStart
	ld bc, sFeatureSaveEnd - sFeatureSaveStart
	call .checksum
	ld b, a
	ld a, [sFeatureSaveChecksum]
	cp b
	jr nz, .invalid
.valid
	and a
	ret
.invalid
	scf
	ret
.magic
	db "QOLS"
.checksum
	ld d, 0
.sum
	ld a, [hli]
	add d
	ld d, a
	dec bc
	ld a, b
	or c
	jr nz, .sum
	ld a, d
	cpl
	ret

GreenPlayerCharacterTitleGraphics::
	INCBIN "gfx/title/green_player.2bpp"
.end
	ASSERT .end - GreenPlayerCharacterTitleGraphics == 35 tiles
	ASSERT PlayerCharacterTitleGraphicsEnd - PlayerCharacterTitleGraphics == 35 tiles
