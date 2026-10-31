SECTION "DX Edition Title Lettering", ROMX

Version_GFX:
IF DEF(_RED)
	INCBIN "gfx/title/red_version.1bpp", 0, 9 * 8 ; omit empty trailing tile
ENDC
IF DEF(_BLUE)
	INCBIN "gfx/title/blue_version.1bpp", 0, 9 * 8 ; omit empty trailing tile
ENDC
	; Keep the original German edition lettering and add a readable DX suffix
	; using existing font tiles, without changing the original PNG artwork.
IF GEN_2_GRAPHICS
	INCBIN "gfx/gs/font.1bpp", ("D" - $80) * 8, 8
	INCBIN "gfx/gs/font.1bpp", ("X" - $80) * 8, 8
ELSE
	INCBIN "gfx/font/font.1bpp", ("D" - $80) * 8, 8
	INCBIN "gfx/font/font.1bpp", ("X" - $80) * 8, 8
ENDC
Version_GFXEnd:
	ASSERT (Version_GFXEnd - Version_GFX) % 8 == 0
	ASSERT (Version_GFXEnd - Version_GFX) / 8 == TITLE_EDITION_TILES
	ASSERT (Version_GFXEnd - Version_GFX) / 8 <= SCREEN_WIDTH
