import json

from graphviz import Digraph

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


def decide_color(route: str) -> str | None:
    for prefix, c in PALETTE.items():
        if route.startswith(prefix):
            return c
    raise ValueError(f"Failed to decide color for route: {route}")


with open("links.json", encoding="utf-8") as f:
    links = json.load(f)

dot = Digraph(
    format="svg",
    name="Links",
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

    # Ignore HTML tags and changelogs
    if (
        "/html/" in route
        and not route.endswith("/html/")
        and not route.endswith("/html/html/")
        and "/html/elem/" not in route
        and "/html/frame/" not in route
    ) or "/changelog/" in route:
        continue

    title: str = info["title"]
    color = decide_color(route)

    dot.node(
        name=route,
        label=title,
        href=f"https://typst.app/docs{route}",
        fillcolor=color,
    )

# Edges
for src_route, src in links.items():
    for dst_route in src["out_links"]:
        # Ignore changelogs (but keep referenced HTML tags)
        if "/changelog/" in src_route:
            continue

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
