"""Check battle silhouette entry and the handoff to the battle window.

Build first, then run with PyBoy 2.8.1:
    python tests/wild_battle_intro_smoke.py [pokered|pokeblue]
No save files are read or written. The real intro initializes CGB state; the
real battle initializer runs for wild and trainer battles, both player genders,
and several overworld scroll positions. Check window timing as well as scroll:
revealing WY=0 mid-frame duplicates the enemy below the scene in VBA-M 2.2.2.
"""

import io
import sys
from pathlib import Path

from pyboy import PyBoy

ROOT = Path(__file__).resolve().parents[1]


def check(rom, mode):
    symbols = {}
    for line in (ROOT / f"{rom}.sym").read_text().splitlines():
        fields = line.split()
        if len(fields) == 2 and ":" in fields[0]:
            bank, addr = fields[0].split(":")
            symbols[fields[1]] = (int(bank, 16), int(addr, 16))

    def address(name):
        return symbols[name][1]

    p = PyBoy(str(ROOT / f"{rom}.gbc"), window="null", sound_emulated=False)
    p.set_emulation_speed(0)
    seen = set()

    def hook(name, callback):
        p.hook_register(*symbols[name], callback, None)

    def call(name):
        bank, pc = symbols[name]
        # EI; CALL native routine; loop if it returns. EI also handles
        # snapshots taken in VBlank. No game routines are replaced.
        for offset, value in enumerate(
            (0xFB, 0xCD, pc & 255, pc >> 8, 0x18, 0xFE)
        ):
            p.memory[0, 0x100 + offset] = value
        p.memory[0xFF70] = 0
        p.memory[0x2000] = bank
        p.memory[address("hLoadedROMBank")] = bank
        p.register_file.SP = address("wStack")
        p.register_file.PC = 0x100

    hook("ChooseGameplayMode", lambda _: seen.add("mode"))
    hook("OverworldLoop", lambda _: seen.add("world"))
    try:
        for frame in range(250):
            p.button("start" if frame < 20 else "a", 2)
            p.tick(20, False)
            if "mode" in seen:
                break
        assert "mode" in seen, "gameplay menu never reached"
        p.tick(20, False)
        if mode:
            p.button("down", 2)
            p.tick(12, False)
        p.button("a", 2)
        p.tick(20, False)
        for _ in range(300):
            p.button("a", 2)
            p.tick(20, False)
            if "world" in seen:
                break
        assert "world" in seen, "intro never reached the overworld"
        assert p.memory[address("wGameplayModeCache")] == mode
        assert p.memory[3, 0xD000] == mode
        # A real, healthy starter gives the transition a valid party level.
        for name, value in (
            ("wPartyCount", 0), ("wMonDataLocation", 0x10),
            ("wcf91", 0x99), ("wCurEnemyLVL", 5),
        ):
            p.memory[address(name)] = value
        call("_AddPartyMon")
        p.tick(120, False)
        assert p.memory[address("wPartyCount")] == 1
        base = io.BytesIO()
        p.save_state(base)
        active = False
        enabled = []
        slides = []
        finished = []
        window_handoffs = []

        def enable(_):
            if active:
                enabled.append((p.memory[0xFF43], p.memory[0xFF42]))

        def slide(_):
            slides.append((p.register_file.C, p.memory[0xFF42]))

        def delay(_):
            if active and len(slides) == 72 and not finished:
                window_handoffs.append(
                    (p.memory[address("hWY")], p.memory[0xFF4A],
                     p.memory[0xFF44])
                )

        def finish(_):
            finished.append((p.memory[address("hWY")], p.memory[0xFF4A]))

        hook("EnableLCD", enable)
        hook("SlidePlayerAndEnemySilhouettesOnScreen.slideSilhouettesLoop", slide)
        hook("Delay3", delay)
        hook("PrintBeginningBattleText", finish)
        # Rattata, Rhydon, Oddish and Youngster #1. Nonzero/wrapped scroll
        # offsets expose stale overworld coordinates. Test both player pics.
        for opponent, gender in ((s, g) for s in (0xA5, 0x01, 0xB9, 0xC9)
                                 for g in (0, 1)):
            for scroll_x, scroll_y in ((0, 0), (40, 88), (248, 248)):
                base.seek(0)
                p.load_state(base)
                enabled.clear()
                slides.clear()
                finished.clear()
                window_handoffs.clear()
                for name, value, register in (
                    ("hSCX", scroll_x, 0xFF43),
                    ("hSCY", scroll_y, 0xFF42),
                ):
                    p.memory[address(name)] = value
                    p.memory[register] = value
                for name, value in (
                    ("wCurOpponent", opponent),
                    ("wEnemyMonSpecies2", opponent),
                    ("wCurEnemyLVL", 5),
                    ("wTrainerNo", 1),
                    ("wPlayerGenderTag", 0x47),
                    ("wPlayerGender", gender),
                ):
                    p.memory[address(name)] = value
                call("InitBattleCommon")
                # Only inspect EnableLCD once the silhouette setup starts.
                active = False

                def start(_):
                    nonlocal active
                    active = True

                hook("SlidePlayerAndEnemySilhouettesOnScreen", start)
                for _ in range(500):
                    p.tick(1, True)
                    if finished:
                        break
                p.hook_deregister(*symbols["SlidePlayerAndEnemySilhouettesOnScreen"])
                context = (rom, mode, opponent, gender, scroll_x, scroll_y)
                assert finished == [(0, 0)], (
                    "battle window not visible before battle text", context, finished
                )
                assert enabled == [(0x90, 0)], (
                    "stale hardware scroll at LCD enable", context, enabled
                )
                assert slides == [(x, 0) for x in range(0x90, 0, -2)], (
                    "silhouette scroll interrupted", context, slides
                )
                assert len(window_handoffs) == 1, (context, window_handoffs)
                shadow_y, hardware_y, scanline = window_handoffs[0]
                assert (shadow_y, hardware_y) == (0, 144), (
                    "battle window revealed before VBlank", context,
                    window_handoffs
                )
                assert 96 <= scanline < 144, (context, scanline)
                # The empty text box must stay clear at the right, where
                # the duplicated enemy flashed after the silhouettes slid in.
                pixels = p.screen.ndarray
                assert (pixels[104:136, 96:152] == pixels[104, 96]).all(), (
                    "enemy pixels below the battle scene", context
                )
        print(f"PASS: {rom} {'Erweitert' if mode else 'Classic'}: "
              "first-frame scroll, complete slide and VBlank window handoff; "
              "three species and a trainer, both genders, three scroll positions")
    finally:
        p.stop(save=False)


if __name__ == "__main__":
    rom = sys.argv[1] if len(sys.argv) > 1 else "pokered"
    for mode in (0, 1):
        check(rom, mode)
