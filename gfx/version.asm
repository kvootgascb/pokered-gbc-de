SECTION "DX Edition Title Lettering", ROMX

; Generated from the original artwork, with matching word gaps and equal
; blank margins around the visible lettering (not just centered tile bounds).
Version_GFX:
IF DEF(_RED)
	INCBIN "gfx/title/red_dx.1bpp"
ENDC
IF DEF(_BLUE)
	INCBIN "gfx/title/blue_dx.1bpp"
ENDC
Version_GFXEnd:
	ASSERT (Version_GFXEnd - Version_GFX) / 8 == TITLE_EDITION_TILES
	ASSERT (Version_GFXEnd - Version_GFX) % 8 == 0
	ASSERT TITLE_EDITION_TILES <= SCREEN_WIDTH
