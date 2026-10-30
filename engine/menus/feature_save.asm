SECTION "Versioned Feature Save", ROMX

; Public entry points expect WRAM bank 0 (the normal game bank). The stack
; resides in banked WRAM, so every return must restore bank 0 first.
InitFeatureData:
	ld a, 3
	ldh [rSVBK], a
	ld hl, wFeatureData
	ld bc, FEATURE_DATA_SIZE
	xor a
	call FillMemory
	xor a
	ldh [rSVBK], a
	ret

; SRAM bank 1 is enabled by LoadSAV0. Only old inventory formats may lack an
; extension. A current save with missing/corrupt/newer extension is rejected.
LoadFeatureSaveData:
	ld a, [wInventoryFormat]
	cp $49
	jp nz, InitFeatureData
	ld a, [wInventoryFormat + 1]
	cp $31
	jp z, InitFeatureData
	cp $32
	jr nz, .bad
	ld hl, sFeatureSaveMagic
	ld de, .magic
	ld b, 4
.magicLoop
	ld a, [de]
	inc de
	cp [hl]
	jr nz, .bad
	inc hl
	dec b
	jr nz, .magicLoop
	ld a, [sFeatureSaveVersion]
	cp FEATURE_SAVE_VERSION
	jr nz, .bad
	ld a, [sFeatureSaveSize]
	cp LOW(FEATURE_DATA_SIZE)
	jr nz, .bad
	ld a, [sFeatureSaveSize + 1]
	cp HIGH(FEATURE_DATA_SIZE)
	jr nz, .bad
	ld hl, sFeatureSaveStart
	ld bc, sFeatureSaveEnd - sFeatureSaveStart
	call FeatureSaveChecksum
	ld b, a
	ld a, [sFeatureSaveChecksum]
	cp b
	jr nz, .bad
	ld a, 3
	ldh [rSVBK], a
	ld hl, sFeatureSavePayload
	ld de, wFeatureData
	ld bc, FEATURE_DATA_SIZE
	call CopyData
	xor a
	ldh [rSVBK], a
	ret
.bad
	scf
	ret
.magic
	db "QOLS"

SaveFeatureSaveData:
	ld a, 3
	ldh [rSVBK], a
	ld hl, wFeatureData
	ld de, sFeatureSavePayload
	ld bc, FEATURE_DATA_SIZE
	call CopyData
	xor a
	ldh [rSVBK], a
	ld hl, sFeatureSaveStart
	ld bc, 16
	xor a
	call FillMemory
	ld hl, LoadFeatureSaveData.magic
	ld de, sFeatureSaveMagic
	ld bc, 4
	call CopyData
	ld a, FEATURE_SAVE_VERSION
	ld [sFeatureSaveVersion], a
	ld a, LOW(FEATURE_DATA_SIZE)
	ld [sFeatureSaveSize], a
	ld a, HIGH(FEATURE_DATA_SIZE)
	ld [sFeatureSaveSize + 1], a
	ld hl, sFeatureSaveStart
	ld bc, sFeatureSaveEnd - sFeatureSaveStart
	call FeatureSaveChecksum
	ld [sFeatureSaveChecksum], a
	ret

; Small standard complemented-sum checksum, matching the base save's scheme.
; Shared by load/save, without depending on the fixed engine-save ROM bank.
FeatureSaveChecksum:
	ld d, 0
.loop
	ld a, [hli]
	add d
	ld d, a
	dec bc
	ld a, b
	or c
	jr nz, .loop
	ld a, d
	cpl
	ret

; Future gameplay code can use these instead of changing WRAM banks itself.
; HL is an absolute address within wFeatureData. C is value/output, clobbered.
GetFeatureByte:
	ld a, 3
	ldh [rSVBK], a
	ld a, [hl]
	ld c, a
	xor a
	ldh [rSVBK], a
	ld a, c
	ret
SetFeatureByte:
	ld a, 3
	ldh [rSVBK], a
	ld [hl], c
	xor a
	ldh [rSVBK], a
	ret
