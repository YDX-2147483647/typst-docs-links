import json

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

print("digraph links {")

# Set default attributes
print("node [style=filled, fontcolor=white, fillcolor=black, color=transparent]")
print("edge [color=gray]")

# For quick debugging:
# print('layout = "sfdp"')

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
            color_attr = ""
        case c:
            color_attr = f'fillcolor="{c}",'

    title: str = info["title"]

    print(
        f'"{route}" [label="{title}", href="https://typst.app/docs{route}", {color_attr}];'
    )

# Edges
for src_route, info in links.items():
    for dst_route in info["out_links"]:
        # Ignore changelogs (but keep referenced HTML tags)
        if "/changelog/" in src_route:
            continue

        print(f'"{src_route}" -> "{dst_route}";')

print("}")
