import json
from collections import deque
from pathlib import Path
from sys import argv
from typing import Literal

from graphviz import Digraph

BUILD_DIR = Path("build")

FOCUS_PREFIXES: list[str]
"""The focused route prefixes

Routes not starting with any focused prefixes will be contracted.
"""
FOCUS_MODE: Literal["focus", "all"]
"""Focus mode

- focus: Only draw edges whose both ends are focused.
- all: Draw all edges.
"""

match argv[1:]:
    case ["all"] | []:
        FOCUS_PREFIXES = []
        FOCUS_MODE = "all"
    case ["overview"]:
        FOCUS_PREFIXES = ["/tutorial/", "/guides/"]
        FOCUS_MODE = "all"
    case prefixes:
        FOCUS_PREFIXES = prefixes
        FOCUS_MODE = "focus"


PALETTE: dict[str, str] = {
    "/tutorial/": "#dd1fcd",
    "/guides/": "#F4442E",
    # Language
    "/reference/syntax/": "#CACA00",
    "/reference/styling/": "#CACA00",
    "/reference/scripting/": "#CACA00",
    "/reference/context/": "#CACA00",
    # Export
    "/reference/pdf/": "#D999B9",
    "/reference/html/": "#D999B9",
    "/reference/png/": "#D999B9",
    "/reference/svg/": "#D999B9",
    # Library
    "/reference/foundations/": "#FE8A15",
    "/reference/model/": "#E5B25D",
    "/reference/text/": "#585858",
    "/reference/math/": "#3ECAED",
    "/reference/symbols/": "#239dad",
    "/reference/layout/": "#94CF0B",
    "/reference/visualize/": "#1691EF",
    "/reference/introspection/": "#5E55FF",
    "/reference/data-loading/": "#AD30EC",
    # Other
    "/": "#ADADAD",
}
"""Route prefix to color"""

SHAPE: dict[str, str] = {
    "html": "box",
    "func": "ellipse",
    "type": "hexagon",
    "group": "house",
    "category": "trapezium",
    "symbols": "octagon",
}
"""Kind to shape"""


def decide_color(route: str) -> str | None:
    for prefix, c in PALETTE.items():
        if route.startswith(prefix):
            return c
    raise ValueError(f"Failed to decide color for route: {route}")


def should_ignore(route: str) -> bool:
    # Ignore HTML tags and changelogs
    return (
        "/html/" in route
        and (not route.endswith("/html/") or route.endswith("/html/html/"))
        and "/html/elem/" not in route
        and "/html/frame/" not in route
    ) or "/changelog/" in route


def is_focused(route: str) -> bool:
    for prefix in FOCUS_PREFIXES:
        if route.startswith(prefix):
            return True

    return False


def contract(route: str) -> str:
    """Contract the route unless it's focused"""
    if not FOCUS_PREFIXES or is_focused(route):
        return route

    for prefix in PALETTE.keys():
        if route.startswith(prefix):
            return prefix

    raise ValueError(f"Failed to contract the route: {route}")


with (BUILD_DIR / "links.json").open(encoding="utf-8") as f:
    links = json.load(f)

dot = Digraph(
    format="svg",
    graph_attr=[
        (
            "label",
            f"Links under {', '.join(links[r]['title'] for r in FOCUS_PREFIXES)}"
            if FOCUS_PREFIXES is not None
            else "All links",
        ),
        ("labelloc", "t"),
    ],
    node_attr=[
        ("style", "filled"),
        ("fontcolor", "white"),
        ("color", "transparent"),
    ],
    edge_attr=[
        ("penwidth", "1.5"),
    ],
    # For quick debugging:
    # body='layout = "sfdp"\n',
)


# Nodes
for route, info in links.items():
    route: str

    if should_ignore(route):
        continue

    if contract(route) != route:
        continue

    title: str = info["title"]
    kind: str = info["kind"]
    color = decide_color(route)

    dot.node(
        name=route,
        label=title,
        tooltip=f"{title} ({kind})",
        href=f"https://typst.app/docs{route}",
        fillcolor=color,
        shape=SHAPE[kind],
    )

# Edges
# There might be duplicate edges after contraction. Therefore, we keep track of drawn edges.
drawn_edges: deque[tuple[str, str]] = deque()
for src_long_route, src in links.items():
    for dst_long_route in src["out_links"]:
        src_route = contract(src_long_route)
        dst_route = contract(dst_long_route)

        if (
            should_ignore(src_route)
            or should_ignore(dst_route)
            or src_route == dst_route
            or (
                FOCUS_MODE == "focus"
                and not is_focused(src_route)
                and not is_focused(dst_route)
            )
        ):
            continue

        if (src_route, dst_route) in drawn_edges:
            continue
        drawn_edges.append((src_route, dst_route))

        dst = links[dst_route]
        src_color = decide_color(src_route)
        dst_color = decide_color(dst_route)

        dot.edge(
            tail_name=src_route,
            head_name=dst_route,
            tooltip=f"{src['title']} → {dst['title']}",
            # Transparentize and concatenate colors
            color=f"{dst_color}66;0.5:{src_color}66",
        )

print(dot.source)
