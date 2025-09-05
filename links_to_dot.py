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
}

with open("links.json", encoding="utf-8") as f:
    links = json.load(f)

dot = Digraph(
    format="svg",
    name="Links",
    node_attr=[
        ("style", "filled"),
        ("fontcolor", "white"),
        ("fillcolor", "black"),
        ("color", "transparent"),
    ],
    edge_attr=[("color", "gray")],
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

    # Select color
    color = None
    for prefix, c in PALETTE.items():
        if route.startswith(prefix):
            color = c
            break
    match color:
        case None:
            color_attr = {}
        case c:
            color_attr = {"fillcolor": c}

    title: str = info["title"]

    dot.node(
        name=route,
        label=title,
        href=f"https://typst.app/docs{route}",
        **color_attr,
    )

# Edges
for src_route, info in links.items():
    for dst_route in info["out_links"]:
        # Ignore changelogs (but keep referenced HTML tags)
        if "/changelog/" in src_route:
            continue

        dot.edge(
            tail_name=src_route,
            head_name=dst_route,
        )

print(dot.source)
