import json

with open("links.json", encoding="utf-8") as f:
    links = json.load(f)

print("digraph links {")

# Set default attributes
print('node [color="#239dad", fontcolor="#239dad"]')
print("edge [color=gray]")

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
    print(f'"{route}" [label="{title}", href="https://typst.app/docs{route}"];')

# Edges
for src_route, info in links.items():
    for dst_route in info["out_links"]:
        # Ignore changelogs (but keep referenced HTML tags)
        if "/changelog/" in src_route:
            continue

        print(f'"{src_route}" -> "{dst_route}";')

print("}")
