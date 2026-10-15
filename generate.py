"""A boy walks a GitHub contribution graph and eats the food on it.

The calendar and the route follow the same idea as a contribution-graph
animation. The boy and the food are drawn here as their own shapes.
"""

from __future__ import annotations

import argparse
import math
import re
import urllib.request
from pathlib import Path

CELL = 11
GAP = 4
STEP = CELL + GAP
PAD_X = 36
PAD_Y = 46
DURATION = 24
SAMPLE_EVERY = 7
EAT_REACH = 16

THEMES = {
    "light": {
        "file": "eater.svg",
        "bg": "#ffffff",
        "empty": "#ebedf0",
        "levels": ("#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"),
    },
    "dark": {
        "file": "eater-dark.svg",
        "bg": "#0d1117",
        "empty": "#161b22",
        "levels": ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"),
    },
}

FOODS = ("meat", "apple", "banana", "rice")

DAY = re.compile(r"<td\b[^>]*class=\"[^\"]*ContributionCalendar-day[^\"]*\"[^>]*>", re.I)
ROW_COL = re.compile(r"contribution-day-component-(\d+)-(\d+)")
LEVEL = re.compile(r"data-level=\"(\d)\"")


def fetch_calendar(user: str) -> list[list[int]]:
    url = f"https://github.com/users/{user}/contributions"
    request = urllib.request.Request(url, headers={"User-Agent": "conversation-anigraph"})
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", "replace")

    cells: dict[tuple[int, int], int] = {}
    for tag in DAY.findall(html):
        slot = ROW_COL.search(tag)
        level = LEVEL.search(tag)
        if not slot or not level:
            continue
        row, col = int(slot.group(1)), int(slot.group(2))
        cells[(col, row)] = int(level.group(1))

    if not cells:
        raise SystemExit(f"No contribution grid found for {user}.")

    cols = max(col for col, _ in cells) + 1
    rows = max(row for _, row in cells) + 1
    return [[cells.get((col, row), 0) for row in range(rows)] for col in range(cols)]


def center(col: int, row: int) -> tuple[float, float]:
    return (PAD_X + col * STEP + CELL / 2, PAD_Y + row * STEP + CELL / 2)


def bend(start: tuple[float, float], end: tuple[float, float], bulge: float) -> list[tuple[float, float]]:
    c1 = (start[0] + bulge, start[1])
    c2 = (end[0] + bulge, end[1])
    points = []
    for step in range(1, 8):
        t = step / 8
        u = 1 - t
        points.append(
            (
                u**3 * start[0] + 3 * u**2 * t * c1[0] + 3 * u * t**2 * c2[0] + t**3 * end[0],
                u**3 * start[1] + 3 * u**2 * t * c1[1] + 3 * u * t**2 * c2[1] + t**3 * end[1],
            )
        )
    return points[:-1]


def walk(cols: int, rows: int) -> tuple[str, list[tuple[int, int, float]], list[float], float]:
    points: list[tuple[float, float]] = []
    visits: list[tuple[int, int, float]] = []
    row_at: list[float] = []
    commands: list[str] = []

    def push(point: tuple[float, float]) -> None:
        points.append(point)

    for row in range(rows):
        order = list(range(cols) if row % 2 == 0 else range(cols - 1, -1, -1))
        row_at.append(length_of(points))
        for index, col in enumerate(order):
            point = center(col, row)
            if not points:
                commands.append(f"M{point[0]:.1f} {point[1]:.1f}")
            elif index == 0:
                bulge = STEP * 0.95 if row % 2 else -STEP * 0.95
                commands.append(
                    f"C{points[-1][0] + bulge:.1f} {points[-1][1]:.1f} "
                    f"{point[0] + bulge:.1f} {point[1]:.1f} {point[0]:.1f} {point[1]:.1f}"
                )
                points.extend(bend(points[-1], point, bulge))
            else:
                commands.append(f"L{point[0]:.1f} {point[1]:.1f}")
            push(point)
            visits.append((col, row, length_of(points)))

    return " ".join(commands), visits, row_at, length_of(points)


def length_of(points: list[tuple[float, float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def choose_food(visits: list[tuple[int, int, float]]) -> list[tuple[int, int, float, str]]:
    picked = []
    for index, (col, row, dist) in enumerate(visits):
        if index % SAMPLE_EVERY != 3:
            continue
        picked.append((col, row, dist, FOODS[len(picked) % len(FOODS)]))
    return picked


def frames(show) -> str:
    previous = 1 if show(0) else 0
    stops = [f"0%{{opacity:{previous}}}"]
    for step in range(1, 181):
        mark = step / 180
        visible = 1 if show(mark) else 0
        if visible != previous:
            stops.append(f"{mark * 100:.2f}%{{opacity:{previous}}}")
            stops.append(f"{min(100, mark * 100 + 0.04):.2f}%{{opacity:{visible}}}")
            previous = visible
    stops.append(f"100%{{opacity:{previous}}}")
    return "".join(stops)


def boy(eating: bool) -> str:
    mouth = (
        '<ellipse cx="2.1" cy="-29" rx="2.7" ry="2.05" fill="#e15a48"/>'
        '<ellipse cx="2.1" cy="-29.7" rx="1.7" ry="0.55" fill="#fff6ea"/>'
        if eating
        else '<path d="M0.3 -29.5 Q2.3 -30.8 4.2 -29.5" fill="none" stroke="#c9846a" stroke-width="0.8" stroke-linecap="round"/>'
    )
    eyes = (
        '<path d="M-2.5 -31.6 Q-1.3 -32.7 -0.1 -31.6" fill="none" stroke="#2b241c" stroke-width="0.7" stroke-linecap="round"/>'
        '<path d="M1.5 -31.6 Q2.7 -32.7 3.9 -31.6" fill="none" stroke="#2b241c" stroke-width="0.7" stroke-linecap="round"/>'
        if eating
        else '<circle cx="-1.4" cy="-31.2" r="0.7" fill="#2b241c"/>'
        '<circle cx="2.5" cy="-31.2" r="0.7" fill="#2b241c"/>'
    )
    legs = """
      <g class="leg back">
        <rect x="-4.4" y="-14" width="3.3" height="10" rx="1.5" fill="#5a4030"/>
        <ellipse cx="-2.7" cy="-2.4" rx="2.7" ry="1.6" fill="#2b241c"/>
      </g>
      <g class="leg front">
        <rect x="1.1" y="-14" width="3.3" height="10" rx="1.5" fill="#6b4b38"/>
        <ellipse cx="2.8" cy="-2.4" rx="2.7" ry="1.6" fill="#2b241c"/>
      </g>
    """
    return f"""
      <g class="{'bite' if eating else 'bob'}">
        {legs}
        <rect x="-6.3" y="-25" width="12.6" height="12.2" rx="3.2" fill="#6f8f4e"/>
        <circle cx="0.4" cy="-30.2" r="6.3" fill="#f0c29a"/>
        <path d="M-5.2 -31.4 Q0.2 -38.6 6.2 -31.2 Q4.6 -34.6 0.2 -34.8 Q-3.4 -34.8 -5.2 -31.4" fill="#1c1a17"/>
        {eyes}
        {mouth}
      </g>
    """


def food_shape(kind: str, x: float, y: float) -> str:
    shapes = {
        "meat": f"""
          <ellipse cx="{x - 1}" cy="{y + 1}" rx="2.2" ry="1.1" fill="#f3e2c4" transform="rotate(-35 {x} {y})"/>
          <ellipse cx="{x + 0.4}" cy="{y - 0.2}" rx="3.3" ry="2.3" fill="#c46a32"/>
          <ellipse cx="{x + 0.2}" cy="{y - 0.7}" rx="2" ry="1.1" fill="#e39a55"/>
        """,
        "apple": f"""
          <circle cx="{x}" cy="{y + 0.4}" r="3.1" fill="#e23b3b"/>
          <rect x="{x - 0.35}" y="{y - 4.2}" width="0.7" height="1.8" rx="0.3" fill="#6b4a2a"/>
          <ellipse cx="{x + 1.6}" cy="{y - 3.5}" rx="1.5" ry="0.7" fill="#67a143" transform="rotate(30 {x + 1.6} {y - 3.5})"/>
        """,
        "banana": f"""
          <path d="M{x - 3.4} {y + 1.2} Q{x - 1} {y - 3.6} {x + 3.2} {y - 1.2}" fill="none" stroke="#f2c14b" stroke-width="2.4" stroke-linecap="round"/>
          <path d="M{x + 3} {y - 1.3} L{x + 4.1} {y - 0.4}" fill="none" stroke="#8a6a32" stroke-width="0.8" stroke-linecap="round"/>
        """,
        "rice": f"""
          <ellipse cx="{x}" cy="{y + 1.5}" rx="4.2" ry="1.5" fill="#f7f4ee"/>
          <ellipse cx="{x}" cy="{y + 1.5}" rx="4.2" ry="1.5" fill="none" stroke="#ddd6cc" stroke-width="0.6"/>
          <ellipse cx="{x}" cy="{y - 0.2}" rx="2.6" ry="1.8" fill="#fffdf8"/>
          <circle cx="{x - 1}" cy="{y - 0.2}" r="0.35" fill="#f3efe6"/>
          <circle cx="{x + 0.8}" cy="{y + 0.2}" r="0.35" fill="#f3efe6"/>
        """,
    }
    return shapes[kind]


def render(grid: list[list[int]], theme: dict) -> str:
    cols = len(grid)
    rows = len(grid[0])
    width = PAD_X * 2 + cols * CELL + (cols - 1) * GAP
    height = PAD_Y * 2 + rows * CELL + (rows - 1) * GAP
    route, visits, row_at, total = walk(cols, rows)
    foods = choose_food(visits)

    def row_of(mark: float) -> int:
        dist = mark * total
        current = 0
        for index, start in enumerate(row_at):
            if dist + 0.1 >= start:
                current = index
        return current

    def eating(mark: float) -> bool:
        dist = mark * total
        return any(abs(dist - food[2]) <= EAT_REACH for food in foods)

    styles = [
        "rect{shape-rendering:geometricPrecision}",
        ".leg{transform-box:fill-box;transform-origin:50% 0%;animation:step .34s ease-in-out infinite alternate}",
        ".leg.front{animation-delay:-.34s}",
        "@keyframes step{from{transform:rotate(-18deg)}to{transform:rotate(16deg)}}",
        ".bob{animation:bob .34s ease-in-out infinite}",
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-1.5px)}}",
        ".actor{animation-timing-function:linear;animation-duration:"
        f"{DURATION}s;animation-iteration-count:infinite}}",
    ]

    cells = []
    for col, week in enumerate(grid):
        for row, level in enumerate(week):
            color = theme["levels"][min(level, 4)]
            cells.append(
                f'<rect x="{PAD_X + col * STEP}" y="{PAD_Y + row * STEP}" '
                f'width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
            )

    plates = []
    for index, (col, row, dist, kind) in enumerate(foods):
        name = f"f{index}"
        styles.append(f"@keyframes {name}{{{frames(lambda mark, dist=dist: mark * total < dist)}}}")
        x, y = center(col, row)
        plates.append(f'<g class="actor" style="animation-name:{name}">{food_shape(kind, x, y)}</g>')

    def pose(name: str, eating_pose: bool, facing_left: bool) -> str:
        styles.append(
            f"@keyframes {name}{{{frames(lambda mark, eating_pose=eating_pose, facing_left=facing_left: (row_of(mark) % 2 == 1) == facing_left and eating(mark) == eating_pose)}}}"
        )
        mirror = ' transform="scale(-1 1)"' if facing_left else ""
        return (
            f'<g class="actor" style="animation-name:{name}"{mirror}>'
            f"{boy(eating_pose)}</g>"
        )

    rider = f"""
      <g>
        <animateMotion dur="{DURATION}s" repeatCount="indefinite" rotate="0" calcMode="linear">
          <mpath href="#route" xlink:href="#route"/>
        </animateMotion>
        {pose("right-walk", False, False)}
        {pose("right-eat", True, False)}
        {pose("left-walk", False, True)}
        {pose("left-eat", True, True)}
      </g>
    """

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">'
        "<title>A boy eating across the GitHub contribution graph</title>"
        f"<style>{''.join(styles)}</style>"
        f'<rect width="100%" height="100%" fill="{theme["bg"]}"/>'
        f'<defs><path id="route" d="{route}"/></defs>'
        f"{''.join(cells)}{''.join(plates)}{rider}</svg>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="rakhmanov-tr")
    parser.add_argument("--out", default="dist")
    args = parser.parse_args()

    grid = fetch_calendar(args.user)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for stale in ("dragon.svg", "dragon-dark.svg"):
        (out / stale).unlink(missing_ok=True)
    for theme in THEMES.values():
        (out / theme["file"]).write_text(render(grid, theme), encoding="utf-8")
    print(f"{args.user}: {len(grid)} weeks -> {out}")


if __name__ == "__main__":
    main()
