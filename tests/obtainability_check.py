"""Verify compiled counterpart slots and the Extended 151-species acquisition graph."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from expanded_wild import map_tables, overrides, wild_tables, generated

version = sys.argv[1] if len(sys.argv) > 1 else "pokeblue"
assert version in ("pokered", "pokeblue")
edition = "red" if version == "pokered" else "blue"
fixture = json.loads((ROOT / "tests/fixtures/yellow_learnsets.json").read_text())[
    "pokemon"
]
ids = {mon["name"]: mon["species"] for mon in fixture}
rom = (ROOT / f"{version}.gbc").read_bytes()
symbols = {}
for line in (ROOT / f"{version}.sym").read_text().splitlines():
    parts = line.split()
    if len(parts) == 2 and ":" in parts[0]:
        bank, address = parts[0].split(":")
        symbols[parts[1]] = int(bank, 16), int(address, 16)


def read(bank, address, size):
    offset = address if bank == 0 else bank * 0x4000 + address - 0x4000
    return list(rom[offset : offset + size])


assert (ROOT / "data/wild/extended_overrides.asm").read_text() == generated()
bank, address = symbols["ExtendedWildOverrides"]
for map_id, terrain, slot, level, species in overrides(edition):
    assert read(bank, address, 5) == [map_id, terrain, slot, level, ids[species]]
    address += 5
assert read(bank, address, 1) == [255]
# Classic's actual compiled map data must still equal its original source.
bank, table = symbols["WildDataPointers"]
for index, name in enumerate(map_tables()):
    low, high = read(bank, table + index * 2, 2)
    cursor = low + 256 * high
    rates, rows = wild_tables(edition)[name]
    for terrain in (0, 1):
        assert read(bank, cursor, 1) == [rates[terrain]], (name, terrain)
        cursor += 1
        for level, species in rows[terrain]:
            assert read(bank, cursor, 2) == [level, ids[species]], (name, terrain)
            cursor += 2

available = set()
for edition in ("red", "blue"):
    for rates, rows in wild_tables(edition).values():
        available.update(ids[species] for terrain in rows for _, species in terrain)
for filename in ("super_rod.asm", "good_rod.asm"):
    text = (ROOT / "data/wild" / filename).read_text()
    available.update(
        ids[species] for species in re.findall(r"\bdb\s+\d+,\s+(\w+)", text)
    )
# Stationary encounters actually declared as species/level objects, not zoo displays.
for path in (ROOT / "data/maps/objects").glob("*.asm"):
    for species in re.findall(
        r"^\s*object_event[^\n]*,\s+(\w+),\s+\d+\s*$", path.read_text(), re.M
    ):
        if species in ids:
            available.add(ids[species])
# Renewable alternatives mean choosing one starter, Eevee evolution, dojo gift
# or fossil no longer prevents completing the other evolutionary branches.
special_sources = {
    "engine/events/oak_battle.asm": ["BULBASAUR", "CHARMANDER", "SQUIRTLE"],
    "engine/events/extra_prizes.asm": ["EEVEE", "HITMONLEE", "HITMONCHAN"],
    "engine/events/rare_encounters.asm": ["OMANYTE", "KABUTO"],
    "engine/events/mew_truck.asm": ["MEW"],
    "scripts/SilphCo7F.asm": ["LAPRAS"],
    "scripts/Route12.asm": ["SNORLAX"],
    "engine/events/cinnabar_lab.asm": ["AERODACTYL"],
    "data/events/prizes.asm": ["PORYGON"],
}
for filename, species_names in special_sources.items():
    text = (ROOT / filename).read_text()
    for name in species_names:
        assert re.search(r"\b" + name + r"\b", text), (filename, name)
        available.add(ids[name])
# Old Amber is available independently of the Mt Moon fossil choice.
museum = (ROOT / "scripts/Museum1F.asm").read_text()
assert "OLD_AMBER" in museum
trades = re.findall(
    r"^\s*db (\w+),\s+(\w+),\s+TRADE_",
    (ROOT / "data/events/trades.asm").read_text(),
    re.M,
)
trades.pop(2)  # unused Butterfree/Beedrill trade
changed = True
while changed:
    before = available.copy()
    for mon in fixture:
        if mon["species"] not in available:
            continue
        entry = iter(mon["evolution"])
        for method in entry:
            if not method:
                break
            next(entry)  # level or evolution stone (all standard stones available)
            if method == 2:
                next(entry)  # minimum level
            available.add(next(entry))
    for give, receive in trades:
        if ids[give] in available:
            available.add(ids[receive])
    changed = before != available
missing = [mon["name"] for mon in fixture if mon["species"] not in available]
assert not missing, f"Unobtainable species: {missing}"
print(
    f"PASS: {version}: counterpart slots match; Classic tables unchanged; all 151 species have acquisition paths"
)
