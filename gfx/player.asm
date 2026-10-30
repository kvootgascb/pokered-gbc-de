IF GEN_2_GRAPHICS
RedPicFront:: INCBIN "gfx/gstrainers/red.pic"
rept 11 ; Padding
	db 0
endr
ELSE
RedPicFront:: INCBIN "gfx/player/red.pic"
ENDC

ShrinkPic1::  INCBIN "gfx/player/shrink1.pic"
ShrinkPic2::  INCBIN "gfx/player/shrink2.pic"

GreenPicFront:: INCBIN "gfx/player/green.pic"
GreenShrinkPic1:: INCBIN "gfx/player/green_shrink1.pic"
GreenShrinkPic2:: INCBIN "gfx/player/green_shrink2.pic"
