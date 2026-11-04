"""Headless ROM regression test. Tested with PyBoy 2.8.1.

Build the ROM first; run: python tests/player_gender_smoke.py [pokered|pokeblue]
Tests execute the real intro and ROM graphics/save routines without writing a save file.
"""

from pyboy import PyBoy
from pathlib import Path
import io
import json
import sys

root = Path(__file__).resolve().parents[1]
rom = sys.argv[1] if len(sys.argv) > 1 else "pokered"
sym = {}
for line in (root / (rom + ".sym")).read_text().splitlines():
    parts = line.split()
    if len(parts) == 2 and ":" in parts[0]:
        b, a = parts[0].split(":")
        sym[parts[1]] = (int(b, 16), int(a, 16))
a = lambda n: sym[n][1]
p = PyBoy(str(root / (rom + ".gbc")), window="null", sound_emulated=False)
p.set_emulation_speed(0)
seen = []
portraits = []
copies = []


def hook(n, cb):
    p.hook_register(*sym[n], cb, None)


def record_pic(_):
    portraits.append((p.register_file.B, p.register_file.D * 256 + p.register_file.E))


def record_copy(_):
    copies.append((p.register_file.B, p.register_file.D * 256 + p.register_file.E))


hook("ChooseGameplayMode", lambda _: seen.append("mode"))
hook("ChoosePlayerGender", lambda _: seen.append("gender"))
hook("HandleMenuInput", lambda _: seen.append("menu"))
hook("IntroDisplayPicCenteredOrUpperRight", record_pic)
hook("CopyVideoData", record_copy)
hook("LoadWalkingPlayerSpriteGraphics", lambda _: seen.append("walking"))
for i in range(250):
    p.button("start" if i < 20 else "a", 2)
    p.tick(20, False)
    if "mode" in seen:
        p.tick(20, False)
        mode_top = list(p.memory[a("wTileMap") : a("wTileMap") + 20])
        mode_bottom = list(p.memory[a("wTileMap") + 120 : a("wTileMap") + 140])
        menu_state = io.BytesIO()
        p.save_state(menu_state)
        p.button("a", 2)
        p.tick(20, False)
        assert p.memory[a("wGameplayModeCache")] == 0
        assert p.memory[3, 0xD000] == 0
        menu_state.seek(0)
        p.load_state(menu_state)
        p.button("down", 2)
        p.tick(12, False)
        p.button("a", 2)
        p.tick(20, False)
        assert p.memory[a("wGameplayModeCache")] == 1
        assert p.memory[3, 0xD000] == 1
        break
assert "gender" in seen
assert list(p.memory[a("wTileMap") : a("wTileMap") + 20]) == mode_top
assert list(p.memory[a("wTileMap") + 120 : a("wTileMap") + 140]) == mode_bottom
bank, addr = sym["DefaultNamesGirlList"]
assert list(p.memory[bank, addr : addr + 20]) == [
    0x8D,
    0x80,
    0x8C,
    0x84,
    0x50,
    0x86,
    0xB1,
    0xD5,
    0xAD,
    0x50,
    0x84,
    0xAB,
    0xAB,
    0xB8,
    0x50,
    0x93,
    0xA8,
    0xAD,
    0xA0,
    0x50,
]

p.tick(30, False)
p.button("down", 2)
p.tick(12, False)
p.button("a", 2)
p.tick(20, False)
assert p.memory[a("wPlayerGender")] == 1
menu_count = seen.count("menu")
for i in range(220):
    if seen.count("menu") > menu_count:
        menu_count = seen.count("menu")
        p.tick(10, False)
        p.button("down", 2)
        p.tick(12, False)
    p.button("a", 2)
    p.tick(20, False)
    if "walking" in seen:
        break
assert sym["GreenPicFront"] in portraits, portraits
assert sym["GreenSprite"] in copies, "female overworld graphics never loaded"
print(
    "PASS: actual intro uses Green front and shrink pictures; female overworld tiles loaded"
)
assert sym["GreenShrinkPic1"] in portraits and sym["GreenShrinkPic2"] in portraits
# Invoke existing ROM subroutines at an initialized emulator state. Execution
# reaches a ROM0 sentinel after the real RET. The sentinel enables the LCD
# and loops so frame stepping also works for routines which disable the LCD.
base = io.BytesIO()
p.save_state(base)


def restore():
    base.seek(0)
    p.load_state(base)


def call(n, limit=180, auto_button=None):
    bank, pc = sym[n]
    # A frame snapshot can be inside an interrupt. Enable interrupts before
    # invoking routines which wait for VBlank, then return to a ROM0 loop.
    trampoline = [
        0xFB,
        0xCD,
        pc & 255,
        pc >> 8,
        0xF3,
        0x3E,
        0x91,
        0xE0,
        0x40,
        0x18,
        0xFE,
    ]
    for offset, byte in enumerate(trampoline):
        p.memory[0, 0x100 + offset] = byte
    p.memory[0xFF70] = 0
    if bank:
        p.memory[0x2000] = bank
        p.memory[a("hLoadedROMBank")] = bank
    p.register_file.PC = 0x100
    # DI after RET keeps the sentinel outside VBlank so PC/flags/registers
    # can be checked reliably, regardless of the routine's frame alignment.
    for frame in range(limit):
        if auto_button and frame % 20 == 0:
            p.button(auto_button() if callable(auto_button) else auto_button, 2)
        p.tick(1, False)
        if p.register_file.PC in (0x109, 0x10A):
            return
    raise AssertionError(
        f"{n} did not return: bank={p.memory[a('hLoadedROMBank')]:02x} "
        f"PC={p.register_file.PC:04x} SP={p.register_file.SP:04x}"
    )


# Enlarged inventory places this table across a 256-byte page boundary.
# Read every NPC slot through the actual update routine, not a Python lookup.
for slot in range(1, 16):
    restore()
    expected_direction = 0xD0 + (slot - 1) % 4
    p.memory[a("wMapSpriteData") + (slot - 1) * 2] = expected_direction
    p.memory[a("wSpriteStateData1") + slot * 16 + 1] = 0  # initialize, then return
    p.memory[a("hCurrentSpriteOffset")] = slot * 16
    call("UpdateNPCSprite")
    actual = p.memory[a("wCurSpriteMovement2")]
    assert actual == expected_direction, (
        "NPC movement lookup crossed a page",
        slot,
        hex(a("wMapSpriteData")),
        actual,
        expected_direction,
    )
restore()
print(
    "PASS: native NPC movement lookup reads all 15 slots correctly across the table page boundary"
)

# The title reads persisted appearance without loading or migrating the save.
call("SaveSAVtoSRAM0")
title_save = list(p.memory[1, 0xA000:0xBFFF])
title_main = list(p.memory[a("wMainDataStart") : a("wMainDataEnd")])


def title_checksum():
    data = p.memory[1, a("sGameData") : a("sGameDataEnd")]
    p.memory[1, a("sMainDataCheckSum")] = (~sum(data)) & 255


def check_title(expected):
    before = list(p.memory[1, 0xA000:0xBFFF])
    call("ReadTitlePlayerGender")
    assert p.memory[a("wTitlePlayerGender")] == expected
    assert list(p.memory[1, 0xA000:0xBFFF]) == before, "title rewrote SRAM"
    # VBlank advances the normal play timer while the routine executes.
    current = list(p.memory[a("wMainDataStart") : a("wMainDataEnd")])
    timer = a("wPlayTimeHours") - a("wMainDataStart")
    assert current[:timer] == title_main[:timer]
    assert current[timer + 5 :] == title_main[timer + 5 :]


check_title(1)
for field, value in [
    ("wPlayerGender", 0),
    ("wPlayerGender", 2),
    ("wPlayerGenderTag", 0),
]:
    p.memory[1, 0xA000:0xBFFF] = title_save
    p.memory[1, a("sMainData") + a(field) - a("wMainDataStart")] = value
    title_checksum()
    check_title(0)
for field in [
    "sMainDataCheckSum",
    "sFeatureSaveMagic",
    "sFeatureSaveVersion",
    "sFeatureSaveSize",
    "sFeatureSavePayload",
    "sFeatureSaveChecksum",
]:
    p.memory[1, 0xA000:0xBFFF] = title_save
    p.memory[1, a(field)] ^= 1
    check_title(0)
p.memory[1, 0xA000:0xBFFF] = title_save
p.memory[1, a("sPlayerName") : a("sPlayerName") + 11] = [255] * 11
title_checksum()
check_title(0)
for marker in [b"I1", bytes(2)]:
    p.memory[1, 0xA000:0xBFFF] = title_save
    offset = a("sMainData") + a("wInventoryFormat") - a("wMainDataStart")
    p.memory[1, offset : offset + 2] = list(marker)
    p.memory[1, a("sFeatureSaveMagic")] = 0
    title_checksum()
    check_title(1)
for gender, graphic in [
    (0, "PlayerCharacterTitleGraphics"),
    (1, "GreenPlayerCharacterTitleGraphics"),
]:
    p.memory[1, 0xA000:0xBFFF] = title_save
    offset = a("sMainData") + a("wPlayerGender") - a("wMainDataStart")
    p.memory[1, offset] = gender
    title_checksum()
    # The persisted value wins over an unsaved live change.
    p.memory[a("wPlayerGender")] = 1 - gender
    p.memory[0xFF40] = 0
    call("LoadTitlePlayerGraphics")
    bank, addr = sym[graphic]
    assert list(p.memory[0, 0x8000:0x8230]) == list(p.memory[bank, addr : addr + 560])
    assert p.memory[a("wPlayerGender")] == 1 - gender
# DX branding matches the original edition font height, weight and baseline.
header_name = b"POKEMON ROT DX" if rom == "pokered" else b"POKEMON BLAU DX"
assert (root / (rom + ".gbc")).read_bytes()[0x134:0x143].rstrip(b"\0") == header_name
original_label = (
    root
    / "gfx/title"
    / ("red_version.1bpp" if rom == "pokered" else "blue_version.1bpp")
).read_bytes()
assert original_label[-8:] == bytes(8), "trimming would remove visible edition pixels"
# Compare D with the actual edition artwork, plus an equally bold five-row X.
small_x = [
    "......",
    "......",
    "......",
    "##..##",
    ".####.",
    "..##..",
    ".####.",
    "##..##",
]
small_dx_rows = []
for y in range(8):
    d_bits = [
        int(bool(original_label[x // 8 * 8 + y] & (1 << (7 - x % 8))))
        for x in range(37, 42)
    ]
    small_dx_rows.append(
        d_bits + [0] + [int(pixel == "#") for pixel in small_x[y]] + [0] * 4
    )
small_dx = bytes(
    sum(small_dx_rows[y][tile * 8 + bit] << (7 - bit) for bit in range(8))
    for tile in range(2)
    for y in range(8)
)
expected_label = original_label[:-8] + bytes(8) + small_dx
assert len(expected_label) == 12 * 8
# Cold boots exercise the actual title path, including the default without a save.
for saved, graphic in [
    (title_save, "GreenPlayerCharacterTitleGraphics"),
    ([255] * len(title_save), "PlayerCharacterTitleGraphics"),
]:
    boot = PyBoy(str(root / (rom + ".gbc")), window="null", sound_emulated=False)
    boot.set_emulation_speed(0)
    boot.memory[1, 0xA000:0xBFFF] = saved
    drawn = []
    boot.hook_register(
        *sym["DrawPlayerCharacter.loop"], lambda _: drawn.append(True), None
    )
    for _ in range(1200):
        boot.tick(1, False)
        if drawn:
            break
    assert drawn, "cold boot never drew the title character"
    boot.tick(180, True)
    bank, addr = sym[graphic]
    assert list(boot.memory[0, 0x8000:0x8230]) == list(
        boot.memory[bank, addr : addr + 560]
    )
    expected_vram = [value for byte in expected_label for value in (byte, byte)]
    assert list(boot.memory[0, 0x9600 : 0x9600 + len(expected_vram)]) == expected_vram
    row = a("wTileMap") + 8 * 20
    assert list(boot.memory[row + 4 : row + 16]) == list(range(0x60, 0x6C))
    assert list(boot.memory[1, 0xA000:0xBFFF]) == saved
    boot.screen.image.save(
        "/tmp/" + rom + "-title-" + ("girl" if saved is title_save else "boy") + ".png"
    )
    boot.stop(save=False)
print("PASS: title selects saved graphics; invalid/legacy saves handled read-only")
restore()

# Real save routine and checksum-checked restore, including the new bytes.
call("SaveSAVtoSRAM0")
p.memory[a("wPlayerGender")] = 0
p.memory[a("wPlayerGenderTag")] = 0
call("LoadSAV0")
assert p.memory[a("wPlayerGender")] == 1 and p.memory[a("wPlayerGenderTag")] == 0x47
print("PASS: save/load with existing SRAM checksum preserves girl selection")
for routine, graphic in [
    ("LoadWalkingPlayerSpriteGraphics", "GreenSprite"),
    ("LoadBikePlayerSpriteGraphics", "GreenBikeSprite"),
    ("LoadSurfingPlayerSpriteGraphics", "SeelSprite"),
]:
    restore()
    call(routine)
    bank, addr = sym[graphic]
    expected = list(p.memory[bank, addr : addr + 384])
    assert list(p.memory[0, 0x8000:0x80C0]) == expected[:192], (
        routine + " first frames differ"
    )
    assert list(p.memory[0, 0x8800:0x88C0]) == expected[192:], (
        routine + " walking frames differ"
    )
    print("PASS: " + routine + " loads the correct graphics into VRAM")
restore()
call("HoFLoadPlayerPics")
print("PASS: Hall of Fame player picture routine returns")
restore()
p.memory[a("wBattleType")] = 0
call("LoadPlayerBackPic")
print("PASS: female battle back picture routine returns")
restore()
p.memory[a("wBattleType")] = 1
call("LoadPlayerBackPic")
print("PASS: old-man tutorial back picture routine returns")
restore()
p.memory[a("wPlayerGenderTag")] = 0
p.register_file.D = 0x12
p.register_file.E = 0x34
p.register_file.HL = 0x5678
call("SelectPlayerGraphics")
assert (p.register_file.D, p.register_file.E) == (0x12, 0x34)
print("PASS: untagged legacy save keeps male graphics")
restore()
p.memory[a("wPlayerGender")] = 0
call("LoadWalkingPlayerSpriteGraphics")
bank, addr = sym["RedSprite"]
assert list(p.memory[0, 0x8000:0x80C0]) == list(p.memory[bank, addr : addr + 192])
print("PASS: boy selection retains original walking graphics")
# Mode-dependent HUD drawing and running use the real ROM routines.
restore()
for mode in (0, 1):
    p.register_file.C = mode
    call("SetGameplayMode")
    assert p.memory[a("wGameplayModeCache")] == mode
    assert p.memory[3, 0xD000] == mode
    p.memory[a("wEXPBarKeepFullFlag")] = 1
    dest = a("wTileMap") + 11 * 20 + 17
    p.memory[dest - 8] = 0x44
    p.memory[dest + 1] = 0x55
    p.register_file.D, p.register_file.E = dest >> 8, dest & 255
    call("PrintEXPBar")
    assert list(p.memory[dest - 7 : dest + 1]) == [0xC0 if mode == 0 else 0xC8] * 8
    assert p.memory[dest - 8] == 0x44 and p.memory[dest + 1] == 0x55
    for held, transport, scripted, jumping in [
        (0, 0, 0, 0),
        (2, 0, 0, 0),
        (2, 2, 0, 0),
        (2, 0, 1, 0),
        (2, 0, 0, 1),
    ]:
        p.memory[a("hJoyHeld")] = held
        p.memory[a("wWalkBikeSurfState")] = transport
        p.memory[a("wd730")] = 0x80 if scripted else 0
        p.memory[a("wd736")] = 0x40 if jumping else 0
        p.memory[a("wNPCMovementScriptPointerTableNum")] = 0
        p.memory[a("wWalkCounter")] = 6
        call("ApplyPlayerSpeedup")
        expected_counter = (
            5
            if mode == 1
            and held == 2
            and transport == 0
            and not scripted
            and not jumping
            else 6
        )
        assert p.memory[a("wWalkCounter")] == expected_counter
    p.memory[a("wWalkBikeSurfState")] = 0
    p.memory[a("wd730")] = 0
    p.memory[a("wd736")] = 0
    p.memory[a("hJoyHeld")] = 2
    p.memory[a("wWalkCounter")] = 1
    call("ApplyPlayerSpeedup")
    assert p.memory[a("wWalkCounter")] == 1, "mid-step B caused counter underflow"
    call("AdvancePlayerSprite")
    assert p.memory[a("wWalkCounter")] == 0
    call("SaveSAVtoSRAM0")
    p.memory[a("wGameplayModeCache")] = 1 - mode
    p.memory[3, 0xD000] = 1 - mode
    call("LoadSAV0")
    assert p.memory[a("wGameplayModeCache")] == mode
print("PASS: new-game modes, HUD visibility, gated running, and mode save/load")

# Compare actual overworld progress with identical input on the bedroom floor.
distances = []
for mode in (0, 1):
    restore()
    p.tick(120, False)
    p.memory[3, 0xD000] = mode
    p.memory[a("wGameplayModeCache")] = mode
    start_x = p.memory[a("wXCoord")]
    p.button_press("right")
    p.button_press("b")
    p.tick(24, False)
    distances.append(p.memory[a("wXCoord")] - start_x)
    p.button_release("right")
    p.button_release("b")
assert distances[1] > distances[0], (
    "running did not increase actual movement",
    distances,
)
print("PASS: held B moves farther in Extended than Classic in actual overworld play")

# The temporary editor generates real Pokemon, leaving ball/story fields alone.
for mode in (0, 1):
    for dex, species in [(1, 0x99), (25, 0x54), (65, 0x95), (151, 0x15)]:
        restore()
        p.memory[a("wCurMap")] = 0x28
        p.memory[a("wEventFlags") + 4] &= ~4  # EVENT_GOT_STARTER
        p.memory[a("wGameplayModeCache")] = mode
        p.memory[a("wPartyCount")] = 0
        p.memory[a("wMonDataLocation")] = 0x10
        p.memory[a("wCurEnemyLVL")] = 5
        p.memory[a("wcf91")] = species
        call("_AddPartyMon")
        moves = list(p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4])
        pp = list(p.memory[a("wPartyMon1PP") : a("wPartyMon1PP") + 4])
        p.memory[a("wPartyCount")] = 0
        p.memory[a("wStarterEditorChoice")] = dex
        p.memory[a("wcf91")] = 0xB1  # Squirtle ball, regardless of replacement.
        p.memory[a("wPlayerStarter")] = 0xB1
        p.memory[a("wRivalStarterTemp")] = 0x99
        call("GiveEditedStarter")
        assert p.memory[a("wPartyCount")] == 1
        assert p.memory[a("wPartyMon1Species")] == species
        assert p.memory[a("wPartySpecies")] == species
        assert p.memory[a("wPartyMon1Level")] == 5
        assert list(p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4]) == moves
        assert list(p.memory[a("wPartyMon1PP") : a("wPartyMon1PP") + 4]) == pp
        assert p.memory[a("wPlayerStarter")] == 0xB1
        assert p.memory[a("wRivalStarterTemp")] == 0x99
        assert p.memory[a("wStarterEditorChoice")] == 0
        assert list(p.memory[a("wPartyMon1OTID") : a("wPartyMon1OTID") + 2]) == list(
            p.memory[a("wPlayerID") : a("wPlayerID") + 2]
        )
# Disabled, out-of-lab, completed, and invalid choices keep the native starter.
for map_id, got, choice in [
    (0x28, False, 0),
    (0, False, 65),
    (0x28, True, 65),
    (0x28, False, 152),
]:
    restore()
    p.memory[a("wCurMap")] = map_id
    p.memory[a("wEventFlags") + 4] = 4 if got else 0
    p.memory[a("wStarterEditorChoice")] = choice
    p.memory[a("wPartyCount")] = 0
    p.memory[a("wMonDataLocation")] = 0x10
    p.memory[a("wCurEnemyLVL")] = 5
    p.memory[a("wcf91")] = 0xB1
    call("GiveEditedStarter")
    assert p.memory[a("wPartyMon1Species")] == 0xB1
# Loading clears the unused choice but preserves an already received replacement.
restore()
p.memory[a("wStarterEditorChoice")] = 65
call("SaveSAVtoSRAM0")
p.memory[a("wStarterEditorChoice")] = 151
call("LoadSAV0")
assert p.memory[a("wStarterEditorChoice")] == 0
p.memory[a("wStarterEditorChoice")] = 65
call("InitFeatureData")
assert p.memory[a("wStarterEditorChoice")] == 0
print(
    "PASS: temporary starter editor generates level-5 Yellow moves/PP in both modes without changing story; load/new-game reset"
)

# Transform must not turn Extended Mew into a captured Ditto. Execute the
# real Transform effect, then the real ball/text/Pokedex/party-or-box paths.
catch_messages = []


def record_catch_message(_):
    if (
        p.register_file.HL == a("ItemUseBallText05")
        and p.memory[a("hLoadedROMBank")] == sym["ItemUseBallText05"][0]
    ):
        catch_messages.append(
            list(p.memory[a("wEnemyMonNick") : a("wEnemyMonNick") + 11])
        )


hook("PrintText", record_catch_message)
for mode, source, transformed, boxed, expected in [
    (1, 0x15, True, False, 0x15),
    (1, 0x15, True, True, 0x15),
    (1, 0x15, False, False, 0x15),
    (0, 0x15, True, False, 0x4C),  # Classic's original assumption remains.
    (1, 0x4C, True, False, 0x4C),  # Ditto still becomes Ditto.
    (1, 0x97, True, False, 0x4C),  # Other Transform/Mirror Move quirks remain.
]:
    restore()
    p.memory[a("wCurMap")] = 0x5E
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[3, 0xD000] = mode
    p.memory[3, 0xD006] = 3
    p.memory[a("wPartyCount")] = 0
    p.memory[a("wIsInBattle")] = 0
    for species in [0x83] + ([0x54] * 5 if boxed else []):
        p.memory[a("wMonDataLocation")] = 0x10
        p.memory[a("wcf91")] = species
        p.memory[a("wCurEnemyLVL")] = 43
        call("_AddPartyMon")
    p.memory[a("wPartyMon1DVs") : a("wPartyMon1DVs") + 2] = [0x12, 0x34]
    p.memory[a("wWhichPokemon")] = 0
    p.memory[a("wPlayerMonNumber")] = 0
    p.memory[a("wBattleMonSpecies2")] = 0x83
    call("LoadBattleMonFromParty")
    p.memory[a("wIsInBattle")] = 1
    p.memory[a("wBattleType")] = 0
    p.memory[a("wEnemyBattleStatus1") : a("wEnemyBattleStatus3") + 1] = [0, 0, 0]
    p.memory[a("wPlayerBattleStatus1") : a("wPlayerBattleStatus3") + 1] = [0, 0, 0]
    p.memory[a("wEnemyMonSpecies2")] = source
    p.memory[a("wcf91")] = source
    p.memory[a("wCurEnemyLVL")] = 30
    call("LoadEnemyMonData")
    original_moves = list(p.memory[a("wEnemyMonMoves") : a("wEnemyMonMoves") + 4])
    original_pp = list(p.memory[a("wEnemyMonPP") : a("wEnemyMonPP") + 4])
    p.memory[a("wEnemyMonDVs") : a("wEnemyMonDVs") + 2] = [0xAB, 0xCD]
    p.memory[a("wEnemyMonHP") : a("wEnemyMonHP") + 2] = [0, 17]
    p.memory[a("wEnemyMonStatus")] = 0x40
    if transformed:
        p.memory[a("wOptions")] |= 0x80
        p.memory[a("hWhoseTurn")] = 1
        p.memory[a("wEnemyMoveNum")] = 144
        p.memory[a("wEnemySelectedMove")] = 144
        p.memory[0xFF40] = 0xE3
        call("TransformEffect_", 2400, "b")
        assert p.memory[a("wEnemyBattleStatus3")] & 8
        assert p.memory[a("wEnemyMonSpecies")] == 0x83
        assert p.memory[a("wEnemyMonSpecies2")] == source
        assert list(
            p.memory[
                a("wTransformedEnemyMonOriginalDVs") : a(
                    "wTransformedEnemyMonOriginalDVs"
                )
                + 2
            ]
        ) == [0xAB, 0xCD]
    p.memory[a("wPokedexOwned") : a("wPokedexOwned") + 19] = [255] * 19
    p.memory[a("wPokedexOwned") + 18] &= ~0x40  # Mew not yet owned.
    p.memory[a("wPokedexOwned") + 16] &= ~8  # Ditto not yet owned.
    p.memory[a("wBoxCount")] = 0
    p.memory[a("wBoxSpecies")] = 255
    p.memory[a("wNumBagItems")] = 1
    p.memory[a("wBagItems") : a("wBagItems") + 3] = [1, 2, 255]
    p.memory[a("wWhichPokemon")] = 0
    p.memory[a("wcf91")] = 1
    p.memory[0xFF40] = 0xE3
    messages_before = len(catch_messages)
    call("ItemUseBall", 2400, "b")
    assert len(catch_messages) == messages_before + 1
    names_bank, names_addr = sym["MonsterNames"]
    default_name = list(
        p.memory[
            names_bank, names_addr + (expected - 1) * 10 : names_addr + expected * 10
        ]
    ) + [0x50]
    assert catch_messages[-1] == default_name, "catch text used the wrong species name"
    prefix = "wBoxMon1" if boxed else "wPartyMon2"
    assert p.memory[a(prefix + "Species")] == expected
    assert p.memory[a(prefix + ("BoxLevel" if boxed else "Level"))] == 30
    assert list(p.memory[a(prefix + "DVs") : a(prefix + "DVs") + 2]) == [0xAB, 0xCD]
    assert list(p.memory[a(prefix + "HP") : a(prefix + "HP") + 2]) == [0, 17]
    assert p.memory[a(prefix + "Status")] == 0x40
    assert p.memory[a("wCapturedMonSpecies")] == expected
    assert bool(p.memory[a("wPokedexOwned") + 18] & 0x40) == (expected == 0x15)
    assert bool(p.memory[a("wPokedexOwned") + 16] & 8) == (expected == 0x4C)
    if expected == 0x15:
        assert (
            list(p.memory[a(prefix + "Moves") : a(prefix + "Moves") + 4])
            == original_moves
        ), (
            mode,
            source,
            transformed,
            boxed,
            original_moves,
            list(p.memory[a(prefix + "Moves") : a(prefix + "Moves") + 4]),
        )
        assert 144 in original_moves
        assert list(p.memory[a(prefix + "PP") : a(prefix + "PP") + 4]) == original_pp
    nick_base = a("wBoxMonNicks") if boxed else a("wPartyMonNicks") + 11
    assert list(p.memory[nick_base : nick_base + 11]) == default_name
    assert p.memory[3, 0xD006] == 3, "capture reset the consumed truck encounter"
    assert p.memory[a("wPartyCount")] == (6 if boxed else 2)
    assert p.memory[a("wBoxCount")] == int(boxed)
print(
    "PASS: native Transform/capture preserves Extended Mew name/species/level/moves/DVs/HP/status/Pokedex in party and box; Classic/Ditto/other quirks unchanged"
)

# Actual Master Ball captures fill the box; only the filling transfer warns.
box_reminders = []
hook("RemindAboutFullBox.warn", lambda _: box_reminders.append(True))
for mode, count in [(0, 19), (1, 18), (1, 19)]:
    restore()
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wCurMap")] = 3
    p.memory[a("wIsInBattle")] = 1
    p.memory[a("wBattleType")] = 0
    p.memory[a("wEnemyMonSpecies2")] = 0x54
    p.memory[a("wCurEnemyLVL")] = 23
    call("LoadEnemyMonData")
    p.memory[a("wPartyCount")] = 6
    p.memory[a("wBoxCount")] = count
    p.memory[a("wBoxSpecies") : a("wBoxSpecies") + count + 1] = [0x24] * count + [255]
    p.memory[a("wPokedexOwned") : a("wPokedexOwned") + 19] = [255] * 19
    p.memory[a("wNumBagItems")] = 1
    p.memory[a("wBagItems") : a("wBagItems") + 3] = [1, 2, 255]
    p.memory[a("wcf91")] = 1  # Master Ball guarantees the capture.
    p.memory[a("wWhichPokemon")] = 0
    p.memory[0xFF40] = 0xE3
    before = len(box_reminders)
    call("ItemUseBall", 1800, "b")
    assert p.memory[a("wBoxCount")] == count + 1
    assert p.memory[a("wPartyCount")] == 6
    assert p.memory[a("wBoxMon1Species")] == 0x54
    assert len(box_reminders) - before == int(mode == 1 and count == 19)
    before = len(box_reminders)
    call("SaveSAVtoSRAM0")
    call("LoadSAV0")
    assert len(box_reminders) == before
print(
    "PASS: native capture transfers warn on filling the box only in Extended; save/load never repeats it"
)

restore()
for roll, species in [(0, 0x62), (1, 0x5A), (2, 0x54), (99, 0x54)]:
    p.memory[a("wCurOpponent")] = 0x54
    p.register_file.A = roll
    call("FossilFishingRoll")
    assert p.memory[a("wCurOpponent")] == species
p.memory[a("wGameplayModeCache")] = 0
p.memory[a("wCurMap")] = 0xE3
p.memory[a("wSpecialSuperRod")] = 1
p.memory[a("wRodResponse")] = 1
p.memory[a("wCurOpponent")] = 0x54
call("TryFossilFishing")
assert p.memory[a("wCurOpponent")] == 0x54
p.register_file.A = 0
call("SurfPikachuRoll")
assert p.memory[a("wEnemyMonSpecies2")] == 0x54
p.memory[a("wIsInBattle")] = 1
call("ApplySurfPikachuMove")
assert p.memory[a("wEnemyMonMoves")] == 57
p.memory[a("wPartyCount")] = 1
p.memory[a("wcf91")] = 0x54
call("PreserveSurfPikachuInParty")
assert p.memory[a("wPartyMon1Moves")] == 57
assert p.memory[a("wPartyMon1PP")] == 15
call("PreserveSurfPikachuInBox")
assert p.memory[a("wBoxMon1Moves")] == 57
assert p.memory[a("wBoxMon1PP")] == 15
print("PASS: rare-roll boundaries, Classic gate, and Surf retained in party/box")

restore()
p.memory[3, 0xD003] = 0
p.memory[a("wNumHoFTeams")] = 2
call("EnsureChampionFeatures")
assert p.memory[3, 0xD004] == 1 and p.memory[3, 0xD005] == 1
p.memory[3, 0xD004] = 0
p.memory[3, 0xD00E] = 0x99
call("RegisterChampionVictory")
call("RegisterChampionVictory")
assert p.memory[3, 0xD004] == 0 and p.memory[3, 0xD00E] == 0x99
assert p.memory[3, 0xD005] == 1
p.memory[3, 0xD00E] = 0
call("RegisterChampionVictory")
assert p.memory[3, 0xD004] == 1
p.memory[a("wGameplayModeCache")] = 1
p.memory[a("wCurrentMapScriptFlags")] = 0x40
p.memory[a("wEventFlags") : a("wEventFlags") + 320] = [255] * 320
call("PrepareAnneVisit")
flags = list(p.memory[a("wEventFlags") : a("wEventFlags") + 320])
assert sum(8 - n.bit_count() for n in flags) == 4
call("ConsumeAnneVisit")
assert p.memory[3, 0xD005] == 0
p.memory[a("wEventFlags") : a("wEventFlags") + 320] = [255] * 320
call("PrepareAnneVisit")
assert list(p.memory[a("wEventFlags") : a("wEventFlags") + 320]) == [255] * 320
print(
    "PASS: champion refresh does not stack, preserves pending reward, and resets only ship exit events"
)

restore()
for roll, species in [(0, 0x99), (1, 0xB0), (2, 0xB1)]:
    p.register_file.A = roll
    call("OakRewardRoll")
    assert p.memory[3, 0xD00E] == species
call("SaveSAVtoSRAM0")
p.memory[3, 0xD00E] = 0
call("LoadSAV0")
assert p.memory[3, 0xD00E] == 0xB1
p.memory[3, 0xD00E] = 0
p.memory[a("wBattleResult")] = 1
call("ResolveOakPostgameBattle")
assert p.memory[3, 0xD00E] == 0
print("PASS: three Oak reward species, pending gift persistence, and no reward on loss")

restore()
p.memory[a("wGameplayModeCache")] = 1
p.memory[3, 0xD006] = 0
p.memory[a("wSpecialSuperRod")] = 1
call("DetermineMewTruckAction")
assert p.memory[3, 0xD006] == 2 and p.memory[a("wPostgameAction")] == 1
call("DetermineMewTruckAction")
assert p.memory[3, 0xD006] == 2 and p.memory[a("wPostgameAction")] == 2
p.memory[a("wSpecialSuperRod")] = 2
p.register_file.A = 1
call("MewTruckRoll")
assert p.memory[3, 0xD006] == 1
p.register_file.A = 0
call("MewTruckRoll")
assert p.memory[3, 0xD006] == 3
call("SetupMewTruckBattle")
assert p.memory[a("wCurEnemyLVL")] == 30
assert p.memory[a("wCurOpponent")] == 0x15
call("DetermineMewTruckAction")
assert p.memory[a("wPostgameAction")] == 0
call("RegisterChampionVictory")
assert p.memory[3, 0xD006] == 3
call("SaveSAVtoSRAM0")
p.memory[3, 0xD006] = 0
call("LoadSAV0")
assert p.memory[3, 0xD006] == 3
print(
    "PASS: first Mew attempt fails, same-side attempts do not roll, and consumed encounter persists"
)

restore()
p.memory[a("wNumBagItems")] = 1
p.memory[a("wBagItems") : a("wBagItems") + 3] = [0x45, 1, 255]
p.memory[a("wPlayerMoney") : a("wPlayerMoney") + 3] = [0x10, 0, 0]
p.memory[a("wPlayerCoins") : a("wPlayerCoins") + 2] = [0, 0]
p.memory[a("wPostgameAction")] = 1
call("BuyExpandedCoins")
assert p.memory[a("wPostgameAction")] == 2
assert list(p.memory[a("wPlayerCoins") : a("wPlayerCoins") + 2]) == [5, 0]
assert list(p.memory[a("wPlayerMoney") : a("wPlayerMoney") + 3]) == [9, 0, 0]
p.memory[a("wPlayerCoins") : a("wPlayerCoins") + 2] = [0x95, 0]
p.memory[a("wPostgameAction")] = 1
call("BuyExpandedCoins")
assert p.memory[a("wPostgameAction")] == 4
assert list(p.memory[a("wPlayerMoney") : a("wPlayerMoney") + 3]) == [9, 0, 0]
p.memory[a("wPlayerCoins") : a("wPlayerCoins") + 2] = [0x99, 0x49]
p.memory[a("wPostgameAction")] = 0
call("BuyExpandedCoins")
assert p.memory[a("wPostgameAction")] == 2
assert list(p.memory[a("wPlayerCoins") : a("wPlayerCoins") + 2]) == [0x99, 0x99]
print("PASS: 500-coin purchase costs 10000, with no overflow or payment on a full case")

# All three regular prize windows use their real menu, level and coin routines.
classic_first = (
    ([0x94, 0x04, 0xA8], [180, 500, 1200], [9, 8, 17])
    if rom == "pokered"
    else ([0x94, 0x04, 0xA7], [120, 750, 1200], [6, 12, 17])
)
second = (
    ([0x58, 0x1A, 0xAA], [2800, 5500, 9999], [18, 25, 26])
    if rom == "pokered"
    else ([0x1D, 0x58, 0xAA], [2500, 4600, 6500], [20, 24, 18])
)


def coin_bytes(value):
    digits = f"{value:04d}"
    return [int(digits[:2], 16), int(digits[2:], 16)]


for mode in (0, 1):
    for window in range(3):
        restore()
        p.memory[a("wGameplayModeCache")] = mode
        p.memory[3, 0xD000] = mode
        p.memory[a("hSpriteIndexOrTextID")] = 3 + window
        call("GetPrizeMenuId")
        if window == 0:
            species, costs, levels = (
                ([0x66, 0x2B, 0x2C], [2500, 4600, 4600], [25, 25, 25])
                if mode else classic_first
            )
        elif window == 1:
            species, costs, levels = second
        else:
            species, costs, levels = [0xDF, 0xD7, 0xFA], [3300, 5500, 7700], None
        assert p.memory[a("wWhichPrizeWindow")] == window
        assert list(p.memory[a("wPrize1"):a("wPrize1") + 3]) == species
        assert list(p.memory[a("wPrize1Price"):a("wPrize1Price") + 6]) == [
            byte for cost in costs for byte in coin_bytes(cost)
        ]
        for index, cost in enumerate(costs):
            p.memory[a("wWhichPrize")] = index
            call("LoadCoinsToSubtract")
            assert list(p.memory[a("hCoins"):a("hCoins") + 2]) == coin_bytes(cost)
            for available in (cost - 1, cost):
                p.memory[a("wPlayerCoins"):a("wPlayerCoins") + 2] = coin_bytes(available)
                call("HasEnoughCoins")
                assert bool(p.register_file.F & 0x10) == (available < cost)
            if levels:
                p.memory[a("wcf91")] = species[index]
                call("GetPrizeMonLevel")
                assert p.memory[a("wCurEnemyLVL")] == levels[index]
print("PASS: regular prize windows, Classic/Extended species, prices, levels and coin checks")

# Finish the optional nickname screen with its normal START shortcut.
prize_naming = []
hook("DisplayNamingScreen", lambda _: prize_naming.append(True))
for index, species in enumerate((0x66, 0x2B, 0x2C)):
    restore()
    prize_naming.clear()
    p.memory[a("wGameplayModeCache")] = 1
    p.memory[3, 0xD000] = 1
    p.memory[a("hSpriteIndexOrTextID")] = 3
    call("GetPrizeMenuId")
    p.memory[a("wCurrentMenuItem")] = index
    p.memory[a("wPlayerCoins"):a("wPlayerCoins") + 2] = [0x99, 0x99]
    p.memory[a("wPartyCount")] = 0
    p.memory[a("wJoyIgnore")] = 0
    call("HandlePrizeChoice", limit=600,
         auto_button=lambda: "start" if prize_naming else "a")
    assert p.memory[a("wPartyCount")] == 1
    assert p.memory[a("wPartyMon1Species")] == species
    assert p.memory[a("wPartyMon1Level")] == 25
    assert list(p.memory[a("wPlayerCoins"):a("wPlayerCoins") + 2]) == coin_bytes(
        9999 - (2500 if index == 0 else 4600)
    )
p.hook_deregister(*sym["DisplayNamingScreen"])
print("PASS: Evoli, Kicklee and Nockchan purchased through the original prize handler")

restore()
p.memory[a("wTutorPartyIndex")] = 0
for index, moves, pp in [
    (1, [1, 3, 4, 0], [0xC5, 0x21, 10, 0]),
    (3, [1, 2, 3, 0], [0xC5, 0x81, 0x21, 0]),
]:
    p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4] = [1, 2, 3, 4]
    p.memory[a("wPartyMon1PP") : a("wPartyMon1PP") + 4] = [0xC5, 0x81, 0x21, 10]
    p.memory[a("wTutorCandidate")] = index
    call("DeleteTutorMove")
    assert list(p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4]) == moves
    assert list(p.memory[a("wPartyMon1PP") : a("wPartyMon1PP") + 4]) == pp
print("PASS: move deletion shifts moves and PP-Up data together, including last slot")

restore()
p.memory[a("wTutorPartyIndex")] = 0
p.memory[a("wPartyMon1")] = 0x55
p.memory[a("wPartyMon1Level")] = 30
p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4] = [0, 0, 0, 0]
call("BuildTutorMoveList")
count = p.memory[a("wTutorMoveCount")]
moves = list(p.memory[a("wTutorMoves") : a("wTutorMoves") + count])
assert 98 in moves, "Raichu cannot recall Pikachu's Quick Attack"
assert 87 not in moves, "level-30 Pokemon offered future Thunder"
assert len(moves) == len(set(moves)) and count <= 64
assert p.memory[a("wTutorMoves") + count] == 255
p.memory[a("wPartyMon1Moves")] = 98
call("BuildTutorMoveList")
count = p.memory[a("wTutorMoveCount")]
assert 98 not in list(p.memory[a("wTutorMoves") : a("wTutorMoves") + count])
p.memory[a("wPartyMon1Level")] = 50
call("BuildTutorMoveList")
count = p.memory[a("wTutorMoveCount")]
assert 87 in list(p.memory[a("wTutorMoves") : a("wTutorMoves") + count])
print(
    "PASS: reminder includes pre-evolution moves, filters known/duplicate/future moves"
)


# Enter the real bow map and speak to each new NPC through the overworld.
# A fresh stack and LCD mode restore leave the subroutine-test trampoline.
def enter_npc_map(
    x, moves, species=0x55, map_id=0x63, width=10, y=6, level=30, setup=None
):
    restore()
    p.tick(120, False)
    p.memory[a("wPartyCount")] = 0
    p.memory[a("wMonDataLocation")] = 0x10  # player party, skip naming prompt
    p.memory[a("wcf91")] = species
    p.memory[a("wCurEnemyLVL")] = level
    call("_AddPartyMon")
    p.memory[a("wPartyMonNicks") : a("wPartyMonNicks") + 11] = [
        0x91,
        0x80,
        0x88,
        0x82,
        0x87,
        0x94,
        0x50,
        0x50,
        0x50,
        0x50,
        0x50,
    ]
    p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4] = moves
    p.memory[a("wPartyMon1PP") : a("wPartyMon1PP") + 4] = [15, 30, 0, 0]
    p.memory[a("wGameplayModeCache")] = 1
    p.memory[3, 0xD000] = 1
    p.memory[a("wNumHoFTeams")] = 1
    p.memory[a("wCurMap")] = map_id
    p.memory[a("wCurMapTileset")] = 0
    if map_id == 0x63:
        # Postgame service tests must not enter an unrelated first-time sailor battle.
        p.memory[a("wEventFlags") + 0x5C0 // 8] |= 0x30
    if map_id == 0x28:
        p.memory[a("wOaksLabCurScript")] = 18
        p.memory[a("wEventFlags") + 4] = 0xFF
    p.memory[a("wYCoord")] = y
    p.memory[a("wXCoord")] = x
    p.memory[a("wYBlockCoord")] = y & 1
    p.memory[a("wXBlockCoord")] = x & 1
    ptr = a("wOverworldMap") + (y // 2 + 1) * (width + 6) + x // 2 + 1
    p.memory[a("wCurrentTileBlockMapViewPointer")] = ptr & 255
    p.memory[a("wCurrentTileBlockMapViewPointer") + 1] = ptr >> 8
    p.memory[0xFF40] = 0xE3
    if setup:
        setup()
    p.register_file.SP = a("wStack")
    entry = a("EnterMap")
    for offset, byte in enumerate([0xFB, 0xC3, entry & 255, entry >> 8]):
        p.memory[0, 0x100 + offset] = byte
    p.register_file.PC = 0x100
    p.tick(120, False)
    p.memory[a("wSpritePlayerStateData1FacingDirection")] = 4  # up


# Execute the full departure animation and automatic exit, rather than only
# the ship-availability helpers. No user save file is needed for these cases.
anne_departures = []
anne_smoke = []
anne_erasures = []
hook("VermilionDockSSAnneLeavesScript", lambda _: anne_departures.append(True))
hook("VermilionDock_EmitSmokePuff", lambda _: anne_smoke.append(True))
hook("VermilionDock_EraseSSAnne", lambda _: anne_erasures.append(True))
for mode, champion, visit in [(0, 0, 0), (1, 0, 0), (1, 1, 1)]:

    def setup_departure():
        p.memory[a("wGameplayModeCache")] = mode
        p.memory[3, 0xD000] = mode
        p.memory[a("wNumHoFTeams")] = champion
        p.memory[3, 0xD003] |= 1
        p.memory[3, 0xD005] = visit
        p.memory[a("wLastMap")] = 5
        flags = a("wEventFlags") + 0x5E0 // 8
        p.memory[flags] = (p.memory[flags] | 3) & ~0x3C

    enter_npc_map(26, [84, 0, 0, 0], map_id=0x5F, width=20, y=2, setup=setup_departure)
    starts, puffs, erasures = len(anne_departures), len(anne_smoke), len(anne_erasures)
    p.button_press("up")
    for _ in range(300):
        p.tick(1, False)
        if p.memory[a("wCurMap")] != 0x5F:
            break
    p.button_release("up")
    assert p.memory[a("wCurMap")] == 0x5E
    for _ in range(4000):
        p.tick(1, False)
        assert len(anne_departures) - starts <= 1, "S.S. Anne departure restarted"
        if (
            p.memory[a("wCurMap")] == 5
            and not p.memory[a("wJoyIgnore")]
            and not p.memory[a("wVermilionCityCurScript")]
            and not p.memory[a("wSimulatedJoypadStatesIndex")]
        ):
            break
    else:
        raise AssertionError(("departure failed to return control", mode, champion))
    p.tick(120, False)
    assert len(anne_departures) - starts == 1
    assert len(anne_smoke) - puffs == 8 and len(anne_erasures) - erasures == 1
    assert p.memory[a("wEventFlags") + 0x5E0 // 8] & 4
    assert p.memory[3, 0xD005] == 0
    before = (p.memory[a("wXCoord")], p.memory[a("wYCoord")])
    p.button("up", 2)
    p.tick(40, False)
    assert p.memory[a("wCurMap")] == 5 and not p.memory[a("wJoyIgnore")]
    assert (p.memory[a("wXCoord")], p.memory[a("wYCoord")]) != before
    assert len(anne_departures) - starts == 1
print(
    "PASS: full S.S. Anne animation runs once with eight puffs and returns control; Classic/Extended first visit and Extended champion revisit"
)


# Route 3 at the reported positions: all trainers are unbeaten and should
# keep their original directions, never turning to engage through scenery.
route3_engagements = []
hook(
    "CheckFightingMapTrainers.trainerEngaging",
    lambda _: route3_engagements.append(
        (p.memory[a("wCurMap")], p.memory[a("wSpriteIndex")])
    ),
)
route3_trainers = {
    2: (10, 6, 12),
    3: (14, 4, 0),
    4: (16, 9, 8),
    5: (19, 5, 0),
    6: (23, 4, 8),
    7: (22, 9, 8),
    8: (24, 6, 12),
    9: (33, 10, 4),
}


def setup_unbeaten_route3(mode):
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[3, 0xD000] = mode
    p.memory[a("wNumHoFTeams")] = 0
    p.memory[a("wRoute3CurScript")] = 0
    p.memory[a("wEventFlags") + 0x3E0 // 8 : a("wEventFlags") + 0x3E0 // 8 + 2] = [0, 0]


for mode in (0, 1):
    for px in (21, 22):
        before = len(route3_engagements)
        enter_npc_map(
            px,
            [84, 0, 0, 0],
            map_id=14,
            width=35,
            y=6,
            setup=lambda mode=mode: setup_unbeaten_route3(mode),
        )
        for _ in range(120):
            p.tick(10, False)
            for obj, (x, y, facing) in route3_trainers.items():
                assert p.memory[a("wSpriteStateData2") + obj * 16 + 4] == y + 4
                assert p.memory[a("wSpriteStateData2") + obj * 16 + 5] == x + 4
                if obj in (5, 6, 7, 8):  # in the visible area of both screenshots
                    assert p.memory[a("wSpriteStateData1") + obj * 16 + 9] == facing, (
                        mode,
                        px,
                        obj,
                    )
            assert p.memory[a("wRoute3CurScript")] == 0
            assert p.memory[a("wIsInBattle")] == 0
        assert len(route3_engagements) == before
        p.tick(1, True)
        p.screen.image.save(
            "/tmp/" + rom + "-route3-fixed-" + str(mode) + "-" + str(px) + ".png"
        )
    # Normal sight engagement and the original walk-up script must still work.
    before = len(route3_engagements)
    enter_npc_map(
        26,
        [84, 0, 0, 0],
        map_id=14,
        width=35,
        y=6,
        setup=lambda mode=mode: setup_unbeaten_route3(mode),
    )
    for _ in range(120):
        p.tick(10, False)
        if p.memory[a("wSpriteStateData2") + 8 * 16 + 5] == 29:
            break
    assert route3_engagements[before:] == [(14, 8)]
    assert p.memory[a("wSpriteStateData2") + 8 * 16 + 4] == 10
    assert p.memory[a("wSpriteStateData2") + 8 * 16 + 5] == 29  # (25,6), next to player
print(
    "PASS: Route 3 unbeaten trainers keep original facings/positions in both modes at both reported positions; normal sight/walk-up still works"
)


# New rumor NPCs load before drawing and preserve all original hide/show IDs.
rumor_talks = []
for talk in ["OakRumorTalk", "MewRumorTalk", "FossilRumorTalk"]:
    hook(talk, lambda _, talk=talk: rumor_talks.append(talk))


def hs_index(map_id, object_id):
    bank, addr = sym["MissableObjects"]
    for index in range(256):
        entry = list(p.memory[bank, addr + index * 3 : addr + index * 3 + 3])
        if entry[:2] == [map_id, object_id]:
            return index
        if entry[0] == 255:
            break
    raise AssertionError((map_id, object_id, "missing hide/show entry"))


def object_hidden(index):
    return bool(p.memory[a("wMissableObjectFlags") + index // 8] & (1 << (index % 8)))


def active_missables():
    values = list(p.memory[a("wMissableObjectList") : a("wMissableObjectList") + 33])
    return dict(zip(values[: values.index(255) : 2], values[1 : values.index(255) : 2]))


rumor_cases = [
    (0, 10, 4, 17, 10, 17, 11, 0x0B, "OakRumorTalk"),
    (0x44, 7, 7, 8, 5, 8, 6, 0x0E, "MewRumorTalk"),
    (8, 10, 3, 8, 13, 8, 12, 0x2F, "FossilRumorTalk"),
]
for map_id, width, obj, x, y, px, py, pic, talk in rumor_cases:
    for mode, champion in [(0, 0), (0, 1), (1, 0), (1, 1)]:

        def setup_rumor():
            p.memory[a("wGameplayModeCache")] = mode
            p.memory[3, 0xD000] = mode
            p.memory[a("wNumHoFTeams")] = champion

        enter_npc_map(
            px, [84, 0, 0, 0], map_id=map_id, width=width, y=py, setup=setup_rumor
        )
        index = hs_index(map_id, obj)
        assert index >= 0xE7, "new NPC shifted an original hide/show ID"
        assert active_missables()[obj] == index
        visible = mode == 1 and (map_id != 0 or champion == 1)
        assert object_hidden(index) != visible
        if not visible:
            assert p.memory[a("wSpriteStateData1") + obj * 16 + 2] == 255
            continue
        assert p.memory[a("wSpriteStateData1") + obj * 16] == pic
        positions = set()
        for _ in range(45):
            p.tick(20, False)
            nx = p.memory[a("wSpriteStateData2") + obj * 16 + 5] - 4
            ny = p.memory[a("wSpriteStateData2") + obj * 16 + 4] - 4
            assert abs(nx - x) <= 1 and ny == y, (talk, nx, ny)
            positions.add((nx, ny))
        assert len(positions) >= 2, talk + " never moved"
        p.tick(1, True)
        p.screen.image.save("/tmp/" + rom + "-" + talk + ".png")
        before = len(rumor_talks)
        p.memory[a("hSpriteIndexOrTextID")] = obj
        call("DisplayTextID", 900, "a")
        assert rumor_talks[before:] == [talk]
        # The next natural reload applies a switch to Classic.
        p.memory[a("wGameplayModeCache")] = 0
        call("LoadMapHeader")
        assert object_hidden(index)
assert hs_index(0, 1) == 0, "original Oak hide/show ID moved"
print(
    "PASS: new rumor NPCs, original hide/show IDs, Classic/champion gates, bounded native walking and real map dialogs"
)

# Four shore-leave sailors share the ship's saved single-visit opportunity.
shore_talks = []
shore_cases = [
    (7, 13, 5, "SurfPikachuRumorTalk"),
    (8, 7, 14, "ShoreSailorFeetTalk"),
    (9, 25, 14, "ShoreSailorSuppliesTalk"),
    (10, 21, 14, "ShoreSailorHarborTalk"),
]
for _, _, _, talk in shore_cases:
    hook(talk, lambda _, talk=talk: shore_talks.append(talk))


def load_shore(mode, champion, visit, initialized=1, px=13, py=6):
    def setup():
        p.memory[a("wGameplayModeCache")] = mode
        p.memory[3, 0xD000] = mode
        p.memory[a("wNumHoFTeams")] = champion
        p.memory[3, 0xD003] = initialized
        p.memory[3, 0xD005] = visit
        p.memory[a("wVermilionCityCurScript")] = 0
        # Start outside the original scripted walk away from a departed ship.
        p.memory[a("wEventFlags") + 0x5E0 // 8] |= 0x0C

    enter_npc_map(px, [84, 0, 0, 0], map_id=5, width=20, y=py, setup=setup)


for mode, champ, visit, initialized, visible in [
    (0, 0, 0, 1, False),
    (0, 1, 1, 1, False),
    (1, 0, 1, 1, False),
    (1, 1, 0, 1, False),
    (1, 1, 1, 1, True),
    (1, 1, 0, 0, True),
]:
    load_shore(mode, champ, visit, initialized)
    assert p.memory[a("wNumSprites")] == 10
    assert len(active_missables()) == 4
    for obj, _, _, _ in shore_cases:
        index = hs_index(5, obj)
        assert active_missables()[obj] == index
        assert object_hidden(index) != visible
        if not visible:
            assert p.memory[a("wSpriteStateData1") + obj * 16 + 2] == 255
    if visible:
        assert p.memory[3, 0xD005] == 1

for obj, x, y, talk in shore_cases:
    load_shore(1, 1, 1, px=x, py=y + (1 if obj != 10 else -1))
    positions = set()
    for _ in range(45):
        p.tick(20, False)
        nx = p.memory[a("wSpriteStateData2") + obj * 16 + 5] - 4
        ny = p.memory[a("wSpriteStateData2") + obj * 16 + 4] - 4
        assert abs(nx - x) <= (0 if obj == 10 else 1) and ny == y
        positions.add((nx, ny))
    assert (len(positions) == 1) if obj == 10 else (len(positions) >= 2)
    p.tick(1, True)
    p.screen.image.save("/tmp/" + rom + "-shore-" + str(obj) + ".png")
    before = len(shore_talks)
    p.memory[a("hSpriteIndexOrTextID")] = obj
    call("DisplayTextID", 900, "a")
    assert shore_talks[before:] == [talk]
    assert p.memory[3, 0xD005] == 1, "a conversation consumed the ship visit"


# The sailor recognizes Surf only on a Pikachu actually in the current team.
def set_reaction_party(members):
    p.memory[a("wPartyCount")] = 0
    p.memory[a("wPartySpecies")] = 255
    p.memory[a("wIsInBattle")] = 0
    for index, (species, moves, fainted) in enumerate(members):
        p.memory[a("wMonDataLocation")] = 0x10
        p.memory[a("wcf91")] = species
        p.memory[a("wCurEnemyLVL")] = 30
        call("_AddPartyMon")
        p.memory[
            a(f"wPartyMon{index + 1}Moves") : a(f"wPartyMon{index + 1}Moves") + 4
        ] = moves
        if fainted:
            p.memory[
                a(f"wPartyMon{index + 1}HP") : a(f"wPartyMon{index + 1}HP") + 2
            ] = [0, 0]
            p.memory[
                a(f"wPartyMon{index + 1}PP") : a(f"wPartyMon{index + 1}PP") + 4
            ] = [0] * 4


surf_reactions = []
hook("SurfPikachuRumorTalk.react", lambda _: surf_reactions.append(True))
normal_pika = (0x54, [84, 0, 0, 0], False)
surf_pika = (0x54, [57, 84, 0, 0], False)
normal_other = (0x55, [84, 0, 0, 0], False)
surf_other = (0x13, [57, 0, 0, 0], False)
for members, expected in [
    ([], False),
    ([normal_pika], False),
    ([surf_other], False),
    ([normal_pika, surf_other], False),
    ([surf_pika], True),
    ([normal_other] * 5 + [(0x54, [84, 0, 0, 57], True)], True),
    ([normal_pika, surf_pika], True),
    ([normal_other], False),
]:
    load_shore(1, 1, 1)
    set_reaction_party(members)
    # A matching boxed Pokemon and stale data after the team end must not count.
    p.memory[a("wBoxCount")] = 1
    p.memory[a("wBoxMon1Species")] = 0x54
    p.memory[a("wBoxMon1Moves")] = 57
    if len(members) < 6:
        p.memory[a(f"wPartyMon{len(members) + 1}Species")] = 0x54
        p.memory[a(f"wPartyMon{len(members) + 1}Moves")] = 57
    team_before = list(p.memory[a("wPartyDataStart") : a("wPartyDataEnd")])
    features_before = list(p.memory[3, 0xD000:0xD200])
    before = len(surf_reactions)
    p.memory[a("hSpriteIndexOrTextID")] = 7
    call("DisplayTextID", 900, "a")
    assert len(surf_reactions) - before == int(expected)
    assert list(p.memory[a("wPartyDataStart") : a("wPartyDataEnd")]) == team_before
    assert list(p.memory[3, 0xD000:0xD200]) == features_before
print(
    "PASS: actual sailor reacts only to a team Pikachu with Surf, including slot six/fourth move/fainted/zero PP; no team/event changes"
)


# The hiker recognizes Mew itself, without any requirement on moves or flags.
mew_reactions = []
hook("MewRumorTalk.react", lambda _: mew_reactions.append(True))
for members, expected in [
    ([], False),
    ([normal_other], False),
    ([(0x25, [33, 0, 0, 0], False)], False),  # Slowpoke is still only a guess.
    ([(0x83, [93, 0, 0, 0], False)], False),  # Mewtwo is a different species.
    ([(0x15, [1, 0, 0, 0], False)], True),
    ([normal_other] * 5 + [(0x15, [1, 0, 0, 0], True)], True),
    ([(0x15, [0, 0, 0, 0], False)], True),
]:
    enter_npc_map(8, [84, 0, 0, 0], map_id=0x44, width=7, y=6)
    set_reaction_party(members)
    p.memory[a("wPokedexOwned") + 18] |= 0x40  # Mew owned, even in negative cases.
    p.memory[a("wBoxCount")] = 1
    p.memory[a("wBoxMon1Species")] = 0x15
    if len(members) < 6:
        p.memory[a(f"wPartyMon{len(members) + 1}Species")] = 0x15
    team_before = list(p.memory[a("wPartyDataStart") : a("wPartyDataEnd")])
    features_before = list(p.memory[3, 0xD000:0xD200])
    before = len(mew_reactions)
    p.memory[a("hSpriteIndexOrTextID")] = 7
    call("DisplayTextID", 900, "a")
    assert len(mew_reactions) - before == int(expected)
    assert list(p.memory[a("wPartyDataStart") : a("wPartyDataEnd")]) == team_before
    assert list(p.memory[3, 0xD000:0xD200]) == features_before
    if expected:
        # The same visit returns to the rumor as soon as Mew leaves the team.
        p.memory[a("wPartyCount")] = 0
        before = len(mew_reactions)
        p.memory[a("hSpriteIndexOrTextID")] = 7
        call("DisplayTextID", 900, "a")
        assert len(mew_reactions) == before
        assert list(p.memory[3, 0xD000:0xD200]) == features_before
print(
    "PASS: actual hiker recognizes team Mew including sixth slot/fainted; ignores other species/box/Pokedex/stale data and returns to rumor after removal"
)


# Enter the actual Route 4 center through its door before the first champion
# victory, including an old hidden flag from an earlier visit/version.
def setup_early_moon():
    p.memory[a("wGameplayModeCache")] = 1
    p.memory[3, 0xD000] = 1
    p.memory[a("wNumHoFTeams")] = 0
    p.memory[a("wRoute4CurScript")] = 0
    p.memory[a("wMissableObjectFlags") + 0xE8 // 8] |= 1 << (0xE8 % 8)


enter_npc_map(11, [84, 0, 0, 0], map_id=15, width=45, y=6, setup=setup_early_moon)
p.button("up", 20)
for _ in range(60):
    p.tick(10, False)
    if p.memory[a("wCurMap")] == 0x44 and p.memory[a("wNumSprites")] == 7:
        break
assert p.memory[a("wCurMap")] == 0x44, "Route 4 door did not enter the Mondberg center"
p.tick(120, False)
assert p.memory[a("wNumHoFTeams")] == 0
assert hs_index(0x44, 7) == 0xE8, "moving the hiker changed its saved flag ID"
assert active_missables()[7] == 0xE8
assert not object_hidden(0xE8)
assert [p.memory[a("wMapSpriteData") + n * 2 + 1] for n in range(6)] == list(
    range(1, 7)
)
before = len(rumor_talks)
p.memory[a("hSpriteIndexOrTextID")] = 7
call("DisplayTextID", 900, "a")
assert rumor_talks[before:] == ["MewRumorTalk"]
call("SaveSAVtoSRAM0")
call("LoadSAV0")
call("LoadMapHeader")
assert p.memory[a("wNumHoFTeams")] == 0 and not object_hidden(0xE8)
enter_npc_map(8, [84, 0, 0, 0], map_id=0x51, width=7, y=6, setup=setup_early_moon)
assert p.memory[a("wNumSprites")] == 4
assert active_missables() == {}, "old Route 10 location retained a duplicate hiker"
print(
    "PASS: actual Route 4 entrance reaches Mew hiker before champion, preserves original center NPCs/save flag/save-load; no Route 10 duplicate"
)


# The two-tile pier must remain passable with either lane occupied by the
# original sailor. Freeze him there in test ROM data; do not remove any NPC.
# This reproduces the bottleneck caused by the former fixed sailor at (22,27).
def walk_to_tile(direction, target_x, target_y):
    p.button_press(direction)
    for _ in range(600):
        p.tick(1, False)
        if (p.memory[a("wXCoord")], p.memory[a("wYCoord")]) == (target_x, target_y):
            p.button_release(direction)
            for _ in range(40):
                p.tick(1, False)
                if not p.memory[a("wWalkCounter")]:
                    break
            assert (p.memory[a("wXCoord")], p.memory[a("wYCoord")]) == (
                target_x,
                target_y,
            )
            return
    p.button_release(direction)
    raise AssertionError(
        (
            "harbor route blocked",
            direction,
            target_x,
            target_y,
            p.memory[a("wXCoord")],
            p.memory[a("wYCoord")],
        )
    )


bank, obj_data = sym["VermilionCity_Object"]
cursor = obj_data + 1
cursor += 1 + p.memory[bank, cursor] * 4  # warps
cursor += 1 + p.memory[bank, cursor] * 3  # signs
original_sailor = cursor + 1 + 5 * 6  # sixth ordinary object, six bytes each
sailor_record = list(p.memory[bank, original_sailor : original_sailor + 6])
try:
    for blocked_y in (26, 27):
        p.memory[bank, original_sailor + 1] = blocked_y + 4
        p.memory[bank, original_sailor + 2] = 22 + 4
        p.memory[bank, original_sailor + 3] = 255  # stay in this lane
        load_shore(1, 1, 1, px=19, py=29)
        assert p.memory[a("wSpriteStateData2") + 6 * 16 + 4] == blocked_y + 4
        assert not object_hidden(
            hs_index(5, 10)
        ), "new standing sailor must remain present"
        walk_to_tile("up", 19, 26)
        if blocked_y == 26:
            walk_to_tile("right", 21, 26)
            p.button("right", 20)
            p.tick(30, False)
            assert (p.memory[a("wXCoord")], p.memory[a("wYCoord")]) == (21, 26)
            walk_to_tile("down", 21, 27)
            walk_to_tile("right", 23, 27)
            walk_to_tile("up", 23, 26)
        walk_to_tile("right", 31, 26)
        walk_to_tile("up", 31, 15)  # city plaza, beyond the narrow pier approach
        walk_to_tile("down", 31, 26)
        if blocked_y == 26:
            walk_to_tile("left", 23, 26)
            walk_to_tile("down", 23, 27)
            walk_to_tile("left", 21, 27)
            walk_to_tile("up", 21, 26)
        walk_to_tile("left", 19, 26)
        walk_to_tile("down", 19, 29)
finally:
    p.memory[bank, original_sailor : original_sailor + 6] = sailor_record
print(
    "PASS: actual harbor/city round trips with all shore sailors and either pier lane deliberately blocked"
)

load_shore(1, 1, 1)
call("SaveSAVtoSRAM0")
call("ConsumeAnneVisit")
call("LoadMapHeader")
assert all(object_hidden(hs_index(5, obj)) for obj, _, _, _ in shore_cases)
call("LoadSAV0")
call("LoadMapHeader")
assert all(not object_hidden(hs_index(5, obj)) for obj, _, _, _ in shore_cases)
call("ConsumeAnneVisit")
call("SaveSAVtoSRAM0")
call("LoadSAV0")
call("LoadMapHeader")
assert all(object_hidden(hs_index(5, obj)) for obj, _, _, _ in shore_cases)
assert p.memory[3, 0xD005] == 0, "reload granted another visit"
call("RegisterChampionVictory")
call("RegisterChampionVictory")
call("LoadMapHeader")
assert p.memory[3, 0xD005] == 1
assert all(not object_hidden(hs_index(5, obj)) for obj, _, _, _ in shore_cases)
p.memory[a("wGameplayModeCache")] = 0
call("LoadMapHeader")
assert all(object_hidden(hs_index(5, obj)) for obj, _, _, _ in shore_cases)
p.memory[a("wGameplayModeCache")] = 1
call("LoadMapHeader")
assert all(not object_hidden(hs_index(5, obj)) for obj, _, _, _ in shore_cases)
assert len(active_missables()) == 4
print(
    "PASS: four shore sailors follow ship availability across departure/next champion/save/load/mode; old champions, patrols and all four dialogs"
)

# Choose each real lab ball with Simsala selected, then let the rival take his.
for x, original, rival in [(6, 0xB0, 0xB1), (7, 0xB1, 0x99), (8, 0x99, 0xB0)]:

    def setup_starter_lab():
        p.memory[a("wPartyCount")] = 0
        p.memory[a("wPartySpecies")] = 255
        p.memory[a("wNumHoFTeams")] = 0
        p.memory[a("wOaksLabCurScript")] = 6
        p.memory[a("wEventFlags") + 4] = 3  # Followed Oak and invited to choose.
        p.memory[a("wMissableObjectFlags") + 5] &= ~0x78  # Three balls + Oak.
        p.memory[a("wStarterEditorChoice")] = 65

    enter_npc_map(x, [0, 0, 0, 0], map_id=0x28, width=5, y=4, setup=setup_starter_lab)
    # Accept the ball; decline only the subsequent optional nickname.
    for _ in range(250):
        p.button("b" if p.memory[a("wPartyCount")] else "a", 2)
        p.tick(20, False)
        if p.memory[a("wEventFlags") + 4] & 4:
            break
    assert p.memory[a("wPartyCount")] == 1, "real ball did not give a starter"
    assert p.memory[a("wPartyMon1Species")] == 0x95
    assert p.memory[a("wPartyMon1Level")] == 5
    assert p.memory[a("wPlayerStarter")] == original
    assert p.memory[a("wRivalStarter")] == rival
    assert p.memory[a("wEventFlags") + 4] & 4
    assert p.memory[a("wStarterEditorChoice")] == 0
    # Save/load keeps the received Simsala, with no persistent editor setting.
    call("SaveSAVtoSRAM0")
    p.memory[a("wStarterEditorChoice")] = 151
    call("LoadSAV0")
    assert p.memory[a("wStarterEditorChoice")] == 0
    assert p.memory[a("wPartyMon1Species")] == 0x95
    assert p.memory[a("wPlayerStarter")] == original
print(
    "PASS: all three actual lab balls give Simsala, preserve original rival/story choices and save the received Pokemon"
)

enter_npc_map(10, [84, 0, 0, 0])
for _ in range(120):
    p.button("a", 2)
    p.tick(20, False)
    if p.memory[a("wPartyMon1Moves") + 1] != 0:
        break
assert p.memory[a("wPartyMon1Moves") + 1] == 45, "NPC reminder failed to teach Growl"
assert p.memory[a("wPartyMon1PP") + 1] == 40
enter_npc_map(8, [57, 84, 0, 0])
for _ in range(120):
    p.button("a", 2)
    p.tick(20, False)
    if p.memory[a("wPartyMon1Moves")] != 57:
        break
assert list(p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4]) == [84, 0, 0, 0]
assert p.memory[a("wPartyMon1PP")] == 30
print("PASS: real bow NPCs open party/attack menus, teach a move and delete an HM")

# Native trade evolutions keep ownership, experience, attacks and nickname.
for source, target in [
    (0x26, 0x95),
    (0x29, 0x7E),
    (0x27, 0x31),
    (0x93, 0x0E),
    (0x54, 0x54),
]:
    restore()
    p.memory[a("wPartyCount")] = 0
    for species in [source, 0x26]:
        p.memory[a("wcf91")] = species
        p.memory[a("wMonDataLocation")] = 0x10
        p.memory[a("wCurEnemyLVL")] = 30
        call("_AddPartyMon")
    nick = [0x93, 0x84, 0x92, 0x93, 0x50] + [0x50] * 6
    p.memory[a("wPartyMonNicks") : a("wPartyMonNicks") + 11] = nick
    mon_before = list(p.memory[a("wPartyMon1") : a("wPartyMon2")])
    other_before = list(p.memory[a("wPartyMon2") : a("wPartyMon3")])
    p.memory[a("wWhichPokemon")] = 0
    p.memory[a("wGameplayModeCache")] = 1
    call("RunLocalTradeEvolution", 1800, "a")
    assert p.memory[a("wPartyMon1")] == target
    assert p.memory[a("wPartySpecies")] == target
    assert p.memory[a("wPartyCount")] == 2
    assert list(p.memory[a("wPartyMon2") : a("wPartyMon3")]) == other_before
    assert list(p.memory[a("wPartyMonNicks") : a("wPartyMonNicks") + 11]) == nick
    # Moves, OT ID, EXP, stat EXP, DVs and PP occupy this unchanged range.
    lo, hi = a("wPartyMon1Moves"), a("wPartyMon1Level")
    assert (
        list(p.memory[lo:hi]) == mon_before[lo - a("wPartyMon1") : hi - a("wPartyMon1")]
    )
    assert p.memory[a("wLinkState")] == 0 and p.memory[a("wForceEvolution")] == 0
    assert p.memory[a("wCanEvolveFlags")] == 0
    p.memory[a("wWhichPokemon")] = 1
    p.memory[a("wGameplayModeCache")] = 0
    call("RunLocalTradeEvolution")
    assert p.memory[a("wPartyMon2")] == 0x26, "Classic allowed a local trade evolution"
print(
    "PASS: all four trade evolutions preserve Pokemon data; non-evolving/Classic cases unchanged"
)

# Real lab scientist dialogue, party choice, evolution and return to map.
trade_done = []
hook("TradeBackTrainerTalk.done", lambda _: trade_done.append(True))
enter_npc_map(8, [93, 0, 0, 0], species=0x26, map_id=0x28, width=5, y=11)
for _ in range(160):
    p.button("a", 2)
    p.tick(20, False)
    if trade_done:
        break
assert trade_done, "trade-back NPC did not return from its dialogue"
assert p.memory[a("wPartyMon1")] == 0x95
assert p.memory[a("wLinkState")] == 0
assert p.memory[a("wGameplayModeCache")] == 1
print("PASS: actual lab NPC selects a Pokemon, evolves it and returns it locally")

# Teach through the original TM/HM item dialogue and party menu.
for mode in [0, 1]:
    for item, move, quantity in [(0xC9, 5, 2), (0xC8, 148, 1)]:
        restore()
        p.memory[a("wPartyCount")] = 0
        p.memory[a("wMonDataLocation")] = 0x10
        p.memory[a("wcf91")] = 0x55
        p.memory[a("wCurEnemyLVL")] = 30
        call("_AddPartyMon")
        p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4] = [84, 0, 0, 0]
        p.memory[a("wGameplayModeCache")] = mode
        p.memory[a("wNumBagItems") : a("wNumBagItems") + 4] = [1, item, quantity, 255]
        p.memory[a("wWhichPokemon")] = 0
        p.memory[a("wcf91")] = item
        call("UseItem_", 1200, "a")
        assert p.memory[a("wPartyMon1Moves") + 1] == move
        expected = quantity - (item == 0xC9 and mode == 0)
        assert p.memory[a("wBagItems") + 1] == expected
        # Refusing the same machine never consumes another item.
        p.memory[a("wcf91")] = item
        call("UseItem_", 600, "b")
        assert p.memory[a("wBagItems") + 1] == expected
        if mode == 1 and item == 0xC9:
            # Forget the taught move, then successfully reuse the same TM.
            p.memory[a("wPartyMon1Moves") + 1] = 0
            p.memory[a("wWhichPokemon")] = 0
            p.memory[a("wcf91")] = item
            call("UseItem_", 1200, "a")
            assert p.memory[a("wPartyMon1Moves") + 1] == move
            assert p.memory[a("wBagItems") + 1] == expected
print("PASS: real TM teaching consumes only in Classic; HMs/cancellation never consume")

# Yellow data is shared by both modes, including generated and level-up moves.
for mode in [0, 1]:
    restore()
    p.memory[a("wPartyCount")] = 0
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wMonDataLocation")] = 0x10
    p.memory[a("wcf91")] = 0x54  # Pikachu
    p.memory[a("wCurEnemyLVL")] = 26
    call("_AddPartyMon")
    assert 85 in list(
        p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4]
    ), "Yellow Pikachu lacks level-26 Thunderbolt"
    p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4] = [84, 0, 0, 0]
    p.memory[a("wWhichPokemon")] = 0
    p.memory[a("wMonDataLocation")] = 0
    p.memory[a("wd11e")] = 0x54
    call("LearnMoveFromLevelUp", 1200, "a")
    assert p.memory[a("wPartyMon1Moves") + 1] == 85
print("PASS: both modes generate and teach Yellow's level-26 Pikachu Thunderbolt")

# Route 7's first exclusive slot can choose either original edition in Extended.
restore()
p.memory[a("wCurMap")] = 18
p.memory[a("wTutorMode")] = 0
p.memory[a("wTutorCandidate")] = 2
own_species = 0xB9 if rom == "pokered" else 0xBC
found = set()
for _ in range(64):
    p.memory[a("wGameplayModeCache")] = 1
    p.memory[a("wcf91")] = own_species
    p.memory[a("wEnemyMonSpecies2")] = own_species
    p.memory[a("wCurEnemyLVL")] = 19
    call("ChooseMergedWildMon")
    found.add(p.memory[a("wcf91")])
    assert p.memory[a("wEnemyMonSpecies2")] == p.memory[a("wcf91")]
    assert p.memory[a("wCurEnemyLVL")] == 19
assert found == {0xB9, 0xBC}, found
for mode, terrain in [(0, 0), (1, 1)]:
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wTutorMode")] = terrain
    p.memory[a("wcf91")] = own_species
    call("ChooseMergedWildMon")
    assert p.memory[a("wcf91")] == own_species
print(
    "PASS: Extended chooses both edition slots; Classic and water slots remain unchanged"
)

# The existing ball glyph is Extended-only and never identifies hidden ghosts.
restore()
p.memory[a("wEnemyMonSpecies2")] = 0x54
p.memory[a("wEnemyMonNick") : a("wEnemyMonNick") + 11] = [
    0x8F,
    0x88,
    0x8A,
    0x80,
    0x50,
] + [0x50] * 6
p.memory[a("wEnemyMonLevel")] = 10
p.memory[a("wEnemyMonStatus")] = 0
for field in ["wEnemyMonHP", "wEnemyMonMaxHP"]:
    p.memory[a(field) : a(field) + 2] = [0, 20]
p.memory[a("wNumBagItems")] = 0
p.memory[a("wBagItems")] = 255
for mode, battle, owned, map_id, expected in [
    (1, 1, 1, 12, 0xE9),
    (1, 1, 0, 12, 0x7F),
    (0, 1, 1, 12, 0x7F),
    (1, 2, 1, 12, 0x7F),
    (1, 1, 1, 0x8E, 0x7F),
    (1, 1, 1, 12, 0xE9),
]:
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wIsInBattle")] = battle
    p.memory[a("wPokedexOwned") + 3] = owned  # dex 25, bit 24
    p.memory[a("wCurMap")] = map_id
    call("DrawEnemyHUDAndHPBar")
    assert p.memory[a("wTileMap") + 21] == expected, (mode, battle, owned, map_id)
print(
    "PASS: actual enemy HUD caught marker is Extended-only, owned-only, wild-only and ghost-safe"
)

# Registration persists in the existing payload, supports replacement/removal,
# and rejects consumables/Classic without mutating the saved selection.
restore()
p.memory[a("wGameplayModeCache")] = 1
for item in [6, 0x4C, 0x4D, 0x4E, 0x47, 0x49, 5]:
    p.memory[a("wcf91")] = item
    call("ToggleRegisteredItem")
    assert p.memory[3, 0xD002] == item
p.memory[a("wcf91")] = 5
call("ToggleRegisteredItem")
assert p.memory[3, 0xD002] == 0
p.memory[a("wcf91")] = 6
call("ToggleRegisteredItem")
p.memory[a("wcf91")] = 20  # Potion cannot be registered
call("ToggleRegisteredItem")
assert p.memory[3, 0xD002] == 6
p.memory[a("wGameplayModeCache")] = 0
p.memory[a("wcf91")] = 0x4E
call("ToggleRegisteredItem")
assert p.memory[3, 0xD002] == 6
call("SaveSAVtoSRAM0")
p.memory[3, 0xD002] = 0
call("LoadSAV0")
assert p.memory[3, 0xD002] == 6

# Register from the real bag, then use SELECT in the overworld twice.
enter_npc_map(8, [84, 0, 0, 0], map_id=12, width=10, y=6)
p.memory[a("wNumBagItems") : a("wNumBagItems") + 4] = [1, 6, 1, 255]
p.memory[a("wCurrentMenuItem")] = 0
p.memory[a("wBagSavedMenuItem")] = 0
p.memory[a("wListScrollOffset")] = 0
p.memory[3, 0xD002] = 0
registered_menus = []
registered_uses = []
hook("RegisteredItemMenu.input", lambda _: registered_menus.append(True))
hook("UseRegisteredItem", lambda _: registered_uses.append(True))


def shortcut_tap(button, frames=20):
    p.button(button, 2)
    p.tick(frames, False)


shortcut_tap("start", 40)
shortcut_tap("down")
shortcut_tap("a")
shortcut_tap("a")
assert registered_menus, "eligible bag item did not offer registration"
shortcut_tap("down")
shortcut_tap("a")
assert p.memory[3, 0xD002] == 6, "bag registration failed"
shortcut_tap("b")
shortcut_tap("b", 60)
for expected_state in [1, 0]:
    before = len(registered_uses)
    shortcut_tap("select")
    for _ in range(20):
        shortcut_tap("a")
        if not p.memory[a("wFontLoaded")] & 1:
            break
    assert len(registered_uses) == before + 1, "SELECT did not activate registered item"
    assert p.memory[a("wWalkBikeSurfState")] == expected_state
    assert p.memory[a("wBagItems") + 1] == 1
p.memory[a("wGameplayModeCache")] = 0
p.memory[3, 0xD000] = 0
before = len(registered_uses)
shortcut_tap("select", 60)
assert len(registered_uses) == before
assert p.memory[a("wWalkBikeSurfState")] == 0
# A missing registered item reports the problem, retaining the registration.
p.memory[a("wGameplayModeCache")] = 1
p.memory[3, 0xD000] = 1
p.memory[a("wNumBagItems") : a("wNumBagItems") + 2] = [0, 255]
shortcut_tap("select")
for _ in range(25):
    shortcut_tap("a")
    if not p.memory[a("wFontLoaded")] & 1:
        break
assert len(registered_uses) == before + 1
assert p.memory[a("wWalkBikeSurfState")] == 0
assert p.memory[3, 0xD002] == 6 and p.memory[a("wNumBagItems")] == 0
# Cycling Road's mandatory-bike flag also applies to the shortcut.
p.memory[a("wNumBagItems") : a("wNumBagItems") + 4] = [1, 6, 1, 255]
p.memory[a("wWalkBikeSurfState")] = 1
p.memory[a("wd732")] |= 1 << 5
shortcut_tap("select")
for _ in range(25):
    shortcut_tap("a")
    if not p.memory[a("wFontLoaded")] & 1:
        break
assert p.memory[a("wWalkBikeSurfState")] == 1
p.memory[a("wd732")] &= ~(1 << 5)
print(
    "PASS: real bag registration, persistent selection, SELECT bike toggle and Classic gate"
)

# The last protection type survives saves; renew exactly that stack/step count.
for item, steps in [(0x1E, 100), (0x38, 200), (0x39, 250)]:
    restore()
    p.memory[a("wGameplayModeCache")] = 1
    p.memory[a("wNumBagItems") : a("wNumBagItems") + 8] = [3, 20, 5, item, 2, 4, 7, 255]
    p.memory[a("wWhichPokemon")] = 1  # item in the second bag slot
    p.memory[a("wcf91")] = item
    call("UseItem_", 1200, "a")
    assert p.memory[a("wRepelRemainingSteps")] == steps
    assert p.memory[3, 0xD00F] == item
    assert p.memory[a("wBagItems") + 3] == 1
    call("SaveSAVtoSRAM0")
    p.memory[3, 0xD00F] = 0
    call("LoadSAV0")
    assert p.memory[3, 0xD00F] == item
    p.memory[a("wRepelRemainingSteps")] = 0
    call("OfferRepeatRepel", 1200, "b")
    assert p.memory[a("wRepelRemainingSteps")] == 0
    assert p.memory[a("wBagItems") + 3] == 1
    p.memory[a("wWhichPokemon")] = 3  # stale unrelated menu index must not be used
    call("RepeatLastRepel", 1200, "a")
    assert p.memory[a("wRepelRemainingSteps")] == steps
    assert p.memory[a("wWhichPokemon")] == 3
    assert list(p.memory[a("wNumBagItems") : a("wNumBagItems") + 6]) == [
        2,
        20,
        5,
        4,
        7,
        255,
    ]
    p.memory[a("wRepelRemainingSteps")] = 0
    call("OfferRepeatRepel")  # no stock, no prompt and no substitution
    assert p.memory[a("wRepelRemainingSteps")] == 0
    p.memory[a("wNumBagItems") : a("wNumBagItems") + 4] = [1, item, 2, 255]
    p.memory[a("wGameplayModeCache")] = 0
    call("OfferRepeatRepel")
    assert p.memory[a("wBagItems") + 1] == 2
    assert p.memory[a("wRepelRemainingSteps")] == 0

# Trigger the real last-step handler, its standard expiry text and Yes prompt.
enter_npc_map(8, [84, 0, 0, 0], map_id=12, width=10, y=6)
p.memory[a("wNumBagItems") : a("wNumBagItems") + 4] = [1, 0x1E, 2, 255]
p.memory[3, 0xD00F] = 0x1E
p.memory[a("wRepelRemainingSteps")] = 1
call("TryDoWildEncounter", 1800, "a")
assert p.memory[a("wRepelRemainingSteps")] == 100
assert p.memory[a("wBagItems") + 1] == 1
assert p.memory[a("wCurOpponent")] == 0
print(
    "PASS: real repel expiry/reuse, all three durations, save/load, No, empty bag and Classic"
)

# Context VM requirements and party scan, including a move on the second mon.
restore()
p.memory[a("wPartyCount")] = 2
p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4] = [84, 0, 0, 0]
p.memory[a("wPartyMon2Moves") : a("wPartyMon2Moves") + 4] = [15, 57, 70, 0]
p.memory[a("wSpritePlayerStateData1FacingDirection")] = 4
p.memory[a("wWalkBikeSurfState")] = 0
for mode, tileset, tile, badges, allowed, action in [
    (1, 0, 0x3D, 2, True, 1),
    (0, 0, 0x3D, 2, False, 1),
    (1, 0, 0x3D, 0, False, 1),
    (1, 7, 0x50, 2, True, 1),
    (1, 0, 0x52, 2, False, 1),
    (1, 0, 0x14, 16, True, 2),
    (1, 0, 0x14, 0, False, 2),
    (1, 0, 0x23, 16, False, 2),
]:
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wCurMapTileset")] = tileset
    p.memory[a("wTileMap") + 7 * 20 + 8] = tile
    p.memory[a("wObtainedBadges")] = badges
    call("CheckContextFieldMove")
    assert bool(p.register_file.F & 0x10) == allowed, (mode, tileset, tile, badges)
    if allowed:
        assert p.memory[a("wPostgameAction")] == action
        assert p.memory[a("wTutorPartyIndex")] == 1
p.memory[a("wPartyMon2Moves") : a("wPartyMon2Moves") + 4] = [84, 0, 0, 0]
p.memory[a("wObtainedBadges")] = 16
p.memory[a("wTileMap") + 7 * 20 + 8] = 0x14
call("CheckContextFieldMove")
assert not p.register_file.F & 0x10, "Surf was offered without a team move"
print("PASS: context VM mode/badge/tile/team requirements and second-party selection")

# Context Cut must not reuse the party-menu fade while accepting the prompt.
context_talks = []
cut_whiteouts = []
hook("ContextFieldMoveDialogue", lambda _: context_talks.append(True))
hook("GBPalWhiteOut", lambda _: cut_whiteouts.append(True))
for prefs, accept in [(0, True), (2, True), (0, False)]:
    enter_npc_map(5, [15, 57, 70, 0], species=0x15, map_id=13, width=10, y=11)
    p.memory[a("wObtainedBadges")] = 2
    p.memory[3, 0xD001] = prefs
    ptr = (
        p.memory[a("wCurrentTileBlockMapViewPointer")]
        + 256 * p.memory[a("wCurrentTileBlockMapViewPointer") + 1]
    )
    cut_block = ptr + 2 * 16 + 2
    before_block = p.memory[cut_block]
    before_talks, before_whiteouts = len(context_talks), len(cut_whiteouts)
    white_frames = []
    p.button("a", 2)
    for frame in range(1600):
        if frame and frame % 20 == 0:
            p.button("a" if accept else "b", 2)
        p.tick(1, True)
        extrema = p.screen.image.crop((0, 0, 160, 96)).getextrema()
        if all(lo >= 248 for lo, hi in extrema[:3]):
            white_frames.append(frame)
        if (
            len(context_talks) > before_talks
            and not p.memory[a("wFontLoaded")] & 1
            and (not accept or p.memory[cut_block] != before_block)
        ):
            break
    else:
        raise AssertionError("context Cut did not close normally")
    assert len(context_talks) == before_talks + 1
    assert (p.memory[cut_block] != before_block) == accept
    assert (
        len(cut_whiteouts) == before_whiteouts
    ), "context Cut flashed the menu whiteout"
    assert not white_frames, (
        "context Cut rendered white world frames",
        prefs,
        white_frames,
    )
    p.tick(80, False)
    assert not p.memory[a("wFontLoaded")] & 1
print(
    "PASS: actual A/Yes Cut with animations on/off and No leaves the world visible, removes only accepted trees and closes normally"
)

# Viridian's hidden Potion is on the cuttable tree at (14,4).
# Take it first, then let the same A interaction reach Cut on later presses.
coords_bank, coords_addr = sym["HiddenItemCoords"]
potion_flag = next(
    index
    for index in range(128)
    if list(
        p.memory[coords_bank, coords_addr + index * 3 : coords_addr + index * 3 + 3]
    )
    == [1, 4, 14]
)
for mode, already_taken in [(0, False), (1, False), (1, True)]:
    enter_npc_map(15, [15, 57, 70, 0], species=0x15, map_id=1, width=20, y=4)
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[3, 0xD000] = mode
    p.memory[a("wObtainedBadges")] = 2
    p.memory[a("wSpritePlayerStateData1FacingDirection")] = 8
    p.memory[a("wNumBagItems")] = 0
    p.memory[a("wBagItems")] = 255
    flag_addr = a("wObtainedHiddenItemsFlags") + potion_flag // 8
    flag_mask = 1 << (potion_flag % 8)
    p.memory[flag_addr] &= ~flag_mask
    if already_taken:
        p.memory[flag_addr] |= flag_mask
    ptr = (
        p.memory[a("wCurrentTileBlockMapViewPointer")]
        + 256 * p.memory[a("wCurrentTileBlockMapViewPointer") + 1]
    )
    tree = ptr + 54
    old_tree = p.memory[tree]
    before_talks = len(context_talks)
    if not already_taken:
        p.button("a", 2)
        for frame in range(1200):
            if frame and frame % 20 == 0:
                p.button("a", 2)
            p.tick(1, False)
            if p.memory[flag_addr] & flag_mask and not p.memory[a("wFontLoaded")] & 1:
                break
        else:
            raise AssertionError("hidden Potion was not collected")
        assert len(context_talks) == before_talks, "Cut stole the uncollected Potion"
        assert p.memory[tree] == old_tree
        assert list(p.memory[a("wBagItems") : a("wBagItems") + 3]) == [0x14, 1, 255]
    p.button("a", 2)
    for frame in range(1200 if mode else 120):
        if frame and frame % 20 == 0:
            p.button("a", 2)
        p.tick(1, False)
        if mode and p.memory[tree] != old_tree and not p.memory[a("wFontLoaded")] & 1:
            break
    assert (p.memory[tree] != old_tree) == bool(mode)
    assert len(context_talks) - before_talks == int(bool(mode))
    assert p.memory[flag_addr] & flag_mask
    assert p.memory[a("wNumBagItems")] == int(
        not already_taken
    ), "spent item was awarded twice"
print(
    "PASS: real Viridian Potion/tree interaction keeps item priority, lets spent items reach Cut in Extended, and preserves Classic"
)

# Actual shore interaction boards Surf in the direction being faced.
enter_npc_map(6, [15, 57, 70, 0], species=0x15, map_id=0, width=10, y=13)
p.memory[a("wSpritePlayerStateData1FacingDirection")] = 0
p.memory[a("wObtainedBadges")] = 16
before_talks = len(context_talks)
shortcut_tap("a")
for _ in range(100):
    shortcut_tap("a")
    if p.memory[a("wWalkBikeSurfState")] == 2 and not p.memory[a("wFontLoaded")] & 1:
        break
p.tick(80, False)
assert len(context_talks) == before_talks + 1
assert p.memory[a("wWalkBikeSurfState")] == 2
assert (p.memory[a("wXCoord")], p.memory[a("wYCoord")]) == (6, 14)

# Existing boulder dialogue now activates Strength, then the original pushing code.
enter_npc_map(18, [15, 57, 70, 0], species=0x15, map_id=0xC0, width=15, y=11)
p.memory[a("wObtainedBadges")] = 8
shortcut_tap("a")
for _ in range(100):
    shortcut_tap("a")
    if p.memory[a("wd728")] & 1 and not p.memory[a("wFontLoaded")] & 1:
        break
assert p.memory[a("wd728")] & 1, "boulder dialogue did not activate Strength"
# Pushing remains the native movement event after activation.
boulder_y = p.memory[a("wSprite01StateData2MapY")]
p.button_press("up")
p.tick(40, False)
p.button_release("up")
p.tick(20, False)
assert (
    p.memory[a("wSprite01StateData2MapY")] < boulder_y
), "activated boulder cannot be pushed"
print(
    "PASS: real A interactions cut a tree, board Surf, activate Strength and push its boulder"
)

# A sign/NPC takes precedence even when its ground tile looks cuttable.
for x, y, map_id, width in [(7, 10, 0, 10), (8, 11, 0x28, 5)]:
    enter_npc_map(x, [15, 57, 70, 0], species=0x15, map_id=map_id, width=width, y=y)
    p.memory[a("wObtainedBadges")] = 0xFF
    p.memory[a("wTileMap") + 7 * 20 + 8] = 0x3D
    before_talks = len(context_talks)
    shortcut_tap("a")
    for _ in range(25):
        shortcut_tap("b")
    assert len(context_talks) == before_talks, "context move stole a normal interaction"
restore()
p.memory[a("wPartyCount")] = 1
p.memory[a("wPartyMon1Moves") : a("wPartyMon1Moves") + 4] = [70, 0, 0, 0]
for mode, badges in [(0, 8), (1, 0)]:
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wObtainedBadges")] = badges
    p.memory[a("wd728")] = 0
    call("TryContextStrength")
    assert not p.memory[a("wd728")] & 1
    assert not p.register_file.F & 0x10
p.memory[a("wGameplayModeCache")] = 1
p.memory[a("wObtainedBadges")] = 8
call("TryContextStrength", 1200, "b")
assert not p.memory[a("wd728")] & 1, "No activated Strength"
print("PASS: signs/NPCs retain A priority; Strength badge/Classic/No checks hold")

# The independent animation setting preserves native Cut effects in both modes.
cut_animations = []
fly_animations = []
hook("AnimCut", lambda _: cut_animations.append(True))
hook("DoFlyAnimation", lambda _: fly_animations.append(True))
for mode, prefs in [(0, 2), (1, 2), (1, 0)]:
    enter_npc_map(5, [15, 57, 70, 0], species=0x15, map_id=13, width=10, y=11)
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[3, 0xD001] = prefs
    p.memory[a("wWhichPokemon")] = 0
    call("_GetTileAndCoordsInFrontOfPlayer")
    call("SaveScreenTilesToBuffer2")
    ptr = (
        p.memory[a("wCurrentTileBlockMapViewPointer")]
        + 256 * p.memory[a("wCurrentTileBlockMapViewPointer") + 1]
    )
    block = ptr + 34
    old = p.memory[block]
    before = len(cut_animations)
    p.memory[0xFF40] = 0xE3
    menu_whiteouts = len(cut_whiteouts)
    call("UsedCut", 1200, "a")
    assert (
        len(cut_whiteouts) == menu_whiteouts + 1
    ), "native party-menu Cut lost its original transition"
    assert p.memory[block] != old
    assert len(cut_animations) - before == (0 if prefs & 2 else 1)
    p.memory[a("wd732")] = 8  # Fly warp; neither Teleport nor dungeon warp.
    p.memory[a("wSpritePlayerStateData1YPixels")] = 60
    p.memory[0xFF40] = 0xE3
    before = len(fly_animations)
    call("_LeaveMapAnim", 1200)
    p.memory[a("wFlags_D733")] |= 0x80
    p.memory[0xFF40] = 0xE3
    call("EnterMapAnim", 1200)
    assert p.memory[a("wSpritePlayerStateData1YPixels")] == 60
    assert not p.memory[a("wFlags_D733")] & 0x80
    assert (len(fly_animations) == before) == bool(prefs & 2)
print(
    "PASS: Cut/Fly cosmetic animation skip works independently of mode and preserves effect/state"
)

# Nurse interaction: identical native healing, short texts and no machine animation.
healing_animations = []
fast_healing_talks = []
hook("AnimateHealingMachine", lambda _: healing_animations.append(True))
hook("TryFastPokemonCenter.enabled", lambda _: fast_healing_talks.append(True))
healing_frames = {}
for mode, prefs, accept in [(0, 1, True), (1, 1, True), (1, 0, True), (1, 1, False)]:
    enter_npc_map(3, [84, 15, 57, 70], species=0x15, map_id=0x3A, width=7, y=3)
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[3, 0xD001] = prefs
    p.memory[a("wLastMap")] = 2
    p.memory[a("wLastBlackoutMap")] = 3
    p.memory[a("wPartyMon1HP") : a("wPartyMon1HP") + 2] = [0, 0]
    p.memory[a("wPartyMon1Status")] = 8
    p.memory[a("wPartyMon1PP") : a("wPartyMon1PP") + 4] = [0x81, 1, 1, 1]
    expected = list(p.memory[a("wPartyMon1") : a("wPartyMon2")])
    if accept:
        hp = a("wPartyMon1HP") - a("wPartyMon1")
        status = a("wPartyMon1Status") - a("wPartyMon1")
        pp = a("wPartyMon1PP") - a("wPartyMon1")
        expected[hp : hp + 2] = list(
            p.memory[a("wPartyMon1MaxHP") : a("wPartyMon1MaxHP") + 2]
        )
        expected[status] = 0
        expected[pp : pp + 4] = [0xAA, 30, 15, 15]
    before_animations = len(healing_animations)
    before_fast = len(fast_healing_talks)
    shortcut_tap("a")
    for frames in range(150):
        shortcut_tap("a" if accept else "b")
        if not p.memory[a("wFontLoaded")] & 1:
            break
    assert frames < 149, "nurse dialogue did not close"
    assert list(p.memory[a("wPartyMon1") : a("wPartyMon2")]) == expected, (
        mode,
        prefs,
        accept,
    )
    assert p.memory[a("wLastBlackoutMap")] == (2 if accept else 3)
    assert len(healing_animations) - before_animations == (
        1 if accept and not prefs else 0
    )
    assert len(fast_healing_talks) - before_fast == (1 if prefs else 0)
    if accept:
        healing_frames[mode, prefs] = frames
assert healing_frames[1, 1] < healing_frames[1, 0]
print(
    "PASS: actual nurse heals HP/status/PP/PP-Ups in both modes; fast/normal/No/blackout checks"
)


# Ship merchant: each exact price, repeat purchases, insufficient money and capacity.
def set_money(value):
    p.memory[a("wPlayerMoney") : a("wPlayerMoney") + 3] = list(
        bytes.fromhex(f"{value:06d}")
    )


def money_value():
    return int(
        "".join(f"{v:02x}" for v in p.memory[a("wPlayerMoney") : a("wPlayerMoney") + 3])
    )


for choice, item, price in [
    (0, 0x4F, 20000),
    (1, 0x51, 3000),
    (2, 0x52, 5000),
    (3, 0x53, 10000),
    (4, 0x0A, 5000),
]:
    restore()
    p.memory[a("wGameplayModeCache")] = 1
    p.memory[a("wNumHoFTeams")] = 1
    p.memory[a("wNumBagItems") : a("wNumBagItems") + 2] = [0, 255]
    p.memory[a("wTutorCandidate")] = choice
    set_money(price - 1)
    call("BuyShipMerchantItem")
    assert p.memory[a("wPostgameAction")] == 2
    assert money_value() == price - 1 and p.memory[a("wNumBagItems")] == 0
    set_money(price)
    call("BuyShipMerchantItem")
    assert p.memory[a("wPostgameAction")] == 1
    assert money_value() == 0
    assert list(p.memory[a("wBagItems") : a("wBagItems") + 2]) == [item, 1]
    set_money(price * 2)
    call("BuyShipMerchantItem")
    call("BuyShipMerchantItem")
    assert p.memory[a("wBagItems") + 1] == 3 and money_value() == 0
restore()
p.memory[a("wGameplayModeCache")] = 1
p.memory[a("wNumHoFTeams")] = 1
p.memory[a("wTutorCandidate")] = 0
p.memory[a("wNumBagItems")] = 30
for slot in range(30):
    p.memory[a("wBagItems") + slot * 2 : a("wBagItems") + slot * 2 + 2] = [slot + 1, 1]
p.memory[a("wBagItems") + 60] = 255
set_money(20000)
call("BuyShipMerchantItem")
assert p.memory[a("wPostgameAction")] == 3 and money_value() == 20000
p.memory[a("wBagItems") : a("wBagItems") + 2] = [0x4F, 99]
call("BuyShipMerchantItem")
assert p.memory[a("wPostgameAction")] == 3 and money_value() == 20000
p.memory[a("wBagItems") + 1] = 98
call("BuyShipMerchantItem")
assert p.memory[a("wBagItems") + 1] == 99 and money_value() == 0
for mode, champion in [(0, 1), (1, 0)]:
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wNumHoFTeams")] = champion
    set_money(20000)
    call("BuyShipMerchantItem")
    assert p.memory[a("wPostgameAction")] == 4 and money_value() == 20000
print(
    "PASS: ship merchant prices, unlimited stock, bag/stack limits and champion/Classic gates"
)

# A real NPC transaction on deck, plus visibility at the natural refresh point.
merchant_menus = []
hook("ShipMerchantTalk.menu", lambda _: merchant_menus.append(True))
enter_npc_map(10, [84, 0, 0, 0], map_id=0x63, width=10, y=11)
p.memory[a("wNumBagItems") : a("wNumBagItems") + 2] = [0, 255]
set_money(20000)
for _ in range(80):
    shortcut_tap("a")
    if p.memory[a("wNumBagItems")] == 1:
        break
assert merchant_menus, "new merchant NPC cannot be reached"
assert list(p.memory[a("wBagItems") : a("wBagItems") + 2]) == [0x4F, 1]
assert money_value() == 0
for _ in range(25):
    shortcut_tap("b")
assert not p.memory[a("wFontLoaded")] & 1
for mode, champion, hidden in [(0, 1, True), (1, 0, True), (1, 1, False)]:
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wNumHoFTeams")] = champion
    p.memory[a("wCurrentMapScriptFlags")] |= 0x40
    call("RefreshMoveTutorObjects")
    assert (
        bool(p.memory[a("wMissableObjectFlags") + 0xE6 // 8] & (1 << (0xE6 % 8)))
        == hidden
    )
print("PASS: real ship merchant confirmation/payment and post-champion visibility")

# Independent arena bits, one-time existing-champion initialization and saves.
gym_cases = [
    (0x36, "wPewterGymCurScript", ["GEODUDE", "ONIX"], [60, 65], [12, 14]),
    (0x41, "wCeruleanGymCurScript", ["STARYU", "STARMIE"], [60, 65], [18, 21]),
    (
        0x5C,
        "wVermilionGymCurScript",
        ["VOLTORB", "PIKACHU", "RAICHU"],
        [60, 62, 65],
        [21, 18, 24],
    ),
    (
        0x86,
        "wCeladonGymCurScript",
        ["VICTREEBEL", "TANGELA", "VILEPLUME"],
        [60, 62, 65],
        [29, 24, 29],
    ),
    (
        0x9D,
        "wFuchsiaGymCurScript",
        ["KOFFING", "MUK", "KOFFING", "WEEZING"],
        [60, 62, 60, 65],
        [37, 39, 37, 43],
    ),
    (
        0xB2,
        "wSaffronGymCurScript",
        ["KADABRA", "MR_MIME", "VENOMOTH", "ALAKAZAM"],
        [60, 62, 62, 65],
        [38, 37, 38, 43],
    ),
    (
        0xA6,
        "wCinnabarGymCurScript",
        ["GROWLITHE", "PONYTA", "RAPIDASH", "ARCANINE"],
        [60, 60, 62, 65],
        [42, 40, 42, 47],
    ),
    (
        0x2D,
        "wViridianGymCurScript",
        ["RHYHORN", "DUGTRIO", "NIDOQUEEN", "NIDOKING", "RHYDON"],
        [60, 61, 62, 63, 65],
        [45, 42, 44, 45, 50],
    ),
]
restore()
p.memory[a("wNumHoFTeams")] = 2
p.memory[a("wObtainedBadges")] = 255
p.memory[a("wGameplayModeCache")] = 1
p.memory[3, 0xD003] = 1  # existing save, older champion-event initialization
p.memory[3, 0xD010] = 0
call("EnsureGymRematches")
assert p.memory[3, 0xD003] == 3 and p.memory[3, 0xD010] == 255
mask = 255
for index, (map_id, script, *_) in enumerate(gym_cases):
    p.memory[a("wCurMap")] = map_id
    call("ConsumeGymRematch")
    assert p.register_file.F & 0x10
    mask &= ~(1 << index)
    assert p.memory[3, 0xD010] == mask
    call("ConsumeGymRematch")
    assert not p.register_file.F & 0x10 and p.memory[3, 0xD010] == mask
call("SaveSAVtoSRAM0")
p.memory[3, 0xD010] = 255
call("LoadSAV0")
call("EnsureGymRematches")
assert p.memory[3, 0xD010] == 0, "load/initialization restored consumed chances"
call("RegisterChampionVictory")
call("RegisterChampionVictory")
assert p.memory[3, 0xD010] == 255
p.memory[a("wCurMap")] = 0x36
for mode, champ, badges in [(0, 2, 255), (1, 0, 255), (1, 2, 0)]:
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[a("wNumHoFTeams")] = champ
    p.memory[a("wObtainedBadges")] = badges
    call("ConsumeGymRematch")
    assert not p.register_file.F & 0x10
    assert p.memory[3, 0xD010] == 255
print(
    "PASS: eight saved arena opportunities, no stacking/reset on load, Classic/champion/badge gates"
)

# Read the real trainer party engine: original species/order/signature moves,
# new levels, and the untouched original trainer instances.
species_ids = {
    m["name"]: m["species"]
    for m in json.loads((root / "tests/fixtures/yellow_learnsets.json").read_text())[
        "pokemon"
    ]
}
party_stride = a("wEnemyMon2") - a("wEnemyMon1")
bank, table = sym["GymRematchData"]
records = [list(p.memory[bank, table + i * 6 : table + i * 6 + 6]) for i in range(8)]
signature_moves = [117, 61, 85, 72, 92, 149, 126, 90]
for index, ((map_id, script, names, levels, old_levels), record) in enumerate(
    zip(gym_cases, records)
):
    assert record[0] == map_id
    assert record[4] + 256 * record[5] == a(script)
    assert record[3] == (5 if index == 7 else 4)
    for number, expected_levels in [
        (record[2], levels),
        (3 if index == 7 else 1, old_levels),
    ]:
        restore()
        p.memory[a("wCurOpponent")] = record[1]
        p.memory[a("wTrainerNo")] = number
        p.memory[a("wGymLeaderNo")] = index + 1
        p.memory[a("wTrainerBaseMoney") : a("wTrainerBaseMoney") + 2] = [0, 0x20]
        call("ReadTrainer", 600)
        assert p.memory[a("wEnemyPartyCount")] == len(names)
        assert list(
            p.memory[a("wEnemyPartySpecies") : a("wEnemyPartySpecies") + len(names)]
        ) == [species_ids[n] for n in names]
        assert [
            p.memory[a("wEnemyMon1Level") + j * party_stride] for j in range(len(names))
        ] == expected_levels
        assert (
            p.memory[a("wEnemyMon1Moves") + (len(names) - 1) * party_stride + 2]
            == signature_moves[index]
        )
    # Every arena uses a separate post-fight script and never writes original flags.
    restore()
    p.memory[a("wCurMap")] = map_id
    p.memory[a("wGameplayModeCache")] = 1
    p.memory[a("wNumHoFTeams")] = 1
    p.memory[a("wObtainedBadges")] = 255
    p.memory[3, 0xD003] = 3
    p.memory[3, 0xD010] = 255
    flags_before = list(p.memory[a("wEventFlags") : a("wEventFlags") + 320])
    call("StartGymRematch")
    assert p.memory[a("wCurOpponent")] == record[1]
    assert p.memory[a("wTrainerNo")] == record[2]
    assert p.memory[a(script)] == record[3]
    assert p.memory[a("wCurMapScript")] == record[3]
    assert p.memory[a("wGymLeaderNo")] == index + 1
    assert p.memory[3, 0xD010] == 255 & ~(1 << index)
    call("FinishGymRematch")
    assert p.memory[a(script)] == 0 and p.memory[a("wCurMapScript")] == 0
    assert p.memory[a("wJoyIgnore")] == 0
    assert p.memory[a("wObtainedBadges")] == 255
    assert list(p.memory[a("wEventFlags") : a("wEventFlags") + 320]) == flags_before
    p.memory[a("wCurOpponent")] = 0
    call("RefreshGymRematches")
    call("TryGymRematchTalk", 1800, "b")
    assert p.memory[3, 0xD010] == 255
    assert p.memory[a("wCurOpponent")] == 0
print(
    "PASS: all eight original/rematch parties, signature moves, No dialogues and safe post-fight scripts"
)

# Source-defined event indices keep native leader/TM flags in sync with tests.
event_ids = {}
event_counter = 0
for raw in (root / "constants/event_constants.asm").read_text().splitlines():
    parts = raw.split(";")[0].split()
    if not parts:
        continue
    op = parts[0]
    if op in ("const_def", "const_next"):
        event_counter = int(parts[1].replace("$", "0x"), 0) if len(parts) > 1 else 0
    elif op == "const_skip":
        event_counter += int(parts[1], 0) if len(parts) > 1 else 1
    elif op == "const":
        event_ids[parts[1]] = event_counter
        event_counter += 1


def set_event(name):
    event = event_ids[name]
    p.memory[a("wEventFlags") + event // 8] |= 1 << (event % 8)


def champion_gym_setup(mode=1):
    p.memory[a("wGameplayModeCache")] = mode
    p.memory[3, 0xD000] = mode
    p.memory[a("wObtainedBadges")] = 255
    p.memory[3, 0xD003] = 3
    p.memory[3, 0xD010] = 255
    for name in [
        "EVENT_BEAT_BROCK",
        "EVENT_GOT_TM34",
        "EVENT_BEAT_VIRIDIAN_GYM_GIOVANNI",
        "EVENT_GOT_TM27",
    ]:
        set_event(name)
    # Giovanni has already made his original story exit.
    p.memory[a("wMissableObjectFlags") + 0x32 // 8] |= 1 << (0x32 % 8)


# NPC No leaves the chance intact; Yes runs a full native Rocko rematch.
gym_starts = []
gym_finishes = []
gym_parties = []
hook("StartGymRematch", lambda _: gym_starts.append(p.memory[a("wCurMap")]))
hook("FinishGymRematch", lambda _: gym_finishes.append(p.memory[a("wCurMap")]))
hook(
    "ReadTrainer.FinishUp",
    lambda _: gym_parties.append(
        (
            p.memory[a("wCurOpponent")],
            p.memory[a("wTrainerNo")],
            [
                p.memory[a("wEnemyMon1Level") + i * party_stride]
                for i in range(p.memory[a("wEnemyPartyCount")])
            ],
        )
    ),
)
enter_npc_map(
    4,
    [57, 0, 0, 0],
    species=0x15,
    map_id=0x36,
    width=5,
    y=2,
    level=100,
    setup=champion_gym_setup,
)
p.memory[a("wNumBagItems") : a("wNumBagItems") + 2] = [0, 255]
flags_before = list(p.memory[a("wEventFlags") : a("wEventFlags") + 320])
before_money = money_value()
shortcut_tap("a")
for _ in range(50):
    shortcut_tap("b")
    if not p.memory[a("wFontLoaded")] & 1:
        break
assert not gym_starts and p.memory[3, 0xD010] == 255
for _ in range(600):
    shortcut_tap("a")
    if (
        gym_finishes
        and p.memory[a("wPewterGymCurScript")] == 0
        and not p.memory[a("wIsInBattle")]
    ):
        break
assert gym_starts == [0x36] and gym_finishes == [0x36], (gym_starts, gym_finishes)
assert (records[0][1], 2, [60, 65]) in gym_parties
assert p.memory[a("wBattleResult")] == 0
assert money_value() > before_money, "rematch did not pay normal trainer winnings"
assert p.memory[3, 0xD010] == 254
assert p.memory[a("wNumBagItems")] == 0, "rematch granted another TM"
assert p.memory[a("wObtainedBadges")] == 255
assert list(p.memory[a("wEventFlags") : a("wEventFlags") + 320]) == flags_before
assert p.memory[a("wJoyIgnore")] == 0
print(
    "PASS: real Rocko No/Yes, full battle victory, separate finish and no duplicate TM/badge events"
)

# Returning Giovanni is visible only in Extended after his original departure.
for mode in [1, 0]:
    enter_npc_map(
        2,
        [57, 0, 0, 0],
        species=0x15,
        map_id=0x2D,
        width=10,
        y=2,
        setup=lambda: champion_gym_setup(mode),
    )
    hidden = bool(p.memory[a("wMissableObjectFlags") + 0x32 // 8] & (1 << (0x32 % 8)))
    assert hidden == (mode == 0)
    if mode == 1:
        before = len(gym_starts)
        shortcut_tap("a")
        for _ in range(60):
            shortcut_tap("b")
            if not p.memory[a("wFontLoaded")] & 1:
                break
        assert len(gym_starts) == before and p.memory[3, 0xD010] == 255
        p.memory[3, 0xD010] = 127  # his opportunity consumed
        for _ in range(35):
            shortcut_tap("a")
        assert not p.memory[a("wMissableObjectFlags") + 0x32 // 8] & (
            1 << (0x32 % 8)
        ), "returned Giovanni ran his old departure again"
        assert len(gym_starts) == before
print(
    "PASS: Giovanni's natural Extended return, Classic hide, No and consumed-chance dialogue"
)

# Fill both inventories beyond their former limits and verify hard boundaries.
restore()
for inventory, capacity, guard in [
    ("wNumBagItems", 30, "wPlayerMoney"),
    ("wNumBoxItems", 70, "wCurrentBoxNum"),
]:
    p.memory[a(inventory)] = 0
    p.memory[a(inventory) + 1] = 0xFF
    unchanged = p.memory[a(guard)]
    for item in range(1, capacity + 1):
        p.memory[a("wcf91")] = item
        p.memory[a("wItemQuantity")] = 1
        p.register_file.HL = a(inventory)
        call("AddItemToInventory_")
        assert p.memory[a(inventory)] == item
    p.memory[a("wcf91")] = 201
    p.register_file.HL = a(inventory)
    call("AddItemToInventory_")
    assert p.memory[a(inventory)] == capacity
    assert p.memory[a(guard)] == unchanged, "full inventory overwrote adjacent state"
call("SaveSAVtoSRAM0")
p.memory[a("wNumBagItems")] = 0
p.memory[a("wNumBoxItems")] = 0
call("LoadSAV0")
assert p.memory[a("wNumBagItems")] == 30 and p.memory[a("wNumBoxItems")] == 70
print("PASS: 30 bag / 70 PC slots, overflow protection, and full inventory save/load")

# Synthetic legacy-format save with old absolute offsets and a valid checksum.
restore()
start, end = a("wMainDataStart"), a("wMainDataEnd")
legacy = bytearray((i * 17 + 3) & 255 for i in range(end - start))
old_bag, old_pc = 0xD31D - start, 0xD53A - start
old_gap = 0xD6B8 - start
for offset, count in [(old_bag, 20), (old_pc, 50)]:
    legacy[offset] = count
    for i in range(count):
        legacy[offset + 1 + i * 2 : offset + 3 + i * 2] = bytes([i + 1, 3])
    legacy[offset + 1 + count * 2] = 0xFF
legacy[a("wInventoryFormat") - start : a("wInventoryFormat") - start + 2] = bytes(2)
bag_end, pc_end = old_bag + 42, old_pc + 102
expected = (
    legacy[:bag_end]
    + bytes(20)
    + legacy[bag_end:pc_end]
    + bytes(40)
    + legacy[pc_end : old_gap - 4]
    + legacy[old_gap + 56 :]
)
expected = bytearray(expected)
expected[a("wInventoryFormat") - start : a("wInventoryFormat") - start + 2] = b"I2"
expected[a("wCurMapTileset") - start] |= 0x80
expected[a("wGameplayModeCache") - start] = 0
p.memory[1, a("sMainData") : a("sMainData") + len(legacy)] = list(legacy)
data = list(p.memory[1, a("sGameData") : a("sGameDataEnd")])
p.memory[1, a("sMainDataCheckSum")] = (~sum(data)) & 255
call("LoadSAV0")
assert list(p.memory[start:end]) == list(
    expected
), "legacy migration changed saved state"
call("SaveSAVtoSRAM0")
p.memory[start:end] = [0] * (end - start)
call("LoadSAV0")
assert list(p.memory[start:end]) == list(expected), "migrated save was migrated twice"
print(
    "PASS: checksum-validated old 20/50 save migrates without losing any other main data"
)

# Import the previous 30/60 layout (I1), including a completely full PC.
restore()
legacy = bytearray((i * 13 + 7) & 255 for i in range(end - start))
old_bag, old_pc = 0xD31D - start, 0xD54E - start
old_gap = 0xD6E0 - start
for offset, count in [(old_bag, 30), (old_pc, 60)]:
    legacy[offset] = count
    for i in range(count):
        legacy[offset + 1 + i * 2 : offset + 3 + i * 2] = bytes([i + 1, 4])
    legacy[offset + 1 + count * 2] = 0xFF
legacy[a("wInventoryFormat") - start : a("wInventoryFormat") - start + 2] = b"I1"
pc_end = old_pc + 122
expected = bytearray(
    legacy[:pc_end] + bytes(20) + legacy[pc_end : old_gap - 4] + legacy[old_gap + 16 :]
)
expected[a("wInventoryFormat") - start : a("wInventoryFormat") - start + 2] = b"I2"
expected[a("wCurMapTileset") - start] |= 0x80
expected[a("wGameplayModeCache") - start] = 0
p.memory[1, a("sMainData") : a("sMainData") + len(legacy)] = list(legacy)
data = list(p.memory[1, a("sGameData") : a("sGameDataEnd")])
p.memory[1, a("sMainDataCheckSum")] = (~sum(data)) & 255
p.memory[3, 0xD000:0xD200] = [0x55] * 512
call("LoadSAV0")
assert list(p.memory[start:end]) == list(expected), "I1 migration changed saved state"
assert list(p.memory[3, 0xD000:0xD200]) == [0] * 512
print("PASS: full 30/60 save migrates with progress intact and safe feature defaults")

# Every reserved byte survives a normal game save and reload.
restore()
payload = [(i * 29 + 5) & 255 for i in range(512)]
payload[0:3] = [1, 3, 6]  # Extended, both preferences, registered bicycle
payload[6] = 2  # Mew hiding at the rear (storage only; feature not active yet)
p.memory[3, 0xD000:0xD200] = payload
call("SaveSAVtoSRAM0")
p.memory[3, 0xD000:0xD200] = [0] * 512
call("LoadSAV0")
assert list(p.memory[3, 0xD000:0xD200]) == payload
assert not p.register_file.F & 0x10
print("PASS: all 512 feature/reserved bytes persist with independent checksum")

# A corrupt or newer extension must not be silently replaced by defaults.
ext_start, ext_end = a("sFeatureSaveStart"), a("sFeatureSaveChecksum") + 1
extension = list(p.memory[1, ext_start:ext_end])
p.memory[1, a("sFeatureSavePayload") + 17] ^= 1
call("LoadSAV0")
assert p.register_file.F & 0x10, "corrupt extension accepted"
p.memory[1, ext_start:ext_end] = extension
p.memory[1, a("sFeatureSaveVersion")] = 2
data = list(p.memory[1, a("sFeatureSaveStart") : a("sFeatureSaveEnd")])
p.memory[1, a("sFeatureSaveChecksum")] = (~sum(data)) & 255
call("LoadSAV0")
assert p.register_file.F & 0x10, "newer feature schema accepted"
p.memory[1, ext_start:ext_end] = extension
p.memory[1, a("sFeatureSaveMagic")] = 0
call("LoadSAV0")
assert p.register_file.F & 0x10, "missing I2 extension accepted"
p.memory[1, ext_start:ext_end] = extension
call("LoadSAV0")
assert not p.register_file.F & 0x10
assert list(p.memory[3, 0xD000:0xD200]) == payload
print(
    "PASS: corrupted, missing and newer feature blocks rejected without erasing stored data"
)

# New Game initialization clears another playthrough's options and event flags.
call("InitFeatureData")
assert list(p.memory[3, 0xD000:0xD200]) == [0] * 512
p.register_file.HL = 0xD006
p.register_file.C = 2
call("SetFeatureByte")
p.register_file.HL = 0xD006
call("GetFeatureByte")
assert p.register_file.C == 2
assert p.memory[0xFF70] & 7 in (0, 1)
print("PASS: New Game resets feature data; bank-safe byte accessors work")

# Exercise the shortcut through the actual Start -> Options flow.
restore()
p.tick(120, False)
opened = []
options = []
hook("ShowPlayerSpriteMenu", lambda _: opened.append(True))
hook("DisplayInGameOptionMenu", lambda _: options.append(True))


def tap(button):
    p.button(button, 2)
    p.tick(16, False)


def hold_select(frames):
    p.button_press("select")
    p.tick(frames, False)


def release_select():
    p.button_release("select")
    p.tick(12, False)


tap("start")
p.tick(45, False)
for _ in range(4):
    tap("down")
tap("a")
assert options, "Start -> Options was not entered"
option_bits = p.memory[a("wOptions")]
font_before = list(p.memory[0, 0x8800:0x9000])


def assert_menu_font():
    assert (
        list(p.memory[0, 0x8800:0x9000]) == font_before
    ), "sprite switch corrupted menu font"


coords = tuple(
    p.memory[a(n)] for n in ("wCurMap", "wXCoord", "wYCoord", "wWalkBikeSurfState")
)
p.memory[3, 0xD001] = 0x80  # unknown future preference bit must survive UI edits
hold_select(100)
assert not opened, "short hold opened shortcut"
release_select()
hold_select(100)
assert not opened, "separate holds accumulated"
release_select()
hold_select(170)
assert not opened, "shortcut opened too early"
p.tick(20, False)
assert len(opened) == 1, "three-second hold did not open menu"
p.tick(200, False)
assert len(opened) == 1, "continued SELECT reopened menu"
assert p.memory[a("wHiddenMenuPage")] == 0, "opening hold also changed page"
release_select()
assert p.memory[a("wCurrentMenuItem")] == 1, "current Green selection not highlighted"
closed = []
hook("ShowPlayerSpriteMenu.done", lambda _: closed.append(True))
tap("left")
assert p.memory[a("wPlayerGender")] == 0, "Left did not immediately apply boy"
assert not closed, "Left closed the hidden menu"
assert_menu_font()
bank, addr = sym["RedSprite"]
assert list(p.memory[0, 0x8000:0x80C0]) == list(p.memory[bank, addr : addr + 192])
tap("a")
assert not closed, "A on gender closed the hidden menu"
tap("right")
assert p.memory[a("wPlayerGender")] == 1, "Right did not immediately apply Green"
assert_menu_font()
bank, addr = sym["GreenSprite"]
assert list(p.memory[0, 0x8000:0x80C0]) == list(p.memory[bank, addr : addr + 192])
assert p.memory[a("wOptions")] == option_bits, "sprite menu changed game options"
assert (
    tuple(
        p.memory[a(n)] for n in ("wCurMap", "wXCoord", "wYCoord", "wWalkBikeSurfState")
    )
    == coords
)
print(
    "PASS: immediate gender changes stay in hidden menu, including A; font/options/location preserved"
)

# Both settings can be changed repeatedly in one visit. A only exits on Back.
tap("down")
tap("left")
assert p.memory[a("wGameplayModeCache")] == 0
assert p.memory[3, 0xD000] == 0
assert not closed
tap("a")
assert not closed, "A on mode closed the hidden menu"
tap("right")
assert p.memory[a("wGameplayModeCache")] == 1
assert p.memory[3, 0xD000] == 1
assert_menu_font()
tap("up")
assert p.memory[a("wSpriteMenuCursorRow")] == 0
tap("left")
tap("right")
tap("down")
tap("down")
tap("down")
assert p.memory[a("wSpriteMenuCursorRow")] == 3
assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0xED, "Back cursor is not visible"
assert p.memory[a("wTileMap") + 8 * 20 + 9] == 0xEC, "Mode retained the solid cursor"
# Back must have its own cursor position for either active mode.
for direction, mode in [("left", 0), ("right", 1)]:
    tap("up")
    tap("up")
    assert p.memory[a("wSpriteMenuCursorRow")] == 1
    tap(direction)
    assert p.memory[a("wGameplayModeCache")] == mode
    mode_x = 1 if mode == 0 else 9
    assert p.memory[a("wTileMap") + 8 * 20 + mode_x] == 0xED
    assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0x7F
    tap("down")
    tap("down")
    assert p.memory[a("wSpriteMenuCursorRow")] == 3
    assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0xED
    assert p.memory[a("wTileMap") + 8 * 20 + mode_x] == 0xEC
    assert p.memory[a("wTileMap") + 3 * 20 + 13] == 0xEC
tap("left")
assert not closed and p.memory[a("wPlayerGender")] == 1
assert p.memory[a("wGameplayModeCache")] == 1


# Page 1 has all three boxes; SELECT switches without committing/exiting.
def assert_page_number(page):
    assert list(
        p.memory[a("wTileMap") + 16 * 20 + 13 : a("wTileMap") + 16 * 20 + 19]
    ) == [
        0x92,
        0xE8,
        0x7F,
        0xF7 + page,
        0xF3,
        0xF8,
    ], "page number is missing or overlaps Back"


assert_page_number(0)
tap("up")
assert p.memory[a("wSpriteMenuCursorRow")] == 2
assert p.memory[a("wTileMap") + 13 * 20 + 4] == 0xED
tap("right")
assert p.memory[3, 0xD001] == 0x82
assert p.memory[a("wTileMap") + 13 * 20 + 13] == 0xED
tap("a")
assert not closed, "A on VM option closed the menu"
tap("select")
assert p.memory[a("wHiddenMenuPage")] == 1
assert p.memory[a("wSpriteMenuCursorRow")] == 0
assert_page_number(1)
assert not closed
# A fresh long hold changes exactly one page, with no auto-repeat.
hold_select(90)
assert p.memory[a("wHiddenMenuPage")] == 0
p.tick(120, False)
assert p.memory[a("wHiddenMenuPage")] == 0
assert len(opened) == 1 and not closed
release_select()
assert_page_number(0)
tap("select")
assert p.memory[a("wHiddenMenuPage")] == 1
assert_page_number(1)
# Healing is the first box; the starter editor occupies the second box.
tap("right")
assert p.memory[3, 0xD001] == 0x83
assert p.memory[a("wTileMap") + 3 * 20 + 13] == 0xED
tap("a")
assert not closed, "A on fast healing closed the menu"
tap("down")
assert p.memory[a("wSpriteMenuCursorRow")] == 1
assert p.memory[a("wTileMap") + 8 * 20 + 4] == 0xED
# Locked outside the lab; A does not exit and Left/Right cannot edit.
choice_before = p.memory[a("wStarterEditorChoice")]
tap("right")
assert p.memory[a("wStarterEditorChoice")] == choice_before
tap("a")
assert not closed
# Exercise the real page-2 controls before the initial lab choice.
old_map = p.memory[a("wCurMap")]
old_events = p.memory[a("wEventFlags") + 4]
p.memory[a("wCurMap")] = 0x28
p.memory[a("wEventFlags") + 4] &= ~4
p.memory[a("wStarterEditorChoice")] = 0
tap("left")
assert p.memory[a("wStarterEditorChoice")] == 151
tap("right")
assert p.memory[a("wStarterEditorChoice")] == 0
tap("right")
assert p.memory[a("wStarterEditorChoice")] == 1
p.memory[a("wStarterEditorChoice")] = 64
tap("right")
assert p.memory[a("wStarterEditorChoice")] == 65
# SIMSALA is visible and the cursor cannot erase a letter in the name.
assert list(p.memory[a("wTileMap") + 8 * 20 + 5 : a("wTileMap") + 8 * 20 + 12]) == [
    0x92,
    0x88,
    0x8C,
    0x92,
    0x80,
    0x8B,
    0x80,
]
assert (
    p.memory[a("wTileMap") + 8 * 20 + 19] == 0x7C
), "editor text overwrote its box border"
p.tick(30, True)
p.screen.image.save("/tmp/" + rom + "-starter-editor.png")
tap("a")
assert not closed
tap("select")
tap("select")
assert p.memory[a("wStarterEditorChoice")] == 65
p.memory[a("wCurMap")] = old_map
p.memory[a("wEventFlags") + 4] = old_events
tap("down")
tap("down")
assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0xED
tap("select")  # can turn pages from Back, too
assert p.memory[a("wHiddenMenuPage")] == 0
assert p.memory[a("wSpriteMenuCursorRow")] == 0
assert_page_number(0)
assert p.memory[a("wPlayerGender")] == 1
tap("down")
tap("left")  # Classic still allows both independent preferences.
assert p.memory[a("wGameplayModeCache")] == 0
tap("down")
tap("left")
assert p.memory[3, 0xD001] == 0x81
tap("right")
assert p.memory[3, 0xD001] == 0x83
tap("select")
tap("left")
assert p.memory[3, 0xD001] == 0x82
tap("right")
assert p.memory[3, 0xD001] == 0x83
assert p.memory[a("wGameplayModeCache")] == 0
tap("down")
tap("down")
assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0xED
tap("a")
assert len(closed) == 1, "A on page-2 Back failed to exit"
assert p.memory[3, 0xD000] == 0 and p.memory[3, 0xD001] == 0x83
assert p.memory[a("wPlayerGender")] == 1
assert_menu_font()
print(
    "PASS: SELECT pages/hold debouncing, counters, cross-page settings and page-2 Back"
)

# B exits like normal options; changes already applied remain active.
hold_select(190)
release_select()
tap("left")
assert p.memory[a("wPlayerGender")] == 0
tap("b")
assert len(closed) == 2 and p.memory[a("wPlayerGender")] == 0
assert_menu_font()
hold_select(190)
release_select()
assert p.memory[a("wCurrentMenuItem")] == 0
tap("right")
tap("start")
assert len(closed) == 3 and p.memory[a("wPlayerGender")] == 1
assert_menu_font()
hold_select(190)
release_select()
assert p.memory[a("wHiddenMenuPage")] == 0
assert p.memory[3, 0xD001] == 0x83
for _ in range(3):
    tap("down")
assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0xED
tap("a")
assert len(closed) == 4, "A on page-1 Back failed to exit"
assert_menu_font()
tap("b")
tap("b")
# Normal saving keeps all settings from both pages, including unknown bits.
call("SaveSAVtoSRAM0")
p.memory[3, 0xD000:0xD002] = [1, 0]
p.memory[a("wPlayerGender")] = 0
call("LoadSAV0")
assert p.memory[a("wPlayerGender")] == 1
assert p.memory[a("wGameplayModeCache")] == 0
assert list(p.memory[3, 0xD000:0xD002]) == [0, 0x83]
print("PASS: B/Start keep applied settings and return through intact normal menus")
# The same options screen in the title menu cannot unlock this shortcut.
restore()
p.memory[a("wOptionsSelectHoldFrames")] = 0
before = len(opened)
# Enter its real entry point, stopping inside its input loop rather than returning.
bank, pc = sym["DisplayOptionMenu"]
p.memory[0x2000] = bank
p.memory[a("hLoadedROMBank")] = bank
p.register_file.PC = pc
p.tick(30, False)
hold_select(220)
assert len(opened) == before, "title-screen options opened in-game shortcut"
release_select()
print("PASS: hidden menu is unavailable in title-screen options")
p.stop(save=False)
