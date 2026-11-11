"""Load a codec-edited real save in both ROMs and compare native RAM/stats.

First run DX_TEST_SAVE=/path/to/a/valid.sav node tests/save_editor_test.cjs.
Then run this script using PyBoy 2.8.1. No input save is overwritten.
"""
from pathlib import Path
import json
import re
import sys
from pyboy import PyBoy

ROOT = Path(__file__).resolve().parents[1]
SAVE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/dx-editor-tests/real-edited.sav')
source = SAVE.read_bytes()
data = json.loads(re.search(r'globalThis.DX_DATA = (.*);\n', (ROOT / 'tools/save-editor/Pokemon-DX-Saveeditor.html').read_text())[1])
layout = data['layout']

for rom in ('pokered', 'pokeblue'):
    symbols = {}
    for line in (ROOT / f'{rom}.sym').read_text().splitlines():
        fields = line.split()
        if len(fields) == 2 and ':' in fields[0]:
            bank, addr = fields[0].split(':')
            symbols[fields[1]] = (int(bank, 16), int(addr, 16))
    def address(name):
        return symbols[name][1]
    with SAVE.open('rb') as ram:
        p = PyBoy(str(ROOT / f'{rom}.gbc'), window='null', sound_emulated=False, ram_file=ram)
    p.set_emulation_speed(0)
    seen = []
    p.hook_register(*symbols['OverworldLoop'], lambda _: seen.append(True), None)
    try:
        for frame in range(500):
            p.button('start' if frame < 20 else 'a', 2)
            p.tick(20, False)
            if seen:
                break
        assert seen, 'ROM did not load the edited save into the overworld'
        while p.memory[0xFF70] & 7 not in (0, 1):
            p.tick(1, False)
        size = address('wPartyDataEnd') - address('wPartyDataStart')
        assert bytes(p.memory[address('wPartyDataStart'):address('wPartyDataEnd')]) == source[layout['party']:layout['party'] + size]
        count = p.memory[address('wNumBagItems')]
        assert bytes(p.memory[address('wNumBagItems'):address('wNumBagItems') + 2*count + 2]) == source[layout['bag']:layout['bag'] + 2*count + 2]
        assert bytes(p.memory[3, 0xD000:0xD200]) == source[0x3610:0x3810]
        assert p.memory[address('wPartyMon1Species')] == 0x15
        assert p.memory[address('wPartyMon1Level')] == 55

        def call(name):
            bank, pc = symbols[name]
            for offset, byte in enumerate((0xFB, 0xCD, pc & 255, pc >> 8, 0x18, 0xFE)):
                p.memory[0, 0x100 + offset] = byte
            p.memory[0xFF70] = 0
            if bank:
                p.memory[0x2000] = bank
                p.memory[address('hLoadedROMBank')] = bank
            p.register_file.SP = address('wStack')
            p.register_file.PC = 0x100
            p.tick(20, False)

        before = bytes(p.memory[address('wPartyMon1MaxHP'):address('wPartyMon1MaxHP') + 10])
        p.memory[address('wd0b5')] = 0x15
        p.memory[address('wCurEnemyLVL')] = 55
        call('GetMonHeader')
        p.register_file.HL = address('wPartyMon1HPExp') - 1
        p.register_file.D = address('wPartyMon1MaxHP') >> 8
        p.register_file.E = address('wPartyMon1MaxHP') & 255
        p.register_file.B = 1
        call('CalcStats')
        assert bytes(p.memory[address('wPartyMon1MaxHP'):address('wPartyMon1MaxHP') + 10]) == before
        for move, current_pp, expected in ((57, 216, 24), (45, 253, 61)):
            p.memory[address('wPartyMon1Moves')] = move
            p.memory[address('wPartyMon1PP')] = current_pp
            for name in ('wMonDataLocation', 'wWhichPokemon', 'wCurrentMenuItem'):
                p.memory[address(name)] = 0
            call('GetMaxPP')
            assert p.memory[address('wMaxPP')] == expected
        print(f'PASS: {rom} accepts editor save; party/bag/feature bytes match; native stat and PP routines agree')
    finally:
        p.stop(save=False)
