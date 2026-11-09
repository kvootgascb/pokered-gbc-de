#!/usr/bin/env python3
"""Append matching DX lettering and center the visible title within 12 tiles.

Usage: python3 tools/title_edition.py original_version.1bpp output.1bpp
The original German edition artwork remains the source for the font and gaps.
"""

import sys
from pathlib import Path


def title_edition(source):
    rows = [
        [(source[x // 8 * 8 + y] >> (7 - x % 8)) & 1 for x in range(len(source))]
        for y in range(8)
    ]
    ink = [x for x in range(len(source)) if any(row[x] for row in rows)]
    gap = max(right - left - 1 for left, right in zip(ink, ink[1:]))
    # The D comes from EDITION; X uses the same five-row height and weight.
    x_rows = ("......", "......", "......", "##..##", ".####.",
              "..##..", ".####.", "##..##")
    width = ink[-1] - ink[0] + 1 + gap + 12
    assert width <= 96, "edition title exceeds its 12-tile frame"
    padding = (96 - width) // 2
    result = []
    for y, row in enumerate(rows):
        word = row[ink[0]:ink[-1] + 1]
        dx = row[37:42] + [0] + [int(pixel == "#") for pixel in x_rows[y]]
        result.append([0] * padding + word + [0] * gap + dx + [0] * (96 - width - padding))
    return bytes(
        sum(result[y][tile * 8 + bit] << (7 - bit) for bit in range(8))
        for tile in range(12) for y in range(8)
    )


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(title_edition(Path(sys.argv[1]).read_bytes()))
