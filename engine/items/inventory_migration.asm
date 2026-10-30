SECTION "Inventory Save Migration", ROMX

; Called only after the original SRAM checksum has passed. Save block lengths
; and all offsets after the reclaimed scratch gap remain unchanged.
MigrateLegacyInventory:
	ld a, [wInventoryFormat]
	cp $49
	jr nz, .legacy
	ld a, [wInventoryFormat + 1]
	cp $32
	ret z
	cp $31
	jr z, .version1
	jr .legacy
.version1
	; The 30/60 layout already has the final bag and PC start addresses.
	ld hl, wBoxItems + 60 * 2 + 1
	ld bc, (PC_ITEM_CAPACITY - 60) * 2
	xor a
	call FillMemory
	ld hl, sMainData + wCurrentBoxNum - wMainDataStart - (PC_ITEM_CAPACITY - 60) * 2
	ld de, wCurrentBoxNum
	ld bc, wGameProgressFlagsEnd - wCurrentBoxNum
	call CopyData
	jr .tag
.legacy
	; Bag count and old slots have not moved. Clear its new trailing slots.
	ld hl, wBagItems + LEGACY_BAG_ITEM_CAPACITY * 2 + 1
	ld bc, BAG_STORAGE_GROWTH
	xor a
	call FillMemory
	ld hl, sMainData + wPlayerMoney - wMainDataStart - BAG_STORAGE_GROWTH
	ld de, wPlayerMoney
	ld bc, wNumBoxItems - wPlayerMoney
	call CopyData
	ld hl, sMainData + wNumBoxItems - wMainDataStart - BAG_STORAGE_GROWTH
	ld de, wNumBoxItems
	ld bc, 1 + LEGACY_PC_ITEM_CAPACITY * 2 + 1
	call CopyData
	ld hl, wBoxItems + LEGACY_PC_ITEM_CAPACITY * 2 + 1
	ld bc, PC_STORAGE_GROWTH
	xor a
	call FillMemory
	ld hl, sMainData + wCurrentBoxNum - wMainDataStart - BAG_STORAGE_GROWTH - PC_STORAGE_GROWTH
	ld de, wCurrentBoxNum
	ld bc, wGameProgressFlagsEnd - wCurrentBoxNum
	call CopyData

.tag
	ld a, $49
	ld [wInventoryFormat], a
	ld a, $32
	ld [wInventoryFormat + 1], a
	ret

; Guard the legacy format and the offsets after the reclaimed unused bytes.
ASSERT wMainDataStart == $d2f7
ASSERT wNumBagItems == $d31d
ASSERT wObtainedHiddenItemsFlags == $d6f0
ASSERT wInventoryFormat == $da3a
ASSERT wMainDataEnd == $da80
ASSERT wBoxDataEnd == $dee2
