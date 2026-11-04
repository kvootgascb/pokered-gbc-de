"""Check the first wild-battle silhouette frame in both gameplay modes.

Build first, then run with PyBoy 2.8.1:
    python tests/wild_battle_intro_smoke.py [pokered|pokeblue]
No save files are read or written. The real intro initializes CGB state; the
real battle initializer runs from several overworld scroll positions.
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
        base = io.BytesIO()
        p.save_state(base)
        active = False
        enabled = []
        slides = []
        finished = []

        def enable(_):
            if active:
                enabled.append((p.memory[0xFF43], p.memory[0xFF42]))

        def slide(_):
            slides.append((p.register_file.C, p.memory[0xFF42]))

        hook("EnableLCD", enable)
        hook("SlidePlayerAndEnemySilhouettesOnScreen.slideSilhouettesLoop", slide)
        hook("PrintBeginningBattleText", lambda _: finished.append(True))
        # Rattata (small) and Rhydon (large); nonzero/wrapped scroll offsets
        # expose stale overworld coordinates, unlike testing only at (0, 0).
        for species in (0xA5, 0x01):
            for scroll_x, scroll_y in ((0, 0), (40, 88), (248, 248)):
                base.seek(0)
                p.load_state(base)
                enabled.clear()
                slides.clear()
                finished.clear()
                for name, value, register in (
                    ("hSCX", scroll_x, 0xFF43),
                    ("hSCY", scroll_y, 0xFF42),
                ):
                    p.memory[address(name)] = value
                    p.memory[register] = value
                for name, value in (
                    ("wCurOpponent", species),
                    ("wEnemyMonSpecies2", species),
                    ("wCurEnemyLVL", 5),
                ):
                    p.memory[address(name)] = value
                bank, pc = symbols["InitBattleCommon"]
                # EI; CALL real initializer; loop if it returns. No ROM game
                # routines are replaced. EI also handles snapshots in VBlank.
                for offset, value in enumerate(
                    (0xFB, 0xCD, pc & 255, pc >> 8, 0x18, 0xFE)
                ):
                    p.memory[0, 0x100 + offset] = value
                p.memory[0xFF70] = 0
                p.memory[0x2000] = bank
                p.memory[address("hLoadedROMBank")] = bank
                p.register_file.PC = 0x100
                # Only inspect EnableLCD once the silhouette setup starts.
                active = False

                def start(_):
                    nonlocal active
                    active = True

                hook("SlidePlayerAndEnemySilhouettesOnScreen", start)
                for _ in range(500):
                    p.tick(1, False)
                    if finished:
                        break
                p.hook_deregister(*symbols["SlidePlayerAndEnemySilhouettesOnScreen"])
                context = (rom, mode, species, scroll_x, scroll_y)
                assert finished, ("battle intro did not finish", context)
                assert enabled == [(0x90, 0)], (
                    "stale hardware scroll at LCD enable", context, enabled
                )
                assert slides == [(x, 0) for x in range(0x90, 0, -2)], (
                    "silhouette scroll interrupted", context, slides
                )
        print(f"PASS: {rom} {'Erweitert' if mode else 'Classic'}: "
              "first-frame scroll and complete silhouette animation; "
              "two species, three map scroll positions")
    finally:
        p.stop(save=False)


if __name__ == "__main__":
    rom = sys.argv[1] if len(sys.argv) > 1 else "pokered"
    for mode in (0, 1):
        check(rom, mode)
