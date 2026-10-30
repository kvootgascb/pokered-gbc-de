SECTION "Oak Champion Battle", ROMX

OakPostgameTalk::
	ld a, [wGameplayModeCache]
	and a
	ret z
	callfar EnsureChampionFeatures
	ld hl, wFeatureOakPendingStarter
	read_feature_byte
	ld a, c
	and a
	jp nz, GiveOakReward
	ld hl, wFeatureOakBattleAvailable
	read_feature_byte
	ld a, c
	cp 1
	jr z, .offer
	and a ; do not replace the regular Pokedex conversation
	ret
.offer
	ld hl, .invitation
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	jr nz, .handled
	ld a, OPP_PROF_OAK
	ld [wEngagedTrainerClass], a
	ld b, 1
	ld a, [wPlayerStarter]
	cp CHARMANDER
	jr nz, .notCharmander
	ld b, 2
.notCharmander
	cp SQUIRTLE
	jr nz, .team
	ld b, 3
.team
	ld a, b
	ld [wEngagedTrainerSet], a
	call InitBattleEnemyParameters
	ld hl, .wonText
	ld de, .lostText
	call SaveEndBattleTextPointers
	ld hl, wd72d
	set 6, [hl]
	set 7, [hl]
	ld a, 5 ; Oak's lab object
	ld [wSpriteIndex], a
	ld a, 19 ; appended lab post-battle script
	ld [wOaksLabCurScript], a
	ld hl, wFeatureOakBattleAvailable
	ld c, 0
	write_feature_byte
.handled
	scf
	ret
.invitation
	text "Als junger Trainer"
	line "habe ich oft"
	cont "gekämpft ..."
	para "Kämpfst Du mit mir?"
	line "Der Erinnerung"
	cont "wegen, CHAMPION!"
	prompt
.wonText
	text "Wunderbar! Du hast"
	line "mich an früher"
	cont "erinnert!"
	prompt
.lostText
	text "Ein spannender"
	line "Kampf, nicht wahr?"
	prompt

ResolveOakPostgameBattle::
	ld a, [wIsInBattle]
	cp $ff
	ret z
	ld a, [wBattleResult]
	and a
	ret nz
	; 0..2 are equiprobable (reject 255 before reducing modulo three).
.roll
	call Random
	cp 255
	jr z, .roll
.modulo
	cp 3
	jr c, OakRewardRoll
	sub 3
	jr .modulo
OakRewardRoll:
	ld hl, .starters
	ld e, a
	ld d, 0
	add hl, de
	ld c, [hl]
	ld hl, wFeatureOakPendingStarter
	write_feature_byte
	ld a, 3
	ldh [rSVBK], a
	ld hl, wFeatureOakWins
	inc [hl]
	jr nz, .counted
	inc hl
	inc [hl]
.counted
	xor a
	ldh [rSVBK], a
	ret
.starters
	db BULBASAUR, CHARMANDER, SQUIRTLE

GiveOakReward:
	ld a, [wPartyCount]
	cp PARTY_LENGTH
	jr nc, .full
	ld hl, .gift
	call PrintText
	ld hl, wFeatureOakPendingStarter
	read_feature_byte
	ld b, c
	ld c, 5
	call GivePokemon
	jr nc, .done
	ld hl, wFeatureOakPendingStarter
	ld c, 0
	write_feature_byte
.done
	scf
	ret
.full
	ld hl, .comeBack
	call PrintText
	scf
	ret
.gift
	text "Ein junges #MON"
	line "begleitet Dich."
	para "Hier, nimm es mit!"
	prompt
.comeBack
	text "Dein Team ist voll."
	para "Mach bitte Platz."
	line "Ich bewahre Dein"
	cont "Geschenk für Dich!"
	prompt
