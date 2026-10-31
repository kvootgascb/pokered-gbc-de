SECTION "DX Edition Title Lettering", ROMX

Version_GFX:
IF DEF(_RED)
	INCBIN "gfx/title/red_version.1bpp", 0, 9 * 8 ; omit empty trailing tile
ENDC
IF DEF(_BLUE)
	INCBIN "gfx/title/blue_version.1bpp", 0, 9 * 8 ; omit empty trailing tile
ENDC
	; Match the edition lettering's bold five-pixel height and baseline.
	ds 8, 0 ; one ordinary space before DX
Version_DX_GFX:
	; Packed D (identical to EDITION's D), one pixel gap, then X.
	; Both letters occupy rows 3..7, as the original edition name does.
	db 0, 0, 0, %11110011, %11001001, %11001000, %11001001, %11110011
	db 0, 0, 0, %00110000, %11100000, %11000000, %11100000, %00110000
Version_GFXEnd:
	ASSERT Version_GFXEnd - Version_DX_GFX == 2 * 8
	ASSERT (Version_GFXEnd - Version_GFX) % 8 == 0
	ASSERT (Version_GFXEnd - Version_GFX) / 8 == TITLE_EDITION_TILES
	ASSERT (Version_GFXEnd - Version_GFX) / 8 <= SCREEN_WIDTH
