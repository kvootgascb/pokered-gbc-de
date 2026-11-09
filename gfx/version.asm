SECTION "DX Edition Title Lettering", ROMX

Version_GFX:
IF DEF(_RED)
	INCBIN "gfx/title/red_version.1bpp", 0, 9 * 8 ; omit empty trailing tile
ENDC
IF DEF(_BLUE)
	INCBIN "gfx/title/blue_version.1bpp", 0, 9 * 8 ; omit empty trailing tile
ENDC
	; EDITION ends at pixel 69. Its last tile already has two blank columns.
	; Add six more for RED (8-pixel word gap), two for BLUE (4-pixel gap).
Version_DX_GFX:
	; Same five-pixel-high D/X lettering and one-pixel letter gap as before.
IF DEF(_RED)
	db 0, 0, 0, %00000011, %00000011, %00000011, %00000011, %00000011
	db 0, 0, 0, %11001100, %00100111, %00100011, %00100111, %11001100
	db 0, 0, 0, %11000000, %10000000, %00000000, %10000000, %11000000
ELSE
	db 0, 0, 0, %00111100, %00110010, %00110010, %00110010, %00111100
	db 0, 0, 0, %11001100, %01111000, %00110000, %01111000, %11001100
	ds 8, 0
ENDC
Version_GFXEnd:
	ASSERT Version_GFXEnd - Version_DX_GFX == 3 * 8
	ASSERT (Version_GFXEnd - Version_GFX) % 8 == 0
	ASSERT (Version_GFXEnd - Version_GFX) / 8 == TITLE_EDITION_TILES
	ASSERT (Version_GFXEnd - Version_GFX) / 8 <= SCREEN_WIDTH
