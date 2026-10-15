"""Contribution level, adapted from sapthesh/Mario-Contribution-Graph.

Copyright (c) 2026 Sapthesh V
Released under the MIT License. The pirate sprite in this copy is original.
"""

from __future__ import annotations

import argparse
import json
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
BUSH_PIXELS = ["      GGGG      ", "   GGGGGGGGGG   ", " GGGGGGGGGGGGGG ", " GGGGGGGGGGGGGG "]
# Diagonal ham traced from the drawing: bone knob, long cut, bone at the face.
MEAT_PIXELS = [
    "  KKKK                ",
    "KNNNNK                ",
    "KNNNNNKKKBBBK         ",
    "KNNNNBBBBBBBBK        ",
    " KKKBBBBBBBBBBKK      ",
    "   KBBBBBBBBBBBBKK    ",
    "   KBBBBBBBBBBBBBKK   ",
    "   KDBBBBBBBPPPNNNKK  ",
    "   KDBBBBBPPPNPPPPNK  ",
    "   KDDBBBBPPPNPPPPPK  ",
    "    KKBBBBPPPNPPPPPK  ",
    "      KBBBPPPPNNPPPK  ",
    "       KKPPPPPPNNNNNKK",
    "         KPPPPPPNNNNNK",
    "          KNPPPPNNNNNK",
    "           KKNNKKNNKK ",
]
MEAT_COLORS = {
    "K": "#000000",
    "N": "#f0d8b0",
    "B": "#c46a38",
    "D": "#8a3e24",
    "P": "#e07a88",
}


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
        headers={"Authorization": f"Bearer {token}", "User-Agent": "conversation-anigraph"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode())
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def fetch_public(username: str) -> list[dict]:
    request = urllib.request.Request(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "conversation-anigraph"},
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
    top_padding = int(runner_height + 26)
    flag_x = grid_x_offset + (cols * step) + 15
    castle_x = flag_x + 35
    width = castle_x + 80
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
        "    .bg { fill: #87CEEB; }",
        "    .empty { fill: rgba(255,255,255,0.2); }",
        "    .lvl1 { fill: #0e4429; stroke: #000; stroke-width: 0.5; }",
        "    .lvl2 { fill: #006d32; stroke: #000; stroke-width: 0.5; }",
        "    .lvl3 { fill: #26a641; stroke: #000; stroke-width: 0.5; }",
        "    .lvl4 { fill: #39d353; stroke: #000; stroke-width: 0.5; }",
        "    .ground { fill: #c84c0c; }",
        "    .ground-top { fill: #000000; }",
        "  </style>",
        "  <defs>",
        draw_sprite("runner", RUNNER_PIXELS, RUNNER_COLORS, RUNNER_SCALE, runner_foot_x()),
        draw_sprite("cloud", CLOUD_PIXELS, {"W": "#FFFFFF"}, 2.0),
        draw_sprite("bush", BUSH_PIXELS, {"G": "#00A800"}, 2.0),
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

    svg.append(f'  <rect x="0" y="{ground_y}" width="{width}" height="{height - ground_y}" class="ground" />')
    svg.append(f'  <rect x="0" y="{ground_y}" width="{width}" height="2" class="ground-top" />')
    for index in range(10):
        svg.append(f'  <use href="#bush" x="{index * 120 + 30}" y="{ground_y - 8}" />')

    pipe_x, pipe_top = 10, ground_y - 30
    svg.append(f'  <rect x="{pipe_x}" y="{pipe_top}" width="24" height="30" fill="#00A800" stroke="#000"/>')
    svg.append(f'  <rect x="{pipe_x - 2}" y="{pipe_top}" width="28" height="10" fill="#00A800" stroke="#000"/>')

    total_travel = (castle_x + 25) - pipe_x
    path = f"M {pipe_x + 4} {ground_y} L {pipe_x + 4} {pipe_top - runner_height} "
    current_x, current_y = pipe_x + 4, pipe_top - runner_height
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
                meats.append({"x": col_x + meat_x, "y": block_y + meat_y, "t": (col_x - pipe_x) / total_travel})
        empty_streak = empty_streak + 1 if empty_week else 0
        target_x = col_x
        target_y = (top_padding + highest * step) - runner_height
        if empty_streak == 4:
            target_y -= 25
            meats.append({"x": col_x + meat_x, "y": target_y - meat_height, "t": (col_x - pipe_x) / total_travel})
            empty_streak = 0
        if target_y != current_y:
            path += f" Q {current_x + (target_x - current_x) / 2} {min(current_y, target_y) - 25} {target_x} {target_y}"
        else:
            path += f" L {target_x} {target_y}"
        current_x, current_y = target_x, target_y

    flag_top = top_padding - 10
    path += f" Q {current_x + 10} {current_y - 20} {flag_x - 4} {flag_top + 10} "
    path += f" L {flag_x - 4} {ground_y - runner_height} "
    path += f" L {castle_x + 15} {ground_y - runner_height} "

    for meat in meats:
        end = min(1.0, meat["t"] + 0.03)
        svg.append(f'  <g transform="translate({meat["x"]}, {meat["y"]})">')
        svg.append("    <g>")
        svg.append(
            f'      <animateTransform attributeName="transform" type="translate" values="0,0; 0,0; 0,-20; 0,-20" keyTimes="0;{meat["t"]:.3f};{end:.3f};1" dur="20s" repeatCount="indefinite" />'
        )
        svg.append(
            f'      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{meat["t"]:.3f};{end:.3f};1" dur="20s" repeatCount="indefinite" />'
        )
        svg.append('      <use href="#meat" x="0" y="0" />')
        svg.append("    </g>")
        svg.append("  </g>")

    flag_time = min(1.0, (flag_x - pipe_x) / total_travel)
    flag_end = min(1.0, flag_time + 0.05)
    svg.append(
        f'  <rect x="{flag_x}" y="{flag_top}" width="3" height="{ground_y - flag_top}" fill="#FFF" stroke="#000" stroke-width="0.5"/>'
    )
    svg.append(f'  <circle cx="{flag_x + 1.5}" cy="{flag_top}" r="4" fill="#f8d820" stroke="#000"/>')
    svg.append("  <g>")
    svg.append(
        f'    <animateTransform attributeName="transform" type="translate" values="0,0; 0,0; 0,{ground_y - flag_top - 15}; 0,{ground_y - flag_top - 15}" keyTimes="0;{flag_time:.3f};{flag_end:.3f};1" dur="20s" repeatCount="indefinite" />'
    )
    svg.append(
        f'    <polygon points="{flag_x - 15},{flag_top + 5} {flag_x},{flag_top + 5} {flag_x},{flag_top + 15}" fill="#00A800" stroke="#000"/>'
    )
    svg.append("  </g>")
    svg.append(f'  <path id="parkour-path" d="{path}" fill="none" stroke="none" />')
    svg.append('  <use href="#runner">')
    svg.append('    <animateMotion dur="20s" repeatCount="indefinite"><mpath href="#parkour-path"/></animateMotion>')
    svg.append("  </use>")

    castle_y = ground_y - 40
    svg.append(
        f'  <path d="M {castle_x} {ground_y} L {castle_x} {castle_y} L {castle_x+10} {castle_y} L {castle_x+10} {castle_y+10} L {castle_x+20} {castle_y+10} L {castle_x+20} {castle_y} L {castle_x+30} {castle_y} L {castle_x+30} {castle_y+10} L {castle_x+40} {castle_y+10} L {castle_x+40} {castle_y} L {castle_x+50} {castle_y} L {castle_x+50} {ground_y} Z" fill="#c84c0c" stroke="#000" stroke-width="1" />'
    )
    svg.append(
        f'  <path d="M {castle_x+15} {ground_y} L {castle_x+15} {ground_y-20} A 10 10 0 0 1 {castle_x+35} {ground_y-20} L {castle_x+35} {ground_y} Z" fill="#000" />'
    )
    svg.append(
        f'  <text x="{flag_x - 70}" y="{top_padding - 10}" fill="#f8d820" font-family="monospace" font-weight="bold" font-size="16" stroke="#000" stroke-width="1" opacity="0">'
    )
    svg.append("    CLEAR")
    svg.append(
        f'    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{flag_end:.3f};{flag_end+0.01:.3f};0.98;1" dur="20s" repeatCount="indefinite" />'
    )
    svg.append(
        f'    <animateTransform attributeName="transform" type="translate" values="0,10; 0,10; 0,0; 0,0" keyTimes="0;{flag_end:.3f};{flag_end+0.02:.3f};1" dur="20s" repeatCount="indefinite" />'
    )
    svg.append("  </text>")
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
