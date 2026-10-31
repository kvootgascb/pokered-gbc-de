# Green player graphics

The female player graphics were sourced from [Nog-Frog/pokered-girl](https://github.com/Nog-Frog/pokered-girl), commit `573e9b9b8859b642d79ce30d2d6b5cc0a2adabc8`.
These depict the classic female protagonist with a dark dress, rather than Leaf's FireRed/LeafGreen hat design.

Imported PNGs retain the original pixels; only filenames changed:

- `gfx/player/red.png`, `redb.png`, `shrink1.png`, `shrink2.png` → `gfx/player/green.png`, `greenb.png`, `green_shrink1.png`, `green_shrink2.png`
- `gfx/sprites/red.png`, `red_bike.png` → `gfx/sprites/green.png`, `green_bike.png`
- `gfx/overworld/red_fish_{front,back,side}.png` → corresponding `green_fish_*.png`
- `gfx/title/player.png` → `gfx/title/green_player.png`

The source repository does not provide an explicit graphics license or identify a separate sprite artist in its README. This attribution is a record of provenance, not a claim of an unrestricted license. Original Pokémon characters belong to their respective owners.

The gender choice uses two previously unused bytes in the existing saved main-data block. A girl is recognized only when `wPlayerGenderTag` is `$47` and `wPlayerGender` is `1`; untagged legacy saves use the boy's graphics. Save-data offsets and sizes remain unchanged. The standard save checksum covers these bytes.

Walking, cycling, fishing, introduction (including shrinking), trainer card, local battle back view and Hall of Fame select the player's graphics. Surfing retains the shared Seel sprite. Link opponents retain their existing graphics: the old link protocol does not transmit gender.

The title screen also shows the saved protagonist, using Green's matching 40×56 title sprite. Without a valid save it shows the original boy. An appearance change in the hidden menu affects the next title display after the player saves normally. The title reads SRAM without loading gameplay state, migrating inventory, or rewriting any save bytes. It checks the original save checksum, the gender tag, and, for current I2 saves, the versioned feature header and checksum. Tagged legacy saves remain supported; untagged or invalid saves fall back to the boy. Logo, cycling Pokémon, ball animation and existing title palette remain unchanged. The title's temporary gender byte uses existing unsaved padding; save layout and version are unchanged.

The female back picture uses the original 32×32 sprite scaling path, while the boy and old-man tutorial keep the existing Gen 2 back-picture path.

## Hidden in-game appearance menu

Open **Start → OPTION** and hold **SELECT alone for about three seconds** (180 frames). Release SELECT when the menu appears. Choose **♂** (boy) or **♀** (Green) with Left/Right; the change takes effect immediately and the menu stays open. Page 1 contains gender, game mode, VM animations and **ZURÜCK**. Up/Down changes rows; SELECT switches between pages, with **S. 1/2** / **S. 2/2** at the bottom right. Holding SELECT does not repeatedly turn pages. Left/Right also applies the game mode immediately. A exits only on **ZURÜCK**; B or Start also return to the regular options screen. Applied changes remain active when leaving the menu.

The hidden menu matches the regular text-speed option: one standard box headed **GESCHLECHT**, male/female symbols on the same row with a horizontal cursor, a second matching box for **SPIELMODUS** (Classic/Erweitert), and **ZURÜCK** below near the bottom of the screen. After applying a sprite change it reloads the font and text-box graphics before returning to Options: the second set of player animation tiles shares VRAM at `$8800` with the menu font. The normal Start-menu close path reloads the overworld animation tiles again. Regression checks compare the font VRAM before and after both switch directions and on return to the Start menu.

The shortcut is available only from the in-game Start menu, not the title-screen options. A short hold does nothing; releasing SELECT or pressing another button resets the hold timer. Switching updates the player graphics immediately without changing the name, position, facing, transport mode, or game options. Use the normal **SICHERN** command to retain the appearance in the save file.

## Validation

Build all three ROM targets with the pinned RGBDS 0.6.1 toolchain. For the headless integration checks, install `pyboy==2.8.1` in a separate Python virtual environment, then run from the repository root:

```sh
python tests/player_gender_smoke.py pokered
python tests/player_gender_smoke.py pokeblue
```

These checks execute the actual intro and Start → Options shortcut, verify hold/reset/cancel behavior, compare player VRAM with the selected sprite data, exercise checksum-checked save/load, and check the title-screen restriction. Battle-back and Hall-of-Fame graphics routines are exercised directly; this is not a full playthrough of those sequences.
