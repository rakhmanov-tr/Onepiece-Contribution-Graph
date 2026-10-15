"""Draw an original dragon across a GitHub contribution graph.

The motion follows the same idea as Platane/snk: read the public contribution
calendar, walk the grid, and publish an animated SVG. The mark itself is a
short tapered dragon, not the snk snake.
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
PAD_X = 48
PAD_Y = 52
DURATION = 18
BODY = 18
SPACING = 4.0
SAMPLE = 8

THEMES = {
    "light": {
        "file": "dragon.svg",
        "bg": "#ffffff",
        "empty": "#ebedf0",
        "levels": ("#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"),
        "ink": "#242220",
        "accent": "#a6844a",
    },
    "dark": {
        "file": "dragon-dark.svg",
        "bg": "#0d1117",
        "empty": "#161b22",
        "levels": ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"),
        "ink": "#f3efe7",
        "accent": "#d4b483",
    },
}

DAY = re.compile(
    r"<td\b[^>]*class=\"[^\"]*ContributionCalendar-day[^\"]*\"[^>]*>",
    re.I,
)
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


def route_d(cols: int, rows: int) -> str:
    start = center(0, 0)
    commands = [f"M{start[0]:.1f} {start[1]:.1f}"]
    for row in range(rows):
        order = list(range(cols) if row % 2 == 0 else range(cols - 1, -1, -1))
        for col in order[1:]:
            x, y = center(col, row)
            commands.append(f"L{x:.1f} {y:.1f}")
        if row + 1 < rows:
            x0, y0 = center(order[-1], row)
            x1, y1 = center(order[-1], row + 1)
            bulge = STEP * 0.95 if row % 2 == 0 else -STEP * 0.95
            commands.append(
                f"C{x0 + bulge:.1f} {y0:.1f} {x1 + bulge:.1f} {y1:.1f} {x1:.1f} {y1:.1f}"
            )
    return " ".join(commands)


def route(cols: int, rows: int) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for row in range(rows):
        order = range(cols) if row % 2 == 0 else range(cols - 1, -1, -1)
        for col in order:
            points.append(center(col, row))
        if row + 1 < rows:
            end_col = cols - 1 if row % 2 == 0 else 0
            bulge = STEP * 0.95 if row % 2 == 0 else -STEP * 0.95
            points.extend(bend(points[-1], center(end_col, row + 1), bulge))
    return points


def resample(points: list[tuple[float, float]], step: float) -> list[tuple[float, float]]:
    samples = [points[0]]
    cursor = step
    walked = 0.0
    for start, end in zip(points, points[1:]):
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        if length == 0:
            continue
        while walked + length >= cursor:
            t = (cursor - walked) / length
            samples.append((start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t))
            cursor += step
        walked += length
    if math.hypot(samples[-1][0] - points[-1][0], samples[-1][1] - points[-1][1]) > 0.4:
        samples.append(points[-1])
    return samples


def length_of(points: list[tuple[float, float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def nearest(x: float, y: float, samples: list[tuple[float, float]]) -> float:
    best_at = 0
    best = float("inf")
    for index, (sx, sy) in enumerate(samples):
        dist = (sx - x) ** 2 + (sy - y) ** 2
        if dist < best:
            best = dist
            best_at = index
    return best_at / max(1, len(samples) - 1)


def body_radius(index: int) -> tuple[float, float]:
    t = index / (BODY - 1)
    rx = 6.6 * (1 - t) ** 0.6 + 2.9
    ry = 3.6 * (1 - t) ** 0.4 + 1.75
    return rx, ry


def render(grid: list[list[int]], theme: dict) -> str:
    cols = len(grid)
    rows = len(grid[0])
    width = PAD_X * 2 + cols * CELL + (cols - 1) * GAP
    height = PAD_Y * 2 + rows * CELL + (rows - 1) * GAP
    samples = resample(route(cols, rows), SAMPLE)
    travel = length_of(samples)
    speed = travel / DURATION

    styles = ["rect{shape-rendering:geometricPrecision}"]

    cells = []
    eaten = 0
    for col, week in enumerate(grid):
        for row, level in enumerate(week):
            x = PAD_X + col * STEP
            y = PAD_Y + row * STEP
            color = theme["levels"][min(level, 4)]
            extra = ""
            if level:
                name = f"e{eaten}"
                eaten += 1
                cut = nearest(*center(col, row), samples) * 100
                after = min(100, cut + 0.2)
                styles.append(
                    f"@keyframes {name}{{0%,{cut:.2f}%{{fill:{color}}}"
                    f"{after:.2f}%,100%{{fill:{theme['empty']}}}}}"
                )
                extra = f' class="eat" style="animation:{name} {DURATION}s linear infinite"'
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"{extra}/>'
            )

    def actor(delay: float, shapes: str) -> str:
        return (
            "<g>"
            f'<animateMotion dur="{DURATION}s" repeatCount="indefinite" rotate="auto" '
            f'begin="{delay:.3f}s" calcMode="linear">'
            '<mpath href="#route" xlink:href="#route"/>'
            "</animateMotion>"
            f"{shapes}</g>"
        )

    lead = (BODY + 1) * SPACING / speed
    parts = []
    for index in range(BODY - 1, -1, -1):
        delay = -lead + (index + 1) * SPACING / speed
        rx, ry = body_radius(index)
        parts.append(
            actor(delay, f'<ellipse rx="{rx:.2f}" ry="{ry:.2f}" fill="{theme["ink"]}"/>')
        )

    parts.append(
        actor(
            -lead,
            f'<g fill="{theme["ink"]}">'
            f'<circle cx="1.2" cy="0" r="6.6"/>'
            f'<polygon points="-1.2,-5.2 -0.2,-18 3.4,-5.6"/>'
            f'<polygon points="-1.2,5.2 -0.2,18 3.4,5.6"/>'
            f'<circle cx="3.4" cy="-1.7" r="1.45" fill="{theme["accent"]}"/>'
            f'<circle cx="3.4" cy="1.7" r="1.45" fill="{theme["accent"]}"/>'
            f"</g>",
        )
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">'
        "<title>Dragon crossing the GitHub contribution graph</title>"
        f"<style>{''.join(styles)}</style>"
        f'<rect width="100%" height="100%" fill="{theme["bg"]}"/>'
        f'<defs><path id="route" d="{route_d(cols, rows)}"/></defs>'
        f"{''.join(cells)}{''.join(parts)}</svg>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="rakhmanov-tr")
    parser.add_argument("--out", default="dist")
    args = parser.parse_args()

    grid = fetch_calendar(args.user)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    filled = sum(level > 0 for week in grid for level in week)
    for theme in THEMES.values():
        (out / theme["file"]).write_text(render(grid, theme), encoding="utf-8")
    print(f"{args.user}: {len(grid)} weeks, {filled} active days -> {out}")


if __name__ == "__main__":
    main()
