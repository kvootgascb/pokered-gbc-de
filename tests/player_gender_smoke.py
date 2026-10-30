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
    trampoline = [0xFB, 0xCD, pc & 255, pc >> 8, 0x3E, 0x91, 0xE0, 0x40, 0x18, 0xFE]
    for offset, byte in enumerate(trampoline):
        p.memory[0, 0x100 + offset] = byte
    p.memory[0xFF70] = 0
    if bank:
        p.memory[0x2000] = bank
        p.memory[a("hLoadedROMBank")] = bank
    p.register_file.PC = 0x100
    for frame in range(limit):
        if auto_button and frame % 20 == 0:
            p.button(auto_button, 2)
        p.tick(1, False)
        if p.register_file.PC in (0x108, 0x109):
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

restore()
p.memory[a("wPartyCount")] = 5
p.memory[a("wPlayerCoins") : a("wPlayerCoins") + 2] = [0x25, 0]
p.memory[a("wPostgameAction")] = 0
call("ValidateExtraPrizePurchase")
assert p.memory[a("wPostgameAction")] == 0
p.memory[a("wPostgameAction")] = 1
call("ValidateExtraPrizePurchase")
assert p.memory[a("wPostgameAction")] == 4
p.memory[a("wPartyCount")] = 6
p.memory[a("wPostgameAction")] = 0
call("ValidateExtraPrizePurchase")
assert p.memory[a("wPostgameAction")] == 5
print("PASS: extra prize prices and full-party checks")

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
def enter_npc_map(x, moves, species=0x55, map_id=0x63, width=10, y=6):
    restore()
    p.tick(120, False)
    p.memory[a("wPartyCount")] = 0
    p.memory[a("wMonDataLocation")] = 0x10  # player party, skip naming prompt
    p.memory[a("wcf91")] = species
    p.memory[a("wCurEnemyLVL")] = 30
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
    p.register_file.SP = a("wStack")
    entry = a("EnterMap")
    for offset, byte in enumerate([0xFB, 0xC3, entry & 255, entry >> 8]):
        p.memory[0, 0x100 + offset] = byte
    p.register_file.PC = 0x100
    p.tick(120, False)
    p.memory[a("wSpritePlayerStateData1FacingDirection")] = 4  # up


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
assert p.memory[a("wSpriteMenuCursorRow")] == 2
assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0xED, "Back cursor is not visible"
assert p.memory[a("wTileMap") + 8 * 20 + 9] == 0xEC, "Mode retained the solid cursor"
# Back must have its own cursor position for either active mode.
for direction, mode in [("left", 0), ("right", 1)]:
    tap("up")
    assert p.memory[a("wSpriteMenuCursorRow")] == 1
    tap(direction)
    assert p.memory[a("wGameplayModeCache")] == mode
    mode_x = 1 if mode == 0 else 9
    assert p.memory[a("wTileMap") + 8 * 20 + mode_x] == 0xED
    assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0x7F
    tap("down")
    assert p.memory[a("wSpriteMenuCursorRow")] == 2
    assert p.memory[a("wTileMap") + 16 * 20 + 1] == 0xED
    assert p.memory[a("wTileMap") + 8 * 20 + mode_x] == 0xEC
    assert p.memory[a("wTileMap") + 3 * 20 + 13] == 0xEC
tap("left")
assert not closed and p.memory[a("wPlayerGender")] == 1
assert p.memory[a("wGameplayModeCache")] == 1
tap("a")
assert len(closed) == 1, "A on Back failed to exit"
assert_menu_font()
print("PASS: immediate mode changes, navigation between rows, and A on Back")

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
tap("b")
tap("b")
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
