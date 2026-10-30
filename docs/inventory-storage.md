# Expanded item storage

The bag holds **30 item stacks**, formerly 20. The player PC holds **70 item
stacks**, formerly 50. Stacks still hold up to 99 items; sorting, categories,
shop prices and item behavior are unchanged. The capacities apply independently
of any future Classic/Extended mode.

The extra 60 bytes come from the previously unused 56-byte gap after
`wGameProgressFlagsEnd` plus four unused bytes at the end of the map-script
scratch area before it. Main save-block lengths, party/box data and all
addresses after the gap remain unchanged. Constants and compile-time assertions
guard this layout. The Pokémon PC boxes are unaffected.

## Existing saves

After the original checksum has passed, `MigrateLegacyInventory` recognizes
unversioned 20/50 saves and the previous `I1` 30/60 saves and copies their bag/PC-related fields from the original SRAM
positions to the expanded WRAM layout. It initializes the newly available slots
and preserves the remaining saved data. The `I2` marker in two previously unused
bytes marks the expanded format. Normal saving writes the marker and the
standard checksum; loading that format does not migrate it again. `I2` saves
also require the separate versioned feature extension described in
[save-format.md](save-format.md).

Keep a backup before upgrading a ROM. Once saved in the expanded format, a
save should not be used with earlier ROM versions: those versions do not
understand the expanded inventory layout. Emulator save states also retain
old RAM/code execution state; use an ordinary in-game save when upgrading.

## Validation

`tests/player_gender_smoke.py` exercises the real inventory add routine through
both capacities, rejection at the new limits, adjacent-field preservation,
full-capacity save/load, and checksum-validated migration of a synthetic legacy
20/50 save and a full `I1` 30/60 save. Migration checks compare the complete main-data block, including
progress, names, money and location, followed by another save/load to catch
accidental repeated migration. Its existing UI tests also cover the horizontal
gender selector, cancellation, return to Options/Start, and intact font VRAM.
