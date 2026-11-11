#!/usr/bin/env python3
"""Bundle the offline editor using the current ROM's symbols, data and graphics."""
from pathlib import Path
import base64
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def symbols(edition):
    result = {}
    for line in (ROOT / f'{edition}.sym').read_text().splitlines():
        fields = line.split()
        if len(fields) == 2 and ':' in fields[0]:
            bank, addr = fields[0].split(':')
            result[fields[1]] = (int(bank, 16), int(addr, 16))
    return result


def build():
    syms = symbols('pokered')
    blue = symbols('pokeblue')
    rom = (ROOT / 'pokered.gbc').read_bytes()

    def read(name, count):
        bank, addr = syms[name]
        offset = bank * 0x4000 + addr % 0x4000 if bank else addr
        return list(rom[offset:offset + count])

    chars = {}
    for char, number in re.findall(r'charmap\s+"([^"\n]+)",\s*\$([0-9a-fA-F]+)', (ROOT / 'constants/charmap.asm').read_text().split('; Japanese kana,')[0]):
        if len(char) == 1 and char != '@':
            chars[int(number, 16)] = char
    chars[0x54] = 'POKé'

    def decode(data):
        return ''.join(chars.get(x, '?') for x in data[:data.index(0x50)] if x != 0x50) if 0x50 in data else ''.join(chars.get(x, '?') for x in data)

    def strings(name, count):
        data = read(name, 8000)
        result = []
        for _ in range(count):
            end = data.index(0x50)
            result.append(decode(data[:end]))
            data = data[end + 1:]
        return result

    def sram(name):
        bank, addr = syms[name]
        return bank * 0x2000 + addr - 0xA000

    main = sram('sMainData')
    party = sram('sPartyData')
    layout = {key: sram(value) for key, value in {
        'start': 'sGameData', 'end': 'sGameDataEnd', 'checksum': 'sMainDataCheckSum',
        'playerName': 'sPlayerName', 'party': 'sPartyData',
    }.items()}
    for key, name in {'bag': 'wNumBagItems', 'format': 'wInventoryFormat',
                      'playerId': 'wPlayerID', 'owned': 'wPokedexOwned', 'seen': 'wPokedexSeen'}.items():
        layout[key] = main + syms[name][1] - syms['wMainDataStart'][1]
    for key, name in {'mons': 'wPartyMons', 'otNames': 'wPartyMonOT', 'nicknames': 'wPartyMonNicks'}.items():
        layout[key] = party + syms[name][1] - syms['wPartyDataStart'][1]
    for name in ('sGameData', 'sGameDataEnd', 'sPartyData', 'sMainData', 'wPartyDataStart',
                 'wMainDataStart', 'wInventoryFormat', 'wNumBagItems', 'wPlayerID'):
        assert syms[name] == blue[name], f'Red/Blue layouts differ: {name}'

    dex = read('PokedexOrder', 190)
    bases = read('BaseStats', 150 * 28)
    names = read('MonsterNames', 190 * 10)
    files = re.findall(r'base_stats/(\w+)\.asm', (ROOT / 'data/pokemon/base_stats.asm').read_text())
    pokemon = []
    for index, number in enumerate(dex, 1):
        if not number:
            continue
        base = read('MewBaseStats', 28) if number == 151 else bases[(number - 1) * 28:number * 28]
        assert base[0] == number
        key = 'mew' if number == 151 else files[number - 1]
        base_source = (ROOT / f'data/pokemon/base_stats/{key}.asm').read_text()
        picture = re.search(r'gfx/pokemon/gsfront/([^"]+)\.pic', base_source).group(1)
        pic = ROOT / f'gfx/pokemon/gsfront/{picture}.png'
        pokemon.append(dict(id=index, dex=number, name=decode(names[(index - 1)*10:index*10]),
                            stats=base[1:6], types=base[6:8], catchRate=base[8],
                            moves=base[15:19], growth=base[19],
                            image='data:image/png;base64,' + base64.b64encode(pic.read_bytes()).decode()))
    pokemon.sort(key=lambda mon: mon['dex'])
    assert len(pokemon) == 151
    move_names = strings('MoveNames', 165)
    move_bytes = read('Moves', 165 * 6)
    moves = [dict(id=i + 1, name=name, pp=move_bytes[i * 6 + 5]) for i, name in enumerate(move_names)]
    item_names = strings('ItemNames', 83)
    items = [dict(id=i + 1, name=name) for i, name in enumerate(item_names)
             if '?' not in name and not 0x15 <= i + 1 <= 0x1C]
    machines = read('TechnicalMachines', 55)
    for i in range(5):
        items.append(dict(id=0xC4 + i, name=f'VM{i+1:02} · {move_names[machines[50+i]-1]}'))
    for i in range(50):
        items.append(dict(id=0xC9 + i, name=f'TM{i+1:02} · {move_names[machines[i]-1]}'))
    growth_bytes = read('GrowthRateTable', 24)
    growth_rates = []
    for i in range(0, 24, 4):
        a, b, c, d = growth_bytes[i:i+4]
        growth_rates.append([a >> 4, a & 15, -(b & 127) if b & 128 else b, c, d])
    data = dict(layout=layout, chars=chars, pokemon=pokemon, moves=moves, items=items,
                featureMagic=read('LoadFeatureSaveData.magic', 4), growthRates=growth_rates)
    result = (HERE / 'editor.template.html').read_text()
    result = result.replace('/*__DATA__*/', 'globalThis.DX_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';')
    result = result.replace('/*__CORE__*/', (HERE / 'core.js').read_text())
    result = result.replace('/*__APP__*/', (HERE / 'app.js').read_text())
    target = HERE / 'Pokemon-DX-Saveeditor.html'
    target.write_text(result)
    with zipfile.ZipFile(HERE / 'Pokemon-DX-Saveeditor.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in ((target.name, result.encode('utf-8')),
                              ('Lies-mich.txt', (HERE / 'Lies-mich.txt').read_bytes())):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)
    print(f'{target.name}: {target.stat().st_size:,} bytes, {len(pokemon)} Pokémon, {len(items)} items')


if __name__ == '__main__':
    build()
