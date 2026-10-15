"""A boy crosses a GitHub contribution grid and eats the food on it.

The timing matches a contribution crawl: one cell at a time, a pause on each
bite, and a sprite that stays inside the cell. The boy and the food are original.
"""

from __future__ import annotations

import argparse
import random
import re
import urllib.request
from collections import deque
from pathlib import Path

CELL = 22
GAP = 4
STEP = CELL + GAP
MOVE = 0.24
BITE = 0.62
FOOD_COUNT = 16

THEMES = {
    "light": {
        "file": "eater.svg",
        "bg": "#ffffff",
        "floor": "#ebedf0",
        "walls": ("#9be9a8", "#40c463", "#30a14e", "#216e39"),
    },
    "dark": {
        "file": "eater-dark.svg",
        "bg": "#0d1117",
        "floor": "#161b22",
        "walls": ("#0e4429", "#006d32", "#26a641", "#39d353"),
    },
}
FOODS = ("meat", "apple", "banana", "rice")

DAY = re.compile(r"<td\b[^>]*class=\"[^\"]*ContributionCalendar-day[^\"]*\"[^>]*>", re.I)
ROW_COL = re.compile(r"contribution-day-component-(\d+)-(\d+)")
LEVEL = re.compile(r"data-level=\"(\d)\"")

PALETTE = {
    "H": "#1c1a17",
    "S": "#f3c7a0",
    "E": "#2a241c",
    "W": "#fff8ee",
    "G": "#6f8f4e",
    "P": "#6b4b38",
    "B": "#2b241c",
    "M": "#d98474",
    "C": "#2a241c",
    "R": "#e15a48",
    "T": "#fff6ea",
}

WALK_A = [
    "....HHHHHH......",
    "...HHHHHHHH.....",
    "..HHSSSSSSHH....",
    "..HSSEWWSSSH....",
    "..HSSSSSSSSH....",
    "...SSSMSSSSS....",
    "....SSSSSS......",
    "...GGGGGGGG.....",
    "..GGGGGGGGGG....",
    "..GGGGGGGGGG....",
    "..GGGGGGGGGG....",
    "...PPPP..PPP....",
    "...PPPP..PPP....",
    "...PPPP..PPP....",
    "...BBBB..BBB....",
    "....BB....BB....",
    "................",
]
WALK_B = [
    "....HHHHHH......",
    "...HHHHHHHH.....",
    "..HHSSSSSSHH....",
    "..HSSEWWSSSH....",
    "..HSSSSSSSSH....",
    "...SSSMSSSSS....",
    "....SSSSSS......",
    "...GGGGGGGG.....",
    "..GGGGGGGGGG....",
    "..GGGGGGGGGG....",
    "..GGGGGGGGGG....",
    "..PPPP..PPPP....",
    "..PPPP...PPP....",
    "..PPPP...PPP....",
    "..BBBB...BBB....",
    "...BB.....BB....",
    "................",
]
EAT = [
    "....HHHHHH......",
    "...HHHHHHHH.....",
    "..HHSSSSSSHH....",
    "..HSSCCSSCCSH...",
    "..HSSSSSSSSH....",
    "...SSRRRRSS.....",
    "...SSTTTTSS.....",
    "....SSSSSS......",
    "...GGGGGGGG.....",
    "..GGGGGGGGGG....",
    "..GGGGGGGGGG....",
    "..GGGGGGGGGG....",
    "...PPPPPPPP.....",
    "...PPPPPPPP.....",
    "...BBBBBBBB.....",
    "....BBBBBB......",
    "................",
]


def fetch_calendar(user: str) -> list[list[int]]:
    url = f"https://github.com/users/{user}/contributions"
    request = urllib.request.Request(url, headers={"User-Agent": "conversation-anigraph"})
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
        raise SystemExit(f"No contribution grid found for {user}.")

    cols = max(col for col, _ in found) + 1
    rows = max(row for _, row in found) + 1
    return [[found.get((col, row), 0) for row in range(rows)] for col in range(cols)]


def pixels(frame: list[str]) -> str:
    rects = []
    for y, row in enumerate(frame):
        for x, mark in enumerate(row):
            if mark == ".":
                continue
            rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{PALETTE[mark]}"/>')
    return "".join(rects)


def hero(size: int) -> str:
    sprite_w, sprite_h = 16, 17
    scale = (size * 1.35) / sprite_w
    width = sprite_w * scale
    height = sprite_h * scale
    y_offset = size / 2 - height
    body = f'<g transform="translate({-width / 2:.2f} {y_offset:.2f}) scale({scale:.3f})">'
    walk = f"""
      <g>
        <animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" dur="0.28s" repeatCount="indefinite" calcMode="discrete"/>
        {pixels(WALK_A)}
      </g>
      <g>
        <animate attributeName="opacity" values="0;1;0" keyTimes="0;0.5;1" dur="0.28s" repeatCount="indefinite" calcMode="discrete"/>
        {pixels(WALK_B)}
      </g>
    """
    return body + "{walk}</g>".replace("{walk}", walk), body + pixels(EAT) + "</g>"


def food_art(kind: str, cx: float, cy: float, size: float) -> str:
    radius = size * 0.42
    arts = {
        "meat": f"""
          <ellipse cx="{cx - radius * 0.15:.1f}" cy="{cy + radius * 0.2:.1f}" rx="{radius:.1f}" ry="{radius * 0.42:.1f}" fill="#f4e4c8" transform="rotate(-38 {cx:.1f} {cy:.1f})"/>
          <ellipse cx="{cx + radius * 0.12:.1f}" cy="{cy - radius * 0.02:.1f}" rx="{radius * 0.95:.1f}" ry="{radius * 0.7:.1f}" fill="#c45b2a"/>
          <ellipse cx="{cx + radius * 0.02:.1f}" cy="{cy - radius * 0.18:.1f}" rx="{radius * 0.5:.1f}" ry="{radius * 0.28:.1f}" fill="#e59858"/>
        """,
        "apple": f"""
          <circle cx="{cx:.1f}" cy="{cy + 1:.1f}" r="{radius:.1f}" fill="#e03131"/>
          <circle cx="{cx - radius * 0.28:.1f}" cy="{cy - radius * 0.22:.1f}" r="{radius * 0.22:.1f}" fill="#ff8d86"/>
          <rect x="{cx - 0.7:.1f}" y="{cy - radius - 2.4:.1f}" width="1.4" height="3.2" rx="0.6" fill="#6a4324"/>
          <ellipse cx="{cx + radius * 0.45:.1f}" cy="{cy - radius - 0.4:.1f}" rx="{radius * 0.42:.1f}" ry="{radius * 0.2:.1f}" fill="#5ea33a" transform="rotate(28 {cx + radius * 0.45:.1f} {cy - radius - 0.4:.1f})"/>
        """,
        "banana": f"""
          <path d="M{cx - radius:.1f} {cy + radius * 0.45:.1f} Q{cx:.1f} {cy - radius * 1.15:.1f} {cx + radius:.1f} {cy - radius * 0.15:.1f}" fill="none" stroke="#f2c14b" stroke-width="{radius * 0.72:.1f}" stroke-linecap="round"/>
          <path d="M{cx + radius * 0.82:.1f} {cy - radius * 0.22:.1f} L{cx + radius * 1.15:.1f} {cy + radius * 0.05:.1f}" fill="none" stroke="#8a6230" stroke-width="1.3" stroke-linecap="round"/>
        """,
        "rice": f"""
          <ellipse cx="{cx:.1f}" cy="{cy + radius * 0.35:.1f}" rx="{radius * 1.05:.1f}" ry="{radius * 0.48:.1f}" fill="#f7f3ec"/>
          <path d="M{cx - radius:.1f} {cy + radius * 0.15:.1f} Q{cx:.1f} {cy + radius * 0.85:.1f} {cx + radius:.1f} {cy + radius * 0.15:.1f}" fill="#efe8dc"/>
          <ellipse cx="{cx:.1f}" cy="{cy - radius * 0.05:.1f}" rx="{radius * 0.72:.1f}" ry="{radius * 0.46:.1f}" fill="#fffdf8"/>
          <circle cx="{cx - radius * 0.28:.1f}" cy="{cy - radius * 0.08:.1f}" r="0.7" fill="#f0ebe3"/>
          <circle cx="{cx + radius * 0.22:.1f}" cy="{cy + radius * 0.08:.1f}" r="0.7" fill="#f0ebe3"/>
          <circle cx="{cx:.1f}" cy="{cy - radius * 0.22:.1f}" r="0.55" fill="#f0ebe3"/>
        """,
    }
    return f"""
      <g>
        <animateTransform attributeName="transform" type="translate" values="0 0;0 -1.4;0 0" dur="0.9s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1" keyTimes="0;0.5;1"/>
        {arts[kind]}
      </g>
    """


def neighbors(x: int, y: int, cols: int, rows: int, walls: list[list[bool]], through_walls: bool) -> list[tuple[int, int]]:
    found = []
    for dx, dy in ((1, 0), (0, -1), (0, 1), (-1, 0)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows and (through_walls or not walls[ny][nx]):
            found.append((nx, ny))
    return found


def shortest(start: tuple[int, int], end: tuple[int, int], cols: int, rows: int, walls: list[list[bool]]) -> list[tuple[int, int]] | None:
    queue = deque([start])
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    while queue:
        current = queue.popleft()
        if current == end:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]
        for nxt in neighbors(*current, cols, rows, walls, False):
            if nxt not in parent:
                parent[nxt] = current
                queue.append(nxt)
    return None


def place_food(walls: list[list[bool]], start: tuple[int, int]) -> list[tuple[int, int, str]]:
    rows = len(walls)
    cols = len(walls[0])
    rng = random.Random(7)
    chosen = []
    taken = {start}
    for index in range(FOOD_COUNT):
        x0 = int(index / FOOD_COUNT * cols)
        x1 = max(x0, int((index + 1) / FOOD_COUNT * cols) - 1)
        spots = [
            (x, y)
            for x in range(x0, x1 + 1)
            for y in range(rows)
            if not walls[y][x] and (x, y) not in taken
        ]
        if not spots:
            continue
        spot = rng.choice(spots)
        taken.add(spot)
        chosen.append((spot[0], spot[1], FOODS[index % len(FOODS)]))
    chosen.sort()
    return chosen


def build_trip(walls: list[list[bool]]) -> tuple[list[tuple[int, int]], list[dict]]:
    rows = len(walls)
    cols = len(walls[0])
    empty = [(x, y) for y in range(rows) for x in range(cols) if not walls[y][x]]
    if not empty:
        return [], []
    start = min(empty)
    foods = place_food(walls, start)
    path = [start]
    bites = []
    current = start
    clock = 0.0
    for x, y, kind in foods:
        route = shortest(current, (x, y), cols, rows, walls)
        if not route or len(route) < 2:
            continue
        for step in route[1:]:
            path.append(step)
            clock += MOVE
            if step == (x, y):
                bites.append({"at": step, "kind": kind, "time": clock})
                clock += BITE
        current = (x, y)
    return path, bites


def cell_center(x: int, y: int, offset_y: float) -> tuple[float, float]:
    return (x * STEP + GAP + CELL / 2, y * STEP + GAP + CELL / 2 + offset_y)


def track(events: list[tuple[float, float]], total: float, on_inside: bool) -> tuple[str, str]:
    marks = [(0.0, 0 if on_inside else 1)]
    for start, end in events:
        a = max(0.001, min(0.998, start / total))
        b = max(a + 0.004, min(0.999, end / total))
        marks.append((a, 1 if on_inside else 0))
        marks.append((b, 0 if on_inside else 1))
    marks.append((1.0, 0 if on_inside else 1))
    marks.sort()
    cleaned = []
    for time, value in marks:
        if cleaned and time <= cleaned[-1][0] + 0.0005:
            cleaned[-1] = (time, value)
        else:
            cleaned.append((time, value))
    return (
        ";".join(str(value) for _, value in cleaned),
        ";".join(f"{time:.4f}" for time, _ in cleaned),
    )


def render(columns: list[list[int]], theme: dict) -> str:
    cols = len(columns)
    rows = len(columns[0])
    walls = [[columns[x][y] > 0 for x in range(cols)] for y in range(rows)]
    path, bites = build_trip(walls)
    offset_y = 16
    width = cols * STEP + GAP
    height = rows * STEP + GAP + offset_y + 8

    segments = []
    clock = 0.0
    bite_at = {item["at"]: item for item in bites}
    for index in range(len(path) - 1):
        start, end = path[index], path[index + 1]
        pause = BITE if end in bite_at and abs(bite_at[end]["time"] - (clock + MOVE)) < 0.01 else 0
        # Bite is recorded after the move onto the food, so the pause follows arrival.
        if end in bite_at:
            pause = BITE
        segments.append((start, end, clock, pause))
        clock += MOVE + pause
    total = clock or 1

    frames: list[tuple[float, float, float, int]] = []
    facing = 1
    for start, end, delay, pause in segments:
        sx, sy = cell_center(*start, offset_y)
        ex, ey = cell_center(*end, offset_y)
        if end[0] > start[0]:
            facing = 1
        elif end[0] < start[0]:
            facing = -1
        frames.append((delay / total, sx, sy, facing))
        frames.append(((delay + MOVE) / total, ex, ey, facing))
        if pause:
            frames.append(((delay + MOVE + pause) / total, ex, ey, facing))
    if path:
        fx, fy = cell_center(*path[-1], offset_y)
        frames.append((1, fx, fy, facing))
    frames.sort()
    unique = []
    for frame in frames:
        if not unique or frame[0] > unique[-1][0] + 0.0004:
            unique.append(frame)

    key_times = ";".join(f"{frame[0]:.4f}" for frame in unique)
    positions = ";".join(f"{frame[1]:.1f} {frame[2]:.1f}" for frame in unique)
    scales = ";".join(f"{frame[3]} 1" for frame in unique)

    eat_windows = []
    for start, end, delay, pause in segments:
        if pause and end in bite_at:
            eat_windows.append((delay + MOVE, delay + MOVE + pause))
    eat_values, eat_times = track(eat_windows, total, True)
    walk_values, walk_times = track(eat_windows, total, False)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>A boy eating across the GitHub contribution graph</title>",
        f'<rect width="{width}" height="{height}" fill="{theme["bg"]}"/>',
    ]
    for y in range(rows):
        for x in range(cols):
            px = x * STEP + GAP
            py = y * STEP + GAP + offset_y
            level = columns[x][y]
            color = theme["walls"][min(level, 4) - 1] if level else theme["floor"]
            parts.append(f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>')

    eaten = {}
    for item in bites:
        eaten.setdefault(item["at"], item)
    for (x, y), item in eaten.items():
        cx, cy = cell_center(x, y, offset_y)
        disappear = item["time"] / total
        appear_end = min(0.999, max(0.01, disappear))
        parts.append(
            f'<g><animate attributeName="opacity" values="1;1;0;0;1" '
            f'keyTimes="0;{appear_end:.4f};{min(0.999, appear_end + 0.008):.4f};0.999;1" '
            f'dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete"/>'
            f'{food_art(item["kind"], cx, cy, CELL)}</g>'
        )

    if len(unique) > 1:
        walk_sprite, eat_sprite = hero(CELL)
        parts.append(
            f'''<g>
              <animateTransform attributeName="transform" type="translate" values="{positions}" keyTimes="{key_times}" dur="{total:.2f}s" repeatCount="indefinite" calcMode="linear"/>
              <g>
                <animateTransform attributeName="transform" type="scale" values="{scales}" keyTimes="{key_times}" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete"/>
                <g>
                  <animate attributeName="opacity" values="{walk_values}" keyTimes="{walk_times}" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete"/>
                  {walk_sprite}
                </g>
                <g>
                  <animate attributeName="opacity" values="{eat_values}" keyTimes="{eat_times}" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete"/>
                  {eat_sprite}
                </g>
              </g>
            </g>'''
        )
    parts.append("</svg>\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="rakhmanov-tr")
    parser.add_argument("--out", default="dist")
    args = parser.parse_args()
    columns = fetch_calendar(args.user)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name in ("dragon.svg", "dragon-dark.svg"):
        (out / name).unlink(missing_ok=True)
    for theme in THEMES.values():
        (out / theme["file"]).write_text(render(columns, theme), encoding="utf-8")
    print(f"{args.user}: {len(columns)} weeks -> {out}")


if __name__ == "__main__":
    main()
