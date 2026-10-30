"""Headless ROM regression test. Tested with PyBoy 2.8.1.

Build the ROM first; run: python tests/player_gender_smoke.py [pokered|pokeblue]
Tests execute the real intro and ROM graphics/save routines without writing a save file.
"""

from pyboy import PyBoy
from pathlib import Path
import io
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


hook("ChoosePlayerGender", lambda _: seen.append("gender"))
hook("HandleMenuInput", lambda _: seen.append("menu"))
hook("IntroDisplayPicCenteredOrUpperRight", record_pic)
hook("CopyVideoData", record_copy)
hook("LoadWalkingPlayerSpriteGraphics", lambda _: seen.append("walking"))
for i in range(250):
    p.button("start" if i < 20 else "a", 2)
    p.tick(20, False)
    if "gender" in seen:
        break
assert "gender" in seen
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


def call(n, limit=180):
    sentinel = (0, 0x100)
    for offset, byte in enumerate([0x3E, 0x91, 0xE0, 0x40, 0x18, 0xFE]):
        p.memory[0, 0x100 + offset] = byte
    bank, pc = sym[n]
    if bank:
        p.memory[0x2000] = bank
        p.memory[a("hLoadedROMBank")] = bank
    sp = p.register_file.SP - 2
    p.register_file.SP = sp
    p.memory[sp] = sentinel[1] & 255
    p.memory[sp + 1] = sentinel[1] >> 8
    p.register_file.PC = pc
    for _ in range(limit):
        p.tick(1, False)
        if p.register_file.PC in (0x104, 0x105):
            return
    raise AssertionError(n + " did not return")


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
release_select()
assert p.memory[a("wCurrentMenuItem")] == 1, "current Green selection not highlighted"
tap("left")
tap("a")
p.tick(30, False)
assert p.memory[a("wPlayerGender")] == 0, "boy choice not applied"
assert_menu_font()
bank, addr = sym["RedSprite"]
assert list(p.memory[0, 0x8000:0x80C0]) == list(p.memory[bank, addr : addr + 192])
assert p.memory[a("wOptions")] == option_bits, "sprite menu changed game options"
assert (
    tuple(
        p.memory[a(n)] for n in ("wCurMap", "wXCoord", "wYCoord", "wWalkBikeSurfState")
    )
    == coords
)
print(
    "PASS: real Start -> Options, continuous three-second hold, immediate boy graphics; options/location preserved"
)

# Cancellation and a second change work without leaving Options.
hold_select(190)
release_select()
tap("down")
tap("b")
assert p.memory[a("wPlayerGender")] == 0, "B committed a selection"
hold_select(190)
release_select()
tap("down")
tap("a")
assert p.memory[a("wPlayerGender")] == 0, "ZURÜCK changed the selected figure"
hold_select(190)
release_select()
tap("right")
tap("a")
p.tick(30, False)
assert p.memory[a("wPlayerGender")] == 1, "Green choice not applied"
assert_menu_font()
bank, addr = sym["GreenSprite"]
assert list(p.memory[0, 0x8000:0x80C0]) == list(p.memory[bank, addr : addr + 192])
tap("b")
assert_menu_font()
tap("b")
print("PASS: cancellation and repeated switching to Green, with normal return to game")

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
