SECTION "Full Box Reminder", ROMX

; Only called after a successful wild capture has been transferred to the PC.
; Reaching 20 entries is the transition to full: later captures cannot enter
; this path until the player makes room or changes boxes. No saved latch needed.
RemindAboutFullBox::
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wBoxCount]
	cp MONS_PER_BOX
	ret nz
.warn
	ld hl, .text
	jp PrintText
.text
	text "Ich sollte meine"
	line "#MON-Box prüfen."
	para "Vielleicht ist sie"
	line "schon voll ..."
	done
