"""Reproduce a complete S.S. Anne departure using an external in-game save.

Run: python tests/ss_anne_departure_smoke.py pokeblue /path/to/pokeblue.sav
The save must be on 1F near the gangway (x=26/27, y=0..3), with Cut obtained.
PyBoy 2.8.1; the supplied save is read into memory and never overwritten.
"""

import argparse
import hashlib
import io
from collections import Counter
from pathlib import Path

from pyboy import PyBoy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", choices=("pokered", "pokeblue"))
    parser.add_argument("save", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    rom = root / (args.rom + ".gbc")
    symbols = {}
    for line in rom.with_suffix(".sym").read_text().splitlines():
        parts = line.split()
        if len(parts) == 2 and ":" in parts[0]:
            bank, addr = parts[0].split(":")
            symbols[parts[1]] = (int(bank, 16), int(addr, 16))

    def address(name):
        return symbols[name][1]

    data = args.save.read_bytes()
    original_hash = hashlib.sha256(data).digest()
    assert len(data) == 32768, "expected a 32 KiB cartridge save"
    emulator = PyBoy(
        str(rom), window="null", sound_emulated=False, ram_file=io.BytesIO(data)
    )
    emulator.set_emulation_speed(0)
    counts = Counter()

    def read(name):
        return emulator.memory[address(name)]

    def world(_):
        counts[("world", read("wCurMap"))] += 1

    emulator.hook_register(*symbols["OverworldLoop"], world, None)
    for key, label in [
        ("departures", "VermilionDockSSAnneLeavesScript"),
        ("puffs", "VermilionDock_EmitSmokePuff"),
        ("erasures", "VermilionDock_EraseSSAnne"),
    ]:
        emulator.hook_register(
            *symbols[label], lambda _, key=key: counts.update([key]), None
        )
    try:
        # Continue through the actual title and save-validation menus.
        for frame in range(250):
            emulator.button("start" if frame < 20 else "a", 2)
            emulator.tick(20, False)
            if counts[("world", 0x5F)]:
                break
        assert counts[("world", 0x5F)], "Continue did not reach S.S. Anne 1F"
        assert read("wXCoord") in (26, 27) and read("wYCoord") <= 3
        assert emulator.memory[address("wEventFlags") + 0x5E0 // 8] & 1
        emulator.tick(10, False)
        emulator.button_press("up")
        for _ in range(300):
            emulator.tick(1, False)
            if read("wCurMap") != 0x5F:
                break
        emulator.button_release("up")
        assert read("wCurMap") == 0x5E, "leaving the gangway did not enter the dock"

        for _ in range(4000):
            emulator.tick(1, False)
            assert counts["departures"] <= 1, "departure animation restarted"
            if (
                read("wCurMap") == 5
                and counts[("world", 5)] > 5
                and not read("wJoyIgnore")
                and not read("wVermilionCityCurScript")
                and not read("wSimulatedJoypadStatesIndex")
            ):
                break
        else:
            raise AssertionError("departure did not return control in Vermilion City")

        emulator.tick(120, False)
        assert counts["departures"] == 1
        assert counts["puffs"] == 8 and counts["erasures"] == 1
        assert emulator.memory[address("wEventFlags") + 0x5E0 // 8] & 4
        assert emulator.memory[3, 0xD005] == 0
        old_position = (read("wXCoord"), read("wYCoord"))
        emulator.button("up", 2)
        emulator.tick(40, False)
        assert read("wCurMap") == 5 and not read("wJoyIgnore")
        assert (read("wXCoord"), read("wYCoord")) != old_position
        assert counts["departures"] == 1
        print(
            "PASS: supplied save continues normally; one complete departure, "
            "eight smoke puffs, automatic dock exit and working player control"
        )
    finally:
        emulator.stop(save=False)
        assert hashlib.sha256(args.save.read_bytes()).digest() == original_hash


if __name__ == "__main__":
    main()
