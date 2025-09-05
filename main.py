import json
import re
from collections import deque
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BUILD_DIR = Path("build")


@dataclass
class Node:
    title: str
    kind: str
    out_links: list[str]

    def to_dict(self) -> dict:
        return {"title": self.title, "kind": self.kind, "out_links": self.out_links}


def extract_links_from_html(html: str) -> list[str]:
    """Match `<a href="/xxx/">` links"""
    return re.findall(r'<a[^>]+href=["\'](/[^"\'#]+)(?:#[^"\']+)?["\']', html)


def collect_routes(page: dict[str, Any]) -> deque[dict[str, Any]]:
    """Collect current page and all child pages"""
    routes = deque([])
    stack = deque([page])
    while stack:
        p = stack.pop()
        routes.append(p)
        for child in p["children"]:
            stack.append(child)
    return routes


# Extract links
def parse_content(content: str | dict) -> Generator[str]:
    """Yield content strings to be parsed for links.

    The string might be empty.
    """
    if isinstance(content, str):
        yield content
    else:
        yield content["details"]
        yield content.get("description", "")

        for nesting in ["params", "scope", "functions"]:
            for child in content.get(nesting, []):
                yield from parse_content(child)


def main() -> None:
    docs_path = BUILD_DIR / "docs.json"
    with docs_path.open("r", encoding="utf-8") as f:
        docs = json.load(f)

    catalog: dict[str, Node] = {}
    # docs is a list of pages
    for page in docs:
        for p in collect_routes(page):
            route: str = p["route"]
            title: str = p["title"]

            body = p["body"]
            kind = body["kind"]
            content = body["content"]

            links: deque[str] = deque()
            if kind == "category":
                links += {item["route"] for item in content["items"]}
            for part in parse_content(content):
                links += extract_links_from_html(part)

            # Remove duplicates and self reference
            out_links = set(links)
            if route in out_links:
                out_links.remove(route)

            catalog[route] = Node(
                title=title, kind=kind, out_links=list(sorted(out_links))
            )

    links_path = BUILD_DIR / "links.json"
    with links_path.open("w", encoding="utf-8") as f:
        json.dump(
            {k: v.to_dict() for k, v in catalog.items()},
            f,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    main()
