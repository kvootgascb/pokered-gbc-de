; Logical WRAM bank-3 layout, like color/wram.asm. This project links with
; rgblink -d, so switchable WRAM is addressed explicitly rather than WRAMX.
; Access only with bank 3 selected or through the public byte accessors.
DEF wFeatureData EQU $d000
DEF wFeatureMode EQU wFeatureData + 0
DEF wFeaturePreferences EQU wFeatureData + 1
DEF wFeatureRegisteredItem EQU wFeatureData + 2
DEF wFeatureSchemaFlags EQU wFeatureData + 3
DEF wFeatureOakBattleAvailable EQU wFeatureData + 4
DEF wFeatureAnneState EQU wFeatureData + 5
DEF wFeatureMewState EQU wFeatureData + 6
DEF wFeatureBoxReminderState EQU wFeatureData + 7
DEF wFeatureEliteFourWins EQU wFeatureData + 8 ; word
DEF wFeatureOakWins EQU wFeatureData + 10 ; word
DEF wFeatureStarterRewards EQU wFeatureData + 12
DEF wFeatureTradeBackState EQU wFeatureData + 13
DEF wFeatureOakPendingStarter EQU wFeatureData + 14
DEF wFeatureLastRepel EQU wFeatureData + 15
DEF wFeatureEventFlags EQU wFeatureData + 16 ; 64 bytes
DEF wFeatureGymRematches EQU wFeatureEventFlags ; one availability bit per arena
DEF wFeatureCounters EQU wFeatureData + 80 ; 32 bytes
DEF wFeatureReserved EQU wFeatureData + 112
DEF wFeatureDataEnd EQU wFeatureData + FEATURE_DATA_SIZE
ASSERT wFeatureDataEnd <= $d200
