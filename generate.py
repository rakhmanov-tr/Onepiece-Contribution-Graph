"""Contribution level, adapted from sapthesh/Mario-Contribution-Graph.

Copyright (c) 2026 Sapthesh V
Released under the MIT License. The pirate sprite in this copy is original.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import urllib.request
from pathlib import Path

LEVELS = ("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")
DAY = re.compile(r"<td\b[^>]*class=\"[^\"]*ContributionCalendar-day[^\"]*\"[^>]*>", re.I)
ROW_COL = re.compile(r"contribution-day-component-(\d+)-(\d+)")
LEVEL = re.compile(r"data-level=\"(\d)\"")

# Front-facing pirate, traced from the drawn sprite. Each character is one pixel.
RUNNER_SCALE = 1.2
RUNNER_PIXELS = [
    "      KKKKKKK      ",
    "     KYYYYYYYK     ",
    "    KYYYYYYYYYK    ",
    "    KYYYRRRYYYK    ",
    "   KYRRRYYYRRRYK   ",
    "   KRYYYKKKYYYRK   ",
    " KKYKKKKKKKKKKYYKK ",
    "KYYKKKKSKSKSKKKKYYK",
    " KYYKKSKSSSKSKKYYK ",
    "  KKKSSKSSSKSSKKK  ",
    "    KSSKSSSKSSK    ",
    "     KSPSSSPSK     ",
    "      KKKKKKK      ",
    "       KRWRK       ",
    "      KRRWRRK      ",
    "     KSRRWRRSK     ",
    "    KSKKBBBKKSK    ",
    "     K KBBBK K     ",
    "       KSKSK       ",
    "       KSKSK       ",
    "        K K        ",
]
RUNNER_COLORS = {
    "K": "#000000",
    "Y": "#e0a42b",
    "R": "#c72828",
    "S": "#e6c791",
    "P": "#d47bbc",
    "B": "#0351ee",
    "W": "#ffffff",
}

# Decorations. Edit the pixel strings or the colors.
CLOUD_PIXELS = ["      WWWW      ", "   WWWWWWWWWW   ", " WWWWWWWWWWWWWW ", " WWWWWWWWWWWWWW "]
# Tangerine shrubs for the deck edge. Lit from the upper right, like the barrel.
BUSH_COLORS = {
    "K": "#10280e",
    "D": "#16441e",
    "G": "#2a7430",
    "L": "#3f9a3c",
    "H": "#8ed45e",
    "O": "#e87814",
    "C": "#c45a0c",
    "P": "#f0b030",
    "S": "#6a3204",
    "R": "#4a2810",
}
BUSH_PIXELS = [
    "....H......H......H...",
    "...KLK....KLK....KLK..",
    "..KDGLK..KDGLK..KDGLK.",
    ".KDGGGGLKDGGGGLKDGGGL.",
    ".KDKKKGGGGGGGGKKKGGGL.",
    ".KKPPPKGGGGGGKPPPKGGL.",
    ".KKPOCKGGGGGGKPOCKGGL.",
    ".KKCCCKGGGGGGKCCCKGGL.",
    ".KGKKKGGGGGGGGKKKGGDL.",
    "..KGGGGGGGGGGGGGGGDL..",
    "..KDDGGGGGGGGGGGGDDK..",
    "...KK...RRSSRR...KK...",
    ".....K.RSSSSSSR.K.....",
    "......KRRRRRRRRK......",
]
BUSH_B_PIXELS = [
    "....H......H......H...",
    "...KLK....KLK....KLK..",
    "..KDGLK..KDGLK..KDGLK.",
    ".KDGGGGLKDGGGGKKKGGGL.",
    ".KDGGGGGGGGGGKPPPKGGL.",
    ".KDGKKKGGGGGGKPOCKGGL.",
    ".KGKPPPKGGGGGKCCCKGGL.",
    ".KGKPOCKGGGGGGKKKGGGL.",
    ".KGKCCCKGGGGGGGGGGGDL.",
    "..KGKKKGGGGGGGGGGGDL..",
    "..KDDGGGGGGGGGGGGDDK..",
    "...KK...RRSSRR...KK...",
    ".....K.RSSSSSSR.K.....",
    "......KRRRRRRRRK......",
]
# Lookout in the crow's nest, traced from the drawn sprite.
# Same front-facing grid as the pirate. Scaled so his height matches.
LOOKOUT_PIXELS = [
    "   KKKKKKK   ",
    "  KDDDDDDDK  ",
    " KDDDDDDDDDK ",
    " KDDDDDDDDDK ",
    "KDDDDDDDDDDDK",
    "KDDDDDDDDDDDK",
    "KBBBBBBBBBBBK",
    "KGGSKSSSKSGGK",
    "KLGSKSSSKSGLK",
    " KGSSSSSSSGK ",
    "  KSSSSSSSK  ",
    "   KKKKKKK   ",
    "    KWWWK    ",
    "   KWWWWWK   ",
    "  KWWGGGWWK  ",
    " KWKKGGGKKWK ",
    "  K KEEEK K  ",
    "    KEKEK    ",
    "    KEKEK    ",
    "     K K     ",
]
LOOKOUT_COLORS = {
    "K": "#101010",
    "D": "#0c6a36",
    "B": "#084422",
    "G": "#3a9a44",
    "L": "#d4f0c4",
    "S": "#f4d7a8",
    "W": "#f7f4ee",
    "E": "#1a6b38",
}
# The original diagonal ham, with the same shading steps as the barrel.
MEAT_PIXELS = [
    "  KKKK                ",
    "KNWWNK                ",
    "KNWNNNKKKHHHK         ",
    "KNNNNHBBBBLLBK        ",
    " KKKBBBBBBLLBBKK      ",
    "   KHBBBLLBBBBBBKK    ",
    "   KBBBBBBBBBBBBBKK   ",
    "   KDBBBBBBBQQQNNNKK  ",
    "   KDBBBBBPPPQQQQQNK  ",
    "   KDDBBBBPPPPQQQQPK  ",
    "    KKBBBBPPPPNPPPPK  ",
    "      KDBBPPPPNNPPPK  ",
    "       KKPPPPPPNWNNNKK",
    "         KPPPPPPNNNNNK",
    "          KNPPPPWNNNNK",
    "           KKNNKKNNKK ",
]
MEAT_COLORS = {
    "K": "#3a140c",
    "D": "#8a3418",
    "B": "#c45a30",
    "L": "#e88848",
    "H": "#f0b070",
    "P": "#e07080",
    "Q": "#f4a8a8",
    "N": "#f0d8b0",
    "W": "#fff6e4",
}
# Barrel traced from the drawing: staves, two hoops, and a tap. No background.
BARREL_SCALE = 1.0
BARREL_PIXELS = [
    ".........DDDDKDDDDKDDDDDKKDDD    ",
    "........DDDAADDABBADBCCBDBCCCD   ",
    "........DAAAAADBCCAACLLCDCLLLD   ",
    "........KAAAADACCCAACLLLCDLHLD   ",
    ".......KKDDKKKKKKKDDKKKKDKKDKKK  ",
    ".......KMMMMMMMMMMMNNMMNNNMMMNK  ",
    ".......KNMMMMMMMMMMNNMMNNNMMMMD  ",
    "......KKKDKDDKDKKKKKKKKKDKDKDKKK ",
    "......KDAAADABBCBBAACLLLLCDCLLLD ",
    "......DDAAADABBCBBAACLLLLCDLLHLK ",
    "......DAAAADACCCCCBACLLLLCDCLLLD ",
    ".....DDAAAADACCCBBAACLLLLCDCLLLCK",
    ".....DDAAAADBBBCBBAACLLLLCDCLLLLD",
    ".....DDAAAAZZZBCZBAZCZLZZZDCLLLLD",
    ".....DAAAAAZABBZBZAZZLLZLCDLLLLLD",
    ".....DAAAAAZZZCZZZAZCLLZZCDLLLLLD",
    ".....DAAAAADBZBZCZAZZLLZLCDLLLLLD",
    ".....DAAAAAZZZBZBZAZCZLZZZDLLLLLD",
    ".....DAAAAADACCBBCAACLLLLCDLLLLLD",
    ".....DAAAAADBCBCBCAACLLLLCDLLLLLD",
    ".....DAAAAADBCBCCCAACLLLLCDLLLLLD",
    ".....DAAAAADBCBCCCAACLLLLCDLLLLLD",
    ".....DAAAAADBBBCCCAACLLLLCDLLLLLD",
    ".....KDAAAADCCBBBCAACLLLLCDLLLLLK",
    "......KAAAADBCBBBCAACLLLLCDLLLLA ",
    "..LGG.KDAAADABBBBCAACLLLLCDLLLLK ",
    "..PCP.DAAAAADCBCBBAACLLLCDCLLLLK ",
    "..GLGGKKKKKKKKDKKKKKDDDKDKKDDDDK ",
    ".GYYYYYDBMMMMMMMMNNMMMMNNNMMMMK  ",
    "YYYYGCCDNMMMMMMMMNNMMMMNNMMMMMK  ",
    "YYYC...KKKKKKKKKKKKKDDDKKKKDDDK  ",
    "YGCC....KAAAADABBCAACLLLCDCLLD   ",
    "........KAAAAADBBBAACLLCACLLLD   ",
    "........KDAAAADABBAACLCCDCLLLK   ",
    ".........DAAAADAAAADADDDDDDDA    ",
]
BARREL_COLORS = {
    "K": "#4a2810",
    "D": "#6a3204",
    "A": "#7c3a06",
    "B": "#8a420c",
    "C": "#a04e14",
    "L": "#c05e1c",
    "H": "#d07028",
    "M": "#6e6864",
    "N": "#c4bbb2",
    "G": "#c47a18",
    "Y": "#f0b028",
    "P": "#ffe08a",
    "Z": "#1a0c08",
}
WHEEL_COLORS = {
    "K": "#4a2810",
    "D": "#6a3204",
    "A": "#7c3a06",
    "C": "#a04e14",
    "L": "#c05e1c",
    "H": "#d07028",
    "M": "#6e6864",
    "N": "#c4bbb2",
}


def wheel_pixels() -> list[str]:
    """Ship's wheel from the front: rim, eight spokes, handles, iron hub."""
    size = 31
    center = size // 2
    mask = [["."] * size for _ in range(size)]
    rank = {".": 0, "spoke": 1, "rim": 2, "line": 3, "handle": 4, "knob": 5, "hub": 6}

    def mark(x: int, y: int, kind: str) -> None:
        if 0 <= x < size and 0 <= y < size and rank[kind] >= rank[mask[y][x]]:
            mask[y][x] = kind

    def circle(radius: int) -> list[tuple[int, int]]:
        x, y, error = radius, 0, 1 - radius
        points: list[tuple[int, int]] = []
        while x >= y:
            points += [
                (x, y), (y, x), (-x, y), (-y, x),
                (x, -y), (y, -x), (-x, -y), (-y, -x),
            ]
            y += 1
            if error < 0:
                error += 2 * y + 1
            else:
                x -= 1
                error += 2 * (y - x) + 1
        return points

    for dx, dy in circle(9) + circle(12):
        mark(center + dx, center + dy, "line")
    for dx, dy in circle(10) + circle(11):
        mark(center + dx, center + dy, "rim")
    for step in range(8):
        angle = -math.pi / 2 + step * math.pi / 4
        side_x = int(round(-math.sin(angle)))
        side_y = int(round(math.cos(angle)))
        for radius in range(4, 11):
            spoke_x = center + int(round(math.cos(angle) * radius))
            spoke_y = center + int(round(math.sin(angle) * radius))
            mark(spoke_x, spoke_y, "spoke")
            mark(spoke_x + side_x, spoke_y + side_y, "spoke")
        handle_x = center + int(round(math.cos(angle) * 14))
        handle_y = center + int(round(math.sin(angle) * 14))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    mark(handle_x, handle_y, "knob")
                elif abs(dx) + abs(dy) == 1:
                    mark(handle_x + dx, handle_y + dy, "handle")
                else:
                    mark(handle_x + dx, handle_y + dy, "line")
        mark(
            center + int(round(math.cos(angle) * 13)),
            center + int(round(math.sin(angle) * 13)),
            "rim",
        )
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if max(abs(dx), abs(dy)) <= 1 or abs(dx) + abs(dy) <= 2:
                mark(center + dx, center + dy, "hub")

    rows: list[str] = []
    for y in range(size):
        chars: list[str] = []
        for x in range(size):
            kind = mask[y][x]
            light = (x - center) - (y - center)
            if kind == "line":
                chars.append("K")
            elif kind == "knob":
                chars.append("H")
            elif kind == "handle":
                chars.append("L")
            elif kind == "hub":
                if x == center and y == center:
                    chars.append("K")
                elif light > 1:
                    chars.append("N")
                else:
                    chars.append("M")
            elif kind == "rim":
                if light > 8:
                    chars.append("H")
                elif light > 2:
                    chars.append("L")
                elif light > -4:
                    chars.append("C")
                else:
                    chars.append("A")
            elif kind == "spoke":
                if light > 4:
                    chars.append("C")
                elif light > -2:
                    chars.append("A")
                else:
                    chars.append("D")
            else:
                chars.append(".")
        rows.append("".join(chars))
    return rows


WHEEL_PIXELS = wheel_pixels()


def fetch_graphql(username: str, token: str) -> list[dict]:
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            weeks { contributionDays { contributionLevel } }
          }
        }
      }
    }
    """
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"userName": username}}).encode(),
        headers={"Authorization": f"Bearer {token}", "User-Agent": "Onepiece-Contribution-Graph"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode())
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def fetch_public(username: str) -> list[dict]:
    request = urllib.request.Request(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Onepiece-Contribution-Graph"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", "replace")
    found: dict[tuple[int, int], int] = {}
    for tag in DAY.findall(html):
        slot = ROW_COL.search(tag)
        level = LEVEL.search(tag)
        if not slot or not level:
            continue
        row, col = int(slot.group(1)), int(slot.group(2))
        found[(col, row)] = int(level.group(1))
    if not found:
        return []
    cols = max(col for col, _ in found) + 1
    rows = max(row for _, row in found) + 1
    weeks = []
    for col in range(cols):
        weeks.append(
            {
                "contributionDays": [
                    {"contributionLevel": LEVELS[min(found.get((col, row), 0), 4)]}
                    for row in range(rows)
                ]
            }
        )
    return weeks


def fetch_contributions(username: str, token: str | None) -> list[dict]:
    if token:
        try:
            weeks = fetch_graphql(username, token)
            if weeks:
                return weeks
        except Exception as error:
            print(f"GraphQL fetch failed: {error}")
    try:
        return fetch_public(username)
    except Exception as error:
        print(f"Public fetch failed: {error}")
        return []


def draw_sprite(
    name: str,
    pixels: list[str],
    colors: dict[str, str],
    scale: float,
    anchor_x: float = 0,
) -> str:
    svg = [f'    <g id="{name}" shape-rendering="crispEdges">']
    if anchor_x:
        svg.append(f'      <g transform="translate({-anchor_x:.1f}, 0)">')
    for y_index, row in enumerate(pixels):
        for x_index, mark in enumerate(row):
            if mark not in colors:
                continue
            svg.append(
                f'      <rect x="{x_index * scale:.1f}" y="{y_index * scale:.1f}" '
                f'width="{scale}" height="{scale}" fill="{colors[mark]}" />'
            )
    if anchor_x:
        svg.append("      </g>")
    svg.append("    </g>")
    return "\n".join(svg)


def runner_foot_x() -> float:
    foot = [index for index, mark in enumerate(RUNNER_PIXELS[-1]) if mark in RUNNER_COLORS]
    return ((min(foot) + max(foot) + 1) / 2) * RUNNER_SCALE


def path_samples(segments: list[tuple]) -> list[tuple[float, float]]:
    """Points of (x, length) along the parkour path. Length is the distance walked so far."""
    samples: list[tuple[float, float]] = []
    length = 0.0
    for segment in segments:
        kind = segment[0]
        if kind == "L":
            _, x0, y0, x1, y1 = segment
            steps = 6
            previous_x, previous_y = x0, y0
            for step in range(1, steps + 1):
                blend = step / steps
                x = x0 + (x1 - x0) * blend
                y = y0 + (y1 - y0) * blend
                length += ((x - previous_x) ** 2 + (y - previous_y) ** 2) ** 0.5
                samples.append((x, length))
                previous_x, previous_y = x, y
        else:
            _, x0, y0, cx, cy, x1, y1 = segment
            steps = 12
            previous_x, previous_y = x0, y0
            for step in range(1, steps + 1):
                blend = step / steps
                remain = 1 - blend
                x = remain * remain * x0 + 2 * remain * blend * cx + blend * blend * x1
                y = remain * remain * y0 + 2 * remain * blend * cy + blend * blend * y1
                length += ((x - previous_x) ** 2 + (y - previous_y) ** 2) ** 0.5
                samples.append((x, length))
                previous_x, previous_y = x, y
    return samples


def time_at_x(samples: list[tuple[float, float]], target_x: float, total: float) -> float:
    if total <= 0:
        return 0.5
    walked = total
    for x, length in samples:
        if x >= target_x:
            walked = length
            break
    return min(0.97, max(0.01, walked / total))


# Deck floor in the barrel's wood. Light comes from above, so each board is a
# stave turned on its side: dark caulking, lit edge, body, shade.
DECK_OUTLINE = "#4a2810"
DECK_DARKER = {
    "#d07028": "#c05e1c",
    "#c05e1c": "#a04e14",
    "#a04e14": "#8a420c",
    "#8a420c": "#7c3a06",
    "#7c3a06": "#6a3204",
    "#6a3204": "#6a3204",
    "#4a2810": "#4a2810",
}
DECK_LIGHTER = {
    "#4a2810": "#6a3204",
    "#6a3204": "#7c3a06",
    "#7c3a06": "#8a420c",
    "#8a420c": "#a04e14",
    "#a04e14": "#c05e1c",
    "#c05e1c": "#d07028",
    "#d07028": "#d07028",
}
# Gunwale the pirate stands on: outline, sun lip, lit oak, shadow under the nosing.
DECK_RIM = ("#4a2810", "#d07028", "#c05e1c", "#6a3204")
# Face of a plank, top to bottom. Seams between planks are drawn separately.
DECK_FACES = (
    ("#d07028", "#c05e1c", "#a04e14", "#8a420c", "#6a3204"),
    ("#c05e1c", "#a04e14", "#8a420c", "#7c3a06", "#6a3204"),
    ("#d07028", "#c05e1c", "#a04e14", "#7c3a06", "#6a3204"),
    ("#a04e14", "#8a420c", "#7c3a06", "#6a3204", "#6a3204"),
    ("#d07028", "#c05e1c", "#a04e14", "#8a420c", "#7c3a06"),
    ("#c05e1c", "#a04e14", "#8a420c", "#7c3a06", "#6a3204"),
)
DECK_BOARD_LENGTHS = (28, 36, 22, 44, 31, 39, 26, 42)


def _deck_joints(width: int, index: int, above: list[int]) -> list[int]:
    """Butt joints for one plank. Staggered, and kept off the joints of the plank above."""
    joints: list[int] = []
    cursor = 0
    step = 0
    if index % 2:
        cursor = DECK_BOARD_LENGTHS[index % len(DECK_BOARD_LENGTHS)] // 2
    while cursor < width - 2:
        length = DECK_BOARD_LENGTHS[(index + step) % len(DECK_BOARD_LENGTHS)]
        step += 1
        joint = cursor + length
        if joint >= width - 1:
            break
        if any(abs(joint - other) < 6 for other in above):
            joint += 8
        if joint < width - 1:
            joints.append(joint)
            cursor = joint
        else:
            break
    return joints


def _deck_paint_plank(
    grid: list[list[str]], y: int, face: tuple[str, ...], index: int, above: list[int]
) -> list[int]:
    """One horizontal board: seam, shaded face, staggered butts, grain, knots, nails."""
    width = len(grid[0])
    height = len(grid)
    seam = min(y, height)
    if seam >= height:
        return []
    for x in range(width):
        grid[seam][x] = DECK_OUTLINE
    face_top = seam + 1
    face_h = min(len(face), height - face_top)
    if face_h <= 0:
        return []
    for row in range(face_h):
        color = face[row]
        for x in range(width):
            grid[face_top + row][x] = color

    joints = _deck_joints(width, index, above)
    edges = [0, *joints, width]
    for board, (start, end) in enumerate(zip(edges, edges[1:])):
        if (index + board) % 5 == 0:
            for row in range(face_h):
                for x in range(start, end):
                    grid[face_top + row][x] = DECK_DARKER[grid[face_top + row][x]]
        span = end - start
        if span > 14:
            marks = (
                (1, 4 + ((index * 3 + board) % 6), 2 + (board % 3)),
                (min(3, face_h - 2), span // 2 + 3, 2 + (index % 2)),
            )
            for row_off, x_off, length in marks:
                if row_off <= 0 or row_off >= face_h - 1:
                    continue
                row = face_top + row_off
                for dx in range(length):
                    pixel = start + x_off + dx
                    if start < pixel < end - 2:
                        grid[row][pixel] = DECK_DARKER[grid[row][pixel]]
        if face_h >= 4 and (index * 3 + board) % 7 == 2 and end - start > 16:
            knot_x = start + max(6, (end - start) // 3)
            knot_y = face_top + face_h // 2 - 1
            knot = ("#7c3a06", "#6a3204", "#7c3a06")
            for dx, color in enumerate(knot):
                pixel = knot_x + dx - 1
                if 0 <= pixel < width:
                    grid[knot_y][pixel] = color
            if knot_y + 1 < face_top + face_h:
                grid[knot_y + 1][knot_x] = DECK_OUTLINE

    for joint in joints:
        for row in range(face_h):
            grid[face_top + row][joint] = DECK_OUTLINE
            if joint - 1 >= 0 and row != 0:
                grid[face_top + row][joint - 1] = DECK_DARKER[grid[face_top + row][joint - 1]]
        if joint + 1 < width:
            grid[face_top][joint + 1] = DECK_LIGHTER[grid[face_top][joint + 1]]

    nail_row = face_top + face_h // 2
    for start, end in zip(edges, edges[1:]):
        span = end - start
        if span < 10:
            continue
        nails = [start + 3, end - 4]
        if span > 36:
            nails.append(start + span // 2)
        for nail_x in nails:
            if nail_x <= 0 or nail_x >= width - 1 or nail_x in joints:
                continue
            grid[nail_row][nail_x] = DECK_OUTLINE
            grid[nail_row][nail_x + 1] = "#c4bbb2"
            if nail_row + 1 < face_top + face_h and nail_x + 1 not in joints:
                grid[nail_row + 1][nail_x] = "#6e6864"
    return joints


def deck_rects(width: int, top: int, bottom: int) -> list[tuple[int, int, int, int, str]]:
    """Horizontal deck planks from the walking line down, in the barrel palette."""
    height = bottom - top
    if width <= 0 or height <= 0:
        return []
    grid = [["#6a3204"] * width for _ in range(height)]
    for row, color in enumerate(DECK_RIM[:height]):
        for x in range(width):
            grid[row][x] = color
        if row == 2:
            bolt = 9
            while bolt < width - 1:
                grid[row][bolt] = DECK_OUTLINE
                grid[row][bolt + 1] = "#c4bbb2"
                bolt += 27

    y = min(len(DECK_RIM), height)
    index = 0
    above: list[int] = []
    while y < height:
        face = DECK_FACES[index % len(DECK_FACES)]
        above = _deck_paint_plank(grid, y, face, index, above)
        y += 1 + len(face)
        index += 1
    for x in range(width):
        grid[-1][x] = DECK_OUTLINE

    rects: list[tuple[int, int, int, int, str]] = []
    for row, pixels in enumerate(grid):
        x = 0
        while x < width:
            color = pixels[x]
            end = x + 1
            while end < width and pixels[end] == color:
                end += 1
            rects.append((x, top + row, end - x, 1, color))
            x = end
    return rects


MAST_FACE = ("#4a2810", "#6a3204", "#7c3a06", "#a04e14", "#c05e1c", "#d07028", "#4a2810")
MAST_HOOP = ("#4a2810", "#6e6864", "#6e6864", "#c4bbb2", "#c4bbb2", "#c4bbb2", "#4a2810")
MAST_HOOP_SHADE = ("#4a2810", "#4a2810", "#6e6864", "#6e6864", "#c4bbb2", "#6e6864", "#4a2810")


def _append_rects(svg: list[str], rects: list[tuple[int, int, int, int, str]]) -> None:
    for x, y, w, h, fill in rects:
        svg.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" />')


def _rle_rows(grid: list[list[str | None]], origin_x: int, origin_y: int) -> list[tuple[int, int, int, int, str]]:
    rects: list[tuple[int, int, int, int, str]] = []
    for y, row in enumerate(grid):
        x = 0
        while x < len(row):
            color = row[x]
            if color is None:
                x += 1
                continue
            end = x + 1
            while end < len(row) and row[end] == color:
                end += 1
            rects.append((origin_x + x, origin_y + y, end - x, 1, color))
            x = end
    return rects


def mast_rects(mast_x: int, top: int, bottom: int, nest_top: int, nest_bottom: int) -> list[tuple[int, int, int, int, str]]:
    """Vertical spar: barrel stave, iron hoops, and a truck at the head."""
    rects: list[tuple[int, int, int, int, str]] = []
    for column, color in enumerate(MAST_FACE):
        rects.append((mast_x + column, top, 1, bottom - top, color))
    cap_x = mast_x - 1
    cap = ("..KHHHK..", ".KLLLLLK.", "KLLLLLLLK")
    cap_colors = {"K": "#4a2810", "H": "#d07028", "L": "#c05e1c"}
    for row, marks in enumerate(cap):
        for column, mark in enumerate(marks):
            if mark in cap_colors:
                rects.append((cap_x + column, top - 2 + row, 1, 1, cap_colors[mark]))
    grain_y = top + 16
    while grain_y < bottom - 8:
        if not nest_top <= grain_y <= nest_bottom:
            rects.append((mast_x + 2, grain_y, 1, 3, "#6a3204"))
        grain_y += 18
    hoop_y = top + 10
    while hoop_y < bottom - 10:
        if not nest_top - 2 <= hoop_y <= nest_bottom:
            for column, color in enumerate(MAST_HOOP):
                rects.append((mast_x + column, hoop_y, 1, 1, color))
            for column, color in enumerate(MAST_HOOP_SHADE):
                rects.append((mast_x + column, hoop_y + 1, 1, 1, color))
        hoop_y += 26
    return rects


def ladder_rects(mast_x: int, mast_w: int, top: int, bottom: int) -> list[tuple[int, int, int, int, str]]:
    """Ratlines beside the mast: twisted ropes and wooden rungs."""
    if bottom - top < 6:
        return []
    left = mast_x + mast_w
    right = left + 10
    height = bottom - top
    twist_a = ("#4a2810", "#c05e1c", "#c05e1c", "#4a2810")
    twist_b = ("#6a3204", "#d07028", "#a04e14", "#6a3204")
    columns = [[] for _ in range(4)]
    for y in range(height):
        colors = twist_a if (y // 2) % 2 == 0 else twist_b
        for index, color in enumerate(colors):
            columns[index].append(color)
    rects: list[tuple[int, int, int, int, str]] = []
    for index, x in enumerate((left, left + 1, right, right + 1)):
        start = 0
        while start < height:
            end = start + 1
            while end < height and columns[index][end] == columns[index][start]:
                end += 1
            rects.append((x, top + start, 1, end - start, columns[index][start]))
            start = end
    rung_w = right + 2 - left
    rung_y = top + 4
    while rung_y + 1 < bottom:
        rects.append((left, rung_y, rung_w, 1, "#d07028"))
        rects.append((left, rung_y + 1, rung_w, 1, "#6a3204"))
        rects.append((left, rung_y, 1, 2, "#4a2810"))
        rects.append((right + 1, rung_y, 1, 2, "#4a2810"))
        rung_y += 8
    return rects


def nest_rects(mast_x: int, mast_w: int, lookout_w: float, nest_floor: float) -> list[tuple[int, int, int, int, str]]:
    """Crow's nest: hoop, back staves, and a plank floor the lookout stands on."""
    width = int(round(lookout_w + 18))
    if width % 2 == 0:
        width += 1
    left = int(round(mast_x + mast_w / 2 - width / 2))
    top = int(nest_floor) - 16
    grid: list[list[str | None]] = [[None] * width for _ in range(22)]

    def fill(x: int, y: int, color: str) -> None:
        if 0 <= x < width and 0 <= y < len(grid):
            grid[y][x] = color

    for y in range(22):
        for x, color in enumerate(("#4a2810", "#6a3204", "#8a420c")):
            fill(x, y, color)
        for x, color in enumerate(("#c05e1c", "#d07028", "#4a2810")):
            fill(width - 3 + x, y, color)
    for x in range(1, width - 1):
        fill(x, 0, "#4a2810")
    for x in range(2, width - 2):
        fill(x, 1, "#d07028")
        fill(x, 2, "#6a3204")
    for x in range(5, width - 5, 4):
        face = "#a04e14" if (x // 4) % 2 == 0 else "#8a420c"
        for y in range(3, 16):
            fill(x, y, "#6a3204")
            fill(x + 1, y, face)
    for row, color in enumerate(("#4a2810", "#d07028", "#c05e1c", "#a04e14", "#6a3204", "#4a2810")):
        for x in range(width):
            fill(x, 16 + row, color)
        fill(0, 16 + row, "#4a2810")
        fill(width - 1, 16 + row, "#4a2810")
    bolt = 6
    while bolt < width - 6:
        fill(bolt, 17, "#4a2810")
        fill(bolt + 1, 17, "#c4bbb2")
        bolt += 8
    return _rle_rows(grid, left, top)


def helm_rects(wheel_x: int, wheel_y: int, ground_y: int) -> list[tuple[int, int, int, int, str]]:
    """Binnacle and the step under the wheel, in the deck's wood."""
    rects: list[tuple[int, int, int, int, str]] = []
    plat_w = 36
    plat_x = wheel_x - plat_w // 2
    plat_y = ground_y - 6
    for row, color in enumerate(("#4a2810", "#d07028", "#c05e1c", "#a04e14", "#6a3204", "#4a2810")):
        rects.append((plat_x, plat_y + row, plat_w, 1, color))
    bolt = plat_x + 6
    while bolt < plat_x + plat_w - 6:
        rects.append((bolt, plat_y + 2, 1, 1, "#4a2810"))
        rects.append((bolt + 1, plat_y + 2, 1, 1, "#c4bbb2"))
        bolt += 10
    post_x = wheel_x - 3
    post_top = wheel_y + 12
    for column, color in enumerate(MAST_FACE):
        rects.append((post_x + column, post_top, 1, plat_y - post_top, color))
    for column, color in enumerate(MAST_HOOP):
        rects.append((post_x + column, post_top + 2, 1, 1, color))
    rects.append((post_x - 3, plat_y - 4, 3, 4, "#6a3204"))
    rects.append((post_x + len(MAST_FACE), plat_y - 4, 3, 4, "#a04e14"))
    rects.append((post_x - 3, plat_y - 4, 3, 1, "#4a2810"))
    rects.append((post_x + len(MAST_FACE), plat_y - 4, 3, 1, "#4a2810"))
    return rects


def generate(username: str, filename: str) -> None:
    token = os.environ.get("GITHUB_TOKEN")
    weeks_data = fetch_contributions(username, token)
    cell_size = 10
    meat_cols = max(len(row) for row in MEAT_PIXELS)
    meat_rows = len(MEAT_PIXELS)
    meat_scale = cell_size / max(meat_cols, meat_rows)
    meat_width = meat_cols * meat_scale
    meat_height = meat_rows * meat_scale
    gap = 4
    step = cell_size + gap
    cols = len(weeks_data) if weeks_data else 53
    rows = 7
    grid_x_offset = 40
    runner_height = len(RUNNER_PIXELS) * RUNNER_SCALE
    lookout_scale = runner_height / len(LOOKOUT_PIXELS)
    top_padding = int(runner_height + 26)
    mast_x = grid_x_offset + (cols * step) + 22
    helm_x = mast_x + 58
    width = helm_x + 64
    height = top_padding + (rows * step) + 40
    ground_y = top_padding + (rows * step)
    level_map = {
        "NONE": "empty",
        "FIRST_QUARTILE": "lvl1",
        "SECOND_QUARTILE": "lvl2",
        "THIRD_QUARTILE": "lvl3",
        "FOURTH_QUARTILE": "lvl4",
    }

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        "  <style>",
        "    .bg { fill: #8ecae6; }",
        "    .empty { fill: rgba(255,255,255,0.2); }",
        "    .lvl1 { fill: #0e4429; stroke: #000; stroke-width: 0.5; }",
        "    .lvl2 { fill: #006d32; stroke: #000; stroke-width: 0.5; }",
        "    .lvl3 { fill: #26a641; stroke: #000; stroke-width: 0.5; }",
        "    .lvl4 { fill: #39d353; stroke: #000; stroke-width: 0.5; }",
        "  </style>",
        "  <defs>",
        draw_sprite("runner", RUNNER_PIXELS, RUNNER_COLORS, RUNNER_SCALE, runner_foot_x()),
        draw_sprite("cloud", CLOUD_PIXELS, {"W": "#FFFFFF"}, 2.0),
        draw_sprite("bush", BUSH_PIXELS, BUSH_COLORS, 1.0),
        draw_sprite("bush-b", BUSH_B_PIXELS, BUSH_COLORS, 1.0),
        draw_sprite("lookout", LOOKOUT_PIXELS, LOOKOUT_COLORS, lookout_scale),
        draw_sprite("barrel", BARREL_PIXELS, BARREL_COLORS, BARREL_SCALE),
        draw_sprite("wheel", WHEEL_PIXELS, WHEEL_COLORS, 1.0),
        draw_sprite("meat", MEAT_PIXELS, MEAT_COLORS, meat_scale),
        "  </defs>",
        '  <rect width="100%" height="100%" class="bg" />',
    ]
    for index in range(4):
        svg.append(f'  <use href="#cloud" x="0" y="{10 if index % 2 == 0 else 30}">')
        svg.append(
            f'    <animate attributeName="x" from="{width}" to="-100" dur="{40 + (index * 5)}s" repeatCount="indefinite" />'
        )
        svg.append("  </use>")

    svg.append('  <g id="deck" shape-rendering="crispEdges">')
    for deck_x, deck_y, deck_w, deck_h, deck_fill in deck_rects(width, ground_y, height):
        svg.append(
            f'    <rect x="{deck_x}" y="{deck_y}" width="{deck_w}" height="{deck_h}" fill="{deck_fill}" />'
        )
    svg.append("  </g>")
    bush_height = len(BUSH_PIXELS)
    bush_width = max(len(row) for row in BUSH_PIXELS)
    bush_x = 78
    bush_kind = 0
    while bush_x + bush_width < mast_x - 80:
        bush_name = "bush" if bush_kind % 2 == 0 else "bush-b"
        svg.append(f'  <use href="#{bush_name}" x="{bush_x}" y="{ground_y - bush_height + 3}" />')
        bush_x += 96
        bush_kind += 1

    barrel_w = max(len(row) for row in BARREL_PIXELS) * BARREL_SCALE
    barrel_h = len(BARREL_PIXELS) * BARREL_SCALE
    barrel_x = 2
    barrel_top = ground_y - barrel_h
    barrel_cx = barrel_x + barrel_w / 2
    svg.append(f'  <use href="#barrel" x="{barrel_x}" y="{barrel_top}" />')

    start_x = barrel_cx
    segments: list[tuple] = []
    commands = [f"M {start_x:.1f} {ground_y:.1f}"]
    current_x, current_y = start_x, ground_y

    def add_line(x: float, y: float) -> None:
        nonlocal current_x, current_y
        segments.append(("L", current_x, current_y, x, y))
        commands.append(f"L {x:.1f} {y:.1f}")
        current_x, current_y = x, y

    def add_quad(x: float, y: float, lift: float = 25) -> None:
        nonlocal current_x, current_y
        control_x = current_x + (x - current_x) / 2
        control_y = min(current_y, y) - lift
        segments.append(("Q", current_x, current_y, control_x, control_y, x, y))
        commands.append(f"Q {control_x:.1f} {control_y:.1f} {x:.1f} {y:.1f}")
        current_x, current_y = x, y

    add_line(start_x, barrel_top - runner_height)
    empty_streak = 0
    meats = []
    meat_x = (cell_size - meat_width) / 2
    meat_y = (cell_size - meat_height) / 2

    for col, week in enumerate(weeks_data):
        highest = rows
        col_x = grid_x_offset + col * step
        empty_week = True
        for row, day in enumerate(week["contributionDays"]):
            level = level_map.get(day.get("contributionLevel", "NONE"), "empty")
            block_y = top_padding + row * step
            svg.append(
                f'  <rect x="{col_x}" y="{block_y}" width="{cell_size}" height="{cell_size}" rx="2" class="{level}" />'
            )
            if level != "empty":
                empty_week = False
                if row < highest:
                    highest = row
            if level == "lvl4":
                meats.append({"x": col_x + meat_x, "y": block_y + meat_y, "hit": col_x + cell_size * 0.85})
        empty_streak = empty_streak + 1 if empty_week else 0
        target_x = col_x
        target_y = (top_padding + highest * step) - runner_height
        if empty_streak == 4:
            target_y -= 25
            meats.append({"x": col_x + meat_x, "y": target_y - meat_height, "hit": col_x + cell_size * 0.85})
            empty_streak = 0
        if target_y != current_y:
            add_quad(target_x, target_y)
        else:
            add_line(target_x, target_y)

    slide_x = mast_x + 10
    grab_y = 10
    add_quad(slide_x, grab_y, 36)
    add_line(slide_x, ground_y - runner_height)
    add_line(helm_x + 16, ground_y - runner_height)
    samples = path_samples(segments)
    total_length = samples[-1][1] if samples else 1.0
    slide_start = time_at_x(samples, slide_x - 1, total_length)
    deck_hit = None
    for x, length in samples:
        if x >= slide_x - 1 and deck_hit is None:
            deck_hit = length
    # The slide is the vertical run after the grab. Use the length once x has
    # stayed at the mast and y has reached the deck: the last sample at slide_x.
    slide_end_length = deck_hit or total_length
    for x, length in samples:
        if abs(x - slide_x) < 1.5:
            slide_end_length = length
    slide_end = min(0.98, max(slide_start + 0.04, slide_end_length / total_length))

    for meat in meats:
        grabbed = time_at_x(samples, meat["hit"], total_length)
        end = min(0.995, grabbed + 0.012)
        svg.append(f'  <g transform="translate({meat["x"]}, {meat["y"]})">')
        svg.append("    <g>")
        svg.append(
            f'      <animateTransform attributeName="transform" type="translate" values="0,0; 0,0; 0,-20; 0,-20" keyTimes="0;{grabbed:.3f};{end:.3f};1" dur="20s" repeatCount="indefinite" />'
        )
        svg.append(
            f'      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{grabbed:.3f};{end:.3f};1" dur="20s" repeatCount="indefinite" />'
        )
        svg.append('      <use href="#meat" x="0" y="0" />')
        svg.append("    </g>")
        svg.append("  </g>")

    mast_w = len(MAST_FACE)
    lookout_h = runner_height
    lookout_w = max(len(row) for row in LOOKOUT_PIXELS) * lookout_scale
    nest_floor = lookout_h + 10
    lookout_x = mast_x + mast_w / 2 - lookout_w / 2
    lookout_y = nest_floor - lookout_h
    drop = ground_y - lookout_h - lookout_y
    nest_top = int(nest_floor) - 16
    nest_bottom = nest_top + 22
    svg.append('  <g id="rigging" shape-rendering="crispEdges">')
    _append_rects(svg, mast_rects(mast_x, 6, ground_y, nest_top, nest_bottom))
    _append_rects(svg, ladder_rects(mast_x, mast_w, int(nest_floor) + 2, ground_y - 1))
    _append_rects(svg, nest_rects(mast_x, mast_w, lookout_w, nest_floor))
    svg.append("  </g>")
    svg.append("  <g>")
    svg.append(
        f'    <animateTransform attributeName="transform" type="translate" values="0,0; 0,0; 0,{drop:.1f}; 0,{drop:.1f}" keyTimes="0;{slide_start:.3f};{slide_end:.3f};1" dur="20s" repeatCount="indefinite" />'
    )
    svg.append(f'    <use href="#lookout" x="{lookout_x}" y="{lookout_y}" />')
    svg.append("  </g>")
    wheel_x = helm_x + 24
    wheel_y = ground_y - 24
    svg.append('  <g id="helm" shape-rendering="crispEdges">')
    _append_rects(svg, helm_rects(wheel_x, wheel_y, ground_y))
    svg.append(f'    <use href="#wheel" x="{wheel_x - 15}" y="{wheel_y - 15}" />')
    svg.append("  </g>")
    svg.append(f'  <path id="parkour-path" d="{" ".join(commands)}" fill="none" stroke="none" />')
    svg.append('  <use href="#runner">')
    svg.append('    <animateMotion dur="20s" repeatCount="indefinite"><mpath href="#parkour-path"/></animateMotion>')
    svg.append("  </use>")
    svg.append("</svg>")
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    Path(filename).write_text("\n".join(svg), encoding="utf-8")
    print(f"Wrote {filename}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default=os.environ.get("GITHUB_ACTOR", "rakhmanov-tr"))
    parser.add_argument("--out", default="dist/level.svg")
    args = parser.parse_args()
    generate(args.user, args.out)
    out = Path(args.out).parent
    for stale in ("eater.svg", "eater-dark.svg", "dragon.svg", "dragon-dark.svg"):
        (out / stale).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
