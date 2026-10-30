# Persistent feature save: schema 1

The current ROM can load existing unmarked 20/50 and `I1` 30/60 in-game saves
without starting a new game. On loading, it migrates inventories to 30/70,
preserves existing progress and initializes feature data to safe zero defaults.
The ordinary save command writes the new `I2` format and feature extension.

Mode selection, the EXP-bar switch, running and the champion events are implemented.
The independent preferences and registered-item shortcut remain reserved.
The existing gender field stays in the base save. See [postgame-features.md](postgame-features.md) for the active events.

## Fixed storage

- Base save layout: inventory marker `I2`, main-data length and Pokémon-box
  storage unchanged. Inventory migration is in `engine/items/inventory_migration.asm`.
- Feature SRAM: bank 1, `$b600`–`$b810`, outside the base checksummed block.
- Header at `$b600`: four-byte magic `QOLS`, one-byte schema version `1`,
  two-byte little-endian payload size `512`, nine reserved zero header bytes.
- Payload at `$b610`: 512 bytes, with its own complemented-sum checksum
  immediately afterward at `$b810` (same checksum scheme as the base game).
- Runtime payload: WRAM bank 3, `$d000`–`$d1ff`, kept clear of banked stacks.
  The logical layout is in `ram/feature_data.asm`, following the project's
  explicit bank-addressing convention used by the color engine.
- New Game clears all feature data. Loading old formats also clears it; it
  does not import potentially stale bytes from their unused SRAM space.

| Payload offset | Bytes | Reserved meaning / initial value |
| --- | --- | --- |
| 0 | 1 | Mode: 0 Classic, 1 Extended; default Classic |
| 1 | 1 | Independent preferences: fast healing bit 0, skip VM animation bit 1; both off |
| 2 | 1 | Registered basis item; 0 means none |
| 3 | 1 | Feature-initialization flags; bit 0: champion events initialized |
| 4 | 1 | Oak battle availability; zero |
| 5 | 1 | M.S. Anne availability: 0 unavailable, 1 available |
| 6 | 1 | Mew state: 0 unseen, 1 front, 2 rear, 3 encounter consumed |
| 7 | 1 | Box reminder state; zero |
| 8 | 2 | Elite Four victory counter; zero |
| 10 | 2 | Oak victory counter; zero |
| 12 | 1 | Starter reward tracking; zero |
| 13 | 1 | Trade-back state; zero |
| 14 | 1 | Pending Oak starter species; 0 means no gift |
| 15 | 1 | Reserved |
| 16 | 64 | Future event flags, including per-feature initialization flags |
| 80 | 32 | Future counters |
| 112 | 400 | General reserve |

Pokémon moves, items, badges, existing one-time encounters and normal story
progress remain in their original base structures; they do not need duplicate
fields in this payload. Rules such as reusable TMs and running can derive from
the mode, with any future unlock conditions assigned reserved event flags.

## Updating and accessing features

Keep published offsets stable. Assign new fields from the reserve instead of
inserting bytes. Preserve the entire payload, including currently unused bytes.
For a feature whose initial state cannot simply be zero, assign an initialization
flag and initialize it once from existing game progress when that feature ships.
Oak/Anne initialize once from `wNumHoFTeams` for existing champions, using
schema-flags bit 0. This offers one opportunity without inventing an old victory
count. New championships increment the counter and refresh one opportunity.

If the payload schema ever changes, explicitly migrate supported earlier
versions in `LoadFeatureSaveData`; never silently reset an existing block.
The current version rejects a bad checksum, missing I2 extension, unsupported
schema version or incorrect size through the existing save-error path. It does
not overwrite the file as part of a failed load.

Public `GetFeatureByte`/`SetFeatureByte` take an absolute payload address in HL;
C is the read result/write value. They expect and restore normal WRAM bank 0.
The bulk initialize/load/save routines have the same bank-0 calling contract.
The stack is in banked WRAM: do not return or pop a bank-0 return address while
another WRAM bank is selected. `LoadSAV0` validates the base checksum first,
then the extension, then migrates the inventory. `SaveSAVtoSRAM0` writes both.

## Player upgrade path and limits

Use an ordinary in-game save, keep a backup `.sav`, update the ROM and load
normally. Do not transfer an emulator save state containing an older ROM's
execution/RAM layout. Once saved as I2, do not open the save in an older ROM.

This makes continuing the current playthrough the expected path for the agreed
features. It cannot guarantee compatibility with every future design change:
feature activation, existing progress and any new schema still require migration
work. This infrastructure does not by itself add the planned gameplay.

## Verification

`tests/player_gender_smoke.py` tests full 30/70 boundaries and overflow guards,
whole-main-data migration from 20/50 and I1 30/60, repeated save/load, preservation
of all 512 feature bytes, default initialization, bank-safe accessors, and
rejection of corrupted, missing or newer feature blocks. It also exercises the
intro, sprite selection, font integrity and return to the original menus.


The current mode is mirrored into `wGameplayModeCache` in previously unused
base-save padding for hot rendering/movement paths. Initialize/load rebuild the
mirror from the feature payload; it is not an independent setting. Mode UI uses
`SetGameplayMode` locally or the register-argument-free farcall entry
`CommitGameplayMode`, which reads `wModeMenuChoice`. Normal farcall trampolines
clobber HL and BC, so do not pass their pointers/values through them unchanged.

ROMX callers use `read_feature_byte` / `write_feature_byte` (HL address, C value).
These macros use base-WRAM scratch and register-free farcall entry points.
Do not use `homecall` to switch banks from executing ROMX code.
