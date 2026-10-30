"""Check all 151 assembled learnsets against the pinned Yellow reference.

Run after building: python tests/yellow_learnsets_check.py [pokered|pokeblue]
Only the Python standard library is required.
"""

import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
version = sys.argv[1] if len(sys.argv) > 1 else "pokered"
rom = (root / f"{version}.gbc").read_bytes()
reference = json.loads((root / "tests/fixtures/yellow_learnsets.json").read_text())
symbols = {}
for line in (root / f"{version}.sym").read_text().splitlines():
    parts = line.split()
    if len(parts) == 2 and ":" in parts[0]:
        bank, address = parts[0].split(":")
        symbols[parts[1]] = (int(bank, 16), int(address, 16))


def read(bank, address, count):
    offset = address if bank == 0 else bank * 0x4000 + address - 0x4000
    assert 0 <= offset < len(rom) and offset + count <= len(rom)
    return list(rom[offset : offset + count])


assert len(reference["pokemon"]) == 151
assert {entry["dex"] for entry in reference["pokemon"]} == set(range(1, 152))
for entry in reference["pokemon"]:
    name = entry["name"]
    bank, table = symbols["EvosMovesPointerTable"]
    low, high = read(bank, table + (entry["species"] - 1) * 2, 2)
    cursor = low + high * 256
    evolution = []
    while True:
        method = read(bank, cursor, 1)[0]
        cursor += 1
        evolution.append(method)
        if method == 0:
            break
        assert method in (1, 2, 3), name
        count = 3 if method == 2 else 2
        evolution.extend(read(bank, cursor, count))
        cursor += count
    assert evolution == entry["evolution"], f"{name}: changed evolution conditions"
    levels = []
    while True:
        level = read(bank, cursor, 1)[0]
        cursor += 1
        if level == 0:
            break
        move = read(bank, cursor, 1)[0]
        cursor += 1
        assert 1 <= level <= 100 and 1 <= move <= 165, name
        levels.append([level, move])
        assert len(levels) <= 64, f"{name}: unterminated learnset"
    assert levels == entry["level"], f"{name}: incorrect Yellow level-up moves"
    bank, address = (
        symbols["MewBaseStats"] if entry["dex"] == 151 else symbols["BaseStats"]
    )
    if entry["dex"] != 151:
        address += (entry["dex"] - 1) * 28
    header = read(bank, address, 28)
    assert header[15:19] == entry["start"], f"{name}: incorrect Yellow starting moves"
    assert (
        header[20:27] == entry["tmhm"]
    ), f"{name}: incorrect Yellow TM/HM compatibility"
    assert (
        header[:10] + header[19:20] == entry["unchanged_base"]
    ), f"{name}: changed base data"

print(
    f"PASS: {version}: all 151 Yellow start/level/TM-HM sets; evolution and other base data preserved"
)
