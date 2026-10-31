SECTION "Champion Gym Rematches", ROMX

EnsureGymRematches::
	ld hl, wFeatureSchemaFlags
	read_feature_byte
	bit 1, c
	ret nz
	set 1, c
	write_feature_byte
	ld a, [wNumHoFTeams]
	and a
	ret z
	jr ResetGymRematchMask

RefreshGymRematches::
	ld hl, wFeatureSchemaFlags
	read_feature_byte
	set 1, c
	write_feature_byte
ResetGymRematchMask:
	ld hl, wFeatureGymRematches
	ld c, $ff
	write_feature_byte
	ret

; Each record: map, trainer class, party number, post-battle script, script RAM.
; Record order matches the badge bits. Scratch stays outside menu/VRAM buffers.
LoadGymRematchRecord:
	ld hl, GymRematchData
	ld c, 0
.scan
	ld a, [hli]
	cp $ff
	ret z
	ld b, a
	ld a, [wCurMap]
	cp b
	jr z, .found
	ld de, 5
	add hl, de
	inc c
	jr .scan
.found
	ld a, c
	ld [wTutorPartyIndex], a
	ld b, a
	inc b
	ld a, 1
.mask
	dec b
	jr z, .masked
	sla a
	jr .mask
.masked
	ld [wTutorMode], a
	ld a, l
	ld [wTutorRecordPtr], a
	ld a, h
	ld [wTutorRecordPtr + 1], a
	scf
	ret

GymRematchContext:
	ld a, [wGameplayModeCache]
	and a
	ret z
	ld a, [wNumHoFTeams]
	and a
	ret z
	call LoadGymRematchRecord
	ret nc
	ld a, [wObtainedBadges]
	ld b, a
	ld a, [wTutorMode]
	and b
	ret z
	scf
	ret

CheckGymRematchAvailable::
	call GymRematchContext
	ret nc
	call EnsureGymRematches
	ld hl, wFeatureGymRematches
	read_feature_byte
	ld a, [wTutorMode]
	and c
	ret z
	scf
	ret

ConsumeGymRematch::
	call CheckGymRematchAvailable
	ret nc
	ld a, [wTutorMode]
	cpl
	and c
	ld c, a
	ld hl, wFeatureGymRematches
	write_feature_byte
	scf
	ret

; Called after the original badge/TM handout checks, never before a first win.
TryGymRematchTalk::
	call GymRematchContext
	ret nc
	call CheckGymRematchAvailable
	jr nc, .unavailable
	ld a, [wTutorPartyIndex]
	add a
	ld e, a
	ld d, 0
	ld hl, GymRematchInvitations
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	jr nz, .handled
	call StartGymRematch
.handled
	scf
	ret
.unavailable
	; Returned Giovanni must not run his original farewell/hide script again.
	ld a, [wTutorPartyIndex]
	cp 7
	jr nz, .original
	ld hl, .waitForLeague
	call PrintText
	scf
	ret
.original
	and a
	ret
.waitForLeague
	text "Trainiere weiter."
	para "Nach Deinem"
	line "nächsten Ligasieg"
	cont "gibt es Revanche!"
	done

StartGymRematch::
	call ConsumeGymRematch
	ret nc
	ld a, [wTutorRecordPtr]
	ld l, a
	ld a, [wTutorRecordPtr + 1]
	ld h, a
	ld a, [hli]
	ld [wEngagedTrainerClass], a
	ld a, [hli]
	ld [wEngagedTrainerSet], a
	ld a, [hli]
	ld [wTutorCandidate], a
	ld e, [hl]
	inc hl
	ld d, [hl]
	ld a, [wTutorCandidate]
	ld [de], a
	ld [wCurMapScript], a
	ld a, [wTutorPartyIndex]
	inc a
	ld [wGymLeaderNo], a ; original signature move and victory music
	call InitBattleEnemyParameters
	ld hl, .winText
	ld de, .lossText
	call SaveEndBattleTextPointers
	ld hl, wd72d
	set 6, [hl]
	set 7, [hl]
	ld a, 1 ; all eight leaders are the first arena object
	ld [wSpriteIndex], a
	scf
	ret
.winText
	text "Du hast viel"
	line "gelernt, CHAMPION!"
	prompt
.lossText
	text "Diese Revanche hat"
	line "sich gelohnt!"
	prompt

; No first-win rewards or original event resets, including after a loss.
FinishGymRematch::
	call LoadGymRematchRecord
	ret nc
	inc hl
	inc hl
	inc hl
	ld e, [hl]
	inc hl
	ld d, [hl]
	xor a
	ld [de], a
	ld [wCurMapScript], a
	ld [wJoyIgnore], a
	ld [wGymLeaderNo], a
	ldh [hJoyHeld], a
	ldh [hJoyPressed], a
	ldh [hJoyReleased], a
	ld hl, wd72d
	res 7, [hl]
	ld hl, wFlags_0xcd60
	res 0, [hl]
	ret

PrepareGiovanniRematch::
	ld a, [wCurrentMapScriptFlags]
	bit 6, a
	ret z
	res 6, a
	ld [wCurrentMapScriptFlags], a
	ld a, [wNumHoFTeams]
	and a
	ret z
	CheckEvent EVENT_BEAT_VIRIDIAN_GYM_GIOVANNI
	ret z
	CheckEvent EVENT_GOT_TM27
	ret z
	ld a, HS_VIRIDIAN_GYM_GIOVANNI
	ld [wMissableObjectIndex], a
	ld a, [wGameplayModeCache]
	and a
	jr z, .hide
	predef ShowObject
	ret
.hide
	predef HideObject
	ret

GymRematchData::
	table_width 6, GymRematchData
	db PEWTER_GYM, OPP_BROCK, 2, SCRIPT_PEWTERGYM_REMATCH
	dw wPewterGymCurScript
	db CERULEAN_GYM, OPP_MISTY, 2, SCRIPT_CERULEANGYM_REMATCH
	dw wCeruleanGymCurScript
	db VERMILION_GYM, OPP_LT_SURGE, 2, SCRIPT_VERMILIONGYM_REMATCH
	dw wVermilionGymCurScript
	db CELADON_GYM, OPP_ERIKA, 2, SCRIPT_CELADONGYM_REMATCH
	dw wCeladonGymCurScript
	db FUCHSIA_GYM, OPP_KOGA, 2, SCRIPT_FUCHSIAGYM_REMATCH
	dw wFuchsiaGymCurScript
	db SAFFRON_GYM, OPP_SABRINA, 2, SCRIPT_SAFFRONGYM_REMATCH
	dw wSaffronGymCurScript
	db CINNABAR_GYM, OPP_BLAINE, 2, SCRIPT_CINNABARGYM_REMATCH
	dw wCinnabarGymCurScript
	db VIRIDIAN_GYM, OPP_GIOVANNI, 4, SCRIPT_VIRIDIANGYM_REMATCH
	dw wViridianGymCurScript
	assert_table_length 8
	db $ff

GymRematchInvitations:
	dw .brock, .misty, .surge, .erika, .koga, .sabrina, .blaine, .giovanni
.brock
	text "Seit unserem Kampf"
	line "ist viel passiert."
	para "Zeig, wie stark Du"
	line "geworden bist!"
	cont "Eine Revanche?"
	prompt
.misty
	text "Du bist CHAMPION?"
	para "Bestehst Du gegen"
	line "meine Strömung?"
	cont "Eine Revanche?"
	prompt
.surge
	text "Die Niederlage ist"
	line "mir noch im Kopf,"
	cont "Soldat!"
	para "Zeit für eine"
	line "Revanche! Bereit?"
	prompt
.erika
	text "Dein Können ist"
	line "aufgeblüht."
	para "Darf ich es noch"
	line "einmal erleben?"
	prompt
.koga
	text "Ein Ninja hört nie"
	line "auf zu trainieren."
	para "Prüfen wir, was"
	line "wir gelernt haben?"
	prompt
.sabrina
	text "Du würdest kommen,"
	line "das ahnte ich."
	para "Den Ausgang sehe"
	line "ich nicht. Kämpfen"
	cont "wir noch einmal?"
	prompt
.blaine
	text "Neue Frage: Wie"
	line "bestehst Du gegen"
	cont "mein Feuer?"
	para "Finden wir es"
	line "im Kampf heraus?"
	prompt
.giovanni
	text "Im Rückzug habe"
	line "ich trainiert."
	para "Aus der Niederlage"
	line "musste ich lernen."
	para "Prüfe mich erneut!"
	prompt
